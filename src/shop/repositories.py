from sqlalchemy import select
from sqlalchemy.orm import Session
from shop.models import Product, Category


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(self, category_id: int | None = None) -> list[Product]:
        stmt = select(Product)
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, product_id: int) -> Product | None:
        return self.session.get(Product, product_id)

    def add(self, product: Product) -> Product:
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.session.delete(product)
        self.session.commit()


class CategoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(self) -> list[Category]:
        return list(self.session.scalars(select(Category)).all())

    def get_by_id(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def add(self, category: Category) -> Category:
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category