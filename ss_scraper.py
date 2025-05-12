import requests
from bs4 import BeautifulSoup
import re

def get_auto_info(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    marka, modelis, gads = None, None, None

    # Precīzi no options_list tabulas
    table = soup.select_one("table.options_list")
    if table:
        for row in table.find_all("tr"):
            tds = row.find_all("td")
            if len(tds) == 2:
                key = tds[0].get_text(strip=True).lower()
                value = tds[1].get_text(strip=True)
                if key.startswith("marka"):
                    parts = value.strip().split(" ", 1)
                    marka = parts[0].lower()
                    modelis = parts[1].lower() if len(parts) > 1 else None
                elif "izlaiduma gads" in key:
                    match = re.search(r"\d{4}", value)
                    if match:
                        gads = int(match.group(0))
    return marka, modelis, gads

def search_similar_cars(marka, modelis, gads, original_url):
    # Ja modelim nav savas sadaļas, meklē markas lapā
    search_url = f"https://www.ss.com/lv/transport/cars/{marka}/{modelis}/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(search_url, headers=headers)
    # Ja modelim nav savas sadaļas, pārej uz markas lapu
    if response.status_code != 200 or "Sludinājumi nav atrasti" in response.text:
        search_url = f"https://www.ss.com/lv/transport/cars/{marka}/"
        response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for row in soup.select('tr[id^="tr_"]'):
        title_tag = row.find("a", class_="am")
        if not title_tag:
            continue
        link = "https://www.ss.com" + title_tag.get("href")
        if link == original_url:
            continue
        tds = row.find_all("td")
        year = None
        price = None
        if len(tds) >= 4:
            price = tds[2].get_text(strip=True)
            year_text = tds[-1].get_text(strip=True)
            match = re.search(r"\d{4}", year_text)
            if match:
                year = int(match.group(0))
        # Tikai tieši tas pats gads
        if year and year == gads:
            # Elastīga salīdzināšana: virsraksts sākas ar "marka modelis"
            title = title_tag.get_text(strip=True).lower()
            title_words = title.split()
            if len(title_words) >= 2 and title_words[0] == marka and title_words[1].startswith(modelis):
                results.append((link, price))
    return results

if __name__ == "__main__":
    url = input("Ievadi ss.com auto sludinājuma linku: ").strip()
    marka, modelis, gads = get_auto_info(url)
    print("-" * 40)
    if not all([marka, modelis, gads]):
        print("Neizdevās nolasīt pilnu auto informāciju!")
        print(f"Marka:   {marka}")
        print(f"Modelis: {modelis}")
        print(f"Gads:    {gads}")
    else:
        results = search_similar_cars(marka, modelis, gads, url)
        if results:
            for link, price in results:
                print(f"{link} {price}")
        else:
            print("Līdzīgi sludinājumi nav atrasti.")
    print("-" * 40)
