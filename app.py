from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import json, os, uuid, requests

# ==================== CONFIG ====================
class Config:
    SECRET_KEY = 'vista_market_2024'
    ADMIN_PASSWORD = 'vista2026'
    ADMIN_IDS = [6141183218]
    BOT_TOKEN = '8830375215:AAFS10uy1cGPwqHU26J98Noo2Pv6JjKNr4U'
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and 'render.com' in DATABASE_URL and 'sslmode' not in DATABASE_URL:
        DATABASE_URL += '?sslmode=require'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///vista_market.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SHOP_NAME = 'Vista Market'
    UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== MODELS ====================
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

# ==================== TELEGRAM BOT ====================
def send_telegram(chat_id, text, reply_markup=None):
    if not Config.BOT_TOKEN:
        return None
    url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        return requests.post(url, json=payload, timeout=10).json()
    except:
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if 'message' in data:
            msg = data['message']
            chat_id = msg['chat']['id']
            text = msg.get('text', '')
            user = msg.get('from', {})
            first_name = user.get('first_name', 'Foydalanuvchi')
            user_id = user.get('id')
            
            if text == '/start':
                webapp_url = request.host_url.rstrip('/')
                welcome = f"👋 Assalomu alaykum, {first_name}!\n\n🏪 Vista Market - Har bir uy uchun!"
                reply_markup = {
                    'inline_keyboard': [
                        [{'text': '🛍 DO\'KONGA KIRISH', 'web_app': {'url': webapp_url}}]
                    ]
                }
                send_telegram(chat_id, welcome, reply_markup)
            
            elif text == '/admin':
                if user_id in Config.ADMIN_IDS:
                    webapp_url = request.host_url.rstrip('/')
                    send_telegram(chat_id, f"🔐 Admin Panel\n\n{webapp_url}/admin\nParol: {Config.ADMIN_PASSWORD}")
                else:
                    send_telegram(chat_id, "❌ Siz admin emassiz!")
        
        return jsonify({'ok': True})
    except:
        return jsonify({'ok': False})

# ==================== WEB ROUTES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@app.route('/api/products')
def get_products():
    cat = request.args.get('category', 'all')
    if cat == 'all':
        products = Product.query.all()
    else:
        products = Product.query.filter_by(category=cat).all()
    return jsonify({'success': True, 'products': [p.to_dict() for p in products]})

@app.route('/api/banners')
def get_banners():
    banners = Banner.query.filter_by(active=True).order_by(Banner.order).all()
    return jsonify({'success': True, 'banners': [{'id': b.id, 'image': b.image, 'title': b.title, 'subtitle': b.subtitle, 'link': b.link} for b in banners]})

@app.route('/api/check-admin')
def check_admin():
    uid = request.args.get('user_id', type=int)
    return jsonify({'is_admin': uid in Config.ADMIN_IDS})

# ==================== BUYURTMALAR ====================
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    items = data.get('items', [])
    total = sum(i.get('price', 0) * i.get('quantity', 1) for i in items)
    
    order = Order(
        order_id=str(uuid.uuid4())[:8].upper(),
        user_id=data.get('user_id'),
        customer_name=data.get('name', 'Mijoz'),
        phone=data.get('phone', ''),
        address=data.get('address', ''),
        items=json.dumps(items),
        total=total
    )
    
    # Stokdan ayirish
    for item in items:
        prod = Product.query.get(item['id'])
        if prod:
            prod.in_stock = max(0, prod.in_stock - item.get('quantity', 1))
    
    db.session.add(order)
    db.session.commit()
    
    for admin_id in Config.ADMIN_IDS:
        send_telegram(admin_id, f"🛍 Yangi buyurtma #{order.order_id}\n👤 {order.customer_name}\n💰 {total:,} so'm")
    
    return jsonify({'success': True, 'order': order.to_dict()})

# ==================== ADMIN API ====================
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    if request.json.get('password') == Config.ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/admin/check')
def admin_check():
    return jsonify({'is_admin': session.get('admin', False)})

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/admin/upload', methods=['POST'])
def admin_upload():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    if 'file' not in request.files:
        return jsonify({'success': False})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False})
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4())[:8] + '_' + secure_filename(file.filename)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        return jsonify({'success': True, 'url': f"/static/uploads/{filename}"})
    return jsonify({'success': False})

