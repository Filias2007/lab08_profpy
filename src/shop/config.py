import os


class Config:
    """Глобальна конфігурація застосунку та валідаційні ліміти."""

    APP_ENV: str = os.getenv("APP_ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shop.db")
    MIN_STOCK_THRESHOLD: int = int(os.getenv("MIN_STOCK_THRESHOLD", "1"))
    MAX_PRICE_LIMIT: float = float(os.getenv("MAX_PRICE_LIMIT", "500000.0"))

    @classmethod
    def validate_product_limits(cls, quantity: int, price: float) -> bool:
        """Перевірка відповідності товару глобальним налаштуванням."""
        return quantity >= cls.MIN_STOCK_THRESHOLD and price <= cls.MAX_PRICE_LIMIT


AppConfig = Config


def get_config() -> Config:
    return Config()