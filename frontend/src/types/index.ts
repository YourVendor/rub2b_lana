export interface CompanyItem {
  id: number;
  company_id: number;
  identifier: string;
  ean13?: string;
  name: string;
  unit_id?: number;
  brand?: string | null;
  rrprice: number;
  microwholeprice: number;
  mediumwholeprice: number;
  maxwholeprice: number;
  stock: number;
}

export interface Company {
  id: number;
  name: string;
  inn: string;
}

export interface Price {
  goods_ean13: string;
  company_id: number;
  price_type: string;
  price: number;
}

export interface Goods {
  ean13: string;
  name: string;
  unit_id: number;
  description?: string;
  category?: string;
  brand?: string | null;
  stock: number;
  prices: Price[];
}

export interface Config {
  company_id: number;
  identifier_column: string;
  ean13_column: string;
  name_column: string;
  unit_column: string;
  brand_column: string; // Новое поле
  rrprice_column: string;
  microwholeprice_column: string;
  mediumwholeprice_column: string;
  maxwholeprice_column: string;
  stock_column: string;
  skip_first_row: boolean;
  update_missing: string;
  update_name: boolean;
}