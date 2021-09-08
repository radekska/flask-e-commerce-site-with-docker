from db import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    def __init__(self, product_id, name):
        self._id = product_id
        self._name = name

    @property
    def product_name(self):
        return self._name

    @product_name.setter
    def product_name(self, name: str):
        self._name = name

    @classmethod
    def find_by_id(cls, product_id):
        return cls.query.get(product_id)

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def json(self):
        return {
            "id": self._id,
            "name": self._name
        }
