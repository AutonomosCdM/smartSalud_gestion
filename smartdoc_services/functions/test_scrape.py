import requests
from bs4 import BeautifulSoup

def test_scraper():
    print("Test local del Scraper GES...")
    URL_GES = "https://auge.minsal.cl/problemasdesalud/index"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print(f"Conectando a {URL_GES}...")
        response = requests.get(URL_GES, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        count = 0
        print("\n--- Enlaces encontrados en Auge Minsal ---")
        for link in links:
            href = link['href']
            text = link.get_text(strip=True)
            print(f"DEBUG: {text} -> {href}")
            
            if "pdf" in href.lower():
                count += 1
        
        if count == 0:
            print("❌ No se encontraron PDFs. Revisar lógica de scraping.")
        else:
            print("✅ Test exitoso. Lógica de scraping válida.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_scraper()
