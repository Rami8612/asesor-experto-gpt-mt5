import requests
from bs4 import BeautifulSoup
import os

# Directorio donde guardar las noticias
os.makedirs("noticias_yahoo", exist_ok=True)

def obtener_titulares_yahoo():
    url = "https://finance.yahoo.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    noticias = []

    for item in soup.select('a[href*="/news/"]'):
        titulo = item.text.strip()
        enlace = item.get('href')
        if enlace and not enlace.startswith("http"):
            enlace = url + enlace
        if titulo and len(titulo) > 20:
            noticias.append((titulo, enlace))
    return noticias[:10]

def extraer_noticia_completa(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Intenta localizar los párrafos del artículo
    parrafos = soup.select('article p') or soup.select('div.caas-body p')
    texto = "\n".join(p.text.strip() for p in parrafos if p.text.strip())

    return texto if texto else "[No se pudo extraer el cuerpo de la noticia]"

if __name__ == "__main__":
    noticias = obtener_titulares_yahoo()
    for i, (titulo, enlace) in enumerate(noticias, 1):
        print(f"Descargando noticia {i}...")
        contenido = extraer_noticia_completa(enlace)
        nombre_archivo = f"noticias_yahoo/noticia_{i}.txt"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(f"{titulo}\n{enlace}\n\n{contenido}\n")
    print("✅ Noticias descargadas.")
