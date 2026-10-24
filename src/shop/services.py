from sqlalchemy.orm import Session
from shop.models import Product
from shop.repositories import ProductRepository
from shop.exceptions import ProductNotFoundError, InsufficientStockError


class ShopService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = ProductRepository(session)

    def purchase_product(self, product_id: int, quantity: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError("Product not found")

        if product.quantity < quantity:
            self.session.rollback()
            raise InsufficientStockError("Not enough stock available")

        product.quantity -= quantity
        self.session.commit()
        self.session.refresh(product)
        return product

    def get_total_stock_value(self) -> float:
        products = self.repo.get_all()
        return sum(p.price * p.quantity for p in products)

    def get_most_expensive_product(self) -> Product | None:
        products = self.repo.get_all()
        if not products:
            return None
        return max(products, key=lambda p: p.price)