from sqlalchemy import Column, Integer, String, ForeignKey, Float, BigInteger
import uuid

from rds.utils.base import Base, GUID


class Product(Base):
    __tablename__ = 'products'

    id = Column(GUID, primary_key=True, default=uuid.uuid4, unique=True, nullable=False)    
    store_id = Column(GUID, ForeignKey('stores.id'), nullable=False)
    product_id = Column(BigInteger)
    name = Column(String)
    type = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    length = Column(Integer)
    weight = Column(Float)
    price = Column(Integer)


