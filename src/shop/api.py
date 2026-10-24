import asyncio
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shop.database import get_session, init_db
from shop.models import Product, Category
from shop.repositories import ProductRepository, CategoryRepository
from shop.services import ShopService
from shop.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    CategoryCreate,
    CategoryResponse,
    PurchaseRequest,
    StockSummaryResponse,
)
from shop.exceptions import ProductNotFoundError, InsufficientStockError
from shop.external_api import fetch_multiple_products_async

app = FastAPI(title="E-Commerce REST API", version="1.0.0")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
async def root():
    return {"message": "E-Commerce REST API is running"}


# 1. GET /products (з query parameter category_id)
@app.get("/products", response_model=list[ProductResponse])
async def get_products(category_id: int | None = None, session: Session = Depends(get_session)):
    repo = ProductRepository(session)
    return repo.get_all(category_id=category_id)


# 2. GET /products/{id} (path parameter)
@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, session: Session = Depends(get_session)):
    repo = ProductRepository(session)
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


# 3. POST /products
@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, session: Session = Depends(get_session)):
    repo = ProductRepository(session)
    product = Product(**data.model_dump())
    return repo.add(product)


# 4. PATCH /products/{id}
@app.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, data: ProductUpdate, session: Session = Depends(get_session)):
    repo = ProductRepository(session)
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(product, field, value)

    session.commit()
    session.refresh(product)
    return product


# 5. DELETE /products/{id}
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, session: Session = Depends(get_session)):
    repo = ProductRepository(session)
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    repo.delete(product)


# GET /categories/{id}/products
@app.get("/categories/{category_id}/products", response_model=list[ProductResponse])
async def get_category_products(category_id: int, session: Session = Depends(get_session)):
    cat_repo = CategoryRepository(session)
    if not cat_repo.get_by_id(category_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    prod_repo = ProductRepository(session)
    return prod_repo.get_all(category_id=category_id)


# POST /products/{id}/purchase
@app.post("/products/{product_id}/purchase", response_model=ProductResponse)
async def purchase_product(product_id: int, req: PurchaseRequest, session: Session = Depends(get_session)):
    service = ShopService(session)
    try:
        return service.purchase_product(product_id, req.quantity)
    except ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    except InsufficientStockError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Batch endpoint для асинхронних запитів з Timeout
@app.post("/products/batch-fetch")
async def batch_fetch_products(product_ids: list[int]):
    try:
        return await asyncio.wait_for(
            fetch_multiple_products_async("http://127.0.0.1:8000", product_ids),
            timeout=10.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Batch operation timed out")


@app.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, session: Session = Depends(get_session)):
    repo = CategoryRepository(session)
    category = Category(**data.model_dump())
    return repo.add(category)

@app.get("/products", response_model=list[ProductResponse])
async def get_products(
    category_id: int | None = None,
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    repo = ProductRepository(session)
    products = repo.get_all(category_id=category_id)
    return products[offset : offset + limit]