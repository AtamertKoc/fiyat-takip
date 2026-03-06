import requests
from bs4 import BeautifulSoup
import time

# --- Telegram Ayar Kısmı (BURAYI KENDİ BİLGİLERİNİZ İLE DEĞİŞTİRİN) ---
TELEGRAM_TOKEN = ""
CHAT_ID = ""


# Yeni ürün girmek için aşağıda ki örneklere sadık kalarak yeni dict ekleyiniz
URUNLER = [
    {
        "ad": "Kumtel Ocak (Trendyol)",
        "url": "https://www.trendyol.com/kumtel/lx-7115-ayarlanabilir-termostatli-tekli-elektrikli-ocak-siyah-p-79604490",
        "hedef_fiyat": 900,
        "etiket": "span",
        "sinif": "prc-dsc",
        "son_bildirilen_fiyat": float('inf')
    },
    {
        "ad": "İkinci Ürün (Diğer Site)",
        "url": "https://ornek-site.com/urun-linki",
        "hedef_fiyat": 1000,
        "etiket": "span", 
        "sinif": "price",
        "son_bildirilen_fiyat": float('inf')
    },
    {
        "ad": "Üçüncü Ürün (Farklı Site)",
        "url": "https://baska-site.com/urun-linki",
        "hedef_fiyat": 1500,
        "etiket": "div", 
        "sinif": "sale-price sale-variant-price",
        "son_bildirilen_fiyat": float('inf')
    }
]

def fiyat_cek(urun):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(urun["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        
        fiyat_etiketi = soup.find(urun["etiket"], class_=urun["sinif"])
        
        if fiyat_etiketi:
            fiyat_metni = fiyat_etiketi.get_text()
            
            
            temiz_fiyat = "".join(filter(lambda x: x.isdigit() or x in ",.", fiyat_metni))
            
         
            if "," in temiz_fiyat and "." in temiz_fiyat:
                temiz_fiyat = temiz_fiyat.replace(".", "").replace(",", ".")
            elif "," in temiz_fiyat:
                temiz_fiyat = temiz_fiyat.replace(",", ".")
                
            return float(temiz_fiyat)
    except Exception as e:
        print(f"Hata oluştu ({urun['ad']}): {e}")
    return None

def telegram_bildirim_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj}
    try:
        requests.post(url, data=payload)
    except:
        print("Telegram hatası!")


print("--- SİSTEM BAŞLATILDI ---")
print(f"{len(URUNLER)} adet ürün takip ediliyor...")

while True:
    print(f"\nKontrol zamanı: {time.strftime('%H:%M:%S')}")
    
    for urun in URUNLER:
        guncel_fiyat = fiyat_cek(urun)
        
        if guncel_fiyat:
            print(f"-> {urun['ad']}: {guncel_fiyat} TL")
            
        
            if guncel_fiyat <= urun["hedef_fiyat"] and guncel_fiyat < urun["son_bildirilen_fiyat"]:
                mesaj = f"FİYAT DÜŞTÜ!\n\nÜrün: {urun['ad']}\nFiyat: {guncel_fiyat} TL\nLink: {urun['url']}"
                telegram_bildirim_gonder(mesaj)
                urun["son_bildirilen_fiyat"] = guncel_fiyat 
                print(f"   >>> BİLDİRİM GÖNDERİLDİ!")
            
          
            elif guncel_fiyat > urun["hedef_fiyat"]:
                urun["son_bildirilen_fiyat"] = float('inf')
        else:
            print(f"-> {urun['ad']}: Fiyat bulunamadı! Etiketi kontrol et.")
        
        time.sleep(3) 

    print("-" * 30)
    time.sleep(60) 