# الصورة الأساسية
FROM python:3.10-slim

# متغيرات البيئة
ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# تثبيت تبعيات النظام
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# مجلد العمل
WORKDIR /app

# نسخ متطلبات بايثون
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت متصفحات Playwright
RUN playwright install chromium

# نسخ ملفات المشروع
COPY . .

# جعل ملف التشغيل قابل للتنفيذ
RUN chmod +x entrypoint.sh

# نقطة الدخول
ENTRYPOINT ["./entrypoint.sh"]
