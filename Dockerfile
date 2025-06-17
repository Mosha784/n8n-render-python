# 1) استخدم صورة Playwright/ Python مبنية على Ubuntu (Debian-based)
FROM mcr.microsoft.com/playwright/python:v1.39.0-focal

# 2) حدّد مجلّد العمل
WORKDIR /app

# 3) انسخ ملف المتطلبات لو عندك one، أو ثبت الحزم يدويًا:
# إذا عندك requirements.txt فا استخدم:
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# أما إذا ما عندك requirements.txt فتثبت بالشكل التالي:
RUN pip install --no-cache-dir \
    gspread \
    oauth2client \
    selenium \
    webdriver-manager

# Playwright متضمّن بالصورة، لكن لازم تثبت المتصفّحات:
RUN playwright install --with-deps

# 4) انسخ كل السكربتات الموجودة في المجلّد الحالي إلى داخل الصورة
COPY . .

# 5) حدّد الأمر الافتراضي للتشغيل عند إطلاق الحاوية
CMD ["python", "sheet_images.py"]
