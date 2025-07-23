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
chromedriver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../chromedriver.exe"))

options = Options()
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
wait = WebDriverWait(driver, 15)

url = "https://setpp.kemenkeu.go.id/risalah/IndexPutusan"
driver.get(url)

time.sleep(1)

# ========== 1. Klik dropdown jumlah data per halaman ==========
dropdown_xpath = "//span[@class='k-dropdown-wrap k-state-default']"
wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath))).click()

time.sleep(1)   

# ========== 2. Klik "20 per page" ==========
menu_20_xpath = "//ul[@class='k-list k-reset']/li[.='20']"
wait.until(EC.element_to_be_clickable((By.XPATH, menu_20_xpath))).click()

# ========== 3. Loop semua halaman ==========
all_data = []
base_url = "https://setpp.kemenkeu.go.id"

page = 0
while True:
    # Tunggu tabel muncul
    wait.until(EC.presence_of_element_located((By.XPATH, "//table[@role='grid']//tbody/tr")))

    rows = driver.find_elements(By.XPATH, "//table[@role='grid']//tbody/tr")
    for i in range(len(rows)):
        try:
            row = driver.find_elements(By.XPATH, "//table[@role='grid']//tbody/tr")[i]
            td1 = row.find_element(By.XPATH, ".//td[1]").text.strip()
            td2 = row.find_element(By.XPATH, ".//td[2]").text.strip()
            href = row.find_element(By.XPATH, ".//td[1]/a").get_attribute("href")
        except:
            href = ""
            td1 = td1 if 'td1' in locals() else ""
            td2 = td2 if 'td2' in locals() else ""

        all_data.append((td1, td2, href if href else ""))

    print(f"✅ Halaman selesai, total terkumpul: {len(all_data)}")

    # ========== 4. Klik tombol berikutnya ==========
    try:
        if(page == 3):
            break
        else:
            page = page + 1
        next_button = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div/div/a[3]")
        if "k-state-disabled" in next_button.get_attribute("class"):
            break  # terakhir
        next_button.click()
        time.sleep(1)
    except:
        break  # tombol next tidak ada

driver.quit()

# ========== 5. Cetak hasil ==========
for i, (title, kategori, link) in enumerate(all_data, 1):
    print(f"{i}. {title} | {kategori} | {link}")

now = datetime.now()
df = pd.DataFrame(all_data, columns=["Judul", "Kategori", "Link"])
df.to_csv(f"/assets/data_putusan_{now.strftime('%y%m%d%H%M%S')}.csv", index=False, encoding="utf-8-sig")

print("✅ Data berhasil disimpan ke file: data_putusan.csv")

