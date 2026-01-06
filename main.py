import requests
import base64
import time

# لینک مستقیم و خام
SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/ss.txt"

def main():
    print("Start fetching...")
    try:
        # دریافت محتوا از گیت‌هاب
        response = requests.get(SOURCE_URL, timeout=15)
        lines = response.text.splitlines()
        
        # پیدا کردن لینک‌های شادوساکس
        configs = [l.strip() for l in lines if l.startswith('ss://')]
        print(f"Found {len(configs)} configs.")

        # فعلاً برای اینکه مطمئن بشی فایل ساخته میشه، تست پینگ رو حذف می‌کنیم
        # و فقط 20 تا از کانفیگ‌ها رو برمی‌داریم که حجم فایل اوکی باشه
        if configs:
            selected_configs = configs[:30] # 30 تای اول رو بردار
            
            # اضافه کردن ساعت به اسم کانفیگ‌ها
            current_time = time.strftime("%H:%M")
            final_list = []
            for c in selected_configs:
                clean_c = c.split('#')[0]
                final_list.append(f"{clean_c}#Update_{current_time}")
            
            # تبدیل به Base64 برای اینپورت راحت در برنامه
            combined = "\n".join(final_list)
            encoded = base64.b64encode(combined.encode()).decode()
            
            with open("healthy_ss.txt", "w") as f:
                f.write(encoded)
            print("Done! File created.")
        else:
            print("No ss:// links found in source.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
