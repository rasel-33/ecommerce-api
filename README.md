# FastAPI E-commerce Application

This project is a FastAPI-based e-commerce application that includes user authentication, product management, cart management, and order processing. The application uses PostgreSQL as the database.

## Features

- User registration and login with JWT authentication
- Product management (CRUD operations)
- Category management (CRUD operations)
- Cart management
- Order processing
- Filtering products by category and price range

## Requirements

- Python 3.12+
- PostgreSQL
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- python-jose
- passlib
- python-dotenv

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/fastapi-ecommerce.git
    cd fastapi-ecommerce
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the environment variables**:
    Create a `.env` file in the root directory and add the following variables:
    ```env
    DATABASE_URL=postgresql://username:password@localhost/dbname
    SECRET_KEY=your_secret_key
    ```

5. **Set up PostgreSQL**:
    - Install PostgreSQL if not already installed.
    - Create a new database and user:
        ```sql
        CREATE DATABASE fastapi_ecommerce;
        CREATE USER ecommerce_user WITH PASSWORD 'yourpassword';
        GRANT ALL PRIVILEGES ON DATABASE fastapi_ecommerce TO ecommerce_user;
        ```

6. **Run the database migrations**:
    ```bash
    alembic upgrade head
    ```

## Running the Application

1. **Start the FastAPI application**:
    ```bash
    uvicorn main:app --reload
    ```

2. **Access the API documentation**:
    Open your browser and go to `http://localhost:8000/docs` to see the interactive API documentation.

## Project Structure

- `main.py`: The main entry point of the application.
- `auth.py`: Contains authentication-related functions and dependencies.
- `crud.py`: Contains CRUD operations for the database models.
- `models.py`: Defines the database models using SQLAlchemy.
- `schemas.py`: Defines the Pydantic models for request and response validation.
- `database.py`: Sets up the database connection and session.
- `alembic/`: Contains the database migration scripts.

## API Endpoints

### Authentication

- `POST /register`: Register a new user.
- `POST /login`: Login and obtain a JWT token.

### Categories

- `POST /categories`: Create a new category.
- `GET /categories`: Get a list of categories.
- `PUT /categories/{category_id}`: Update a category.
- `DELETE /categories/{category_id}`: Delete a category.

### Products

- `POST /products`: Create a new product.
- `GET /products`: Get a list of products.
- `GET /products/{product_id}`: Get a product by ID.
- `PUT /products/{product_id}`: Update a product.
- `DELETE /products/{product_id}`: Delete a product.
- `GET /products/filter`: Filter products by category and price range.

### Cart

- `POST /cart`: Add an item to the cart.
- `GET /cart`: Get the items in the cart.
- `PUT /cart/items/{item_id}`: Update the quantity of a cart item.

### Orders

- `POST /orders`: Create a new order.
