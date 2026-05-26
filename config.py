import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'VistaMarket_super_secret_2024_key')
    
    # Admin settings
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'vista2024')  # <-- parolni o'zgartirdim
    ADMIN_IDS = [6141183218]  # <-- SIZNING TELEGRAM ID INGIZ! (𝐀 user)
    
    # Bot
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8830375215:AAFS10uy1cGPwqHU26J98Noo2Pv6JjKNr4U')
    BOT_USERNAME = os.environ.get('BOT_USERNAME', 'vistauz_bot')  # <-- to'g'ri username
    
    # Shop
    SHOP_NAME = 'Vista Market'
    SHOP_DESCRIPTION = 'Har bir uy uchun'
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
    DELIVERY_FREE_FROM = 500000  # <-- 500,000 so'mdan yuqori bepul
    DELIVERY_COST = 10000  # <-- 30,000 so'm
    
    @classmethod
    def is_admin(cls, telegram_id):
        return telegram_id in cls.ADMIN_IDS if telegram_id else False
    
    @classmethod
    def has_admins(cls):
        return len(cls.ADMIN_IDS) > 0