#!/bin/bash

# حفظ بيانات حساب Google في ملف
echo $GOOGLE_CREDS > /app/service_account.json

# تشغيل السكربت
python src/Extract_Photos.py
