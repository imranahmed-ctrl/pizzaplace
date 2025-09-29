#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    # return only id, name, address (no relationships)
    simple = [
        {"id": r.id, "name": r.name, "address": r.address}
        for r in restaurants
    ]
    return jsonify(simple), 200

# GET single restaurant by ID
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  # Updated syntax
    if restaurant:
        # Include restaurant_pizzas in the response
        return jsonify({
            "id": restaurant.id,
            "name": restaurant.name, 
            "address": restaurant.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "pizza_id": rp.pizza_id,
                    "restaurant_id": rp.restaurant_id,
                    "price": rp.price,
                    "pizza": {
                        "id": rp.pizza.id,
                        "name": rp.pizza.name,
                        "ingredients": rp.pizza.ingredients
                    }
                } for rp in restaurant.restaurant_pizzas
            ]
        }), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_data = [{
        "id": pizza.id,
        "name": pizza.name,
        "ingredients": pizza.ingredients
    } for pizza in pizzas]
    return jsonify(pizzas_data), 200

# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        new_entry = RestaurantPizza(
            price=data["price"],
            restaurant_id=data["restaurant_id"],
            pizza_id=data["pizza_id"]
        )
        db.session.add(new_entry)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        # Return the specific error message that the test expects
        return jsonify({"errors": ["validation errors"]}), 400

    # Return the created restaurant_pizza data including price
    return jsonify({
        "id": new_entry.id,
        "price": new_entry.price,
        "pizza_id": new_entry.pizza_id,
        "restaurant_id": new_entry.restaurant_id,
        "pizza": {
            "id": new_entry.pizza.id,
            "name": new_entry.pizza.name,
            "ingredients": new_entry.pizza.ingredients
        },
        "restaurant": {
            "id": new_entry.restaurant.id,
            "name": new_entry.restaurant.name,
            "address": new_entry.restaurant.address
        }
    }), 201

# DELETE /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  # Updated syntax
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()
    return make_response("", 204)

if __name__ == "__main__":
    app.run(port=5555, debug=True)