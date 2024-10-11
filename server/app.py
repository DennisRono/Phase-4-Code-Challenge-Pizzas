#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

api = Api(app)
db.init_app(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        response_body = json.dumps(
            [
                restaurant.to_dict(only=("id", "name", "address"))
                for restaurant in restaurants
            ]
        )
        return make_response(response_body, 200, {"Content-Type": "application/json"})


class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            response_body = json.dumps(
                restaurant.to_dict(
                    rules=(
                        "id",
                        "name",
                        "address",
                        "restaurant_pizzas",
                        "restaurant_pizzas.pizza",
                    )
                )
            )
            return make_response(
                response_body, 200, {"Content-Type": "application/json"}
            )
        else:
            error_message = json.dumps({"error": "Restaurant not found"})
            return make_response(
                error_message, 404, {"Content-Type": "application/json"}
            )

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        else:
            error_message = json.dumps({"error": "Restaurant not found"})
            return make_response(
                error_message, 404, {"Content-Type": "application/json"}
            )


class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        response_body = json.dumps(
            [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas]
        )
        return make_response(response_body, 200, {"Content-Type": "application/json"})


class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            restaurant_pizza = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"],
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            response_body = json.dumps(restaurant_pizza.to_dict())
            return make_response(
                response_body, 201, {"Content-Type": "application/json"}
            )
        except ValueError as e:
            error_message = json.dumps({"errors": [str(e)]})
            return make_response(
                error_message, 400, {"Content-Type": "application/json"}
            )


api.add_resource(RestaurantListResource, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")
api.add_resource(PizzaListResource, "/pizzas")
api.add_resource(RestaurantPizzaResource, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
