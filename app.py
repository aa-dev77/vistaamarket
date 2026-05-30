from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import db, Product, Order, Banner, User
from config import Config
import os, uuid, json, requests
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== DATABASE ====================
def init_db():
    with app.app_context():
        db.create_all()
        # Default mahsulotlar
        if Product.query.count() == 0:
            default_products = [
                Product(id="1", name="Chanel No. 5", description="Legendary ayollar parfyumeriyasi", price=1500000, old_price=1800000, category="parfum", in_stock=15, discount=17, sold_this_week=45),
                Product(id="2", name="Dior Sauvage", description="Erkaklar uchun klassik atir", price=1200000, old_price=1400000, category="parfum", in_stock=20, discount=14, sold_this_week=32),
                Product(id="3", name="Idish To'plami", description="12 dona keramik idish", price=650000, old_price=800000, category="dishes", in_stock=30, discount=19, sold_this_week=15),
                Product(id="4", name="Ariel 5kg", description="Kir yuvish kukuni", price=85000, old_price=100000, category="powders", in_stock=100, discount=15, sold_this_week=200),
                Product(id="5", name="Erkaklar Ko'ylagi", description="Premium sifatli ko'ylak", price=350000, old_price=450000, category="clothes", in_stock=40, discount=22, sold_this_week=18),
                Product(id="6", name="Tiffany Rose Gold", description="Hashamatli atir", price=2200000, old_price=2600000, category="parfum", in_stock=5, discount=15, sold_this_week=12)
            ]
            for p in default_products:
                db.session.add(p)
            db.session.commit()
            print("✅ Default mahsulotlar qo'shildi")

init_db()

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
    
    # Adminlarga xabar
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

# ==================== RUN ====================
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*50)
    print("  🏪 VISTA MARKET - PostgreSQL bilan")
    print("="*50)
    print(f"  🌐 Do'kon: https://vista-market.onrender.com")
    print(f"  🔐 Admin: https://vista-market.onrender.com/admin")
    print(f"  🔑 Parol: {Config.ADMIN_PASSWORD}")
    print("="*50 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)