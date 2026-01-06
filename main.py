import os
import base64
import time
import re

# استفاده از دستور مستقیم سیستم‌عامل برای دور زدن محدودیت‌ها
SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/ss.txt"

def main():
    print("Start fetching using system curl...")
    # دانلود فایل با دستور curl لینوکس
    os.system(f"curl -s -L {SOURCE_URL} -o raw_configs.txt")
    
    if not os.path.exists("raw_configs.txt"):
        print("❌ Could not download the file.")
        return

    with open("raw_configs.txt", "r") as f:
        content = f.read()

    # پیدا کردن لینک‌ها با دقت بالا
    configs = re.findall(r'ss://[^\s]+', content)
    print(f"🔍 Found {len(configs)} configs in the file.")

    if configs:
        # انتخاب 50 تای اول (برای اطمینان از شلوغ نشدن)
        selected = configs[:50]
        current_time = time.strftime("%H:%M")
        
        # تمیزکاری و نام‌گذاری
        final_list = []
        for c in selected:
            # حذف کاراکترهای اضافه مثل ویرگول یا کوتیشن احتمالی
            clean = c.split('#')[0].strip().replace('"', '').replace("'", "")
            final_list.append(f"{clean}#FastSS_{current_time}")
        
        combined = "\n".join(final_list)
        encoded = base64.b64encode(combined.encode()).decode()
        
        with open("healthy_ss.txt", "w") as f:
            f.write(encoded)
        print("✅ File 'healthy_ss.txt' created successfully!")
    else:
        print("❌ Still found 0 configs. Let's check the content...")
        print(f"Content length: {len(content)} characters.")

if __name__ == "__main__":
    main()
