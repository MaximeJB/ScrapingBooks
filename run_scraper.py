import requests
import os
from bs4 import BeautifulSoup
import csv

url = "https://books.toscrape.com/"

def scrape_categories():
    """Récupère les liens des catégories"""
    print("Début de la recherche des catégories...")
    all_categories_links = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.find("div", class_="side_categories")
        links_categories = categories.find_all("a")
        for categories_title in links_categories[1:]:
            addition_url = url + categories_title["href"]
            all_categories_links.append((categories_title.text.strip(), addition_url))
        print(f"{len(all_categories_links)} catégories trouvées")
    return all_categories_links

def download_image(image_url, book_title, category_name):
    """Télécharge l'image avec gestion des caractères spéciaux"""
    print(f"Tentative de téléchargement de l'image pour : {book_title}")
    
    # Nettoyage des noms de dossier et fichier
    safe_category = category_name.replace("/", "_").strip()
    safe_title = book_title.replace(":", "_").replace("#", "_").replace(" ", "_")
    safe_title = safe_title[:50]  # Limite la longueur
    
    # Création du chemin sécurisé
    images_dir = os.path.join(safe_category, "book_images")
    os.makedirs(images_dir, exist_ok=True)
    
    image_name = f"{safe_title.lower()}.jpg"
    image_path = os.path.join(images_dir, image_name)
    
    # Téléchargement
    response_image = requests.get(image_url)
    if response_image.status_code == 200:
        with open(image_path, "wb") as f:
            f.write(response_image.content)
            print(f"Image téléchargée pour : {book_title}")
    else:
        print(f"Erreur de téléchargement pour {book_title}. URL : {image_url}")

def scrape_book_infos(url_product):
    """Récupère les informations détaillées d'un livre"""
    print(f"Récupération des informations du livre : {url_product}")
    try:
        response = requests.get(url_product)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Vérification des données obligatoires
        products_infos = soup.find_all("td")
        if len(products_infos) < 6:
            print(f"Données incomplètes pour : {url_product}")
            return None
            
        product_infos_values = [info.text.strip() for info in products_infos]
        
        # Extraction des données avec vérifications
        data = {
            "upc": product_infos_values[0],
            "price_incl_tax": product_infos_values[2],
            "price_excl_tax": product_infos_values[3],
            "availability": product_infos_values[5].replace("In stock (", "").replace("available)", ""),
            "description": soup.find_all("p")[3].text if len(soup.find_all("p")) > 3 else "",
            "category": soup.find_all("a")[3].text if len(soup.find_all("a")) > 3 else "",
            "review_rating": 0,
            "image_url": ""
        }
        
        # Gestion de la note
        review_element = soup.find("p", class_="star-rating")
        if review_element:
            review = review_element["class"][1]
            mapping = {"Four": 4, "One": 1, "Two": 2, "Three": 3, "Five": 5}
            data["review_rating"] = mapping.get(review, 0)
        
        # Gestion de l'image
        thumbnail_div = soup.find("div", class_="thumbnail")
        if thumbnail_div:
            image_cover = thumbnail_div.find("img")["src"].lstrip("./")
            data["image_url"] = url + image_cover
        
        return data
        
    except Exception as e:
        print(f"Erreur grave lors de la récupération : {e}")
        return None

def scrape_pages_book_urls(url, category_name):
    """Scrape tous les livres d'une catégorie"""
    print(f"Exploration de la catégorie : {url}")
    all_books = []
    
    try:
        os.makedirs(category_name.replace("/", "_"), exist_ok=True)
    except Exception as e:
        print(f"Erreur création dossier : {e}")
        return all_books

    while url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            books = soup.find_all('article', class_='product_pod')
            
            for book in books: 
                try:
                    title = book.find('h3').find('a')['title']
                    book_relative_url = book.find('h3').find('a')['href']
                    book_url = url.rsplit('/', 4)[0] + "/" + book_relative_url.replace('../', '')
                    
                    book_info = scrape_book_infos(book_url)
                    if not book_info:
                        continue
                        
                    book_data = {
                        "titre": title,
                        "prix": book.find('p', class_='price_color').text,
                        "Dispo": book.find('p', class_='instock availability').text.strip(),
                        **book_info  
                    }
                    
                    if book_info.get('image_url'):
                        download_image(book_info['image_url'], title, category_name)
                    
                    all_books.append(book_data)
                
                except Exception as e:
                    print(f"Erreur traitement livre : {e}")
                    continue

            # Gestion pagination
            next_page = soup.find('li', class_='next')
            if next_page:
                next_page_url = next_page.find('a')['href']
                base_url = url.rsplit('/', 1)[0]
                url = base_url + '/' + next_page_url
            else:
                break
                
        except Exception as e:
            print(f"Erreur récupération page : {e}")
            break

    # Écriture CSV robuste
    if all_books:
        csv_filename = os.path.join(
            category_name.replace("/", "_"), 
            f"{category_name.replace('/', '_')}.csv"
        )
        
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['titre', 'prix', 'Dispo', 'upc', 'price_incl_tax',
                            'price_excl_tax', 'availability', 'description',
                            'category', 'review_rating', 'image_url']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_books)
        except Exception as e:
            print(f"Erreur écriture CSV : {e}")

    return all_books

# Exécution principale
if __name__ == "__main__":
    print("Démarrage du scraping...")
    categories = scrape_categories()
    all_books = []
    for name, link in categories:
        all_books.extend(scrape_pages_book_urls(link, name))
    print(f"Scraping terminé. {len(all_books)} livres traités.")