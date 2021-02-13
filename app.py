import json
from db import db, User, Restaurant, Dish, Order, Driver, Review
from flask import Flask, request
import dao
from datetime import datetime
import users_dao
import os

app = Flask(__name__)
db_filename = "delivery.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def extract_token(request):
    auth_header = request.headers.get("Authorization")
    if auth_header is None: 
        return False, json.dumps({"error": "Missing authorization header."})
    
    bearer_token = auth_header.replace("Bearer ", "").strip()
    if bearer_token is None or not bearer_token:
        return False, json.dumps(({"error": "Invalid authorization header"}))
    return True, bearer_token

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

@app.route("/")
def header():
    return ("Ding-Dong: backend for a simplified version of a food delivery app")

@app.route("/users/")
def get_all_users():
    return success_response(dao.get_all_users())

@app.route("/user/<int:user_id>/")
def get_user_by_id(user_id):
    user = dao.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.")
    return success_response(user)

@app.route("/user/<int:user_id>/balance/", methods=["POST"])
def add_to_balance(user_id):
    successful, session_token = extract_token(request)
    if not successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return json.dumps({"error": "Invalid session token."})
        
    body = json.loads(request.data)
    amount = body.get("amount")
    user = dao.add_to_balance(user_id, amount)
    if user is None:
        return failure_response("User not found.")
    return success_response(user)

@app.route("/user/<int:user_id>/", methods=["POST"])
def update_user(user_id):
    successful, session_token = extract_token(request)
    if not successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return json.dumps({"error": "Invalid session token."})

    body = json.loads(request.data)
    user = dao.update_user(user_id, body)
    if user is None:
        return failure_response("User not found.")
    return success_response(user)

