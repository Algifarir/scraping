import requests
from bs4 import BeautifulSoup

url = "https://setpp.kemenkeu.go.id/ALL/Details/003457152021"
response = requests.get(url)
html = response.text 

soup = BeautifulSoup(html, "html.parser")

tabel = soup.find("div", class_="containerWrap").find("table")

data = {}
for row in tabel.find_all("tr"):
    cols = row.find_all("td")
    if len(cols) == 2:
        key = cols[0].get_text(strip=True)
        value = cols[1].get_text(strip=True).replace(":", "", 1).strip()
        data[key] = value

for k, v in data.items():
    print(f"{k} \t: {v}")
