import requests
import socket
import base64
import re
from concurrent.futures import ThreadPoolExecutor

SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Splitted-By-Protocol/ss.txt"

def decode_ss(config):
    try:
        # حذف فضاها و جدا کردن نام سرور
        config = config.strip()
        clean_link = config.split('#')[0].replace('ss://', '')
        
        if '@' in clean_link:
            # فرمت استاندارد
            server_part = clean_link.split('@')[1]
            # حذف پارامترهای بعد از پورت (مثل /?plugin=...)
            host_port = re.split(r'[/?]', server_part)[0]
            host, port = host_port.split(':')
            return host, int(port)
        else:
            # فرمت تمام Base64
            decoded = base64.b64decode(clean_link + '===').decode('utf-8', errors='ignore')
            match = re.search(r'@?([^:]+):(\d+)', decoded)
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
        # افزایش تایم‌اوت به 5 ثانیه برای اطمینان بیشتر
        with socket.create_connection((host, port), timeout=5):
            return config
    except:
        return None

def main():
    print("Fetching configs...")
    response = requests.get(SOURCE_URL)
    # فیلتر کردن خطوط خالی
    configs = [line for line in response.text.splitlines() if line.startswith('ss://')]
    
    print(f"Found {len(configs)} configs. Testing...")
    
    # تست همزمان
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(check_connection, configs))
    
    healthy = [c for c in results if c is not None]
    print(f"Healthy configs: {len(healthy)}")
    
    if healthy:
        combined = "\n".join(healthy)
        encoded_output = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
        with open("healthy_ss.txt", "w") as f:
            f.write(encoded_output)
    else:
        # اگر هیچ‌کدام سالم نبودند، برای خالی نماندن فایل یک پیام تست می‌نویسیم
        with open("healthy_ss.txt", "w") as f:
            f.write("") 

if __name__ == "__main__":
    main()
