import os
import json
import re
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 1) Load credentials and sheet URL from environment
service_account_info = json.loads(os.getenv("SERVICE_ACCOUNT_INFO"))
SHEET_URL = os.getenv("SHEET_URL")

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

# 2) Open the sheet
sheet = client.open_by_url(SHEET_URL)
worksheet = sheet.worksheet("Missing In Form")

# 3) Copy M:U into A:I at first empty row
print("Copying columns M–U into A–I…")
data = worksheet.get_all_values()
rows = [row for row in data[1:] if any(row[12:21])]
first_empty = next(
    (i + 1 for i, row in enumerate(data) if not row[0].strip()),
    len(data) + 1
)
for row in rows:
    values = row[12:21]
    if any(values):
        worksheet.update(f"A{first_empty}:I{first_empty}", [values])
        first_empty += 1
print("Done copying.")

# 4) Refresh data, then extract images for empty G from links in H
data = worksheet.get_all_values()
col_g = [row[6] if len(row) > 6 else "" for row in data]
col_h = [row[7] if len(row) > 7 else "" for row in data]

def smart_get_image_url(link, page):
    if not link:
        return None
    if "drive.google.com" in link:
        match = re.search(r"/d/([^/]+)", link)
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}" if match else None
    if link.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return link
    # Amazon
    if "amazon." in link:
        img = page.query_selector("#landingImage")
        if img:
            return img.get_attribute("src")
        meta = page.query_selector('meta[property="og:image"]')
        if meta:
            return meta.get_attribute("content")
    # Noon
    if "noon.com" in link:
        meta = page.query_selector('meta[property="og:image"]')
        if meta:
            return meta.get_attribute("content")
    # Wordpress and others
    meta = page.query_selector('meta[property="og:image"]')
    if meta:
        return meta.get_attribute("content")
    img = page.query_selector('img[src*=".jpg"], img[src*=".jpeg"], img[src*=".png"], img[src*=".webp"]')
    if img:
        return img.get_attribute("src")
    return None

print("Extracting images for empty G from links in H…")
failed_links = []
failed_rows = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    for idx in range(1, len(data)):
        img_g = col_g[idx]
        link = col_h[idx]
        if not img_g.strip() and link.strip():
            print(f"Row {idx+1}: visiting {link}")
            try:
                if "drive.google.com" in link or link.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
                    img_url = smart_get_image_url(link, page=None)
                else:
                    page.goto(link, timeout=60000)
                    time.sleep(5)
                    img_url = smart_get_image_url(link, page)
                if img_url:
                    worksheet.update_cell(idx+1, 7, img_url)
                    print(f"  → G{idx+1} = {img_url}")
                else:
                    print(f"  × no image found")
                    failed_links.append(link)
                    failed_rows.append(idx+1)
            except Exception as e:
                print(f"  ! error: {e}")
                failed_links.append(link)
                failed_rows.append(idx+1)
    browser.close()

# Selenium fallback
if failed_links:
    print("Retrying failed links via Selenium…")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    for link, row_num in zip(failed_links, failed_rows):
        try:
            print(f"Fallback row {row_num}: {link}")
            driver.get(link)
            time.sleep(5)
            img_url = None
            # try og:image
            try:
                og = driver.find_element(By.XPATH, '//meta[@property="og:image"]')
                img_url = og.get_attribute("content")
            except:
                pass
            if not img_url:
                imgs = driver.find_elements(By.XPATH, '//img[contains(@src,".jpg") or contains(@src,".png")]')
                for img in imgs:
                    src = img.get_attribute("src")
                    if src:
                        img_url = src
                        break
            if img_url:
                worksheet.update_cell(row_num, 7, img_url)
                print(f"  → updated G{row_num}")
            else:
                print(f"  × still no image")
        except Exception as e:
            print(f"  ! fallback error: {e}")
    driver.quit()

print("All done.")
