# main.py
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from auth import token_required, authenticate_user, create_access_token, get_db, get_current_user
from schemas import UserCreate, UserOut, CategoryOut, CategoryCreate, ProductOut, ProductCreate, CartItemOut, \
    CartItemCreate, OrderOut, OrderCreate
from crud import create_user, get_user_by_email, get_products, get_product, add_to_cart, get_cart_items, \
    get_filtered_products, get_categories, create_order, create_category, create_product, update_cart_item
from database import SessionLocal, engine, Base
from fastapi.openapi.utils import get_openapi
import models
import os

Base.metadata.create_all(bind=engine)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()





app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI application",
        version="1.0.0",
        description="JWT Authentication and Authorization",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get('/')
def home():
    return {"info": "Please, inspect into docs"}

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)

@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email}, secret_key=SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/categories", response_model=CategoryOut)
def create_category_endpoint(category: CategoryCreate, db: Session = Depends(get_db)):
    new_category = create_category(db, category)
    if new_category.description is None:
        new_category.description = ""
    return new_category

@app.get("/categories", response_model=List[CategoryOut])
def read_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    categories = get_categories(db, skip=skip, limit=limit)
    for category in categories:
        if category.description is None:
            category.description = ""
    return categories

@app.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.dict().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.delete("/categories/{category_id}", response_model=CategoryOut)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Ensure "not defined" category exists
    not_defined_category = db.query(models.Category).filter(models.Category.name == "not defined").first()
    if not not_defined_category:
        not_defined_category = models.Category(name="not defined",
                                               description="Default category for uncategorized products")
        db.add(not_defined_category)
        db.commit()
        db.refresh(not_defined_category)

    # Reassign products to "not defined" category
    db.query(models.Product).filter(models.Product.category_id == category_id).update(
        {"category_id": not_defined_category.id})
    db.commit()

    # Delete the category
    db.delete(db_category)
    db.commit()
    return db_category

@app.post("/products", response_model=ProductOut)
def create_product_endpoint(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, product)

@app.get("/products", response_model=List[ProductOut])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=ProductOut)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@app.delete("/products/{product_id}", response_model=ProductOut)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return db_product

@app.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.post("/cart", response_model=CartItemOut)
def create_cart_item(cart_item: CartItemCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = token_required(token, db)
    user_id = payload.get("sub")
    return add_to_cart(db, user_id=user_id, item=cart_item)


@app.post("/orders", response_model=OrderOut)
def create_order_endpoint(order: OrderCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = token_required(token, db)
    user_id = payload.get("sub")
    return create_order(db, user_id=user_id, order=order)

@app.get("/products/filter", response_model=List[ProductOut])
def filter_products(
    category_id: int = None,
    min_price: int = None,
    max_price: int = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return get_filtered_products(db, category_id, min_price, max_price, skip, limit)




def get_cart_details(db: Session, user_id: int):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    total_quantity = sum(item.quantity for item in cart_items)
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    return {
        "items": cart_items,
        "total_quantity": total_quantity,
        "total_price": total_price
    }

@app.post("/cart/items", response_model=CartItemOut)
def add_to_cart_endpoint(item: CartItemCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = token_required(token, db)
    user_id = payload.get("sub")
    return add_to_cart(db, user_id=user_id, item=item)

@app.put("/cart/items/{item_id}", response_model=CartItemOut)
def update_cart_item_endpoint(item_id: int, quantity: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = token_required(token, db)
    user_id = payload.get("sub")
    updated_item = update_cart_item(db, user_id=user_id, item_id=item_id, quantity=quantity)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return updated_item

@app.get("/cart", response_model=List[CartItemOut])
def read_cart_items(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = token_required(token, db)
    user_id = payload.get("sub")
    return get_cart_items(db, user_id=user_id)


@app.post("/logout")
def logout(current_user: models.User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}