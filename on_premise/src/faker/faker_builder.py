from faker import Faker
import numpy as np
import pandas as pd
import uuid, random
from datetime import datetime

class EcommerceDataGenerator:
    def __init__(self, locale="en_US"):
        self._fake = Faker(locale, use_weighting=True)
        self._users = []
        self._product_categories = set()
        self._products = []
        self._addresses = []
        self._prices = []
        self.orders= []
    
    def initialize(self, 
                   num_users=1_000,
                   num_products=50,
                   num_orders=10_000
                   ):
         self.generate_users(num_users)
         self.generate_products(num_products)
         self.generate_orders(num_orders)

         self.save_to_dataset_dir()
    
    def add_product(self, product_name, category, price=-1):
        if category not in self._product_categories:
            self._product_categories.add(category)
        self._products.append({
            "product_id": str(uuid.uuid4()),
            "name": product_name,
            "price": round(random.uniform(5, 500), 2) if price == -1 else price
        })
        return self._product_categories, self._products

    def generate_products(self, product_count=50):
        categories = self._product_categories
        for _ in range(product_count):
            self._products.append({
                "product_id": str(uuid.uuid4()),
                "name": self._fake.catch_phrase(),
                "price": round(random.uniform(5, 500), 2)
            })
        return self._products
    
    def generate_users(self, user_count=1_000):
        for _ in range(user_count):
            self._users.append({
                "user_id": str(uuid.uuid4()),
                "email": self._fake.email(),
                "first_name": self._fake.first_name(),
                "last_name": self._fake.last_name(),
                "date_of_birth": self._fake.date_of_birth(),
                "gender": random.randint(0, 1),
                "loyalty_tier": 0,
                "is_email_verified": random.choices([0, 1], weights=[15, 85])[0]
                "is_active": True,
                "created_at": self._fake.date_time_this_year(),
                "updated_at": None,
                "life_time_order_count": 0
            })

    def generate_orders(self, order_count=10_000):
        if not self._users or not self._products:
            raise ValueError("Generate users & products first!")

        for _ in range(order_count):
            user = random.choice(self._users)
            product = random.choice(self._products)
            random_qty = random.randint(1, 10)
            self.orders.append({
                "order_id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "product_id": product["product_id"],
                "timestamp": self._fake.date_time_between_dates(user["register_date"], 
                                                                datetime(2026, 12, 31)),
                "quantity": random_qty,
                "revenue": product["price"] * random_qty
            })
        return self.orders
    
    def save_to_dataset_dir(self, base_path="../../datasets/faker_ecommerce/raw"):
        pd.DataFrame(self._users).to_csv(f"{base_path}/users.csv", index=False)
        pd.DataFrame(self._products).to_json(f"{base_path}/products.json", 
                                             orient="records",
                                             indent=4)
        pd.DataFrame(self.orders).to_parquet(f"{base_path}/orders.parquet")

if __name__ == "__main__":
    generator = EcommerceDataGenerator()
    generator.initialize(num_orders=100_000)