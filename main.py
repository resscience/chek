import requests
import socket
import base64
import re
import time
from concurrent.futures import ThreadPoolExecutor

# منبع اصلی
SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Splitted-By-Protocol/ss.txt"

def decode_ss(config):
    try:
        # استخراج بخش اصلی لینک قبل از علامت #
        link_part = config.split('#')[0].replace('ss://', '')
        
        if '@' in link_part:
            # فرمت استاندارد: ss://method:pass@host:port
            server_info = link_part.split('@')[1]
            # حذف پارامترهای احتمالی بعد از پورت
            host_port = re.split(r'[/?]', server_info)[0]
            host, port = host_port.split(':')
            return host, int(port)
        else:
            # فرمت تمام Base64
            decoded = base64.b64decode(link_part + '===').decode('utf-8', errors='ignore')
            match = re.search(r'([^@:]+):(\d+)$', decoded) # پیدا کردن host:port در انتهای متن
            if not match:
                match = re.search(r'@([^:]+):(\d+)', decoded)
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
        # تست اتصال با تایم‌اوت 7 ثانیه
        with socket.create_connection((host, port), timeout=7):
            return config
    except:
        return None

def main():
    print("Fetching configs...")
    try:
        response = requests.get(SOURCE_URL, timeout=15)
        content = response.text
        
        # پیدا کردن تمام لینک‌هایی که با ss:// شروع می‌شوند با استفاده از Regex
        # این کار باعث می‌شود حتی اگر فضایی قبل یا بعد لینک باشد، باز هم پیدا شود
        configs = re.findall(r'ss://[^\s]+', content)
        
        print(f"Found {len(configs)} raw configs. Testing...")
        
        if not configs:
            print("No ss:// links found in the source!")
            return

        # تست همزمان برای سرعت بالا
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(check_connection, configs))
        
        healthy = [c for c in results if c is not None]
        print(f"Healthy configs: {len(healthy)}")
        
        current_time = time.strftime("%Y-%m-%d %H:%M")
        
        if healthy:
            # اضافه کردن برچسب زمان به انتهای هر کانفیگ
            final_list = []
            for c in healthy:
                clean_c = c.split('#')[0]
                final_list.append(f"{clean_c}#Updated_{current_time.replace(' ', '_')}")
            
            combined = "\n".join(final_list)
            # تبدیل کل لیست به Base64 برای استفاده در اپلیکیشن‌ها
            encoded_output = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
            
            with open("healthy_ss.txt", "w") as f:
                f.write(encoded_output)
            print("File 'healthy_ss.txt' updated successfully.")
        else:
            # اگر هیچ‌کدام کار نکرد، فایل را با یک متن ساده آپدیت کن که بدانی اسکریپت اجرا شده
            with open("healthy_ss.txt", "w") as f:
                f.write(base64.b64encode(f"None_Found_At_{current_time}".encode()).decode())
            print("No healthy configs found, file updated with empty state.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
