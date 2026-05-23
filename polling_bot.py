import requests
import time
import json
from datetime import datetime

# SIZNING MA'LUMOTLARINGIZ
BOT_TOKEN = '8716353787:AAGAddW33W3jbOa0CVZVxez1MqqHL-bvCf0'  # YANGI TOKEN OLING!
WEBAPP_URL = 'https://zenilpro-backend.onrender.com'  # Keyinchalik serverga qo'yganingizda

# Admin ID
ADMIN_IDS = [6769229781]

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json()
    except:
        return None

def handle_message(message):
    chat_id = message['chat']['id']
    text = message.get('text', '')
    user = message.get('from', {})
    first_name = user.get('first_name', 'Foydalanuvchi')
    user_id = user.get('id')
    
    # /start
    if text == '/start':
        welcome = f"""🎉 <b>Assalomu alaykum, {first_name}!</b>

🔥 <b>Vista</b> - Premium Parfyumeriya Do'koni

🛍 Bu yerda siz:
• 💎 Original parfyumeriya
• 🎨 Kosmetika
• 🍽️ Idish-tovoq
• 👕 Kiyim-kechak
• 🧴 Kir yuvish kukunlari

<i>Do'konga kirish uchun pastdagi tugmani bosing:</i>"""

        # Hozircha server bo'lmagani uchun URL ni ko'rsatamiz
        # Serverga qo'yganingizda WEBAPP_URL ni o'zgartirasiz
        reply_markup = {
            'inline_keyboard': [
                [{
                    'text': '🛍 Do\'konga kirish',
                    'web_app': {'url': WEBAPP_URL}
                }],
                [
                    {'text': 'ℹ️ Yordam', 'callback_data': 'help'}
                ]
            ]
        }
        
        send_message(chat_id, welcome, reply_markup)
        
        # Menu keyboard
        menu_markup = {
            'keyboard': [
                [{'text': '🛍 Katalog'}, {'text': '🛒 Savat'}],
                [{'text': '❤️ Sevimlilar'}, {'text': '👤 Profil'}]
            ],
            'resize_keyboard': True
        }
        send_message(chat_id, "Tez menyu:", menu_markup)
    
    # /menu
    elif text == '/menu' or text == '🛍 Katalog':
        reply_markup = {
            'inline_keyboard': [[{
                'text': '🛍 Do\'konga kirish',
                'web_app': {'url': WEBAPP_URL}
            }]]
        }
        send_message(chat_id, "Do'konga kirish:", reply_markup)
    
    # /help
    elif text == '/help' or text == 'ℹ️ Yordam':
        help_text = f"""📚 <b>Yordam</b>

/start - Botni ishga tushirish
/menu - Katalogga kirish
/help - Yordam

<i>Savollar bo'lsa adminga yozing</i>"""
        send_message(chat_id, help_text)
    
    # /admin
    elif text == '/admin':
        if user_id in ADMIN_IDS:
            send_message(chat_id, f"🔐 Admin panel URL: {WEBAPP_URL}/admin\nParol: zeniladmin2024")
        else:
            send_message(chat_id, "❌ Siz admin emassiz!")
    
    # Profil
    elif text == '👤 Profil':
        send_message(chat_id, f"👤 <b>{first_name}</b>\nID: {user_id}\nWeb App da ko'ring: /menu")
    
    # Savat
    elif text == '🛒 Savat':
        send_message(chat_id, "Savat Web App da. /menu bosing")
    
    # Sevimlilar
    elif text == '❤️ Sevimlilar':
        send_message(chat_id, "Sevimlilar Web App da. /menu bosing")

def handle_callback(callback):
    callback_id = callback['id']
    data = callback.get('data', '')
    chat_id = callback['message']['chat']['id']
    
    # Callback ga javob
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    requests.post(url, json={'callback_query_id': callback_id})
    
    if data == 'help':
        send_message(chat_id, "📚 Yordam uchun /help bosing")

def main():
    print("=" * 50)
    print("  🤖 ZenilPro Bot Polling")
    print("=" * 50)
    print("  Bot ishga tushdi...")
    print("  /start ni bosing!")
    print("  CTRL+C to'xtatish")
    print("=" * 50)
    
    # Avval eski webhook ni o'chirish
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    
    offset = 0
    
    while True:
        try:
            # Yangi xabarlarni olish
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {'offset': offset, 'timeout': 30}
            r = requests.get(url, params=params, timeout=35)
            data = r.json()
            
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        handle_message(update['message'])
                    
                    elif 'callback_query' in update:
                        handle_callback(update['callback_query'])
            
        except KeyboardInterrupt:
            print("\nBot to'xtatildi!")
            break
        except Exception as e:
            print(f"Xatolik: {e}")
            time.sleep(5)

if __name__ == '__main__':
    # Bot komandalarini o'rnatish
    commands = {
        "commands": [
            {"command": "start", "description": "Botni ishga tushirish"},
            {"command": "menu", "description": "Menyu"},
            {"command": "help", "description": "Yordam"},
            {"command": "admin", "description": "Admin panel"}
        ]
    }
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands", json=commands)
    
    main()
