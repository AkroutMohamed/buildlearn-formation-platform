from fastapi import HTTPException

from app.models.product import Product, ProductStatus
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class AdminProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def list_products(self):
        return self.repository.get_all()

    def get_product(self, product_id):
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def create_product(self, product_data: ProductCreate) -> Product:
        product = Product(
            name=product_data.name.strip(),
            description=product_data.description.strip() if product_data.description else None,
            category=product_data.category.strip() if product_data.category else None,
            status=product_data.status,
        )
        return self.repository.create(product)

    def update_product(self, product_id, product_data: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ("name", "description", "category") and value is not None:
                value = value.strip() if value else None
            setattr(product, field, value)
        return self.repository.update(product)

    def delete_product(self, product_id) -> None:
        product = self.get_product(product_id)
        self.repository.delete(product)

    def publish_product(self, product_id) -> Product:
        product = self.get_product(product_id)
        product.status = ProductStatus.PUBLISHED
        return self.repository.update(product)

    def unpublish_product(self, product_id) -> Product:
        product = self.get_product(product_id)
        product.status = ProductStatus.DRAFT
        return self.repository.update(product)
