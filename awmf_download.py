from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import re
import requests
import random

def sanitize_filename(name):
    """Entfernt unzulässige Zeichen aus Dateinamen und begrenzt die Länge."""
    if not name:
        return "unnamed"
    clean_name = re.sub(r'[\\/*?:"<>|]', "_", name)
    if len(clean_name) > 150:
        clean_name = clean_name[:147] + "..."
    return clean_name

# Vollständiges Scrollen, um ALLE Leitlinien zu laden
def scroll_thoroughly(driver):
    # Ermittle die volle Höhe der Seite
    total_height = driver.execute_script("return document.body.scrollHeight")
    
    # 1. Langsames Scrollen von oben nach unten mit kleinen Schritten
    print("Langsames Scrollen von oben nach unten...")
    for scroll_pos in range(0, total_height, 100):
        driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
        time.sleep(0.3)  # Kurze Pause, um Inhalte laden zu lassen

    # 2. Ein paar Mal komplett nach unten und oben scrollen
    print("Scroll-Zyklen von oben nach unten und zurück...")
    for i in range(3):
        # Ganz nach unten
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Ganz nach oben
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    
    # 3. Nochmals die aktualisierte Höhe überprüfen (falls mehr Inhalte geladen wurden)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height > total_height:
        print(f"Mehr Inhalte geladen, Seite ist gewachsen: {total_height}px -> {new_height}px")
        # Nochmals durchscrollen, um sicherzugehen
        for scroll_pos in range(0, new_height, 150):
            driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
            time.sleep(0.2)

