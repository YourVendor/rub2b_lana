# backend/routers/moderator.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.database import get_db
from backend.models import CompanyItem, Goods, Prices, PriceHistory, Unit, Company, EmployeeCompany, User
import pandas as pd
import tempfile
import json
import io
from datetime import datetime, timedelta
import os
import logging
from backend.utils import PriceUploadConfig, ConfirmUploadConfig, CompanyItemUpdate, get_current_user, oauth2_scheme

logger = logging.getLogger("backend.moderator")
router = APIRouter(tags=["moderator"])

@router.post("/upload-price", operation_id="moderator_upload_price")
async def upload_price(
    file: UploadFile = File(...),
    config: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Received file: {file.filename}")
    try:
        config_data = json.loads(config)
        config_obj = PriceUploadConfig(**config_data)
        logger.info(f"Parsed config: {config_obj}")

        if user.role != "moderator":
            logger.error(f"User {user.login} is not a moderator")
            raise HTTPException(status_code=403, detail="Только для модераторов")

        employee = db.query(EmployeeCompany).filter(
            EmployeeCompany.user_id == user.id,
            EmployeeCompany.company_id == config_obj.company_id
        ).first()
        if not employee:
            logger.error(f"Moderator {user.login} not associated with company {config_obj.company_id}")
            raise HTTPException(status_code=403, detail="Вы не связаны с этой компанией")

        company = db.query(Company).filter(Company.id == config_obj.company_id).first()
        if not company:
            logger.error(f"Company with id {config_obj.company_id} not found")
            raise HTTPException(status_code=404, detail=f"Компания с id {config_obj.company_id} не найдена")

        file_content = await file.read()
        excel_buffer = io.BytesIO(file_content)
        df = pd.read_excel(excel_buffer)
        logger.info(f"Excel columns: {list(df.columns)}")

        required_columns = [
            config_obj.identifier_column,
            config_obj.ean13_column,
            config_obj.name_column,
            config_obj.unit_column,
            config_obj.rrprice_column,
            config_obj.microwholeprice_column,
            config_obj.mediumwholeprice_column,
            config_obj.maxwholeprice_column,
            config_obj.stock_column
        ]
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            logger.error(f"Missing columns in Excel: {missing}")
            raise HTTPException(status_code=400, detail=f"Отсутствуют колонки: {missing}")

        units_in_db = {unit.name for unit in db.query(Unit).all()}
        units_in_file = set(df[config_obj.unit_column].dropna().astype(str))
        unknown_units = list(units_in_file - units_in_db)

        ignored_rows = []
        if config_obj.update_missing == "skip":
            df = df.dropna(subset=[config_obj.rrprice_column, config_obj.microwholeprice_column,
                                  config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column])
            ignored_rows = df[df[[config_obj.rrprice_column, config_obj.microwholeprice_column,
                                  config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]].isna().any(axis=1)].to_dict(orient='records')
        elif config_obj.update_missing == "zero":
            df[[config_obj.rrprice_column, config_obj.microwholeprice_column,
                config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]] = df[[
                config_obj.rrprice_column, config_obj.microwholeprice_column,
                config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]].fillna(0)
        elif config_obj.update_missing == "null":
            pass
        elif config_obj.update_missing == "ignore":
            ignored_rows = df[df[[config_obj.rrprice_column, config_obj.microwholeprice_column,
                                  config_obj.mediumwholeprice_column, config_obj.maxwholeprice_column]].isna().any(axis=1)].to_dict(orient='records')

        preview = df.to_dict(orient="records")
        logger.info(f"Preview rows: {len(preview)}")

        return {
            "status": "success",
            "columns": list(df.columns),
            "preview": preview,
            "unknown_units": unknown_units,
            "ignored_rows": ignored_rows
        }
    except HTTPException as e:
        logger.error(f"HTTP error in upload_price: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm-upload", operation_id="moderator_confirm_upload")
async def confirm_upload(
    file: UploadFile = File(...),
    config: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Received confirm-upload for file: {file.filename}")
    try:
        config_data = json.loads(config)
        config_obj = ConfirmUploadConfig(**config_data)
        logger.info(f"Parsed config: {config_obj}")
        logger.info(f"Confirmed items: {config_obj.confirmed_items}")

        if user.role != "moderator":
            raise HTTPException(status_code=403, detail="Только для модераторов")
        employee = db.query(EmployeeCompany).filter(
            EmployeeCompany.user_id == user.id,
            EmployeeCompany.company_id == config_obj.company_id
        ).first()
        if not employee:
            raise HTTPException(status_code=403, detail="Вы не связаны с этой компанией")
        company = db.query(Company).filter(Company.id == config_obj.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail=f"Компания с id {config_obj.company_id} не найдена")

        file_content = await file.read()
        excel_buffer = io.BytesIO(file_content)
        df = pd.read_excel(excel_buffer)
        if config_obj.skip_first_row:
            df = df.iloc[1:]
        df[config_obj.identifier_column] = df[config_obj.identifier_column].astype(str)
        logger.info(f"Excel rows: {len(df)}, columns: {list(df.columns)}")

        if len(df) > 10000:
            raise HTTPException(status_code=400, detail="Слишком много позиций, максимум 10,000")

        units_in_db = {unit.name: unit.id for unit in db.query(Unit).all()}
        logger.info(f"Units in DB: {units_in_db}")
        non_uploaded_items = []
        processed_rows = []

        identifier_counts = df[config_obj.identifier_column].value_counts()
        duplicates = identifier_counts[identifier_counts > 1].index.tolist()
        selected_duplicates = {}
        for dup in duplicates:
            dup_rows = df[df[config_obj.identifier_column] == dup].to_dict("records")
            selected_row = next(
                (row for row in dup_rows if row.get("selected")),
                dup_rows[-1]
            )
            selected_duplicates[dup] = selected_row
            non_uploaded_items.extend(
                [{"identifier": dup, "reason": "Дубликат identifier, выбрана другая строка", **row}
                 for row in dup_rows if row != selected_row]
            )
        logger.info(f"Duplicates found: {duplicates}")

        logger.info(f"Processing {len(df)} rows")
        for _, row in df.iterrows():
            identifier = str(row[config_obj.identifier_column])
            unit = str(row[config_obj.unit_column]) if row[config_obj.unit_column] else None
            prices = {
                "rrprice": row[config_obj.rrprice_column],
                "microwholeprice": row[config_obj.microwholeprice_column],
                "mediumwholeprice": row[config_obj.mediumwholeprice_column],
                "maxwholeprice": row[config_obj.maxwholeprice_column]
            }
            stock = row[config_obj.stock_column]
            name = str(row[config_obj.name_column]) if row[config_obj.name_column] else None
            ean13 = row.get(config_obj.ean13_column, None)
            logger.info(f"Processing row: identifier={identifier}, unit={unit}, ean13={ean13}")

            if any(price is not None and price < 0 for price in prices.values()):
                non_uploaded_items.append({
                    "identifier": identifier, "reason": "Отрицательная цена", **row.to_dict()
                })
                logger.info(f"Rejected: {identifier} - Отрицательная цена")
                continue
            if any(price == 0 or pd.isna(price) for price in prices.values()):
                if config_data.get("zero_price_action", "ignore") == "error":
                    non_uploaded_items.append({
                        "identifier": identifier, "reason": "Пустая/нулевая цена", **row.to_dict()
                    })
                    logger.info(f"Rejected: {identifier} - Пустая/нулевая цена")
                continue

            mapped_unit = config_obj.unit_mappings.get(unit, unit)
            if mapped_unit == "ignore" or mapped_unit not in units_in_db:
                non_uploaded_items.append({
                    "identifier": identifier, "reason": f"Неизвестная единица измерения: {unit}", **row.to_dict()
                })
                logger.info(f"Rejected: {identifier} - Неизвестная единица измерения: {unit}")
                continue
            unit_id = units_in_db[mapped_unit]

            if ean13 is not None:
                ean13_str = str(ean13).strip()
                if not (len(ean13_str) == 13 and ean13_str.isdigit()):
                    non_uploaded_items.append({
                        "identifier": identifier, "reason": f"Невалидный EAN-13: {ean13}", **row.to_dict()
                    })
                    logger.info(f"Rejected: {identifier} - Невалидный EAN-13: {ean13}")
                    continue
                ean13 = ean13_str

            existing_item = db.query(CompanyItem).filter(
                and_(CompanyItem.company_id == config_obj.company_id, CompanyItem.identifier == identifier)
            ).first()

            if existing_item:
                ean13_decision = config_obj.ean13_decisions.get(identifier, "keep")
                if ean13_decision == "update" and ean13:
                    existing_item.ean13 = ean13
                if config_obj.update_name:
                    existing_item.name = name
                existing_item.rrprice = prices["rrprice"]
                existing_item.microwholeprice = prices["microwholeprice"]
                existing_item.mediumwholeprice = prices["mediumwholeprice"]
                existing_item.maxwholeprice = prices["maxwholeprice"]
                existing_item.stock = stock
                processed_rows.append({"identifier": identifier, "action": "updated"})
                logger.info(f"Updated: {identifier}")
            else:
                new_item = CompanyItem(
                    company_id=config_obj.company_id,
                    identifier=identifier,
                    name=name,
                    ean13=ean13,
                    unit_id=unit_id,
                    rrprice=prices["rrprice"],
                    microwholeprice=prices["microwholeprice"],
                    mediumwholeprice=prices["mediumwholeprice"],
                    maxwholeprice=prices["maxwholeprice"],
                    stock=stock
                )
                db.add(new_item)
                processed_rows.append({"identifier": identifier, "action": "added"})
                logger.info(f"Added: {identifier}")

        existing_identifiers = db.query(CompanyItem.identifier).filter(
            CompanyItem.company_id == config_obj.company_id
        ).all()
        existing_identifiers = {x[0] for x in existing_identifiers}
        file_identifiers = set(df[config_obj.identifier_column])
        missing_identifiers = existing_identifiers - file_identifiers
        missing_processed = []
        for identifier in missing_identifiers:
            item = db.query(CompanyItem).filter(
                and_(CompanyItem.company_id == config_obj.company_id, CompanyItem.identifier == identifier)
            ).first()
            if config_obj.update_missing == "zero":
                item.stock = 0
                missing_processed.append({"identifier": identifier, "action": "zeroed"})
            elif config_obj.update_missing == "null":
                item.stock = None
                item.rrprice = None
                item.microwholeprice = None
                item.mediumwholeprice = None
                item.maxwholeprice = None
                missing_processed.append({"identifier": identifier, "action": "nulled"})
            else:
                missing_processed.append({"identifier": identifier, "action": "ignored"})
        logger.info(f"Missing identifiers processed: {len(missing_processed)}")

        db.commit()

        error_file = None
        message = "Обработка завершена успешно, ошибок нет"
        if non_uploaded_items:
            error_df = pd.DataFrame(non_uploaded_items)
            logger.info(f"Non-uploaded items: {len(non_uploaded_items)}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                error_df.to_excel(tmp.name, index=False)
                error_file = os.path.basename(tmp.name)
            message = f"Обработка завершена, найдено ошибок: {len(non_uploaded_items)}"
        else:
            logger.info("No non-uploaded items to save")

        return {
            "status": "success",
            "message": message,
            "updated": len([r for r in processed_rows if r["action"] == "updated"]),
            "added": len([r for r in processed_rows if r["action"] == "added"]),
            "ignored": len([r for r in processed_rows if r["action"] == "ignored"]),
            "missing_processed": missing_processed,
            "error_file": f"/download/{error_file}" if error_file else None
        }
    except HTTPException as e:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in confirm_upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company-items/{company_id}", operation_id="moderator_get_company_items")
def get_company_items(company_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if user.role not in ["moderator", "admin"]:
            raise HTTPException(status_code=403, detail="Только для модераторов или админов")
        items = db.query(CompanyItem).filter(CompanyItem.company_id == company_id).all()
        return [
            {
                "id": item.id,
                "company_id": item.company_id,
                "identifier": item.identifier,
                "ean13": item.ean13,
                "name": item.name,
                "unit_id": item.unit_id,
                "rrprice": item.rrprice,
                "microwholeprice": item.microwholeprice,
                "mediumwholeprice": item.mediumwholeprice,
                "maxwholeprice": item.maxwholeprice,
                "stock": item.stock
            }
            for item in items
        ]
    except Exception as e:
        logger.error(f"Ошибка в get_company_items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/company-item/{item_id}", operation_id="moderator_update_company_item")
async def update_company_item(
    item_id: int,
    item_data: CompanyItemUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Updating company item {item_id} with data: {item_data}")
    try:
        if user.role != "moderator":
            raise HTTPException(status_code=403, detail="Только для модераторов")
        
        item = db.query(CompanyItem).filter(CompanyItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Товар не найден")
        
        for key, value in item_data.model_dump(exclude_unset=True).items():
            if key == "price_type":
                continue
            setattr(item, key, value)
        
        if item_data.price_type and item_data.base_price is not None:
            price = db.query(Prices).filter(
                Prices.goods_ean13 == item.ean13,
                Prices.company_id == item.company_id,
                Prices.price_type == item_data.price_type
            ).first()
            if price:
                db.add(PriceHistory(
                    price_id=price.id,
                    price_type=item_data.price_type,
                    price=item_data.base_price,
                    recorded_at=datetime.utcnow()
                ))
                price.price = item_data.base_price
            else:
                new_price = Prices(
                    goods_ean13=item.ean13,
                    company_id=item.company_id,
                    price_type=item_data.price_type,
                    price=item_data.base_price
                )
                db.add(new_price)
        
        db.commit()
        db.refresh(item)
        
        return {
            "id": item.id,
            "company_id": item.company_id,
            "identifier": item.identifier,
            "ean13": item.ean13,
            "name": item.name,
            "unit_id": item.unit_id,
            "base_price": item_data.base_price,
            "stock": item.stock
        }
    except Exception as e:
        logger.error(f"Ошибка в update_company_item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/average-price/{price_id}", operation_id="moderator_get_average_price")
def get_average_price(price_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if user.role not in ["moderator", "admin"]:
            raise HTTPException(status_code=403, detail="Только для модераторов или админов")
        week_ago = datetime.utcnow() - timedelta(days=7)
        prices = db.query(PriceHistory).filter(
            PriceHistory.price_id == price_id,
            PriceHistory.recorded_at >= week_ago
        ).all()
        if not prices:
            return {"average_price": 0}
        avg_price = sum(p.price for p in prices) / len(prices)
        return {"average_price": avg_price}
    except Exception as e:
        logger.error(f"Ошибка в get_average_price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies", operation_id="moderator_get_companies")
async def get_companies(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    companies = db.query(Company).join(EmployeeCompany).filter(EmployeeCompany.user_id == user.id).all()
    return Response(
        content=json.dumps([{"id": c.id, "name": c.name, "inn": c.inn} for c in companies], ensure_ascii=False),
        media_type="application/json; charset=utf-8"
    )

@router.get("/units", operation_id="moderator_get_units")
async def get_units(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    units = db.query(Unit).all()
    return Response(
        content=json.dumps([{"id": u.id, "name": u.name} for u in units], ensure_ascii=False),
        media_type="application/json; charset=utf-8"
    )

@router.get("/download/{filename}", operation_id="moderator_download_file")
async def download_file(filename: str):
    file_path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=filename)

@router.post("/update-main-catalog", operation_id="moderator_update_main_catalog")
async def update_main_catalog(data: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    logger.info(f"Updating main catalog for company_id: {data.get('company_id')}")
    try:
        if user.role not in ["moderator", "admin"]:
            raise HTTPException(status_code=403, detail="Только для модераторов или админов")

        company_id = data.get("company_id")
        ignore_items = set(data.get("ignore_items", []))
        add_new_items = data.get("add_new_items", False)
        items = data.get("items", [])

        updated = 0
        added = 0
        ignored = 0

        for item in items:
            if item["id"] in ignore_items:
                ignored += 1
                continue

            good = db.query(Goods).filter(Goods.ean13 == item["ean13"]).first()

            if good:
                good.name = item["name"]
                good.unit_id = item["unit_id"]
                good.stock = item["stock"]
                updated += 1
            elif add_new_items:
                new_good = Goods(
                    ean13=item["ean13"],
                    name=item["name"],
                    unit_id=item["unit_id"],
                    stock=item["stock"]
                )
                db.add(new_good)
                added += 1
                good = new_good

            if good:
                price_types = ["rrprice", "microwholeprice", "mediumwholeprice", "maxwholeprice"]
                for price_type in price_types:
                    if item.get(price_type):
                        price = db.query(Prices).filter(
                            Prices.goods_ean13 == item["ean13"],
                            Prices.company_id == company_id,
                            Prices.price_type == price_type
                        ).first()
                        if price and price.price != item[price_type]:
                            db.add(PriceHistory(
                                price_id=price.id,
                                price_type=price_type,
                                price=price.price,
                                recorded_at=datetime.utcnow()
                            ))
                            price.price = item[price_type]
                        elif not price:
                            new_price = Prices(
                                goods_ean13=item["ean13"],
                                company_id=company_id,
                                price_type=price_type,
                                price=item[price_type]
                            )
                            db.add(new_price)

        db.commit()
        return {"updated": updated, "added": added, "ignored": ignored}
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка в update_main_catalog: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))