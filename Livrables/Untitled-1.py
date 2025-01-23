import requests
import os
from bs4 import BeautifulSoup
import csv

url = "https://books.toscrape.com/"

def scrape_total():
    all_categories_links = []
    # Récupérer la liste des URLs des catégories
    response = requests.get(url)

    # Vérifier que la requête a réussi
    if response.status_code == 200:
        # Parse le contenu HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        categories = soup.find("div", class_="side_categories")
        links_categories = categories.find_all("a")

        for categories_title in links_categories:
            addition_url = url + categories_title["href"]
            all_categories_links.append(addition_url)
    return all_categories_links

# Fonction pour télécharger l'image d'un livre
def download_image(image_url, book_title):
    # Créer un répertoire pour les images si nécessaire
    images_dir = "book_images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    # Extraire le nom de l'image (par exemple : 'book1.jpg')
    image_name = book_title.replace(" ", "_").lower() + ".jpg"  # Remplacer les espaces et mettre en minuscule
    image_path = os.path.join(images_dir, image_name)

    # Télécharger l'image
    response_image = requests.get(image_url)
    if response_image.status_code == 200:
        # Sauvegarder l'image dans le dossier local
        with open(image_path, 'wb') as f:
            f.write(response_image.content)
    else:
        print(f"Erreur de téléchargement de l'image pour {book_title}")

def scrape_book_infos(url_product):
    response = requests.get(url_product)
    # Vérifier que la requête a réussi
    if response.status_code == 200:
        # Parse le contenu HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

    all_infos = []
    products_infos = soup.find_all("td")
    product_infos_values = [info.text for info in products_infos]

    upc = product_infos_values[0]
    prices_including_taxes = product_infos_values[2]
    prices_excluding_taxes = product_infos_values[3]
    number_available = product_infos_values[5].replace("In stock (", "").replace("available)", "")
    product_description = soup.find_all("p")[3].text
    category = soup.find_all("a")[3].text
    review = soup.find("p", class_="star-rating")["class"][1]
    mapping = {"Four": 4, "One": 1, "Two": 2, "Three": 3, "Five": 5}
    review_rating = mapping[review]

    thumbnail_div = soup.find("div", class_="thumbnail")
    image_cover = thumbnail_div.find("img")["src"]
    image_url = image_cover.replace("../../", url)

    return {
        "upc": upc,
        "price_incl_tax": prices_including_taxes,
        "price_excl_tax": prices_excluding_taxes,
        "availability": number_available,
        "description": product_description,
        "category": category,
        "review_rating": review_rating,
        "image_url": image_url
    }

def scrape_pages_book_urls(url):
    all_books = []
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Scraping des livres sur la page actuelle
            books = soup.find_all('article', class_='product_pod')

            for book in books:
                title = book.find('h3').find('a')['title']
                price = book.find('p', class_='price_color').text
                availability = book.find('p', class_='instock availability').text.strip()
                book_data = {"titre": title, "prix": price, "Dispo": availability}
                all_books.append(book_data)

            # Trouver l'URL de la page suivante
            next_page = soup.find('li', class_='next')
            if next_page:
                next_page_url = next_page.find('a')['href']
                base_url = url.rsplit('/', 1)[0]
                url = base_url + '/' + next_page_url
            else:
                break
        else:
            print(f"Erreur {response.status_code}: Impossible de récupérer la page.")
            break

    return all_books

# Rattachement de scrape_total et traitement des catégories
livres_categories_links = scrape_total()

all_books = []
for scraping_category_link in livres_categories_links:
    all_books.extend(scrape_pages_book_urls(scraping_category_link))

# Sauvegarde des données dans un fichier CSV
with open('books_by_category.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['titre', 'prix', 'Dispo']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for book_data in all_books:
        writer.writerow(book_data)

