from db import db, User, Restaurant, Dish, Order, Driver, Review, Category

def get_all_users():
    return [u.serialize() for u in User.query.all()]

def get_user_by_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return None
    return user.serialize()

def add_to_balance(user_id, amount):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return None
    user.balance += amount
    db.session.commit()
    return user.serialize()

def update_user(user_id, body):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return None
    user.username = body.get("username", user.username)
    user.balance = body.get("balance", user.balance)
    user.password_digest = body.get("password_digest", user.password_digest)
    db.session.commit()
    return user.serialize()

def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return None
    db.session.delete(user)
    db.session.commit()
    return user.serialize()

def get_all_restaurants():
    return [r.serialize() for r in Restaurant.query.all()]

def create_restaurant(name):
    restaurant = Restaurant(
        name = name
    )
    db.session.add(restaurant)
    db.session.commit()
    return restaurant.serialize()

def get_restaurant_by_id(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return None
    return restaurant.serialize()

def update_restaurant(restaurant_id, body):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return None
    name = body.get("name")
    restaurant.name = name
    db.session.commit()
    return restaurant.serialize()

def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return None
    db.session.delete(restaurant)
    db.session.commit()
    return restaurant.serialize()

def get_all_dishes():
    return [d.serialize() for d in Dish.query.all()]

def create_dish_for_restaurant(name, price, restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return None
    dish = Dish(
        name = name,
        price = price,
        sold_out = False,
        restaurant_id = restaurant_id
    )
    db.session.add(dish)
    db.session.commit()
    return dish.serialize()

def get_dish_by_id(dish_id):
    dish = Dish.query.filter_by(id=dish_id).first()
    if dish is None:
        return None
    return dish.serialize()

def update_dish(dish_id, body):
    dish = Dish.query.filter_by(id=dish_id).first()
    if dish is None:
        return None
    dish.name = body.get("name", dish.name)
    dish.price = body.get("price", dish.price)
    dish.sold_out = body.get("sold_out", dish.sold_out)
    db.session.commit()
    return dish.serialize()

def delete_dish(dish_id):
    dish = Dish.query.filter_by(id=dish_id).first()
    if dish is None:
        return None
    db.session.delete(dish)
    db.session.commit()
    return dish.serialize()

def get_orders_of_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return None
    return [o.serialize() for o in user.orders]

def create_order(date_time, user_id, restaurant_id, driver_id):
    user = User.query.filter_by(id=user_id).first()
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if user is None or restaurant is None:
        return None
    order = Order(
        date_time = date_time,
        paid = False,
        delivered = False,
        user_id = user_id,
        restaurant_id = restaurant_id,
        driver_id = driver_id
    )
    db.session.add(order)
    db.session.commit()
    return order.serialize()

def add_dish_to_order(order_id, body):
    dish_id = body.get("dish_id")
    dish = Dish.query.filter_by(id=dish_id).first()
    if dish is None:
        return None
    order = Order.query.filter_by(id=order_id).first()
    if order is None:
        return None
    order.dishes.append(dish)
    calculate_total(order_id)
    db.session.commit()
    return order.serialize()

def calculate_total(order_id):
    order = Order.query.filter_by(id=order_id).first()
    if order is None:
        return None
    dishes = order.dishes
    total = 0
    for dish in dishes:
        total = total + dish.price
    order.total = total
    db.session.commit()

def get_order_by_id(order_id):
    order = Order.query.filter_by(id=order_id).first()
    if order is None:
        return None
    return order.serialize()

def update_order(order_id, body):
    order = Order.query.filter_by(id=order_id).first()
    if order is None or order.delivered is True:
        return None
    order.driver_id = body.get("driver_id", order.driver_id)
    order.paid = body.get("paid", order.paid)
    order.delivered = body.get("delivered", order.delivered)
    db.session.commit()
    return order.serialize()

def delete_order(order_id):
    order = Order.query.filter_by(id=order_id).first()
    if order is None:
        return None
    db.session.delete(order)
    db.session.commit()
    return order.serialize()

def get_driver_by_id(driver_id):
    driver = Driver.query.filter_by(id=driver_id).first()
    if driver is None:
        return None
    return driver.serialize()

def get_driver_of_order(order_id):
    order = Order.query.filter_by(id=order_id).first()
    if order is None:
        return None
    driver_id = order.driver_id
    driver = Driver.query.filter_by(id=driver_id).first()
    return driver.serialize()

def create_driver(body):
    driver = Driver(
        name = body.get("name"),
        license_plate_number = body.get("license_plate_number")
    )
    db.session.add(driver)
    db.session.commit()
    return driver.serialize()

def delete_driver(driver_id):
    driver = Driver.query.filter_by(id=driver_id).first()
    if driver is None:
        return None
    db.session.delete(driver)
    db.session.commit()
    return driver.serialize()

def get_reviews_by_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return None
    return [r.serialize() for o in user.reviews_posted]

def get_reviews_of_restaurant(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return None
    return [r.serialize() for r in restaurant.reviews]

def create_review_for_restaurant(restaurant_id, body):
    user_id = body.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if user is None or restaurant is None:
        return None
    review = Review(
        rating = body.get("rating"),
        content = body.get("content"),
        user_id = user_id,
        restaurant_id = restaurant_id
    )
    update_rating_for_restaurant(restaurant_id, body.get("rating"), len(restaurant.reviews))
    db.session.add(review)
    db.session.commit()
    
    return review.serialize()

def update_rating_for_restaurant(restaurant_id, new_rating, num_reviews):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return None
    curr_rating = restaurant.rating
    rating = (curr_rating*num_reviews + new_rating)/(num_reviews+1)
    restaurant.rating = rating
    db.session.commit()

def get_review_by_id(review_id):
    review = Review.query.filter_by(id=review_id).first()
    if review is None:
        return None
    return review.serialize()

def update_review(review_id, body):
    review = Review.query.filter_by(id=review_id).first()
    if review is None:
        return None
    restaurant = Restaurant.query.filter_by(id=review.restaurant_id).first()
    num_reviews = len(restaurant.reviews)
    restaurant.rating = (restaurant.rating*num_reviews-review.rating)/(num_reviews-1)
    review.rating = body.get("rating", review.rating)
    review.content = body.get("content", review.content)
    update_rating_for_restaurant(review.restaurant_id, review.rating, num_reviews-1)
    db.session.commit()
    return review.serialize()

def delete_review(review_id):
    review = Review.query.filter_by(id=review_id).first()
    if review is None:
        return None
    restaurant = Restaurant.query.filter_by(id=review.restaurant_id).first()
    num_reviews = len(restaurant.reviews)
    restaurant.rating = (restaurant.rating*num_reviews-review.rating)/(num_reviews-1)
    db.session.delete(review)
    db.session.commit()
    return review.serialize()

def get_all_categories():
    return [c.serialize() for c in Category.query.all()]

def create_category(body):
    category = Category(
        description = body.get("description")
    )
    db.session.add(category)
    db.session.commit()
    return category.serialize()

def get_category_by_id(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category is None:
        return None
    return category.serialize()

def add_restaurant_to_category(category_id, body):
    category = Category.query.filter_by(id=category_id).first()
    if category is None:
        return None
    restaurant_id = body.get("restaurant_id")
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return None
    category.restaurants.append(restaurant)
    db.session.commit()
    return category.serialize()

def delete_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category is None:
        return None
    db.session.delete(category)
    db.session.commit()
    return category.serialize()
