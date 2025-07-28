from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd


import time

# # Ganti path ke lokasi ChromeDriver kamu
# chrome_driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets/chromedriver.exe'))

# # Konfigurasi ChromeDriver
# chrome_options = Options()
# chrome_options.add_argument("--window-size=1920,1080")


# service = Service(chrome_driver_path)
# driver = webdriver.Chrome(service=service, options=chrome_options)

# # Buka halaman
# url = "https://setpp.kemenkeu.go.id/risalah/IndexPutusan"
# driver.get(url)

# # Tunggu data dimuat
# time.sleep(3)

# WebDriverWait(driver, 15).until(
#     EC.presence_of_element_located((By.CSS_SELECTOR, "table[role='grid'] tbody tr"))
# )

# # Ambil daftar putusan di halaman pertama
# rows = driver.find_elements(By.CSS_SELECTOR, "table[role='grid'] tbody tr")

# base_url = "https://setpp.kemenkeu.go.id"

# for row in rows:
#     cols = row.find_elements(By.CSS_SELECTOR, "td[role='gridcell']")
#     if len(cols) < 2:
#         continue

#     try:
#         a_tag = cols[0].find_element(By.TAG_NAME, "a")
#         href = a_tag.get_attribute("href")
#         judul_dokumen = a_tag.text.strip()
#     except:
#         href = ""
#         judul_dokumen = cols[0].text.strip()

#     kategori = cols[1].text.strip()

#     print(f"Judul Dokumen : {judul_dokumen}")
#     print(f"Kategori      : {kategori}")
#     print(f"Link          : {base_url + href}\n")


# driver.quit()


# Setup driver (non-headless agar stabil)
chromedriver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/chromedriver.exe"))

options = Options()
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
wait = WebDriverWait(driver, 15)

url = "https://setpp.kemenkeu.go.id/risalah/IndexPutusan"
driver.get(url)

time.sleep(1)

# === Setup path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'assets'))
os.makedirs(ASSETS_DIR, exist_ok=True)
CHECKPOINT_FILE = os.path.join(ASSETS_DIR, 'data_checkpoint.csv')

# === Load checkpoint
if os.path.exists(CHECKPOINT_FILE):
    df_checkpoint = pd.read_csv(CHECKPOINT_FILE)
    scraped_links = set(df_checkpoint['link'])
    all_data = df_checkpoint.values.tolist()
else:
    scraped_links = set()
    all_data = []

# === 1. Klik dropdown jumlah data per halaman
dropdown_xpath = "//span[@class='k-dropdown-wrap k-state-default']"
wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath))).click()
time.sleep(1)

# === 2. Klik "20 per page"
menu_20_xpath = "//ul[@class='k-list k-reset']/li[.='20']"
wait.until(EC.element_to_be_clickable((By.XPATH, menu_20_xpath))).click()

# === 3. Loop semua halaman
base_url = "https://setpp.kemenkeu.go.id"

def save_checkpoint(data):
    df = pd.DataFrame(data, columns=["nomor", "judul", "link"])
    df.to_csv(CHECKPOINT_FILE, index=False, encoding="utf-8-sig")

def safe_find(xpath, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )
    except:
        return []

while True:
    rows = safe_find("//table[@role='grid']//tbody/tr")
    for row in rows:
        try:
            td1 = row.find_element(By.XPATH, ".//td[1]").text.strip()
            td2 = row.find_element(By.XPATH, ".//td[2]").text.strip()
            href = row.find_element(By.XPATH, ".//td[1]/a").get_attribute("href")
        except Exception as e:
            td1, td2, href = "", "", ""
            print(f"[!] Error baca baris: {e}")
        
        if href and href not in scraped_links:
            all_data.append((td1, td2, href))
            scraped_links.add(href)

            if len(all_data) % 10 == 0:
                print(f"✅ Checkpoint: {len(all_data)} data tersimpan")
                save_checkpoint(all_data)

    # === 4. Klik tombol berikutnya
    try:
        next_button = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div/div/a[3]")
        if "k-state-disabled" in next_button.get_attribute("class"):
            print("🔚 Selesai sampai halaman terakhir.")
            break
        next_button.click()
        time.sleep(1.5)
    except Exception as e:
        print(f"[!] Error klik next: {e}")
        break

driver.quit()

# === Final Save
save_checkpoint(all_data)
print(f"✅ Scraping selesai. Total: {len(all_data)}")


# ========== 5. Cetak hasil ==========
# for i, (title, kategori, link) in enumerate(all_data, 1):
#     print(f"{i}. {title} | {kategori} | {link}")

# now = datetime.now()
# df = pd.DataFrame(all_data, columns=["Judul", "Kategori", "Link"])
# ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
# os.makedirs(ASSETS_DIR, exist_ok=True)
# output_file = os.path.join(ASSETS_DIR, f"data_putusan_{now.strftime('%y%m%d%H%M%S')}.csv")
# df.to_csv(output_file, index=False, encoding="utf-8-sig")

# print("✅ Data berhasil disimpan ke file: data_putusan.csv")

