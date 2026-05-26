import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'VistaMarket_super_secret_2024_key')
    
    # Admin settings
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'zen123')
    ADMIN_IDS = [6769229781]  # O'z Telegram IDlaringizni kiriting
    
    # Bot
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8830375215:AAFS10uy1cGPwqHU26J98Noo2Pv6JjKNr4U')
    BOT_USERNAME = os.environ.get('BOT_USERNAME', 'VistaMarket')
    
    # Shop
    SHOP_NAME = 'VistaMarket'
    SHOP_DESCRIPTION = 'Premium Parfyumeriya Do\'koni'
    CURRENCY = 'UZS'
    CURRENCY_SYMBOL = 'so\'m'
    
    # Files
    PRODUCTS_FILE = 'products.json'
    ORDERS_FILE = 'orders.json'
    USERS_FILE = 'users.json'
    
    # Payments
    PAYMENT_METHODS = [
        {'id': 'cash', 'name': 'Naqd pul', 'icon': 'fa-money-bill-wave'},
        {'id': 'click', 'name': 'Click', 'icon': 'fa-mobile-screen'},
        {'id': 'payme', 'name': 'Payme', 'icon': 'fa-building-columns'}
    ]
    
    # Categories
    CATEGORIES = [
        {'id': 'all', 'name': 'Barchasi', 'icon': 'fa-grid-2'},
        {'id': 'parfum', 'name': 'Parfyumeriya', 'icon': 'fa-spray-can-sparkles'},
        {'id': 'cosmetics', 'name': 'Kosmetika', 'icon': 'fa-palette'},
        {'id': 'dishes', 'name': 'Idish-tovoq', 'icon': 'fa-plate-utensils'},
        {'id': 'clothes', 'name': 'Kiyim-kechak', 'icon': 'fa-shirt'},
        {'id': 'powders', 'name': 'Kukunlar', 'icon': 'fa-jar'}
    ]
    
    # Delivery
    DELIVERY_FREE_FROM = 0
    DELIVERY_COST = 0
    
    @classmethod
    def is_admin(cls, telegram_id):
        return telegram_id in cls.ADMIN_IDS if telegram_id else False
    
    @classmethod
    def has_admins(cls):
        return len(cls.ADMIN_IDS) > 0