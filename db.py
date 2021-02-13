from flask_sqlalchemy import SQLAlchemy
import datetime
import hashlib
import os
import bcrypt

db = SQLAlchemy()

association_order_dishes = db.Table(
    "association_order_dishes",
    db.Model.metadata,
    db.Column("order_id", db.Integer, db.ForeignKey("order.id")),
    db.Column("dish_id", db.Integer, db.ForeignKey("dish.id"))
)

association_restaurant_categories = db.Table(
    "association_restaurant_categories",
    db.Model.metadata,
    db.Column("restaurant_id", db.Integer, db.ForeignKey("restaurant.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id"))
)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password_digest = db.Column(db.String, nullable=False)
    orders = db.relationship("Order")
    reviews_posted = db.relationship("Review")

    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.username = kwargs.get("username", "")
        self.balance = kwargs.get("balance", 0)
        self.email = kwargs.get("email")
        self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
        self.renew_session()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "balance": self.balance,
            "email": self.email,
            "orders": [o.serialize() for o in self.orders],
            "reviews_posted": [r.serialize() for r in self.reviews_posted],
        }

    # Used to randomly generate session/update tokens
    def _urlsafe_base_64(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    # Generates new tokens, and resets expiration time
    def renew_session(self):
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode("utf8"), self.password_digest)

    # Checks if session token is valid and hasn't expired
    def verify_session_token(self, session_token):
        return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        return update_token == self.update_token

class Restaurant(db.Model):
    __tablename__ = "restaurant"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    categories = db.relationship("Category", secondary=association_restaurant_categories, back_populates="restaurants")
    menu = db.relationship("Dish", cascade="delete")
    reviews = db.relationship("Review", cascade="delete")
    orders = db.relationship("Order")

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.rating = kwargs.get("rating", 0)
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "rating": self.rating,
            "categories": [c.serialize() for c in self.categories],
            "menu": [m.serialize() for m in self.menu],
            "reviews": [r.serialize() for r in self.reviews],
            "orders": [o.serialize() for o in self.orders],
        }

class Dish(db.Model):
    __tablename__ = "dish"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    sold_out = db.Column(db.Boolean, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)
    orders = db.relationship("Order", secondary=association_order_dishes, back_populates="dishes")

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.price = kwargs.get("price", 0)
        self.sold_out = kwargs.get("sold_out", False)
        self.restaurant_id = kwargs.get("restaurant_id")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "sold_out": self.sold_out,
        }

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.Integer, nullable=False)
    dishes = db.relationship("Dish", secondary=association_order_dishes, back_populates="orders")
    total = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, nullable=False)
    delivered = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("driver.id"), nullable=False)

    def __init__(self, **kwargs):
        self.date_time = kwargs.get("date_time")
        self.total = kwargs.get("total", 0)
        self.paid = kwargs.get("paid", False)
        self.delivered = kwargs.get("delivered", False)
        self.user_id = kwargs.get("user_id")
        self.restaurant_id = kwargs.get("restaurant_id")
        self.driver_id = kwargs.get("driver_id")

    def serialize(self):
        return {
            "id": self.id,
            "date_time": self.date_time,
            "dishes": [d.serialize() for d in self.dishes],
            "total": self.total,
            "paid": self.paid,
            "delivered": self.delivered,
        }

class Driver(db.Model):
    __tablename__ = "driver"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    license_plate_number = db.Column(db.String, nullable=False)
    orders = db.relationship("Order")

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.license_plate_number = kwargs.get("license_plate_number", "")
        
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "license_plate_number": self.license_plate_number,
            "orders": [o.serialize() for o in self.orders],
        }

class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)

    def __init__(self, **kwargs):
        self.rating = kwargs.get("rating")
        self.content = kwargs.get("content")
        self.user_id = kwargs.get("user_id")
        self.restaurant_id = kwargs.get("restaurant_id")

    def serialize(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "content": self.content,
        }

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    restaurants = db.relationship("Restaurant", secondary=association_restaurant_categories, back_populates="categories")
    
    def __init__(self, **kwargs):
        self.description = kwargs.get("description")

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
        }