from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    price = db.Column(db.Integer, nullable=False)
    old_price = db.Column(db.Integer, default=0)
    image = db.Column(db.String(500), default='https://placehold.co/400')
    category = db.Column(db.String(50), default='parfum')
    in_stock = db.Column(db.Integer, default=10)
    discount = db.Column(db.Integer, default=0)
    sold_this_week = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'old_price': self.old_price,
            'image': self.image,
            'category': self.category,
            'in_stock': self.in_stock,
            'discount': self.discount,
            'sold_this_week': self.sold_this_week
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.String(50), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, default='')
    items = db.Column(db.Text, default='[]')
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')
    status_text = db.Column(db.String(50), default='Tayyorlanmoqda')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'customer_name': self.customer_name,
            'phone': self.phone,
            'address': self.address,
            'items': json.loads(self.items) if self.items else [],
            'total': self.total,
            'status': self.status,
            'status_text': self.status_text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Banner(db.Model):
    __tablename__ = 'banners'
    
    id = db.Column(db.String(20), primary_key=True)
    image = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200), default='')
    subtitle = db.Column(db.String(200), default='')
    link = db.Column(db.String(200), default='/')
    active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(50), primary_key=True)
    first_name = db.Column(db.String(100), default='')
    username = db.Column(db.String(100), default='')
    phone = db.Column(db.String(50), default='')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)