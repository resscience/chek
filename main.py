import requests
import socket
import base64
import re
import time
from concurrent.futures import ThreadPoolExecutor

# لینک درست و خام (Raw) برای دسترسی مستقیم به متن کانفیگ‌ها
SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/ss.txt"

def decode_ss(config):
    try:
        config = config.strip()
        link_part = config.split('#')[0].replace('ss://', '')
        if '@' in link_part:
            server_info = link_part.split('@')[1]
            host_port = re.split(r'[/?]', server_info)[0]
            host, port = host_port.split(':')
            return host, int(port)
        else:
            decoded = base64.b64decode(link_part + '===').decode('utf-8', errors='ignore')
            match = re.search(r'([^@:]+):(\d+)', decoded)
            if match: return match.group(1), int(match.group(2))
    except: return None, None

def check_connection(config):
    host, port = decode_ss(config)
    if not host or not port: return None
    try:
        # تست اتصال TCP با تایم‌اوت 5 ثانیه
        with socket.create_connection((host, port), timeout=5):
            return config
    except: return None

def main():
    print(f"Connecting to Raw Source...")
    try:
        # دریافت محتوا
        response = requests.get(SOURCE_URL, timeout=20)
        content = response.text
        
        # استخراج لینک‌ها
        configs = re.findall(r'ss://[^\s]+', content)
        print(f"Found {len(configs)} configs. Testing now...")

        if not configs:
            print("Zero configs found. Check if the Raw link is still valid.")
            return

        # تست همزمان (Parallel)
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(check_connection, configs))
        
        healthy = [c for c in results if c is not None]
        print(f"Success! {len(healthy)} healthy configs found.")

        # ساخت خروجی نهایی
        if healthy:
            current_time = time.strftime("%H:%M")
            processed = [f"{c.split('#')[0]}#Updated_{current_time}" for c in healthy]
            combined = "\n".join(processed)
            # کدگذاری کل لیست به Base64
            final_b64 = base64.b64encode(combined.encode()).decode()
            
            with open("healthy_ss.txt", "w") as f:
                f.write(final_b64)
        else:
            with open("healthy_ss.txt", "w") as f:
                f.write("")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