def download_awmf_guidelines():
    # Zielordner festlegen
    output_dir = "asclea/backend/data/sources/leitlinien_awmf"
    os.makedirs(output_dir, exist_ok=True)

    # Chrome Optionen konfigurieren
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Auskommentiert für Debugging
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(120)  # Längerer Timeout für langsame Seiten   

    try:
        # Liste aller Fachgesellschaften
        society_list = [
            "Arbeitsgemeinschaft Pädiatrische Immunologie e.V. (API)",
            "Dachverband Osteologie e.V. [assoziiert]",
            "Deutsche AIDS-Gesellschaft e.V. (DAIG)",
            "Deutsche Adipositas-Gesellschaft e.V. (DAG)",
            "Deutsche Dermatologische Gesellschaft e.V. (DDG)",
            "Deutsche Diabetes Gesellschaft e.V. (DDG)",
            "Deutsche Gesellschaft für Allergologie und klinische Immunologie e.V. (DGAKI)",
            "Deutsche Gesellschaft für Allgemein- und Viszeralchirurgie e.V. (DGAV)",
            "Deutsche Gesellschaft für Allgemeinmedizin und Familienmedizin e.V. (DEGAM)",
            "Deutsche Gesellschaft für Angiologie - Gesellschaft für Gefäßmedizin e.V. (DGA)",
            "Deutsche Gesellschaft für Anästhesiologie und Intensivmedizin e.V. (DGAI)",
            "Deutsche Gesellschaft für Arbeitsmedizin und Umweltmedizin e.V. (DGAUM)",
            "Deutsche Gesellschaft für Chirurgie e.V. (DGCH)",
            "Deutsche Gesellschaft für Endokrinologie e.V. (DGE)",
            "Deutsche Gesellschaft für Epidemiologie e.V. (DGEpi)",
            "Deutsche Gesellschaft für Epileptologie e.V. (DGfE)",
            "Deutsche Gesellschaft für Ernährungsmedizin e.V. (DGEM)",
            "Deutsche Gesellschaft für Gastroenterologie, Verdauungs- und Stoffwechselkrankheiten e.V. (DGVS)",
            "Deutsche Gesellschaft für Gefäßchirurgie und Gefäßmedizin - Gesellschaft für operative, endovaskuläre und präventive Gefäßmedizin e.V. (DGG)",
            "Deutsche Gesellschaft für Geriatrie (DGG)",
            "Deutsche Gesellschaft für Gerontologie und Geriatrie e.V. (DGGG)",
            "Deutsche Gesellschaft für Gerontopsychiatrie und -psychotherapie (DGGPP)",
            "Deutsche Gesellschaft für Gynäkologie und Geburtshilfe e.V. (DGGG)",
            "Deutsche Gesellschaft für Hals-Nasen-Ohren-Heilkunde, Kopf- und Hals-Chirurgie e.V. (DGHNO-KHC)",
            "Deutsche Gesellschaft für Handchirurgie e.V. (DGH)",
            "Deutsche Gesellschaft für Hebammenwissenschaft e.V. (DGHWi)",
            "Deutsche Gesellschaft für Humangenetik e.V. (GfH)",
            "Deutsche Gesellschaft für Hygiene und Mikrobiologie e.V. (DGHM)",
            "Deutsche Gesellschaft für Hämatologie und Medizinische Onkologie (DGHO)",
            "Deutsche Gesellschaft für Immunologie e.V. (DGfI)",
            "Deutsche Gesellschaft für Implantologie im Zahn-, Mund- und Kieferbereich e.V. (DGI)",
            "Deutsche Gesellschaft für Infektiologie e.V. (DGI)",
            "Deutsche Gesellschaft für Innere Medizin e.V. (DGIM)",
            "Deutsche Gesellschaft für Internistische Intensivmedizin und Notfallmedizin e.V. (DGIIN)",
            "Deutsche Gesellschaft für Kardiologie - Herz- und Kreislaufforschung e.V. (DGK)",
            "Deutsche Gesellschaft für Kieferorthopädie e.V. (DGKFO)",
            "Deutsche Gesellschaft für Kinder- und Jugendchirurgie e.V. (DGKJCH)",
            "Deutsche Gesellschaft für Kinder- und Jugendmedizin e.V. (DGKJ)",
            "Deutsche Gesellschaft für Kinder- und Jugendpsychiatrie, Psychosomatik und Psychotherapie e.V. (DGKJP)",
            "Deutsche Gesellschaft für Kinderzahnheilkunde e.V. (DGKiZ)",
            "Deutsche Gesellschaft für Klinische Chemie und Laboratoriumsmedizin e.V. (DGKL)",
            "Deutsche Gesellschaft für Koloproktologie e.V. (DGK)",
            "Deutsche Gesellschaft für Krankenhaushygiene e.V. (DGKH)",
            "Deutsche Gesellschaft für Luft- und Raumfahrtmedizin",
            "Deutsche Gesellschaft für Mund-, Kiefer- und Gesichtschirurgie e.V. (DGMKG)",
            "Deutsche Gesellschaft für Nephrologie e.V. (DGfN)",
            "Deutsche Gesellschaft für Neurochirurgie e.V. (DGNC)",
            "Deutsche Gesellschaft für Neurogastroenterologie und Motilität e.V. (DGNM)",
            "Deutsche Gesellschaft für Neurologie e.V. (DGN)",
            "Deutsche Gesellschaft für Neuromodulation e.V. (DGNM)",
            "Deutsche Gesellschaft für Neurorehabilitation e.V. (DGNR)",
            "Deutsche Gesellschaft für Neurowissenschaftliche Begutachtung e.V. (DGNB)",
            "Deutsche Gesellschaft für Nuklearmedizin e.V. (DGN)",
            "Deutsche Gesellschaft für Orthopädie und Orthopädische Chirurgie e.V. (DGOOC)",
            "Deutsche Gesellschaft für Orthopädie und Unfallchirurgie e.V. (DGOU)",
            "Deutsche Gesellschaft für Palliativmedizin e.V. (DGP)",
            "Deutsche Gesellschaft für Parodontologie e.V. (DG PARO)",
            "Deutsche Gesellschaft für Pathologie e.V. (DGP)",
            "Deutsche Gesellschaft für Perinatale Medizin e.V. (DGPM)",
            "Deutsche Gesellschaft für Pflegewissenschaft e.V. (DGP)",
            "Deutsche Gesellschaft für Phlebologie u. Lymphologie e.V. (DGP/L)",
            "Deutsche Gesellschaft für Phoniatrie und Pädaudiologie e.V. (DGPP)",
            "Deutsche Gesellschaft für Plastische, Rekonstruktive und Ästhetische Chirurgie e.V. (DGPRÄC)",
            "Deutsche Gesellschaft für Pneumologie und Beatmungsmedizin e.V. (DGP)",
            "Deutsche Gesellschaft für Prothetische Zahnmedizin und Biomaterialien e.V. (DGPro)",
            "Deutsche Gesellschaft für Psychiatrie und Psychotherapie, Psychosomatik und Nervenheilkunde e.V. (DGPPN)",
            "Deutsche Gesellschaft für Psychoanalyse, Psychotherapie, Psychosomatik und Tiefenpsychologie (DGPT) e.V.",
            "Deutsche Gesellschaft für Psychosomatische Frauenheilkunde und Geburtshilfe e.V. (DGPFG)",
            "Deutsche Gesellschaft für Psychosomatische Medizin und Ärztliche Psychotherapie e.V. (DGPM)",
            "Deutsche Gesellschaft für Public Health (DGPH)",
            "Deutsche Gesellschaft für Pädiatrische Infektiologie e.V. (DGPI)",
            "Deutsche Gesellschaft für Pädiatrische Kardiologie und Angeborene Herzfehler e.V. (DGPK)",
            "Deutsche Gesellschaft für Radioonkologie e.V. (DEGRO)",
            "Deutsche Gesellschaft für Rechtsmedizin e.V. (DGRM)",
            "Deutsche Gesellschaft für Reproduktionsmedizin e.V. (DGRM)",
            "Deutsche Gesellschaft für Rheumatologie und Klinische Immunologie e.V. (DGRh)",
            "Deutsche Gesellschaft für Schlafforschung und Schlafmedizin e.V. (DGSM)",
            "Deutsche Gesellschaft für Sexualforschung e.V. (DGfS)",
            "Deutsche Gesellschaft für Sozialpädiatrie und Jugendmedizin e.V. (DGSPJ)",
            "Deutsche Gesellschaft für Sportmedizin und Prävention e.V. (DGSP)",
            "Deutsche Gesellschaft für Suchtforschung und Suchttherapie e.V. (DG-Sucht)",
            "Deutsche Gesellschaft für Thorax-, Herz- und Gefäßchirurgie e.V. (DGTHG)",
            "Deutsche Gesellschaft für Thoraxchirurgie e.V. (DGT)",
            "Deutsche Gesellschaft für Tropenmedizin, Reisemedizin und Globale Gesundheit e.V. (DTG)",
            "Deutsche Gesellschaft für Ultraschall in der Medizin e.V. (DEGUM)",
            "Deutsche Gesellschaft für Unfallchirurgie e.V. (DGU)",
            "Deutsche Gesellschaft für Urologie e.V. (DGU)",
            "Deutsche Gesellschaft für Verbrennungsmedizin e.V. (DGV)",
            "Deutsche Gesellschaft für Wundheilung und Wundbehandlung e.V.",
            "Deutsche Gesellschaft für Zahn-, Mund- und Kieferheilkunde e.V. (DGZMK)",
            "Deutsche Gesellschaft für Zahnerhaltung e.V. (DGZ)",
            "Deutsche Gesellschaft für pädiatrische und adoleszente Endokrinologie und Diabetologie (DGPAED)",
            "Deutsche Interdisziplinäre Vereinigung für Intensiv- und Notfallmedizin e.V. (DIVI)",
            "Deutsche Krebsgesellschaft e.V. (DKG)",
            "Deutsche Migräne- und Kopfschmerzgesellschaft e.V. (DMKG)",
            "Deutsche Ophthalmologische Gesellschaft e.V. (DOG)",
            "Deutsche Röntgengesellschaft, Gesellschaft für Medizinische Radiologie e.V. (DRG)",
            "Deutsche STI-Gesellschaft e.V. (DSTIG) - Gesellschaft zur Förderung der Sexuellen Gesundheit",
            "Deutsche Schlaganfall-Gesellschaft e.V. (DSG)",
            "Deutsche Schmerzgesellschaft e.V.",
            "Deutsche Sepsis-Gesellschaft e.V. (DSG)",
            "Deutsche Wirbelsäulengesellschaft e.V. (DWG)",
            "Deutsches Kollegium für Psychosomatische Medizin e.V. (DKPM)",
            "Deutschsprachige Gesellschaft für Psychotraumatologie e.V. (DeGPT)",
            "Deutschsprachige Medizinische Gesellschaft für Paraplegiologie e.V.",
            "Deutschsprachige Mykologische Gesellschaft e.V. (DMYKG)",
            "Gesellschaft Deutschsprachiger Lymphologen e.V. (GDL)",
            "Gesellschaft für Hygiene, Umweltmedizin und Präventivmedizin e.V. (GHUP)",
            "Gesellschaft für Kinder- und Jugendrheumatologie e.V. (GKJR)",
            "Gesellschaft für Neonatologie und pädiatrische Intensivmedizin e.V. (GNPI)",
            "Gesellschaft für Neuropädiatrie e.V. (GNP)",
            "Gesellschaft für Pädiatrische Gastroenterologie und Ernährung e.V. (GPGE)",
            "Gesellschaft für Pädiatrische Nephrologie e.V. (GPN)",
            "Gesellschaft für Pädiatrische Onkologie und Hämatologie (GPOH)",
            "Gesellschaft für Pädiatrische Pneumologie e.V. (GPP)",
            "Gesellschaft für Pädiatrische Radiologie e.V. (GPR)",
            "Gesellschaft für Tauch- und Überdruckmedizin e.V. (GTÜM)",
            "Gesellschaft für Thrombose- und Hämostaseforschung e.V. (GTH)",
            "Gesellschaft für Transfusionsmedizin e.V. (GFTM)",
            "Gesellschaft für Virologie e.V. (GfV)",
            "NVL-Programm von BÄK, KBV, AWMF",
            "Paul-Ehrlich-Gesellschaft für Infektionstherapie e.V. (PEG)"
        ]

        # Bekannte IDs für Fachgesellschaften laden oder initialisieren
        known_society_ids = {}
        if os.path.exists("society_ids.txt"):
            try:
                with open("society_ids.txt", "r") as f:
                    for line in f:
                        if '\t' in line:
                            society, society_id = line.strip().split('\t', 1)
                            known_society_ids[society] = society_id
                print(f"Geladene IDs: {known_society_ids}")
            except Exception as e:
                print(f"Fehler beim Laden der IDs: {e}")
        
        # Fest kodierte IDs für einige Gesellschaften
        if "Deutsche Dermatologische Gesellschaft e.V. (DDG)" not in known_society_ids:
            known_society_ids["Deutsche Dermatologische Gesellschaft e.V. (DDG)"] = "013"
        if "Arbeitsgemeinschaft Pädiatrische Immunologie e.V. (API)" not in known_society_ids:
            known_society_ids["Arbeitsgemeinschaft Pädiatrische Immunologie e.V. (API)"] = "189"
        if "Dachverband Osteologie e.V. [assoziiert]" not in known_society_ids:
            known_society_ids["Dachverband Osteologie e.V. [assoziiert]"] = "183"
        if "Deutsche AIDS-Gesellschaft e.V. (DAIG)" not in known_society_ids:
            known_society_ids["Deutsche AIDS-Gesellschaft e.V. (DAIG)"] = "055"
        if "Deutsche Adipositas-Gesellschaft e.V. (DAG)" not in known_society_ids:
            known_society_ids["Deutsche Adipositas-Gesellschaft e.V. (DAG)"] = "050"
        if "Deutsche Gesellschaft für Anästhesiologie und Intensivmedizin e.V. (DGAI)" not in known_society_ids:
            known_society_ids["Deutsche Gesellschaft für Anästhesiologie und Intensivmedizin e.V. (DGAI)"] = "001"
        if "Deutsche Gesellschaft für Arbeitsmedizin und Umweltmedizin e.V. (DGAUM)" not in known_society_ids:
            known_society_ids["Deutsche Gesellschaft für Arbeitsmedizin und Umweltmedizin e.V. (DGAUM)"] = "002"
        if "Deutsche Gesellschaft für Chirurgie e.V. (DGCH)" not in known_society_ids:
            known_society_ids["Deutsche Gesellschaft für Chirurgie e.V. (DGCH)"] = "003"

        # Liste möglicher IDs (systematisch testen)
        possible_ids = []
        for i in range(1, 200):  # Teste IDs von 001 bis 199
            possible_ids.append(f"{i:03d}")  # Format: 001, 002, ..., 199
        
        print(f"Verarbeite {len(society_list)} Fachgesellschaften")
        
        total_downloaded = 0
        processed_count = 0

        # Jede Fachgesellschaft einzeln verarbeiten
        for idx, society_name in enumerate(society_list, start=1):
            # Bei Testläufen nur die ersten paar Gesellschaften verarbeiten
            # if idx > 10:  # Kommentieren für vollständigen Lauf
            #    break
                
            society_dir = os.path.join(output_dir, sanitize_filename(society_name))
            os.makedirs(society_dir, exist_ok=True)

            try:
                print(f"\n=== Verarbeite Fachgesellschaft {idx}/{len(society_list)}: {society_name} ===")
                
                # 1. Bekannte ID verwenden, falls vorhanden
                society_id = None
                expected_guidelines = 0
                
                if society_name in known_society_ids:
                    society_id = known_society_ids[society_name]
                    society_url = f"https://register.awmf.org/de/leitlinien/aktuelle-leitlinien/fachgesellschaft/{society_id}"
                    
                    print(f"Verwende bekannte ID: {society_id}")
                    
                    # Überprüfen, ob diese ID gültig ist
                    driver.get(society_url)
                    time.sleep(5)
                    
                    # Cookies akzeptieren
                    try:
                        cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'Alle akzeptieren')]")
                        if cookie_buttons and len(cookie_buttons) > 0:
                            cookie_buttons[0].click()
                            print("Cookies akzeptiert")
                            time.sleep(2)
                    except:
                        print("Kein Cookie-Banner gefunden oder bereits akzeptiert")
                    
                    # Prüfe, ob die Detailseite den Gesellschaftsnamen enthält
                    if society_name not in driver.page_source:
                        print(f"ID {society_id} scheint nicht korrekt zu sein, suche nach einer besseren...")
                    else:
                        print(f"ID {society_id} ist korrekt, verwende sie")
                        link_url = society_url
                        found_link = True
                        
                        # Für DDG spezielle Behandlung
                        if "Deutsche Dermatologische Gesellschaft e.V. (DDG)" in society_name:
                            expected_guidelines = 44  # DDG hat etwa 44 Leitlinien
                        else:
                            # Erwartete Anzahl der Leitlinien extrahieren (verbesserte Version)
                            try:
                                # Methode 1: Suche Statistiken in Überschriften oder dedizierten Stats-Bereichen
                                stats_elements = driver.find_elements(By.CSS_SELECTOR, ".subtitle, .stats-row, .summary-stats, .statistics")
                                for element in stats_elements:
                                    counts = re.findall(r'\b(\d+)\b', element.text)
                                    for count in counts:
                                        expected_guidelines += int(count)
                                
                                # Methode 2: Prüfe die Anzahl der Zeilen in der Tabelle (falls vorhanden)
                                if expected_guidelines == 0:
                                    tables = driver.find_elements(By.TAG_NAME, "table")
                                    if tables:
                                        rows = tables[0].find_elements(By.TAG_NAME, "tr")
                                        if len(rows) > 1:  # Header-Zeile abziehen
                                            expected_guidelines = len(rows) - 1
                                
                                # Methode 3: Suche nach S1, S2, S3 Kategorien mit Zahlen
                                if expected_guidelines == 0:
                                    s_class_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'S1') or contains(text(), 'S2') or contains(text(), 'S3')]")
                                    for element in s_class_elements:
                                        text = element.text
                                        # Suche nach Mustern wie "S1: 5", "S2k (10)", etc.
                                        matches = re.findall(r'(S[123][ek]?)[\s:-]*(\d+)', text)
                                        for _, count in matches:
                                            expected_guidelines += int(count)
                                
                                if expected_guidelines > 0:
                                    print(f"Erwartete Anzahl von Leitlinien: {expected_guidelines}")
                            except Exception as e:
                                print(f"Fehler beim Extrahieren der erwarteten Leitlinienanzahl: {e}")    
                    
                else:
                    found_link = False
                    link_url = None
                    
                    # 2. Wenn keine bekannte ID, suche zuerst auf der Hauptseite
                    driver.get("https://register.awmf.org/de/leitlinien/aktuelle-leitlinien")
                    print("Hauptseite geladen")
                    time.sleep(5)
                    
                    # Cookies akzeptieren
                    try:
                        cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'Alle akzeptieren')]")
                        if cookie_buttons and len(cookie_buttons) > 0:
                            cookie_buttons[0].click()
                            print("Cookies akzeptiert")
                            time.sleep(2)
                    except:
                        print("Kein Cookie-Banner gefunden oder bereits akzeptiert")
                    
                    # Gründliches Scrollen durch die Hauptseite
                    scroll_thoroughly(driver)
                    
                    # NEU: Suche nach der Erwarteten Anzahl von Leitlinien in der Übersichtstabelle
                    try:
                        # Suche nach der Zeile, die die Gesellschaft enthält
                        society_row = None
                        rows = driver.find_elements(By.TAG_NAME, "tr")
                        for row in rows:
                            if society_name in row.text:
                                society_row = row
                                break
                        
                        if society_row:
                            # Extrahiere alle Zahlen aus der Zeile - typischerweise die Statistiken S1, S2e, S2k, S3
                            numbers = re.findall(r'\b(\d+)\b', society_row.text)
                            # Ignoriere die erste Zahl, falls es eine ID ist
                            relevant_numbers = numbers[1:] if len(numbers) > 1 else numbers
                            for number in relevant_numbers:
                                expected_guidelines += int(number)
                            print(f"Erwartete Anzahl von Leitlinien aus Übersichtstabelle: {expected_guidelines}")
                    except Exception as e:
                        print(f"Fehler beim Extrahieren der Leitlinienanzahl aus der Übersicht: {e}")

                    # Nach der Gesellschaft suchen
                    society_element = None
                    try:
                        # Versuche über direkten Text-Link zu finden
                        society_links = driver.find_elements(By.XPATH, f"//a[text()='{society_name}']")
                        if society_links:
                            society_element = society_links[0]
                            print(f"Gesellschaft über exakten Namen gefunden")
                    except:
                        pass
                    
                    # Falls nicht gefunden, versuche es mit einem breiteren Ansatz
                    if not society_element:
                        all_links = driver.find_elements(By.TAG_NAME, "a")
                        for link in all_links:
                            try:
                                if society_name == link.text.strip():
                                    society_element = link
                                    print(f"Gesellschaft über Link-Text gefunden")
                                    break
                            except:
                                pass
                    
                    # Falls gefunden, klicke darauf
                    if society_element:
                        link_url = society_element.get_attribute("href")
                        if link_url:
                            found_link = True
                            print(f"Link zur Gesellschaft gefunden: {link_url}")
                            
                            # Extrahiere ID aus URL
                            try:
                                society_id = link_url.split("/")[-1]
                                known_society_ids[society_name] = society_id
                                print(f"ID extrahiert und gespeichert: {society_id}")
                            except:
                                pass

                    # 3. Wenn Link nicht gefunden, systematisch IDs testen
                    if not found_link:
                        print("Link nicht direkt gefunden, teste systematisch IDs...")
                        
                        # Abbr aus Klammern extrahieren
                        abbr_match = re.search(r'\(([^)]+)\)', society_name)
                        abbr = abbr_match.group(1) if abbr_match else ""
                        
                        # Teste mögliche IDs
                        for test_id in possible_ids:
                            test_url = f"https://register.awmf.org/de/leitlinien/aktuelle-leitlinien/fachgesellschaft/{test_id}"
                            try:
                                print(f"Teste ID {test_id}...")
                                driver.get(test_url)
                                time.sleep(3)
                                
                                # Prüfe, ob die Gesellschaft auf der Seite erscheint
                                page_content = driver.page_source
                                
                                # Prüfung 1: Vollständiger Name
                                if society_name in page_content:
                                    print(f"ID {test_id} stimmt mit Gesellschaft überein (vollständiger Name)")
                                    link_url = test_url
                                    found_link = True
                                    society_id = test_id
                                    
                                    # Speichere ID für zukünftige Nutzung
                                    known_society_ids[society_name] = test_id
                                    break
                                
                                # Prüfung 2: Abkürzung
                                elif abbr and f"({abbr})" in page_content:
                                    # Zusätzliche Prüfung für Abkürzungen
                                    base_name = society_name.split("(")[0].strip()
                                    if base_name[:20] in page_content:  # Prüfe ersten Teil des Namens
                                        print(f"ID {test_id} stimmt mit Gesellschaft überein (Abkürzung)")
                                        link_url = test_url
                                        found_link = True
                                        society_id = test_id
                                        
                                        # Speichere ID für zukünftige Nutzung
                                        known_society_ids[society_name] = test_id
                                        break
                            except Exception as e:
                                print(f"Fehler beim Testen von ID {test_id}: {e}")
                                continue
                
                # Wenn immer noch kein Link gefunden, diese Gesellschaft überspringen
                if not found_link or not link_url:
                    print(f"Konnte keinen Link für '{society_name}' finden, überspringe")
                    continue
                
                # 4. Zur Detailseite navigieren
                driver.get(link_url)
                print("Zur Detailseite navigiert")
                time.sleep(5)
                
                # Gründliches Scrollen, um ALLE Inhalte zu laden
                scroll_thoroughly(driver)

                # 5. Nach den Leitlinien suchen
                guideline_links = []
                
                # Spezielle Behandlung für die DDG 
                is_special_case = "Deutsche Dermatologische Gesellschaft e.V. (DDG)" in society_name
                
                # In Tabellen suchen
                tables = driver.find_elements(By.TAG_NAME, "table")
                
                if tables:
                    # Tabelle finden - typischerweise die erste auf der Seite
                    table = tables[0]
                    
                    # Tabelle in den Fokus scrollen
                    driver.execute_script("arguments[0].scrollIntoView(true);", table)
                    time.sleep(1)
                    
                    # Innerhalb der Tabelle scrollen (wenn sie scrollbar ist)
                    try:
                        # Höhe der Tabelle ermitteln
                        table_height = int(driver.execute_script("return arguments[0].scrollHeight", table))
                        
                        # In kleinen Schritten durch die Tabelle scrollen
                        for scroll_pos in range(0, table_height, 50):
                            driver.execute_script("arguments[0].scrollTop = arguments[1];", table, scroll_pos)
                            time.sleep(0.3)
                    except Exception as e:
                        print(f"Fehler beim Scrollen innerhalb der Tabelle: {e}")
                    
                    # Zuerst Tabellenhöhe ermitteln (für Debug-Zwecke)
                    table_height = table.get_attribute("offsetHeight")
                    print(f"Tabellenhöhe: {table_height}px")
                    
                    # Nach dem Scrollen alle Zeilen holen
                    guideline_rows = table.find_elements(By.TAG_NAME, "tr")
                    print(f"Gefunden: {len(guideline_rows)} Zeilen in der Tabelle")
                    
                    # Nochmals durch die Seite scrollen, um sicherzustellen, dass alle Inhalte geladen wurden
                    scroll_thoroughly(driver)
                    
                    # Erneut Zeilen zählen nach dem Scrollen
                    guideline_rows = table.find_elements(By.TAG_NAME, "tr")
                    print(f"Nach gründlichem Scrollen: {len(guideline_rows)} Zeilen in der Tabelle")
                    
                    # Header überspringen
                    for g_idx, row in enumerate(guideline_rows[1:] if len(guideline_rows) > 1 else guideline_rows, start=1):
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if not cells or len(cells) < 2:
                                continue
                            
                            reg_number = cells[0].text.strip() if len(cells) > 0 else ""
                            title = cells[1].text.strip() if len(cells) > 1 else ""
                            
                            if not title:
                                continue
                            
                            # Link suchen
                            g_link = None
                            
                            # Im Titel
                            title_links = cells[1].find_elements(By.TAG_NAME, "a")
                            if title_links:
                                g_link = title_links[0].get_attribute("href")
                            
                            # In anderen Zellen
                            if not g_link:
                                for cell in cells:
                                    cell_links = cell.find_elements(By.TAG_NAME, "a")
                                    if cell_links:
                                        g_link = cell_links[0].get_attribute("href")
                                        if g_link:
                                            break
                            
                            if g_link:
                                guideline_links.append((reg_number, title, g_link))
                                print(f"Leitlinie gefunden: {title}")
                        except Exception as e:
                            print(f"Fehler bei Leitlinie {g_idx}: {e}")

                # Alternative Methode, falls keine Tabellen oder keine Leitlinien gefunden wurden
                if not guideline_links:
                    print("Keine Leitlinien in Tabellen gefunden, verwende alternative Methode")
                    
                    # Nochmals durch die Seite scrollen, um sicherzustellen, dass alle Inhalte geladen wurden
                    scroll_thoroughly(driver)
                    
                    # Suche nach Links, die typische Muster für Leitlinien haben
                    all_links = driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        try:
                            href = link.get_attribute("href")
                            text = link.text.strip()
                            
                            # Nur Links mit Titel betrachten
                            if href and text and len(text) > 10:
                                is_guideline = False
                                
                                # Verschiedene Heuristiken für Leitlinien
                                if "leitlinie" in href.lower():
                                    is_guideline = True
                                if re.search(r'\d{3}-\d{3}', href) or re.search(r'\d{3}-\d{3}', text):
                                    is_guideline = True
                                if "diagnostik" in text.lower() or "therapie" in text.lower():
                                    is_guideline = True
                                
                                if is_guideline:
                                    # Registernummer extrahieren
                                    reg_number = ""
                                    reg_match = re.search(r'(\d{3}-\d{3})', href)
                                    if reg_match:
                                        reg_number = reg_match.group(1)
                                    else:
                                        reg_match = re.search(r'(\d{3}-\d{3})', text)
                                        if reg_match:
                                            reg_number = reg_match.group(1)
                                    
                                    # Prüfen, ob es ein Duplikat ist
                                    is_duplicate = False
                                    for _, existing_title, existing_href in guideline_links:
                                        if existing_href == href or existing_title == text:
                                            is_duplicate = True
                                            break
                                    
                                    if not is_duplicate:
                                        guideline_links.append((reg_number, text, href))
                                        print(f"Leitlinie gefunden (alternative Methode): {text}")
                        except Exception as e:
                            print(f"Fehler bei Link-Analyse: {e}")

                # Wenn wir immer noch keine oder zu wenige Leitlinien haben und eine ID bekannt ist,
                # versuche systematisch alle möglichen Leitlinien-IDs für diese Gesellschaft
                if society_id:
                    # Prüfen, ob eine Diskrepanz zwischen erwarteter und tatsächlicher Anzahl besteht
                    found_count = len(guideline_links)
                    
                    # Liste der initial gefundenen Leitlinien-IDs und URLs
                    initial_guideline_ids = {reg_num for reg_num, _, _ in guideline_links if reg_num}
                    initial_guideline_urls = {url for _, _, url in guideline_links}
                    
                    # Sammlung der Registernummern, die während des systematischen Durchlaufs heruntergeladen wurden
                    already_downloaded_reg_nums = set()
                    
                    # Nur die vollständige systematische Suche durchführen, wenn eine Diskrepanz besteht
                    if expected_guidelines > 0 and found_count < expected_guidelines:
                        print(f"Diskrepanz entdeckt: Nur {found_count} von {expected_guidelines} erwarteten Leitlinien gefunden.")
                        print(f"Starte systematische Suche nach allen Leitlinien für {society_name}...")
                        
                        # Systematisch alle möglichen Leitlinien-IDs durchgehen (001-200)
                        for sub_id in range(1, 201):
                            reg_number = f"{society_id}-{sub_id:03d}"  # Format: z.B. 013-001
                            
                            # Überspringen, wenn wir diese Leitlinie bereits haben
                            if reg_number in initial_guideline_ids:
                                continue
                                
                            # Verschiedene Muster für PDF-URLs generieren
                            pdf_urls = [
                                f"https://register.awmf.org/assets/guidelines/{reg_number}l_S1_.pdf",
                                f"https://register.awmf.org/assets/guidelines/{reg_number}l_S2k_.pdf",
                                f"https://register.awmf.org/assets/guidelines/{reg_number}l_S2e_.pdf",
                                f"https://register.awmf.org/assets/guidelines/{reg_number}l_S3_.pdf",
                                f"https://register.awmf.org/assets/guidelines/{society_id}_{society_id[-3:]}_{reg_number[-3:]}.pdf",
                                f"https://register.awmf.org/assets/guidelines/{society_id}_D_{reg_number[-3:]}.pdf"
                            ]
                            
                            detail_url = f"https://register.awmf.org/de/leitlinien/detail/{reg_number}"
                            
                            # Zuerst testen, ob die Detailseite existiert
                            try:
                                response = requests.head(detail_url, timeout=3)
                                
                                # Falls die Seite existiert, versuchen wir die Detailseite zu laden
                                if response.status_code == 200:
                                    try:
                                        # Detailseite laden, um den korrekten Titel zu bekommen
                                        driver.get(detail_url)
                                        time.sleep(2)
                                        
                                        # Titel extrahieren
                                        title = f"Leitlinie {reg_number}"  # Fallback-Titel
                                        title_elements = driver.find_elements(By.TAG_NAME, "h1")
                                        if title_elements:
                                            title_text = title_elements[0].text.strip()
                                            if title_text and "nicht gefunden" not in title_text.lower() and "forbidden" not in title_text.lower():
                                                title = title_text
                                        
                                        # Nach Download-Links suchen
                                        pdf_links = []
                                        
                                        # Scrollen, um alle Inhalte zu laden
                                        scroll_thoroughly(driver)
                                        
                                        # Download-Links suchen
                                        download_elements = driver.find_elements(By.XPATH, "//a[contains(text(), 'Download')]")
                                        for elem in download_elements:
                                            href = elem.get_attribute("href")
                                            if href and href.lower().endswith(".pdf"):
                                                pdf_links.append(href)
                                        
                                        # Alle Links, die auf .pdf enden
                                        pdf_elements = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
                                        for elem in pdf_elements:
                                            href = elem.get_attribute("href")
                                            if href and href not in pdf_links:
                                                pdf_links.append(href)
                                        
                                        # Wenn PDFs gefunden wurden, der Leitlinie hinzufügen
                                        if pdf_links:
                                            guideline_links.append((reg_number, title, detail_url))
                                            print(f"Leitlinie gefunden (systematisch): {reg_number} - {title}")
                                            
                                            # PDFs direkt herunterladen
                                            society_dir = os.path.join(output_dir, sanitize_filename(society_name))
                                            for pdf_url in pdf_links:
                                                try:
                                                    filename = f"{reg_number}_{sanitize_filename(title)}.pdf"
                                                    file_path = os.path.join(society_dir, filename)
                                                    
                                                    response = requests.get(pdf_url, timeout=30)
                                                    if response.status_code == 200:
                                                        with open(file_path, "wb") as f:
                                                            f.write(response.content)
                                                        print(f"PDF direkt heruntergeladen: {filename}")
                                                        total_downloaded += 1
                                                except Exception as e:
                                                    print(f"Fehler beim direkten PDF-Download: {e}")
                                            # Markieren, dass diese Registernummer bereits heruntergeladen wurde
                                            already_downloaded_reg_nums.add(reg_number)
                                        else:
                                            # Wenn keine PDFs gefunden wurden, aber die Seite existiert,
                                            # fügen wir die Leitlinie trotzdem hinzu
                                            guideline_links.append((reg_number, title, detail_url))
                                            print(f"Leitlinie gefunden (systematisch, keine PDFs): {reg_number} - {title}")
                                    except Exception as e:
                                        # Wenn die Detailseite nicht geladen werden kann, versuchen wir direkt PDFs zu finden
                                        # basierend auf dem Standardmuster
                                        for pdf_url in pdf_urls:
                                            try:
                                                response = requests.head(pdf_url, timeout=5)
                                                if response.status_code == 200:
                                                    title = f"Leitlinie {reg_number}"
                                                    guideline_links.append((reg_number, title, detail_url))
                                                    print(f"Leitlinie gefunden (systematisch über PDF): {reg_number}")
                                                    
                                                    # PDF direkt herunterladen
                                                    filename = f"{reg_number}_{sanitize_filename(title)}.pdf"
                                                    file_path = os.path.join(society_dir, filename)
                                                    
                                                    response = requests.get(pdf_url, timeout=30)
                                                    if response.status_code == 200:
                                                        with open(file_path, "wb") as f:
                                                            f.write(response.content)
                                                        print(f"PDF direkt heruntergeladen: {filename}")
                                                        total_downloaded += 1
                                                    # Markieren, dass diese Registernummer bereits heruntergeladen wurde
                                                    already_downloaded_reg_nums.add(reg_number)
                                                    break  # Sobald ein PDF gefunden wurde, keine weiteren Muster probieren
                                            except:
                                                continue
                            except Exception as e:
                                # Fehler ignorieren und mit der nächsten ID fortfahren
                                pass
                            
                            # Nach jeder 10. Anfrage kurz warten, um den Server nicht zu überlasten
                            if sub_id % 10 == 0:
                                time.sleep(1)
                
                # Report über gefundene Leitlinien
                if expected_guidelines > 0:
                    if len(guideline_links) < expected_guidelines:
                        print(f"Warnung: Nur {len(guideline_links)} von {expected_guidelines} erwarteten Leitlinien gefunden.")
                    else:
                        print(f"Erfolg: Alle {expected_guidelines} erwarteten Leitlinien gefunden!")
                
                # Duplikate entfernen (basierend auf URL)
                unique_links = []
                seen_urls = set()
                for reg_num, title, url in guideline_links:
                    if url not in seen_urls:
                        unique_links.append((reg_num, title, url))
                        seen_urls.add(url)
                
                guideline_links = unique_links
                print(f"Insgesamt {len(guideline_links)} einzigartige Leitlinien gefunden")

                # 6. Für jede Leitlinie die PDFs herunterladen (für Leitlinien, die nicht direkt heruntergeladen wurden)
                society_downloads = 0

                # Nur die Leitlinien verarbeiten, die nicht bereits während des systematischen Durchlaufs heruntergeladen wurden
                for g_idx, (reg_number, title, g_link) in enumerate(guideline_links, start=1):
                    # Überspringen, wenn diese Leitlinie bereits während des systematischen Durchlaufs heruntergeladen wurde
                    if reg_number in already_downloaded_reg_nums:
                        print(f"\n  Überspringe Leitlinie {g_idx}/{len(guideline_links)}: {title} (bereits heruntergeladen)")
                        continue
                    
                    try:
                        print(f"\n  Verarbeite Leitlinie {g_idx}/{len(guideline_links)}: {title}")
                        
                        # Wenn der Titel "Forbidden" enthält, versuche den Titel zu korrigieren
                        if "forbidden" in title.lower():
                            title = f"Leitlinie {reg_number}"
                        
                        # Zur Leitlinien-Detailseite
                        driver.get(g_link)
                        print("  Zur Leitlinien-Detailseite navigiert")
                        time.sleep(3)
                        
                        # Gründliches Scrollen, um alle Inhalte zu laden
                        scroll_thoroughly(driver)
                        
                        # Aktuellen Titel nochmals versuchen zu extrahieren, falls er "Forbidden" war
                        if "Leitlinie" in title and reg_number in title:
                            title_elements = driver.find_elements(By.TAG_NAME, "h1")
                            if title_elements:
                                new_title = title_elements[0].text.strip()
                                if new_title and "forbidden" not in new_title.lower() and "nicht gefunden" not in new_title.lower():
                                    title = new_title
                                    print(f"  Titel aktualisiert: {title}")
                        
                        # Download-Links suchen
                        download_links = []
                        
                        # Suche alle Links mit "Download" Text
                        download_elements = driver.find_elements(By.XPATH, "//a[contains(text(), 'Download')]")
                        for elem in download_elements:
                            href = elem.get_attribute("href")
                            if href and href.lower().endswith(".pdf"):
                                download_links.append((elem.text.strip(), href))
                        
                        # Suche alle Links, die auf .pdf enden - immer ausführen, um alle PDF-Links zu finden
                        pdf_links = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
                        for link in pdf_links:
                            href = link.get_attribute("href")
                            if href:
                                # Prüfen, ob der Link bereits in der Liste ist
                                is_duplicate = False
                                for _, existing_url in download_links:
                                    if existing_url == href:
                                        is_duplicate = True
                                        break
                                
                                if not is_duplicate:
                                    download_links.append((link.text.strip(), href))
                        
                        # PDFs herunterladen
                        if download_links:
                            print(f"  {len(download_links)} Download-Links gefunden")
                            
                            # Alle PDFs herunterladen (für vollständige Erfassung)
                            max_downloads = len(download_links)
                            for dl_idx, (text, url) in enumerate(download_links, start=1):
                                try:
                                    # PDF-Typ bestimmen
                                    text_lower = text.lower()
                                    pdf_type = "Unbekannt"
                                    
                                    if "langfassung" in text_lower:
                                        pdf_type = "Langfassung"
                                    elif "kurz" in text_lower:
                                        pdf_type = "Kurzfassung"
                                    elif "patient" in text_lower:
                                        pdf_type = "Patientenversion"
                                    elif "report" in text_lower:
                                        pdf_type = "Leitlinienreport"
                                    
                                    # Dateinamen erstellen
                                    base_name = sanitize_filename(title)
                                    if reg_number:
                                        base_name = f"{reg_number}_{base_name}"
                                    
                                    filename = f"{base_name}_{pdf_type}.pdf"
                                    file_path = os.path.join(society_dir, filename)
                                    
                                    print(f"    Download: {filename}")
                                    print(f"    URL: {url}")
                                    
                                    # PDF herunterladen
                                    try:
                                        response = requests.get(url, timeout=60)
                                        
                                        if response.status_code == 200:
                                            with open(file_path, "wb") as f:
                                                f.write(response.content)
                                            print(f"    Erfolgreich gespeichert als: {file_path}")
                                            total_downloaded += 1
                                            society_downloads += 1
                                        else:
                                            print(f"    HTTP-Fehler: {response.status_code}")
                                    except Exception as e:
                                        print(f"    Download-Fehler: {e}")
                                
                                except Exception as e:
                                    print(f"    Fehler beim Download: {e}")
                        else:
                            print("  Keine Download-Links gefunden")
                            
                            # Wenn keine Download-Links gefunden wurden, versuche direkte PDF-URLs
                            if reg_number:
                                direct_pdf_urls = [
                                    f"https://register.awmf.org/assets/guidelines/{reg_number}l_S1_.pdf",
                                    f"https://register.awmf.org/assets/guidelines/{reg_number}l_S2k_.pdf",
                                    f"https://register.awmf.org/assets/guidelines/{reg_number}l_S2e_.pdf",
                                    f"https://register.awmf.org/assets/guidelines/{reg_number}l_S3_.pdf",
                                ]
                                
                                for url in direct_pdf_urls:
                                    try:
                                        response = requests.head(url, timeout=5)
                                        if response.status_code == 200:
                                            base_name = sanitize_filename(title)
                                            if reg_number:
                                                base_name = f"{reg_number}_{base_name}"
                                                
                                            filename = f"{base_name}.pdf"
                                            file_path = os.path.join(society_dir, filename)
                                            
                                            print(f"    Direkter Download-Versuch: {filename}")
                                            print(f"    URL: {url}")
                                            
                                            response = requests.get(url, timeout=60)
                                            if response.status_code == 200:
                                                with open(file_path, "wb") as f:
                                                    f.write(response.content)
                                                print(f"    Erfolgreich gespeichert als: {file_path}")
                                                total_downloaded += 1
                                                society_downloads += 1
                                            else:
                                                print(f"    HTTP-Fehler: {response.status_code}")
                                    except:
                                        pass
                    
                    except Exception as e:
                        print(f"  Fehler bei Leitlinie {g_idx}: {e}")
                
                processed_count += 1
                print(f"\nFachgesellschaft {idx}/{len(society_list)} abgeschlossen: {society_name}")
                print(f"{society_downloads} PDFs für diese Gesellschaft heruntergeladen")
                print(f"Fortschritt: {processed_count}/{len(society_list)} Fachgesellschaften")
                
                # Speichere bekannte IDs in eine Datei für zukünftige Durchläufe
                with open("society_ids.txt", "w") as f:
                    for society, society_id in known_society_ids.items():
                        f.write(f"{society}\t{society_id}\n")
                
            except Exception as e:
                print(f"Fehler bei Fachgesellschaft {idx}: {e}")
        
        print("\nScraping abgeschlossen!")
        print(f"Insgesamt {total_downloaded} PDFs heruntergeladen")
        print(f"Insgesamt {processed_count}/{len(society_list)} Fachgesellschaften verarbeitet")
        print("Bekannte Fachgesellschafts-IDs wurden in society_ids.txt gespeichert")

    except Exception as e:
        print(f"Kritischer Fehler: {e}")
        driver.save_screenshot("kritischer_fehler.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    download_awmf_guidelines()