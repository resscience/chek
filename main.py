import requests
import socket
import base64
import re
import time
from concurrent.futures import ThreadPoolExecutor

# لینک مستقیم و خام
SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/ss.txt"

def decode_ss(config):
    try:
        # پاکسازی لینک از فضاهای خالی احتمالی
        config = config.strip()
        link_part = config.split('#')[0].replace('ss://', '')
        
        if '@' in link_part:
            server_info = link_part.split('@')[1]
            host_port = re.split(r'[/?]', server_info)[0]
            host, port = host_port.split(':')
            return host, int(port)
        else:
            # دیکود کردن بخش Base64
            decoded = base64.b64decode(link_part + '===').decode('utf-8', errors='ignore')
            # پیدا کردن الگوهای host:port
            match = re.search(r'([^@:]+):(\d+)', decoded)
            if match:
                return match.group(1), int(match.group(2))
    except:
        pass
    return None, None

def check_connection(config):
    host, port = decode_ss(config)
    if not host or not port:
        return None
    try:
        # تست اتصال TCP
        with socket.create_connection((host, port), timeout=5):
            return config
    except:
        return None

def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching from: {SOURCE_URL}")
    try:
        response = requests.get(SOURCE_URL, headers=headers, timeout=20)
        content = response.text
        
        # چاپ 100 کاراکتر اول برای دیباگ در لاگ شما
        print(f"Preview of content: {content[:100]}")
        
        # استخراج لینک‌ها با متد منعطف‌تر
        configs = re.findall(r'ss://[a-zA-Z0-9%=/@#\.\-_]+', content)
        
        # اگر لیست خالی بود، یک شانس دیگر با متد ساده‌تر
        if not configs:
            configs = [line.strip() for line in content.splitlines() if 'ss://' in line]

        print(f"Found {len(configs)} configs. Starting test...")
        
        if not configs:
            print("❌ No configs found! Check the URL or content type.")
            # ایجاد فایل برای جلوگیری از خطای گیت
            with open("healthy_ss.txt", "w") as f: f.write("")
            return

        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(check_connection, configs))
        
        healthy = [c for c in results if c is not None]
        print(f"✅ Healthy configs found: {len(healthy)}")
        
        # ساخت خروجی نهایی
        current_time = time.strftime("%H:%M")
        final_output = ""
        
        if healthy:
            processed_configs = []
            for c in healthy:
                # تمیز کردن لینک و اضافه کردن برچسب زمان
                base_link = c.split('#')[0]
                processed_configs.append(f"{base_link}#Checked_{current_time}")
            
            combined = "\n".join(processed_configs)
            final_output = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
        else:
            final_output = base64.b64encode(f"No_Working_Server_At_{current_time}".encode()).decode()

        with open("healthy_ss.txt", "w") as f:
            f.write(final_output)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
