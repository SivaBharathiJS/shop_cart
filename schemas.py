from pydantic import BaseModel
from typing import List

class CustomerCreate(BaseModel):
    company_name: str
    contact_number: str

class ProductCreate(BaseModel):
    product_name: str
    price: float
    stock_quantity: int

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int

class SaleCreate(BaseModel):
    customer_id: int
    items: List[SaleItemCreate]
