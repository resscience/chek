import os
import base64
import time
import re

SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/ss.txt"

def main():
    print("Start fetching...")
    os.system(f"curl -s -L {SOURCE_URL} -o raw_configs.txt")
    
    if not os.path.exists("raw_configs.txt"):
        return

    with open("raw_configs.txt", "r") as f:
        content = f.read().strip()

    # مرحله ۱: اگر کل فایل Base64 است، آن را باز کنیم
    try:
        if "ss://" not in content:
            print("Content seems encoded, decoding...")
            content = base64.b64decode(content + "====").decode('utf-8', errors='ignore')
    except:
        pass

    # مرحله ۲: استخراج لینک‌ها
    configs = re.findall(r'ss://[^\s]+', content)
    print(f"🔍 Found {len(configs)} configs.")

    if configs:
        # فیلتر کردن و تست پینگ سریع
        import socket
        healthy = []
        print("Testing connections (Top 50)...")
        
        for c in configs[:50]:
            try:
                # استخراج IP و Port برای تست سریع
                link_part = c.split('#')[0].replace('ss://', '')
                if '@' in link_part:
                    host_port = re.split(r'[/?]', link_part.split('@')[1])[0]
                    host, port = host_port.split(':')
                    with socket.create_connection((host, int(port)), timeout=3):
                        healthy.append(c)
            except:
                continue

        print(f"✅ Healthy configs: {len(healthy)}")
        
        # اگر حتی یکی هم سالم بود، یا اگر نبود همان لیست اولیه را بده
        to_save = healthy if healthy else configs[:20]
        
        current_time = time.strftime("%H:%M")
        final_list = [f"{c.split('#')[0]}#Updated_{current_time}" for c in to_save]
        
        encoded_output = base64.b64encode("\n".join(final_list).encode()).decode()
        
        with open("healthy_ss.txt", "w") as f:
            f.write(encoded_output)
        print("Done! Check your repo now.")
    else:
        print("❌ Critical: No ss:// links even after decoding attempt.")

if __name__ == "__main__":
    main()
