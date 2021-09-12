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
    WEB_LOGGER.debug(f"POST /product/ with {request.json}.")

    product_name = request.json.get("name")
    if not product_name:
        return f"'name' data has not been provided.", 400
    new_product = Product(None, product_name)
    try:
        new_product.save_to_db()
        return jsonify(new_product.json), 201
    except exc.SQLAlchemyError:
        message = f"An exception occurred while creating product with name: {product_name}"
        WEB_LOGGER.exception(message)
        return message, 500


@app.route("/product/<int:product_id>", methods=["PUT"])
def update_product(product_id: str) -> Union[Tuple[Response, int], Tuple[str, int]]:
    WEB_LOGGER.debug(f"PUT /product/{product_id}")
    updated_product_name = request.json.get("name")
    if not updated_product_name:
        return f"'name' data has not been provided.", 400

    try:
        product = Product.find_by_id(product_id)
        if product is not None:
            product.name = updated_product_name
            product.save_to_db()
            product = product.json
            product.update({
                "message": "Item updated."
            })
            return jsonify(product), 200
        WEB_LOGGER.warning(f"PUT /product/{product_id}: Existing product not found.")
        return f"Product with id {product_id} not found.", 404
    except exc.SQLAlchemyError:
        message = f"An exception occurred while updating product with name: {updated_product_name}."
        WEB_LOGGER.exception(message)
        return message, 500


@app.route("/product/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: str):
    WEB_LOGGER.debug(f"DELETE /product/{product_id}")
    try:
        product = Product.find_by_id(product_id)
        if product is not None:
            product.delete_from_db()
            return jsonify({
                "message": f"Product with id {product_id} deleted."}
            ), 200
        warning_message = f"Product with id {product_id} not found."
        WEB_LOGGER.warning(warning_message)
        return warning_message, 404
    except exc.SQLAlchemyError:
        message = f"An exception occurred while deleting product with id: {product_id}."
        WEB_LOGGER.exception(message)
        return message, 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