@app.route('/api/admin/products', methods=['GET', 'POST', 'DELETE'])
def admin_products():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify({'success': True, 'products': [p.to_dict() for p in products]})
    
    elif request.method == 'POST':
        data = request.json
        new_product = Product(
            id=str(uuid.uuid4())[:8],
            name=data['name'],
            description=data.get('description', ''),
            price=int(data['price']),
            old_price=int(data.get('old_price', data['price'])),
            image=data.get('image', 'https://placehold.co/400'),
            category=data.get('category', 'parfum'),
            in_stock=int(data.get('in_stock', 10)),
            discount=int(data.get('discount', 0))
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        pid = request.json.get('id')
        Product.query.filter_by(id=pid).delete()
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/admin/products/update', methods=['PUT'])
def admin_update_product():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    data = request.json
    product = Product.query.get(data['id'])
    if product:
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = int(data.get('price', product.price))
        product.old_price = int(data.get('old_price', product.price))
        product.image = data.get('image', product.image)
        product.category = data.get('category', product.category)
        product.in_stock = int(data.get('in_stock', product.in_stock))
        product.discount = int(data.get('discount', product.discount))
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/admin/orders')
def admin_orders():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify({'success': True, 'orders': [o.to_dict() for o in orders]})

@app.route('/api/admin/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    order = Order.query.get(order_id)
    if order:
        order.status = request.json.get('status', order.status)
        status_map = {'pending': 'Tayyorlanmoqda', 'confirmed': 'Yo\'lda', 'delivered': 'Yetkazilgan', 'cancelled': 'Bekor qilingan'}
        order.status_text = status_map.get(order.status, order.status)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/admin/banners', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_banners():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    
    if request.method == 'GET':
        banners = Banner.query.order_by(Banner.order).all()
        return jsonify({'success': True, 'banners': [{'id': b.id, 'image': b.image, 'title': b.title, 'subtitle': b.subtitle, 'link': b.link, 'active': b.active, 'order': b.order} for b in banners]})
    
    elif request.method == 'POST':
        data = request.json
        new_banner = Banner(
            id=str(uuid.uuid4())[:8],
            image=data['image'],
            title=data.get('title', ''),
            subtitle=data.get('subtitle', ''),
            link=data.get('link', '/'),
            active=data.get('active', True),
            order=data.get('order', Banner.query.count() + 1)
        )
        db.session.add(new_banner)
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'PUT':
        data = request.json
        banner = Banner.query.get(data['id'])
        if banner:
            banner.image = data.get('image', banner.image)
            banner.title = data.get('title', banner.title)
            banner.subtitle = data.get('subtitle', banner.subtitle)
            banner.link = data.get('link', banner.link)
            banner.active = data.get('active', banner.active)
            banner.order = data.get('order', banner.order)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False})
    
    elif request.method == 'DELETE':
        banner_id = request.json.get('id')
        Banner.query.filter_by(id=banner_id).delete()
        db.session.commit()
        return jsonify({'success': True})

# ==================== RUN ====================
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Faqat jadvallarni yaratish, DEFAULT MAHSULOT YO'Q
    with app.app_context():
        db.create_all()
        print("✅ Ma'lumotlar bazasi jadvallari yaratildi")
        print(f"📦 Mahsulotlar soni: {Product.query.count()} ta")
    
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*50)
    print("  🏪 VISTA MARKET - PostgreSQL bilan")
    print("="*50)
    print(f"  🌐 Do'kon: https://vista-market.onrender.com")
    print(f"  🔐 Admin: https://vista-market.onrender.com/admin")
    print(f"  🔑 Parol: {Config.ADMIN_PASSWORD}")
    print("="*50)
    print("\n  ⚠️ DEFAULT MAHSULOTLAR YO'Q!")
    print("  Admin panel orqali o'zingiz qo'shing")
    print("="*50 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)