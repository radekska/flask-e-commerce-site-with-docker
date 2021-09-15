import configparser
import os
from typing import Tuple, Union

import pydevd_pycharm
from Product import Product
from flask import Flask, jsonify, request
from flask.wrappers import Response
from logger import WEB_LOGGER
from sqlalchemy import exc

from db import db

# Setup Pycharm debugger connecting to container.
debug = os.getenv("DEBUG", False)
if debug == "True":
    WEB_LOGGER.info("Connecting to PyCharm debugger.")
    pydevd_pycharm.settrace(
        'host.docker.internal',
        port=12345,
        stdoutToServer=True,
        stderrToServer=True,
        suspend=False
    )


def read_db_password():
    with open("/run/secrets/db_password", "r", encoding="utf-8") as file_stream:
        return file_stream.read()


def get_database_url():
    config_parser = configparser.ConfigParser()
    config_parser.read("config/db.ini")
    database_configuration = config_parser["mysql"]

    database_username = database_configuration["username"]
    database_password = read_db_password()
    database = database_configuration["database"]

    database_url = f"mysql://{database_username}:{database_password}@db/{database}"
    WEB_LOGGER.info(f"Connecting to a database: {database_url}")
    return database_url


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
db.init_app(app)


@app.route("/products")
def get_products() -> Response:
    WEB_LOGGER.debug("GET /products/")
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
    except exc.SQLAlchemyError:
        message = f"An exception occurred while deleting product with id: {product_id}."
        WEB_LOGGER.exception(message)
        return message, 500
    else:
        warning_message = f"Product with id {product_id} not found."
        WEB_LOGGER.warning(warning_message)
        return warning_message, 404


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
