# 1) إبدأ من صورة n8n الرسمية
FROM n8nio/n8n:latest

# 2) انتقل لروت عشان تثبت بايثون وباقي الأدوات
USER root

# 3) ثبت Python3، pip، bash، Chromium و Chromedriver
#    ثم ثبّت مكتبات gspread/oauth2client و selenium و webdriver-manager
RUN apk add --no-cache \
      python3 \
      py3-pip \
      bash \
      chromium \
      chromium-chromedriver \
    && pip3 install \
      gspread \
      oauth2client \
      selenium \
      webdriver-manager

# 4) انسخ السكربت وخلي الصلاحيات خاصة بمستخدم node
COPY sheet_images.py /home/node/sheet_images.py
RUN chown node:node /home/node/sheet_images.py

# 5) عدّل للصلاحيات الاعتيادية
USER node
