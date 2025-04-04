import pyrogram
import telebot
import os
import logging
import subprocess
import config  # config.py dosyasını içe aktar
import random
import string

from telebot import types  # types modülünü import etmeliyiz

# Configure logging
logging.basicConfig(level=logging.INFO)

# config.py'den token'ı ve diğer ayarları alıyoruz
TOKEN = config.TOKEN
ADMIN_ID = config.ADMIN_ID
ALLOWED_USERS_FILE = config.ALLOWED_USERS_FILE
RUNNING_FILES = config.RUNNING_FILES
START_IMG = config.START_IMG

allowed_users = set()

def load_allowed_users():
    if os.path.exists(ALLOWED_USERS_FILE):
        with open(ALLOWED_USERS_FILE, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def save_allowed_user(user_id):
    with open(ALLOWED_USERS_FILE, 'a') as file:
        file.write(f"{user_id}\n")

def save_running_file(file_path):
    with open(RUNNING_FILES, 'a') as file:
        file.write(f"{file_path}\n")

allowed_users = load_allowed_users()

# Botu başlatma
bot = telebot.TeleBot(TOKEN)

# START MESAJ V2
@bot.message_handler(commands=['start'])
def start(message):
    first_name = message.from_user.first_name
    welcome_text = f"""
╔════════════════════╗
   🎩 HOŞGELDİN {first_name} 💚
╚════════════════════╝

🚀 BEN PYTHON SAAS HİZMET BOTUYUM KESİNTİSİZ DESTEK İÇİN BURADAYIM \n\n  
❤️ GENELDE BENİ TELEGRAM BOTLARIM İÇİN İDARE EDİYORLAR, 

🔥 POWERED BY OPEN Aİ
    """

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("KURUCU", url="https://t.me/ViosCeo"))
    markup.add(types.InlineKeyboardButton("KULLANIM", callback_data="help"))
    markup.add(types.InlineKeyboardButton("FİYATLANDIRMA", callback_data="price"))

    bot.send_photo(message.chat.id, config.START_IMG, caption=welcome_text, parse_mode="Markdown", reply_markup=markup)

# Callback işlemleri
@bot.callback_query_handler(func=lambda call: call.data == "help")
def callback_help(call):
    bot.send_message(call.message.chat.id, "[1] ✅ PROJE AKTİF \n\n [ ÖRNEK CERENLOVELY.PY ] İLET VEYA GÖNDER ] \n\n [2] ✅ LİSTELEMEK \n\n [ /docs : AKTİF OLAN PROJELER LİSTELENİR ] \n\n [3] ✅ ÇÖP KUTUSU \n\n [ ÖRNEK /delete CERENLOVELY.PY ]")

@bot.callback_query_handler(func=lambda call: call.data == "price")
def callback_price(call):
    bot.send_message(call.message.chat.id, "🎲 FİYATLAR : \n\n [1] 💬 1 AY : [10 TRY] \n [2] 💬 2 AY : [20 TRY] \n [3] 💬 3 AY : [30 TRY] \n [4] 💬 5 AY : [50 TRY] \n\n NOT : ÖZEL BÜTÇELENDİRME VE PLAN TASSARUF İÇİN KURUCU İLE İLETİŞİME GEÇEBİLİRSİN ✓")


@bot.message_handler(commands=['authorize'])
def authorize_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            save_allowed_user(user_id)
            allowed_users.add(user_id)
            bot.send_message(message.chat.id, f"✅ BAŞARILI : \n\n Kullanıcı {user_id} yetkilendirildi.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "📛 BAŞARISIZ : \n\n Lütfen geçerli bir kullanıcı ID'si girin.")
    else:
        bot.send_message(message.chat.id, "📛 BAŞARISIZ : \n\n Bu komutu kullanma yetkiniz yok.")

# DOCS 
# /docs komutu ile aktif dosyaların listelenmesi ve kategorilere ayıran yapı
@bot.message_handler(commands=['docs'])
def list_user_files(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "📛 UYARI : \n\n Bu komut yalnızca yetkili kullanıcılar içindir.")
        return

    try:
        # Kullanıcının Chat ID'sini alalım
        user_chat_id = message.from_user.id
        
        # Kullanıcıya özel bir klasör belirleyelim
        user_folder = f"run/{user_chat_id}"

        # Eğer kullanıcıya ait dosya klasörü varsa
        if os.path.exists(user_folder):
            user_files = os.listdir(user_folder)
            active_files = []
            sleeping_files = []
            suspicious_files = []

            # Dosyaları kategorilere ayıralım
            for file in user_files:
                file_path = os.path.join(user_folder, file)
                if file.endswith('.py'):
                    try:
                        # Dosyanın içeriğine göre durumunu kontrol et
                        with open(file_path, 'r') as f:
                            content = f.read()
                        # Aktif dosyayı belirleme basit kontrolü
                        if "active" in content:
                            active_files.append(file)
                        else:
                            sleeping_files.append(file)
                    except Exception as e:
                        suspicious_files.append(file)

# Rastgele dosya adı oluşturma fonksiyonu
def generate_random_filename(extension=".py"):
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    return f"{random_string}{extension}"

@bot.message_handler(commands=['delete'])
def delete_file(message):
    if message.from_user.id in allowed_users or message.from_user.id == ADMIN_ID:
        # Dosya silme mantığı
        pass  # Buraya uygun kodu ekleyin

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "Bu komutu kullanma yetkiniz yok.")
        return

    try:
        if not message.document.file_name.endswith('.py'):
            bot.send_message(message.chat.id, "Lütfen sadece Python dosyaları (.py) gönderin.")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Dosyayı kaydetme
        file_path = message.document.file_name
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Kodu güvenli bir şekilde arka planda çalıştırma
        subprocess.Popen(["python3", file_path])
        bot.send_message(message.chat.id, f"✅ BAŞARILI :\n\n {file_path} dosyası arka planda çalıştırılıyor.")

    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        bot.send_message(message.chat.id, f"Hata oluştu: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.send_message(message.chat.id, "Bilinmeyen komut. Lütfen geçerli bir komut kullanın.")

# Bot başlatıldığında yetkilileri yükle
allowed_users = load_allowed_users()

bot.polling()