@app.route("/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    successful, session_token = extract_token(request)
    if not successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return json.dumps({"error": "Invalid session token."})

    user = dao.delete_user(user_id)
    if user is None:
        return failure_response("User not found.")
    return success_response(user)

@app.route("/restaurants/")
def get_all_restaurants():
    return success_response(dao.get_all_restaurants())

@app.route("/restaurant/", methods=["POST"])
def create_restaurant():
    body = json.loads(request.data)
    restaurant = dao.create_restaurant(
        name = body.get("name")
    )
    return success_response(restaurant)

@app.route("/restaurant/<int:restaurant_id>/")
def get_restaurant_by_id(restaurant_id):
    restaurant = dao.get_restaurant_by_id(restaurant_id)
    if restaurant is None:
        return failure_response("Restaurant not found.")
    return success_response(restaurant)

@app.route("/restaurant/<int:restaurant_id>/", methods=["POST"])
def update_restaurant(restaurant_id):
    body = json.loads(request.data)
    restaurant = dao.update_restaurant(restaurant_id, body)
    if restaurant is None:
        return failure_response("Restaurant not found.")
    return success_response(restaurant)

@app.route("/restaurant/<int:restaurant_id>/", methods=["DELETE"])
def delete_restaurant(restaurant_id):
    restaurant = dao.delete_restaurant(restaurant_id)
    if restaurant is None:
        return failure_response("Restaurant not found.")
    return success_response(restaurant)

@app.route("/dishes/")
def get_all_dishes():
    return success_response(dao.get_all_dishes())

@app.route("/restaurants/<int:restaurant_id>/dish/", methods=["POST"])
def create_dish_for_restaurant(restaurant_id):
    body = json.loads(request.data)
    dish = dao.create_dish_for_restaurant(
        name = body.get("name"), 
        price = body.get("price"),
        restaurant_id = restaurant_id
    )
    if dish is None:
        return failure_response("Restaurant not found.")
    return success_response(dish)

@app.route("/dish/<int:dish_id>/")
def get_dish_by_id(dish_id):
    dish = dao.get_dish_by_id(dish_id)
    if dish is None:
        return failure_response("Dish not found.")
    return success_response(dish)

@app.route("/dish/<int:dish_id>/", methods=["POST"])
def update_dish(dish_id):
    body = json.loads(request.data)
    dish = dao.update_dish(dish_id, body)
    if dish is None:
        return failure_response("Dish not found.")
    return success_response(dish)

@app.route("/dish/<int:dish_id>/", methods=["DELETE"])
def delete_dish(dish_id):
    dish = dao.delete_dish(dish_id)
    if dish is None:
        return failure_response("Dish not found.")
    return success_response(dish)

@app.route("/user/<int:user_id>/orders/")
def get_orders_of_user(user_id):
    orders = dao.get_orders_of_user(user_id)
    if orders is None:
        return failure_response("User does not exist.")
    return success_response(orders)

@app.route("/user/<int:user_id>/restaurant/<int:restaurant_id>/order/", methods=["POST"])
def create_order(user_id, restaurant_id):
    body = json.loads(request.data)
    order = dao.create_order(
        date_time = datetime.now(), 
        user_id = user_id,
        restaurant_id = restaurant_id,
        driver_id = body.get("driver_id")
    )
    if order is None:
        return failure_response("User or restaurant not found.")
    return success_response(order)

@app.route("/order/<int:order_id>/add/", methods=["POST"])
def add_dish_to_order(order_id):
    body = json.loads(request.data)
    order = dao.add_dish_to_order(order_id, body)
    if order is None:
        return failure_response("Order or dish not found.")
    return success_response(order)

@app.route("/order/<int:order_id>/")
def get_order_by_id(order_id):
    order = dao.get_order_by_id(order_id)
    if order is None:
        return failure_response("Order not found.")
    return success_response(order)

@app.route("/order/<int:order_id>/", methods=["POST"])
def update_order(order_id):
    body = json.loads(request.data)
    order = dao.update_order(order_id, body)
    if order is None:
        return failure_response("Order not found or has been delivered.")
    return success_response(order)

@app.route("/order/<int:order_id>/", methods=["DELETE"])
def delete_order(order_id):
    order = dao.delete_order(order_id)
    if order is None:
        return failure_response("Order not found.")
    return success_response(order)

@app.route("/driver/<int:driver_id>/")
def get_driver_by_id(driver_id):
    driver = dao.get_driver_by_id(driver_id)
    if driver is None:
        return failure_response("Driver does not exist.")
    return success_response(driver)

@app.route("/order/<int:order_id>/driver/")
def get_driver_of_order(order_id):
    driver = dao.get_driver_of_order(order_id)
    if driver is None:
        return failure_response("Order not found.")
    return success_response(driver)

@app.route("/driver/", methods=["POST"])
def create_driver():
    body = json.loads(request.data)
    driver = dao.create_driver(body)
    return success_response(driver)

@app.route("/driver/<int:driver_id>/", methods=["DELETE"])
def delete_driver(driver_id):
    driver = dao.delete_driver(driver_id)
    if driver is None:
        return failure_response("Driver does not exist.")
    return success_response(driver)

@app.route("/user/<int:user_id>/reviews/")
def get_reviews_by_user(user_id):
    reviews = dao.get_reviews_by_user(user_id)
    if reviews is None:
        return failure_response("User does not exist.")
    return success_response(reviews)

@app.route("/restaurant/<int:restaurant_id>/reviews/")
def get_reviews_of_restaurant(restaurant_id):
    reviews = dao.get_reviews_of_restaurant(restaurant_id)
    if reviews is None:
        return failure_response("Restaurant does not exist.")
    return success_response(reviews)

@app.route("/restaurant/<int:restaurant_id>/review/", methods=["POST"])
def create_review_for_restaurant(restaurant_id):
    body = json.loads(request.data)
    review = dao.create_review_for_restaurant(restaurant_id, body)
    if review is None:
        return failure_response("User or restaurant not found.")
    return success_response(review)

@app.route("/review/<int:review_id>/")
def get_review_by_id(review_id):
    review = dao.get_review_by_id(review_id)
    if review is None:
        return failure_response("Review not found.")
    return success_response(review)

@app.route("/review/<int:review_id>/", methods=["POST"])
def update_review(review_id):
    body = json.loads(request.data)
    review = dao.update_review(review_id, body)
    if review is None:
        return failure_response("Review not found.")
    return success_response(review)

@app.route("/review/<int:review_id>/", methods=["DELETE"])
def delete_review(review_id):
    review = dao.delete_review(review_id)
    if review is None:
        return failure_response("Review not found.")
    return success_response(review)

@app.route("/categories/")
def get_all_categories():
    return success_response(dao.get_all_categories())

@app.route("/category/", methods=["POST"])
def create_category():
    body = json.loads(request.data)
    category = dao.create_category(body)
    return success_response(category)

@app.route("/category/<int:category_id>/")
def get_category_by_id(category_id):
    category = dao.get_category_by_id(category_id)
    if category is None:
        return failure_response("Category not found.")
    return success_response(category)

@app.route("/category/<int:category_id>/add/", methods=["POST"])
def add_restaurant_to_category(category_id):
    body = json.loads(request.data)
    category = dao.add_restaurant_to_category(category_id, body)
    if category is None:
        return failure_response("Category or restaurant not found.")
    return success_response(category)

@app.route("/category/<int:category_id>/", methods=["DELETE"])
def delete_category(category_id):
    category = dao.delete_category(category_id)
    if category is None:
        return failure_response("Category not found.")
    return success_response(category)

@app.route("/register/", methods=["POST"])
def register_account():
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    email = body.get("email")
    password = body.get("password")

    if name is None or username is None or email is None or password is None:
        return json.dumps({"error": "Invalid name, username, email or password."})
    
    created, user = users_dao.create_user(name, username, email, password)
    if not created:
        return json.dumps({"error": "User already exists."})

    return json.dumps({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token,
    })

@app.route("/login/", methods=["POST"])
def login():
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")
    if email is None or password is None:
        return json.dumps({"error": "Invalid email or password."})

    successful, user = users_dao.verify_credentials(email, password)
    if not successful:
        return json.dumps({"error": "Incorrect email or password."})

    return json.dumps(
        {
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token,
        }
    )

@app.route("/session/", methods=["POST"])
def update_session():
    successful, update_token = extract_token(request)
    if not successful:
        return update_token

    try:
        user = users_dao.renew_session(update_token)
    except Exception as e:
        return json.dumps({"error": f"Invalid update token: {str(e)}"})

    return json.dumps(
        {
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token,
        }
    )

@app.route("/secret/", methods=["GET"])
def secret_message():
    successful, session_token = extract_token(request)
    if not successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return json.dumps({"error": "Invalid session token."})
    
    return json.dumps({
        "message": "You have successfully implemented sessions"}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)