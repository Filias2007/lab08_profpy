from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    category_id: int = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, gt=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    category_id: int

    model_config = {"from_attributes": True}


class PurchaseRequest(BaseModel):
    quantity: int = Field(gt=0)


class StockSummaryResponse(BaseModel):
    total_stock_value: float
    most_expensive_product: ProductResponse | None