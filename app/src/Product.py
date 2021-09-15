from db import db
from logger import WEB_LOGGER

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    def __init__(self, product_id, name):
        self.id = product_id
        self.name = name

    @classmethod
    def find_by_id(cls, product_id):
        WEB_LOGGER.debug(f"Find product with id: {product_id}.")
        return cls.query.get(product_id)

    @classmethod
    def find_all(cls):
        WEB_LOGGER.debug("Query for all products.")
        return cls.query.all()

    def save_to_db(self):
        WEB_LOGGER.debug(f"Save product with id: {self.id} name: {self.name} to DB.")
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        WEB_LOGGER.debug(f"Delete product with id: {self.id} name: {self.name} to DB.")
        db.session.delete(self)
        db.session.commit()

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name
        }
