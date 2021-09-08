from flask import Flask, request, jsonify
from flask.wrappers import Response
from typing import Union, Tuple

products = {
    1: {
        "id": 1,
        "name": "Product 1"
    },
    2: {
        "id": 2,
        "name": "Product 2"
    }
}

app = Flask(__name__)


@app.route("/products")
def get_products() -> Response:
    return jsonify(products)


@app.route("/product/<int:id>")
def get_product(id: str) -> Union[Response, Tuple[str, int]]:
    product = products.get(id)
    if product is not None:
        return jsonify(product)
    return f"Product with id {id} not found.", 404


@app.route("/product", methods=["POST"])
def post_product() -> Union[Tuple[str, int], Tuple[Response, int]]:
    product_name = request.json.get("name")
    if not product_name:
        return f"'name' data has not been provided.", 400

    new_product_id = max(products.keys()) + 1
    new_product = {
        "id": int(new_product_id),
        "name": product_name
    }
    products[new_product_id] = new_product
    return jsonify(new_product), 201


@app.route("/product/<int:id>", methods=["PUT"])
def update_product(id: str) -> Union[Tuple[Response, int], Tuple[str, int]]:
    updated_product_name = request.json.get("name")
    if not updated_product_name:
        return f"'name' data has not been provided.", 400

    if products.get(id):
        product = products[id]
        product["name"] = updated_product_name
        return jsonify(product), 200
    return f"Product with id {id} not found.", 404


@app.route("/product/<int:id>", methods=["DELETE"])
def delete_product(id: str):
    if products.get(id):
        del products[id]
        return f"Product with id {id} deleted.", 200
    return f"Product with id {id} not found.", 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
