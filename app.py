from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json, os, uuid, requests
from datetime import datetime

class Config:
    SECRET_KEY = 'vista_market_2024'
    ADMIN_PASSWORD = 'vista2026'
    ADMIN_IDS = [6141183218]  # O'z Telegram IDingiz
    
    # ========== BOT TOKEN ==========
    BOT_TOKEN = '8830375215:AAFS10uy1cGPwqHU26J98Noo2Pv6JjKNr4U'
    
    PRODUCTS_FILE = 'products.json'
    ORDERS_FILE = 'orders.json'
    BANNERS_FILE = 'banners.json'
    USERS_FILE = 'users.json'
    UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
CORS(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_json(f, d=None):
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as fl:
            return json.load(fl)
    return d if d is not None else []

def save_json(f, data):
    with open(f, 'w', encoding='utf-8') as fl:
        json.dump(data, fl, ensure_ascii=False, indent=2)

# ==================== TELEGRAM BOT ====================
def send_telegram(chat_id, text, reply_markup=None):
    if not Config.BOT_TOKEN:
        print("⚠️ Bot token o'rnatilmagan!")
        return None
    url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"📤 Xabar yuborildi: {r.status_code}")
        return r.json()
    except Exception as e:
        print(f"❌ Xabar yuborishda xatolik: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print(f"📩 Webhook ma'lumot: {data}")
        
        if 'message' in data:
            msg = data['message']
            chat_id = msg['chat']['id']
            text = msg.get('text', '')
            user = msg.get('from', {})
            first_name = user.get('first_name', 'Foydalanuvchi')
            user_id = user.get('id')
            
            # Foydalanuvchini saqlash
            users = load_json(Config.USERS_FILE, {})
            users[str(user_id)] = {
                'user_id': user_id,
                'first_name': user.get('first_name', ''),
                'username': user.get('username', ''),
                'last_seen': datetime.now().isoformat()
            }
            save_json(Config.USERS_FILE, users)
            
            if text == '/start':
                webapp_url = request.host_url.rstrip('/')
                
                welcome = f"""👋 <b>Assalomu alaykum, {first_name}!</b>

🏪 <b>Vista Market</b> - Har bir uy uchun kerakli hamma narsa!

✅ <b>Bizning do'konda:</b>
• 🔥 Yuqori sifatli mahsulotlar
• 💰 Arzon narxlar
• 🚚 Tez yetkazib berish
• 💳 Click, Payme, Naqd to'lov

👇 <b>Do'konga kirish uchun tugmani bosing:</b>"""

                reply_markup = {
                    'inline_keyboard': [
                        [{'text': '🛍 VISTA MARKETGA KIRISH', 'web_app': {'url': webapp_url}}],
                        [{'text': 'ℹ️ Yordam', 'callback_data': 'help'}]
                    ]
                }
                
                send_telegram(chat_id, welcome, reply_markup)
            
            elif text == '/admin':
                if user_id in Config.ADMIN_IDS:
                    webapp_url = request.host_url.rstrip('/')
                    send_telegram(chat_id, f"🔐 <b>Admin Panel</b>\n\n🔗 {webapp_url}/admin\n🔑 Parol: {Config.ADMIN_PASSWORD}")
                else:
                    send_telegram(chat_id, "❌ Siz admin emassiz!")
            
            elif text == '/help':
                help_text = f"""📚 <b>Yordam</b>

🛍 <b>Do'konga kirish:</b> /start tugmasini bosing
📦 <b>Buyurtma holati:</b> Profil -> Buyurtmalarim
👤 <b>Profil:</b> Do'kon ichida "Mening" bo'limi"""
                send_telegram(chat_id, help_text)
            
            else:
                webapp_url = request.host_url.rstrip('/')
                reply_markup = {
                    'inline_keyboard': [
                        [{'text': '🛍 Do\'konga kirish', 'web_app': {'url': webapp_url}}]
                    ]
                }
                send_telegram(chat_id, f"👋 {first_name}, do'konimizga xush kelibsiz!\n\n👇 Tugmani bosing:", reply_markup)
        
        elif 'callback_query' in data:
            callback = data['callback_query']
            callback_id = callback['id']
            chat_id = callback['message']['chat']['id']
            data_cb = callback.get('data', '')
            
            url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/answerCallbackQuery"
            requests.post(url, json={'callback_query_id': callback_id})
            
            if data_cb == 'help':
                help_text = """📚 <b>Yordam bo'limi</b>

🛍 <b>Qanday xarid qilish?</b>
1. Do'konga kiring
2. Mahsulotni tanlang
3. Savatga qo'shing
4. Buyurtma bering

📦 <b>Buyurtma holati</b>
Profil -> Buyurtmalarim bo'limidan kuzatishingiz mumkin"""
                send_telegram(chat_id, help_text)
        
        return jsonify({'ok': True})
    except Exception as e:
        print(f"❌ Webhook xatolik: {e}")
        return jsonify({'ok': False})

# ==================== MAHSULOTLAR ====================
DEFAULT_PRODUCTS = [
    {"id":"1","name":"Chanel No. 5","description":"Legendary ayollar parfyumeriyasi","price":1500000,"old_price":1800000,"image":"https://images.unsplash.com/photo-1541643600914-78b084683601?w=400","category":"parfum","in_stock":15,"discount":17},
    {"id":"2","name":"Dior Sauvage","description":"Erkaklar uchun klassik atir","price":1200000,"old_price":1400000,"image":"https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=400","category":"parfum","in_stock":20,"discount":14},
    {"id":"3","name":"Idish To'plami","description":"12 dona keramik idish","price":650000,"old_price":800000,"image":"https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=400","category":"dishes","in_stock":30,"discount":19},
    {"id":"4","name":"Ariel 5kg","description":"Kir yuvish kukuni","price":85000,"old_price":100000,"image":"https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400","category":"powders","in_stock":100,"discount":15},
    {"id":"5","name":"Erkaklar Ko'ylagi","description":"Premium sifatli ko'ylak","price":350000,"old_price":450000,"image":"https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400","category":"clothes","in_stock":40,"discount":22},
    {"id":"6","name":"Tiffany Rose Gold","description":"Hashamatli atir","price":2200000,"old_price":2600000,"image":"https://images.unsplash.com/photo-1595425964058-1b30d2d112ed?w=400","category":"parfum","in_stock":5,"discount":15}
]

def load_products():
    p = load_json(Config.PRODUCTS_FILE)
    if not p:
        save_json(Config.PRODUCTS_FILE, DEFAULT_PRODUCTS)
        return DEFAULT_PRODUCTS
    return p

def save_products(p):
    save_json(Config.PRODUCTS_FILE, p)

def load_orders():
    return load_json(Config.ORDERS_FILE, [])

def save_orders(o):
    save_json(Config.ORDERS_FILE, o)

def load_banners():
    data = load_json(Config.BANNERS_FILE)
    if not data or 'banners' not in data:
        default = {
            "banners": [
                {"id": "1", "image": "https://images.pexels.com/photos/5632402/pexels-photo-5632402.jpeg?w=800", "title": "🔥 Super Chegirma!", "subtitle": "Barcha mahsulotlarga 20% gacha", "link": "/", "active": True, "order": 1},
                {"id": "2", "image": "https://images.pexels.com/photos/2927008/pexels-photo-2927008.jpeg?w=800", "title": "✨ Yangi Mahsulotlar", "subtitle": "Eng sifatli tovarlar", "link": "/", "active": True, "order": 2}
            ]
        }
        save_json(Config.BANNERS_FILE, default)
        return default
    return data

def save_banners(data):
    save_json(Config.BANNERS_FILE, data)

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
    p = load_products()
    cat = request.args.get('category', 'all')
    if cat and cat != 'all':
        p = [i for i in p if i.get('category') == cat]
    return jsonify({'success': True, 'products': p})

@app.route('/api/banners')
def get_banners():
    data = load_banners()
    active_banners = [b for b in data.get('banners', []) if b.get('active', True)]
    active_banners.sort(key=lambda x: x.get('order', 999))
    return jsonify({'success': True, 'banners': active_banners})

@app.route('/api/check-admin')
def check_admin():
    uid = request.args.get('user_id', type=int)
    return jsonify({'is_admin': uid in Config.ADMIN_IDS})

# ==================== BUYURTMALAR ====================
@app.route('/api/orders', methods=['GET', 'POST'])
def handle_orders():
    if request.method == 'POST':
        d = request.json
        p = load_products()
        
        sub = sum(i.get('price', 0) * i.get('quantity', 1) for i in d.get('items', []))
        
        order = {
            'order_id': str(uuid.uuid4())[:8].upper(),
            'user_id': d.get('user_id'),
            'customer_name': d.get('name', 'Mijoz'),
            'phone': d.get('phone', ''),
            'address': d.get('address', ''),
            'items': d.get('items', []),
            'total': sub,
            'status': 'pending',
            'status_text': 'Tayyorlanmoqda',
            'created_at': datetime.now().isoformat()
        }
        
        for item in order['items']:
            prod = next((x for x in p if x['id'] == item['id']), None)
            if prod:
                prod['in_stock'] = max(0, prod['in_stock'] - item.get('quantity', 1))
        
        save_products(p)
        orders = load_orders()
        orders.append(order)
        save_orders(orders)
        
        for admin_id in Config.ADMIN_IDS:
            send_telegram(admin_id, f"🛍 <b>Yangi buyurtma!</b>\n\n🆔 #{order['order_id']}\n👤 {order['customer_name']}\n📱 {order['phone']}\n💰 {order['total']:,} so'm")
        
        if d.get('user_id'):
            send_telegram(d['user_id'], f"✅ <b>Buyurtma qabul qilindi!</b>\n\n🆔 #{order['order_id']}\n💰 {order['total']:,} so'm\n📊 Holat: {order['status_text']}")
        
        return jsonify({'success': True, 'order': order})
    else:
        uid = request.args.get('user_id', type=int)
        orders = load_orders()
        if uid:
            orders = [o for o in orders if o.get('user_id') == uid]
        return jsonify({'success': True, 'orders': orders[::-1]})

# ==================== USER ====================
@app.route('/api/user', methods=['POST'])
def save_user():
    d = request.json
    users = load_json(Config.USERS_FILE, {})
    users[str(d.get('user_id', ''))] = {
        'user_id': d.get('user_id'),
        'first_name': d.get('first_name', ''),
        'username': d.get('username', ''),
        'phone': d.get('phone', ''),
        'updated_at': datetime.now().isoformat()
    }
    save_json(Config.USERS_FILE, users)
    return jsonify({'success': True})

# ==================== ADMIN ====================
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    d = request.json
    if d.get('password') == Config.ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/admin/check', methods=['GET'])
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

@app.route('/api/admin/products', methods=['POST', 'DELETE'])
def admin_products():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    p = load_products()
    if request.method == 'POST':
        d = request.json
        new = {
            'id': str(uuid.uuid4())[:8],
            'name': d.get('name', ''),
            'description': d.get('description', ''),
            'price': int(d.get('price', 0)),
            'old_price': int(d.get('old_price', d.get('price', 0))),
            'image': d.get('image', 'https://placehold.co/400'),
            'category': d.get('category', 'parfum'),
            'in_stock': int(d.get('in_stock', 10)),
            'discount': int(d.get('discount', 0))
        }
        p.append(new)
        save_products(p)
        return jsonify({'success': True})
    elif request.method == 'DELETE':
        pid = request.json.get('id')
        p = [x for x in p if x['id'] != pid]
        save_products(p)
        return jsonify({'success': True})

@app.route('/api/admin/products/update', methods=['PUT'])
def admin_update_product():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    d = request.json
    p = load_products()
    for i, prod in enumerate(p):
        if prod['id'] == d.get('id'):
            p[i].update(d)
            save_products(p)
            return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/admin/orders', methods=['GET'])
def admin_orders():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    orders = load_orders()
    return jsonify({'success': True, 'orders': orders[::-1]})

@app.route('/api/admin/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    d = request.json
    orders = load_orders()
    for o in orders:
        if o['order_id'] == order_id:
            o['status'] = d.get('status', o['status'])
            status_map = {'pending': 'Tayyorlanmoqda', 'confirmed': 'Yo\'lda', 'delivered': 'Yetkazilgan', 'cancelled': 'Bekor qilingan'}
            o['status_text'] = status_map.get(o['status'], o['status'])
            save_orders(orders)
            
            if o.get('user_id'):
                send_telegram(o['user_id'], f"📦 <b>Buyurtma statusi yangilandi!</b>\n\n🆔 #{o['order_id']}\n📊 Yangi holat: {o['status_text']}")
            
            return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/admin/banners', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_banners():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    
    data = load_banners()
    
    if request.method == 'GET':
        return jsonify({'success': True, 'banners': data.get('banners', [])})
    elif request.method == 'POST':
        d = request.json
        new_banner = {
            'id': str(uuid.uuid4())[:8],
            'image': d.get('image', ''),
            'title': d.get('title', ''),
            'subtitle': d.get('subtitle', ''),
            'link': d.get('link', '/'),
            'active': d.get('active', True),
            'order': d.get('order', len(data.get('banners', [])) + 1)
        }
        data['banners'].append(new_banner)
        save_banners(data)
        return jsonify({'success': True})
    elif request.method == 'PUT':
        d = request.json
        for i, b in enumerate(data['banners']):
            if b['id'] == d.get('id'):
                data['banners'][i].update({
                    'image': d.get('image', b['image']),
                    'title': d.get('title', b['title']),
                    'subtitle': d.get('subtitle', b['subtitle']),
                    'link': d.get('link', b['link']),
                    'active': d.get('active', b['active']),
                    'order': d.get('order', b['order'])
                })
                save_banners(data)
                return jsonify({'success': True})
        return jsonify({'success': False})
    elif request.method == 'DELETE':
        banner_id = request.json.get('id')
        data['banners'] = [b for b in data['banners'] if b['id'] != banner_id]
        save_banners(data)
        return jsonify({'success': True})

# ==================== RUN ====================
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*50)
    print("  🏪 VISTA MARKET - Telegram Bot bilan")
    print("="*50)
    print(f"  🌐 Do'kon: https://vista-market.onrender.com")
    print(f"  🔐 Admin: https://vista-market.onrender.com/admin")
    print(f"  🔑 Parol: {Config.ADMIN_PASSWORD}")
    print("="*50 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)