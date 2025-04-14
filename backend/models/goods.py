class Goods(Base):
    __tablename__ = "goods"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    price = Column(Integer)
    description = Column(String(500), nullable=True)

class GoodsIn(BaseModel):
    name: str
    price: int
    description: Optional[str] = None