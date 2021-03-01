import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

pageNumber = 1
retry = 0
max_retry = 5
result = []

while True:
    print(f"Page: {pageNumber}")
    html = requests.get(f'http://cekfakta.com/page/{pageNumber}')
    bs = BeautifulSoup(html.content, "lxml")

    cards = bs.select("li.card")
    print(f"Total News: {len(cards)}")

    if len(cards) == 0:
        if retry == max_retry:
            break

        retry += 1
        continue

    for card in cards:
        url = card.select_one(".title a").get('href')
        status_url = card.select_one(".status a").get('href')
        label = status_url.split("/")[len(status_url.split("/")) - 1]

        if any(data[0] == url for data in result):
            continue
        elif label != "salah" and label != "benar":
            continue

        try:
            title = card.select_one(".title a").text
            title = re.sub(r'(^\[\S+\] )|(^\S+\s?\S+: )', "", title)
            description = card.select_one(".description .content").text.replace("\n", "")
            content = card.select_one(".description~.content").text.replace("\n", "")

            if label == "salah":
                result.append([url, title, description, "salah"])

            result.append([url, title, content if label == "salah" else f"{description} {content}", "benar"])
        except Exception:
            continue

    pageNumber += 1
    retry = 0

df = pd.DataFrame(result, columns=["Tautan", "Judul", "Berita", "Label"])
df.to_csv("data.csv", sep=";", index=False)
