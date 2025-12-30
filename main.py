from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models, schemas, views
from db import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shop Cart Sales API")

@app.post("/customers")
def add_customer(data: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return views.create_customer(db, data)

@app.post("/products")
def add_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    return views.create_product(db, data)

@app.post("/sales")
def create_sale(data: schemas.SaleCreate, db: Session = Depends(get_db)):
    return views.create_sale(db, data)

@app.get("/invoice/{sale_id}")
def get_invoice(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    items = db.query(models.SaleItem).filter(models.SaleItem.sale_id == sale_id).all()
    return {
        "sale_id": sale.id,
        "total": sale.total_amount,
        "items": items
    }
