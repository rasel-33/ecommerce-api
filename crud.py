# crud.py
from sqlalchemy.orm import Session

import models
from models import User, Category, Product, CartItem, Order, Cart
from schemas import UserCreate, CategoryCreate, ProductCreate, CartItemCreate, OrderCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    create_cart(db, db_user.id)
    return db_user

# crud.py
def create_category(db: Session, category: CategoryCreate):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Product).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def add_to_cart(db: Session, user_id: int, item: CartItemCreate):
    db_item = CartItem(user_id=user_id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_cart_items(db: Session, user_id: int):
    return db.query(CartItem).filter(CartItem.user_id == user_id).all()

def update_cart_item(db: Session, user_id: int, item_id: int, quantity: int):
    db_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user_id).first()
    if db_item:
        db_item.quantity = quantity
        db.commit()
        db.refresh(db_item)
    return db_item

def create_cart(db: Session, user_id: int):
    db_cart = Cart(user_id=user_id)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def get_cart_details(db: Session, user_id: int):
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    total_quantity = sum(item.quantity for item in cart_items)
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    return {
        "items": cart_items,
        "total_quantity": total_quantity,
        "total_price": total_price
    }

def create_order(db: Session, user_id: int, order: OrderCreate):
    db_order = Order(user_id=user_id, **order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

# crud.py
def get_filtered_products(
    db: Session,
    category_id: int = None,
    min_price: int = None,
    max_price: int = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(models.Product)
    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    return query.offset(skip).limit(limit).all()

def get_categories(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Category).offset(skip).limit(limit).all()