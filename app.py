from flask import Flask, request, jsonify

products = {
    "1": {
        "id": 1,
        "name": "Product 1"
    },
    "2": {
        "id": 2,
        "name": "Product 2"
    }
}

app = Flask(__name__)


@app.route("/products")
def get_products():
    jsonify(products)


@app.route("/product/<int:id>")
def get_product(id):
    product = products.get(id)
    if product is not None:
        return jsonify(product)
    return f"Product with id {id} not found.", 404
