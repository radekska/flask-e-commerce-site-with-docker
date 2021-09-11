from typing import Tuple, Union

from Product import Product
from flask import Flask, jsonify, request
from flask.wrappers import Response
from sqlalchemy import exc

from db import db
from .logger import WEB_LOGGER

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:password@db/products"
db.init_app(app)


@app.route("/products")
def get_products() -> Response:
    try:
        products = [product.json for product in Product.find_all()]
        return jsonify(products)
    except exc.SQLAlchemyError:
        message = "An exception occurred while retrieving all products."
        WEB_LOGGER.exception(message)
        return message, 500


@app.route("/product/<int:product_id>")
def get_product(product_id: str) -> Union[Response, Tuple[str, int]]:
    WEB_LOGGER.debug(f"GET /product/{product_id}")
    try:
        product = Product.find_by_id(product_id)
        if product is not None:
            return jsonify(product.json)
        WEB_LOGGER.warning(f"GET /product/{product_id}: item not found.")
        return f"Product with id {product_id} not found.", 404
    except exc.SQLAlchemyError:
        message = f"An exception occurred while retrieving product with id: {product_id}."
        WEB_LOGGER.exception(message)
        return message, 500



@app.route("/product", methods=["POST"])
def post_product() -> Union[Tuple[str, int], Tuple[Response, int]]:
    product_name = request.json.get("name")

    if not product_name:
        return f"'name' data has not been provided.", 400

    new_product = Product(None, product_name)
    new_product.save_to_db()
    return jsonify(new_product.json), 201


@app.route("/product/<int:product_id>", methods=["PUT"])
def update_product(product_id: str) -> Union[Tuple[Response, int], Tuple[str, int]]:
    updated_product_name = request.json.get("name")
    if not updated_product_name:
        return f"'name' data has not been provided.", 400

    product = Product.find_by_id(product_id)
    if product is not None:
        product.name = updated_product_name
        product.save_to_db()
        product = product.json
        product.update({
            "message": "Item updated."
        })
        return jsonify(product), 200
    return f"Product with id {product_id} not found.", 404


@app.route("/product/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: str):
    product = Product.find_by_id(product_id)
    if product is not None:
        product.delete_from_db()
        return jsonify({
            "message": f"Product with id {product_id} deleted."}
        ), 200
    return f"Product with id {product_id} not found.", 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
