from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re
import requests

def sanitize_filename(name):
    """Entfernt unzulässige Zeichen aus Dateinamen."""
    if not name:
        return "unnamed"
    clean_name = re.sub(r'[\\/*?:"<>|]', "_", name)
    # Begrenze die Länge auf max. 150 Zeichen
    if len(clean_name) > 150:
        clean_name = clean_name[:147] + "..."
    return clean_name

def download_awmf_guidelines():
    output_dir = "patrickjorge/documents/asclea/asclea/backend/data/sources/leitlinien_awmf"
    os.makedirs(output_dir, exist_ok=True)

    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Falls du wirklich headless brauchst
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 1) Auf die Hauptseite gehen
        driver.get("https://register.awmf.org/de/leitlinien/aktuelle-leitlinien")
        time.sleep(5)  # Kurz warten, bis alles geladen ist

        # ---------------------------------------------------------------------
        # Ggf. Tab "Nach Fachgesellschaft" anklicken, falls nicht standardmäßig aktiv
        # Beispiel (wenn notwendig):
        # tab_link = driver.find_element(By.XPATH, "//a[contains(text(),'Nach Fachgesellschaft')]")
        # tab_link.click()
        # time.sleep(3)
        # ---------------------------------------------------------------------

        # 2) Alle Zeilen der Tabelle mit Fachgesellschaften holen
        #    i.d.R. gibt es ein <table> mit <tbody> und mehreren <tr>.
        #    Die erste Zeile kann Header sein, deshalb ggf. filtern.
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

        print(f"Gefundene Fachgesellschaften (Zeilen in der Tabelle): {len(rows)}")

        total_downloaded = 0

        for idx, row in enumerate(rows, start=1):
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 2:
                # Vermutlich Kopfzeile oder leere Zeile
                continue

            # Fachgesellschaftsname steht oft in der ersten oder zweiten Zelle,
            # probier ggf. aus, welche Zelle den Text enthält.
            society_name = cells[0].text.strip()
            # Der Pfeil/Detail-Link ist oft in der letzten Zelle
            try:
                detail_link_element = cells[-1].find_element(By.TAG_NAME, "a")
            except:
                # Falls kein Link vorhanden, weiter
                continue

            detail_link = detail_link_element.get_attribute("href")
            if not detail_link:
                continue

            print(f"\n=== {idx}. Fachgesellschaft: {society_name} ===")
            print(f"Detail-URL: {detail_link}")

            # Ordner für diese Fachgesellschaft anlegen
            society_dir = os.path.join(output_dir, sanitize_filename(society_name))
            os.makedirs(society_dir, exist_ok=True)

            # 3) Auf die Seite der Fachgesellschaft gehen
            driver.get(detail_link)
            time.sleep(3)

            # Dort sollte es eine Tabelle mit Leitlinien geben:
            guideline_rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            print(f"  Gefundene Leitlinien: {len(guideline_rows)-1} (ohne Header)")

            # Oft ist die erste Zeile ein Header -> skippen
            # Du kannst sie hier so filtern:
            # guideline_rows = guideline_rows[1:]  # falls du sicher bist, dass #0 ein Header ist

            # 4) Pro Leitlinie: Detail-Link öffnen und PDFs holen
            for g_idx, g_row in enumerate(guideline_rows[1:], start=1):
                g_cells = g_row.find_elements(By.TAG_NAME, "td")
                if not g_cells:
                    continue

                # Titel kann in Zelle[1] oder [0] sein, je nach Layout
                # Registriernummer meist in Zelle[0]
                reg_number = g_cells[0].text.strip()  # falls du sie brauchst
                guideline_title = g_cells[1].text.strip() if len(g_cells) > 1 else "Unbekannte_Leitlinie"

                # Link zum Detail
                try:
                    guideline_link_el = g_row.find_element(By.CSS_SELECTOR, "td:last-child a")
                    guideline_link = guideline_link_el.get_attribute("href")
                except:
                    guideline_link = ""

                if not guideline_link:
                    print(f"    Keine Detail-URL für Leitlinie {guideline_title}")
                    continue

                print(f"    -> Leitlinie {g_idx}: {guideline_title}")
                print(f"       Registriernummer: {reg_number}")
                print(f"       URL: {guideline_link}")

                # Detailseite der Leitlinie aufrufen
                driver.get(guideline_link)
                time.sleep(2)

                # Jetzt nach Download-Links suchen (Langfassung, Kurzfassung, Patientenversion)
                # Häufig sind die Buttons mit Text "Download" gekennzeichnet
                # oder als a[href$=".pdf"]
                download_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Download')]")
                if not download_links:
                    # Alternativ PDF-Links
                    download_links = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")

                if download_links:
                    print(f"       Gefundene Download-Links: {len(download_links)}")
                    # Wir laden maximal 3 (Lang-, Kurz-, Patientenversion)
                    max_downloads = min(3, len(download_links))
                    local_download_count = 0

                    for k in range(max_downloads):
                        dl_link = download_links[k]
                        pdf_url = dl_link.get_attribute('href')
                        if not pdf_url or not pdf_url.lower().endswith('.pdf'):
                            continue

                        # Typ bestimmen
                        pdf_type = "Unbekannt"
                        link_text = dl_link.text.strip().lower()
                        if "langfassung" in link_text or "vollversion" in link_text:
                            pdf_type = "Langfassung"
                        elif "kurz" in link_text:
                            pdf_type = "Kurzfassung"
                        elif "patient" in link_text:
                            pdf_type = "Patientenversion"

                        # Dateiname bauen
                        filename = f"{sanitize_filename(guideline_title)}_{sanitize_filename(pdf_type)}.pdf"
                        if reg_number:
                            filename = f"{sanitize_filename(guideline_title)}_{reg_number}_{sanitize_filename(pdf_type)}.pdf"

                        file_path = os.path.join(society_dir, filename)
                        print(f"         Download: {filename}")
                        print(f"         URL: {pdf_url}")

                        try:
                            response = requests.get(pdf_url, timeout=60)
                            if response.status_code == 200:
                                # Grob prüfen, ob es wirklich PDF sein könnte
                                content_type = response.headers.get('Content-Type', '')
                                if 'application/pdf' in content_type or len(response.content) > 1000:
                                    with open(file_path, 'wb') as f:
                                        f.write(response.content)
                                    local_download_count += 1
                                    total_downloaded += 1
                                    print(f"         -> Gespeichert als: {file_path}")
                                else:
                                    print(f"         -> Kein PDF-Content-Type: {content_type}")
                            else:
                                print(f"         -> HTTP-Fehler {response.status_code}")
                        except Exception as e:
                            print(f"         -> Download-Fehler: {str(e)}")

                        time.sleep(1)  # Kleiner Delay pro Download
                    print(f"       {local_download_count} PDFs erfolgreich heruntergeladen.")
                else:
                    print("       Keine Download-Links gefunden.")

                # Zurück zur Fachgesellschaftsseite, damit wir die nächste Leitlinie anklicken können
                # (wenn du den Umweg nicht willst, kannst du auch direkt alle Leitlinien-Links
                #  vorher abgreifen und dann in einer Schleife nacheinander abarbeiten.)
                if g_idx < len(guideline_rows) - 1:
                    driver.get(detail_link)
                    time.sleep(2)

            # Nach Fertigstellung der Leitlinien wieder zurück zur Hauptseite
            driver.get("https://register.awmf.org/de/leitlinien/aktuelle-leitlinien")
            time.sleep(2)

        print(f"\nFertig. Insgesamt {total_downloaded} PDF-Dateien heruntergeladen.")

    finally:
        driver.quit()

if __name__ == "__main__":
    download_awmf_guidelines()