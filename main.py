import requests
import socket
import base64
import time
from concurrent.futures import ThreadPoolExecutor

SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Splitted-By-Protocol/ss.txt"

def decode_ss(config):
    try:
        config = config.strip()
        if not config.startswith('ss://'): return None
        clean_link = config.split('#')[0].replace('ss://', '')
        if '@' in clean_link:
            server_part = clean_link.split('@')[1]
            host, port = server_part.split(':')
            return host.split('/')[0], int(port.split('/')[0])
    except: return None, None

def check_connection(config):
    host, port = decode_ss(config)
    if not host or not port: return None
    try:
        # افزایش تایم‌اوت به 7 ثانیه برای سرورهای کندتر
        with socket.create_connection((host, port), timeout=7):
            return config
    except: return None

def main():
    print("Fetching...")
    response = requests.get(SOURCE_URL)
    configs = [line for line in response.text.splitlines() if line.strip()]
    
    with ThreadPoolExecutor(max_workers=40) as executor:
        results = list(executor.map(check_connection, configs))
    
    healthy = [c for c in results if c is not None]
    
    # اضافه کردن یک نام متغیر به انتهای هر کانفیگ برای تغییر محتوا و شناسایی
    # این کار باعث می‌شود گیت‌هاب همیشه تغییر را حس کند
    final_configs = []
    current_time = time.strftime("%H:%M")
    for c in healthy:
        final_configs.append(f"{c.split('#')[0]}#Checked_{current_time}")

    if final_configs:
        combined = "\n".join(final_configs)
        encoded_output = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
        with open("healthy_ss.txt", "w") as f:
            f.write(encoded_output)
        print(f"Success! Found {len(healthy)} healthy configs.")
    else:
        # اگر هیچی سالم نبود، یک فایل خالی با یک کاراکتر رندوم بساز که آپدیت شود
        with open("healthy_ss.txt", "w") as f:
            f.write(f"No_Active_Configs_At_{current_time}")

if __name__ == "__main__":
    main()
