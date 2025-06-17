FROM n8nio/n8n:latest

# 1) انتقل إلى المستخدم root عشان تثبت الأدوات
USER root

# 2) ثبت بايثون وبايب وباقي الأدوات مع مكتبات Chromium اللازمة
RUN apk add --no-cache python3 py3-pip bash chromium nss \
    && pip3 install \
         gspread \
         oauth2client \
         selenium \
         webdriver-manager \
         playwright \
    && python3 -m playwright install --with-deps

# 3) انسخ السكربت الخاص فينا
COPY sheet_images.py /home/node/sheet_images.py
RUN chown node:node /home/node/sheet_images.py

# 4) عدّل للصلاحيات الاعتيادية للمستخدم node
USER node
