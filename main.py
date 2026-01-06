import requests
import socket
import base64
from concurrent.futures import ThreadPoolExecutor

SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Splitted-By-Protocol/ss.txt"

def decode_ss(config):
    try:
        clean_link = config.split('#')[0].replace('ss://', '')
        if '@' in clean_link:
            server_part = clean_link.split('@')[1]
            host, port = server_part.split(':')
            return host, int(port)
        else:
            decoded = base64.b64decode(clean_link + '===').decode('utf-8')
            import re
            match = re.search(r'@?([^:]+):(\d+)', decoded)
            if match: return match.group(1), int(match.group(2))
    except: return None, None

def check_connection(config):
    host, port = decode_ss(config)
    if not host or not port: return None
    try:
        # تست اتصال با تایم‌اوت کوتاه برای سرعت بیشتر
        with socket.create_connection((host, port), timeout=2.5):
            return config
    except: return None

def main():
    response = requests.get(SOURCE_URL)
    configs = list(set(response.text.splitlines()))
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_connection, configs))
    
    healthy = [c for c in results if c is not None]
    
    # استانداردسازی برای اپلیکیشن‌ها:
    # تبدیل لیست به یک متن واحد و سپس کدگذاری کل متن به Base64
    combined_configs = "\n".join(healthy)
    encoded_output = base64.b64encode(combined_configs.encode('utf-8')).decode('utf-8')
    
    with open("healthy_ss.txt", "w") as f:
        f.write(encoded_output)

if __name__ == "__main__":
    main()
