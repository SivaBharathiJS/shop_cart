from sqlalchemy.orm import Session
from models import Customer, Product, Sale, SaleItem
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)
def create_customer(db: Session, data):
    logger.info("Creating new customer: %s", data.company_name)

    try:
        customer = Customer(**data.dict())
        db.add(customer)
        db.commit()
        db.refresh(customer)

        logger.info("Customer created successfully with ID: %s", customer.id)
        return customer

    except Exception as e:
        db.rollback()
        logger.error("Failed to create customer: %s", str(e))
        raise Exception("Unable to create customer at this time")

def create_product(db: Session, data):
    logger.info("Adding new product: %s", data.product_name)

    if data.stock_quantity < 0:
        raise ValueError("Stock quantity cannot be negative")

    try:
        product = Product(**data.dict())
        db.add(product)
        db.commit()

        logger.info("Product added successfully: %s", data.product_name)
        return product

    except Exception as e:
        db.rollback()
        logger.error("Product creation failed: %s", str(e))
        raise Exception("Unable to add product")


def create_sale(db: Session, data):
    logger.info("Starting sale for customer_id: %s", data.customer_id)

    # 🔹 Validate customer
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        logger.warning("Customer not found: %s", data.customer_id)
        raise ValueError("Customer does not exist")

    try:
        total_amount = 0
        sale = Sale(customer_id=data.customer_id, total_amount=0)
        db.add(sale)
        db.commit()
        db.refresh(sale)

        logger.info("Sale record created with ID: %s", sale.id)

        for item in data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()

            # 🔹 Product validation
            if not product:
                raise ValueError(f"Product ID {item.product_id} not found")

            if product.stock_quantity < item.quantity:
                raise ValueError(
                    f"Insufficient stock for {product.product_name}. "
                    f"Available: {product.stock_quantity}, Requested: {item.quantity}"
                )

            item_total = product.price * item.quantity
            total_amount += item_total

            logger.info(
                "Adding item -> Product: %s | Qty: %s | Price: %s",
                product.product_name, item.quantity, product.price
            )

            # 🔹 Reduce stock
            product.stock_quantity -= item.quantity

            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=product.price
            )
            db.add(sale_item)

        # 🔹 Update total
        sale.total_amount = total_amount
        db.commit()

        logger.info(
            "Sale completed successfully | Sale ID: %s | Total Amount: %.2f",
            sale.id, total_amount
        )

        return sale

    except Exception as e:
        db.rollback()
        logger.error("Sale failed: %s", str(e))
        raise Exception(f"Sale creation failed: {str(e)}")
