FROM n8nio/n8n:latest

# نصب بايثون وباقي الأدوات
USER root
RUN apk add --no-cache python3 py3-pip bash \
    && pip3 install gspread oauth2client playwright selenium webdriver-manager \
    && playwright install chromium

# انسخ السكربت لمجلد المستخدم في الحاوية
COPY sheet_images.py /home/node/sheet_images.py
RUN chown node:node /home/node/sheet_images.py

# عدّل للصلاحيات الافتراضية
USER node
