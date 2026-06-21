import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

# ۱. تنظیمات اتصال به گوگل شیت
# فایل credentials.json باید دقیقا کنار همین فایل پایتون باشد
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
#  کد جدید و هوشمند:
if os.path.exists("credentials.json"):
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
else:
    secret_data = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))
    creds = Credentials.from_service_account_info(secret_data, scopes=SCOPES)

client = gspread.authorize(creds)

SHEET_ID = '1acgDg8OK1GSfppROnfjuIFpB6191nz2cQLBDZZgFbgQ'
sheet = client.open_by_key(SHEET_ID).sheet1

# ۲. تنظیمات هدر برای فریب دادن سرور دیجی‌کالا
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.digikala.com/",
    "Origin": "https://www.digikala.com"
}

# ---> مهم: آدرس‌های خود را اینجا جایگذاری کنید <---
URL_INCREDIBLES = "https://api.digikala.com/v1/incredible-offers/"
URL_SEARCH = "https://api.digikala.com/v1/incredible-offers/products/?page=1&q= &sort=26"

def fetch_data(url):
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # بررسی خطاهای HTTP
        return response.json()
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def main():
    print("در حال دریافت اطلاعات از دیجی‌کالا...")
    all_products = []

    # استخراج شگفت‌انگیزها
    data_inc = fetch_data(URL_INCREDIBLES)
    if data_inc and 'data' in data_inc and 'incredible_products_list' in data_inc['data']:
        products = data_inc['data']['incredible_products_list'].get('products', [])
        all_products.extend(products)

    # استخراج جستجو
    data_search = fetch_data(URL_SEARCH)
    if data_search and 'data' in data_search and 'products' in data_search['data']:
        products = data_search['data'].get('products', [])
        all_products.extend(products)

    high_discount_deals = []

    # فیلتر و پردازش داده‌ها
    for p in all_products:
        try:
            variant = p.get('default_variant')
            if not variant: continue
            
            price_info = variant.get('price')
            if not price_info: continue

            discount = price_info.get('discount_percent', 0)
            
            if discount >= 90:
                title = p.get('title_fa', 'نامشخص')
                selling_price = price_info.get('selling_price', 0)
                product_url = f"https://www.digikala.com/product/dkp-{p.get('id')}"
                
                # برای جلوگیری از تکراری شدن کالاها در لیست
                if not any(item[0] == title for item in high_discount_deals):
                    high_discount_deals.append([title, discount, selling_price, product_url])
        except Exception as e:
            continue

    # مرتب‌سازی نزولی بر اساس درصد تخفیف
    high_discount_deals.sort(key=lambda x: x[1], reverse=True)

    print(f"تعداد {len(high_discount_deals)} کالای با تخفیف بالای 90 درصد پیدا شد. در حال آپدیت شیت...")

    # آماده‌سازی داده‌ها برای گوگل شیت
    tehran_tz = pytz.timezone('Asia/Tehran')
    update_time = datetime.now(tehran_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    headers_row = ["نام محصول", "درصد تخفیف", "قیمت فروش (ریال)", "لینک محصول", f"آخرین بروزرسانی: {update_time}"]
    
    # تبدیل تخفیف به فرمت رشته‌ای دارای %
    final_data = [headers_row]
    if high_discount_deals:
        for item in high_discount_deals:
            final_data.append([item[0], f"{item[1]}%", item[2], item[3], ""])
    else:
        final_data.append(["هیچ کالایی با تخفیف بالای ۹۰٪ یافت نشد.", "-", "-", "-", "-"])

    # پاک کردن شیت و نوشتن داده‌های جدید
    sheet.clear()
    sheet.update(range_name='A1', values=final_data)
    
    # فرمت دادن به ردیف اول (اختیاری - با استفاده از API پیشرفته‌تر gspread انجام می‌شود، اما برای سادگی اینجا فقط داده‌ها را نوشتیم)
    print("گوگل شیت با موفقیت آپدیت شد!")

if __name__ == "__main__":
    main()