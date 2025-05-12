import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from tabulate import tabulate

class SSAutoScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }

    def _get_html(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Kļūda, iegūstot datus no {url}: {e}")
            exit(1)

    def _clean_text(self, text):
        if text:
            return re.sub(r'\s+', ' ', text).strip()
        return ""

    def _extract_number(self, text):
        if text:
            numbers = re.findall(r'\d+', text.replace(" ", ""))
            if numbers:
                return int("".join(numbers))
        return None

    def nolasit_sista_auto_datus(self, url):
        html = self._get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        auto_dati = {
            'marka': None,
            'modelis': None,
            'gads': None,
            'dzinējs': None,
            'ātrumkārba': None,
            'nobraukums': None,
            'cena': None,
            'saite': url
        }
        try:
            info_table = soup.find('table', class_='options_list')
            if info_table:
                tr_elements = info_table.select('tr')
                for tr in tr_elements:
                    td_elements = tr.select('td')
                    if len(td_elements) == 2:
                        param_nos = self._clean_text(td_elements[0].text).lower()
                        param_vert = self._clean_text(td_elements[1].text)
                        if 'auto marka' in param_nos:
                            auto_dati['marka'] = param_vert
                        elif 'modelis' in param_nos:
                            auto_dati['modelis'] = param_vert
                        elif 'izlaiduma gads' in param_nos:
                            auto_dati['gads'] = re.search(r'\d{4}', param_vert).group(0) if re.search(r'\d{4}', param_vert) else None
                        elif 'nobraukums' in param_nos:
                            auto_dati['nobraukums'] = self._extract_number(param_vert)
                        elif 'dzinējs' in param_nos:
                            auto_dati['dzinējs'] = param_vert
                        elif 'ātrumkārba' in param_nos:
                            auto_dati['ātrumkārba'] = param_vert

            price_element = soup.select_one('.ads_price')
            if not price_element:
                price_element = soup.select_one('div.ads_price_container span.ads_price')
            if price_element:
                auto_dati['cena'] = self._extract_number(price_element.text)

            if auto_dati['marka'] is None or auto_dati['modelis'] is None:
                title = soup.select_one('h1.page_header')
                if title:
                    title_text = self._clean_text(title.text)
                    parts = title_text.split(' ', 1)
                    if len(parts) >= 2 and auto_dati['marka'] is None:
                        auto_dati['marka'] = parts[0]
                    if len(parts) >= 2 and auto_dati['modelis'] is None:
                        auto_dati['modelis'] = parts[1]

            return auto_dati

        except Exception as e:
            print(f"Kļūda, nolasot sistā auto datus: {e}")
            return auto_dati

    def izveidot_meklēšanas_saiti(self, auto_dati):
        base_url = "https://www.ss.lv/lv/transport/cars/"
        url_parts = []

        if auto_dati.get('marka'):
            marka = auto_dati['marka'].lower().replace(' ', '-')
            url_parts.append(marka)
        if auto_dati.get('modelis'):
            modelis = auto_dati['modelis'].lower().replace(' ', '-')
            url_parts.append(modelis)

        url = base_url + "/".join(url_parts) + "/filter/"
        query_params = []
        if auto_dati.get('gads'):
            try:
                gads = int(auto_dati['gads'])
                year_min = max(gads - 5, 1900)
                year_max = gads + 5
                query_params.append(f"year_min={year_min}")
                query_params.append(f"year_max={year_max}")
            except Exception:
                pass

        if query_params:
            url += "?" + "&".join(query_params)
        return url

    def meklēt_nesistus_auto(self, meklēšanas_saite, gads=None):
        """Meklē līdzīgus nesistus auto pēc meklēšanas saites un filtrē pēc gada ±5"""
        html = self._get_html(meklēšanas_saite)
        soup = BeautifulSoup(html, 'html.parser')

        nesistie_auto = []
        ad_rows = soup.select('tr[id^="tr_"]')

        year_min = year_max = None
        if gads:
            try:
                gads = int(gads)
                year_min = gads - 5
                year_max = gads + 5
            except Exception:
                pass

        for row in ad_rows:
            if 'booster' in row.get('class', []) or row.get('id') == 'head_line' or not row.select_one('td.msga2-o'):
                continue

            auto = {
                'marka': None,
                'modelis': None,
                'gads': None,
                'dzinējs': None,
                'ātrumkārba': None,
                'nobraukums': None,
                'cena': None,
                'saite': None
            }

            saite_elements = row.select('a[id^="dm_"]')
            if saite_elements:
                href = saite_elements[0].get('href')
                if href:
                    auto['saite'] = "https://www.ss.com" + href

            cena_element = row.select_one('.msga2-o')
            if cena_element:
                auto['cena'] = self._extract_number(cena_element.text)

            columns = row.select('td')
            # Pareiza kolonnu atpazīšana
            if len(columns) >= 3:
                marka_val = self._clean_text(columns[2].text)
                if marka_val:
                    auto['marka'] = marka_val

                # Modelis vai Gads
                if len(columns) >= 4:
                    col3 = self._clean_text(columns[3].text)
                    if re.fullmatch(r'\d{4}', col3):
                        auto['gads'] = int(col3)
                    else:
                        auto['modelis'] = col3

                # Ja nav gads, tad pārbaudām nākamo kolonnu
                if len(columns) >= 5:
                    col4 = self._clean_text(columns[4].text)
                    if auto['gads'] is None and re.fullmatch(r'\d{4}', col4):
                        auto['gads'] = int(col4)
                    elif auto['modelis'] is None:
                        auto['modelis'] = col4

                # Dzinējs
                if len(columns) >= 6:
                    auto['dzinējs'] = self._clean_text(columns[5].text)
                # Nobraukums
                if len(columns) >= 7:
                    auto['nobraukums'] = self._extract_number(self._clean_text(columns[6].text))
                 # Ātrumkārba (tiek lasīta, bet netiek iekļauta CSV)
                if len(columns) >= 8:
                     auto['ātrumkārba'] = self._clean_text(columns[7].text)

            # Filtrējam pēc gada ±5
            if year_min is not None and year_max is not None:
                if auto['gads'] is None or not (year_min <= auto['gads'] <= year_max):
                    continue

            if auto['cena'] is not None:
                nesistie_auto.append(auto)

        return nesistie_auto

    def salīdzināt_cenas(self, sista_auto, nesistie_auto):
        print("\n--- Cenu salīdzinājums ---")
        print(f"Sistā auto:")
        print(f"  Marka: {sista_auto.get('marka', '-')}")
        print(f"  Modelis: {sista_auto.get('modelis', '-')}")
        print(f"  Gads: {sista_auto.get('gads', '-')}")
        print(f"  Dzinējs: {sista_auto.get('dzinējs', '-')}")
        print(f"  Nobraukums: {sista_auto.get('nobraukums', '-')} km")
        print(f"  Cena: {sista_auto.get('cena', '-')} EUR")
        print(f"  Saite: {sista_auto.get('saite', '-')}")

        print("\nLīdzīgi nesisti auto (meklēts pēc pieejamajiem parametriem):")

        if nesistie_auto:
            # Šī tabula konsolē attēlo vairāk datus salīdzinājumam, nekā CSV fails
            headers = ["Marka", "Dzinējs", "Gads", "Nobraukums", "Cena", "Saite"]
            tabulas_dati = []
            for auto in nesistie_auto:
                tabulas_dati.append([
                    auto.get('marka', '-'),
                    auto.get('modelis', '-'),
                    auto.get('gads', '-'),
                    f"{auto.get('dzinējs', '-')} km",
                    f"{auto.get('nobraukums', '-')} EUR",
                    auto.get('saite', '-')
                ])
            print(tabulate(tabulas_dati, headers=headers, tablefmt="grid"))
            cenas = [auto['nobraukums'] for auto in nesistie_auto if isinstance(auto.get('nobraukums'), int)]
            if cenas:
                vidēja_cena = sum(cenas) / len(cenas)
                min_cena = min(cenas)
                max_cena = max(cenas)
                print(f"\nNesisto auto vidējā cena: {vidēja_cena:.2f} EUR")
                print(f"Nesisto auto minimālā cena: {min_cena} EUR")
                print(f"Nesisto auto maksimālā cena: {max_cena} EUR")
        else:
            print("Nav atrasti līdzīgi nesisti auto ar pieejamajiem parametriem.")

# --- Galvenā programmas daļa ---
if __name__ == "__main__":
    scraper = SSAutoScraper()

    sista_auto_url = input("Ievadi sistā auto sludinājuma saiti no ss.com: ")

    print(f"Nolasām datus no: {sista_auto_url}")
    sista_auto_dati = scraper.nolasit_sista_auto_datus(sista_auto_url)

    if not sista_auto_dati or not sista_auto_dati.get('marka'):
        print("Neizdevās nolasīt vismaz auto marku. Meklēšanas saiti nevar izveidot. Pārbaudiet sludinājuma saiti.")
        exit(1)

    meklēšanas_saite = scraper.izveidot_meklēšanas_saiti(sista_auto_dati)
    print(f"\nMeklējam līdzīgus nesistus auto pēc šīs saites: {meklēšanas_saite}")

    nesistie_auto_saraksts = scraper.meklēt_nesistus_auto(meklēšanas_saite, sista_auto_dati.get('gads'))

    scraper.salīdzināt_cenas(sista_auto_dati, nesistie_auto_saraksts)

    try:
        dati_saglabasanai_filtrēti = []

        # Filtrējam sistā auto datus
        sista_auto_filtrēts = {
            'Marka': sista_auto_dati.get('marka', '-'),
            'Dzinējs': sista_auto_dati.get('modelis', '-'),
            'Gads': sista_auto_dati.get('gads', '-'),
            'Nobraukums (km)': f"{sista_auto_dati.get('dzinējs', '-')} km",
            'Cena (EUR)': f"{sista_auto_dati.get('nobraukums', '-')} EUR",
            'Saite': sista_auto_dati.get('saite', '-'),
            'Statuss': 'Sists'
        }
        dati_saglabasanai_filtrēti.append(sista_auto_filtrēts)

        # Filtrējam nesisto auto datus
        for auto in nesistie_auto_saraksts:
            auto_filtrēts = {
                'Marka': auto.get('marka', '-'),
                'Dzinējs': auto.get('modelis', '-'),
                'Gads': auto.get('gads', '-'),
                'Nobraukums (km)': f"{auto.get('dzinējs', '-')} km",
                'Cena (EUR)': f"{auto.get('nobraukums', '-')} EUR",
                'Saite': auto.get('saite', '-'),
                'Statuss': 'Nesists'
            }
            dati_saglabasanai_filtrēti.append(auto_filtrēts)

        # Veidojam DataFrame no filtrētajiem datiem
        df_all = pd.DataFrame(dati_saglabasanai_filtrēti)
        faila_nosaukums = "auto_salidzinajums.csv"
        df_all.to_csv(faila_nosaukums, index=False, encoding='utf-8-sig')
        print(f"\nDati saglabāti failā: {faila_nosaukums}")
    except Exception as e:
        print(f"Kļūda, saglabājot datus CSV failā: {e}")