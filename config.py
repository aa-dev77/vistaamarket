import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'vista_market_2024')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'vista2026')
    ADMIN_IDS = [6141183218]
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8830375215:AAFS10uy1cGPwqHU26J98Noo2Pv6JjKNr4U')
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and 'render.com' in DATABASE_URL and 'sslmode' not in DATABASE_URL:
        DATABASE_URL += '?sslmode=require'
    elif not DATABASE_URL:
        DATABASE_URL = 'postgresql://vista_user:vista_pass@localhost/vista_market'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SHOP_NAME = 'Vista Market'
    UPLOAD_FOLDER = 'static/uploads'