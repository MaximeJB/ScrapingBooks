import requests
import os
from bs4 import BeautifulSoup
import csv

url = "https://books.toscrape.com/"

def scrape_total() : 
    all_categories_links = []
    #récuperer la liste des urls des catégories
    response = requests.get(url)

  # Vérifier que la requête a réussi
    if response.status_code == 200:
        # Parse le contenu HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

    categories = soup.find("div", class_="side_categories" )
    links_categories = categories.find_all("a")

    for categories_title in links_categories :
        addition_url = url + categories_title["href"]
        print(addition_url)
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
    response = requests.get(image_url)
    if response.status_code == 200:
        # Sauvegarder l'image dans le dossier local
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Image sauvegardée sous : {image_path}")
    else:
        print(f"Erreur de téléchargement de l'image pour {book_title}")

# Pour chaque livre, on essaye de prendre les informations correspondantes, prix, titre, dispo, etc...
def scrape_book_infos(url):
    all_books = []

    # Envoyer une requête GET pour récupérer le contenu de la page
    response = requests.get(url)

    # Vérifier que la requête a réussi
    if response.status_code == 200:
        # Parse le contenu HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        print("execute la fonction")

        while soup.find('li', class_='next'):
            print("ca marche")
            # Extraire les données des livres sur la page actuelle
            books = soup.find_all('article', class_='product_pod')  # Recherche des livres
            for book in books:
                title = book.find('h3').find('a')['title']
                price = book.find('p', class_='price_color').text
                availability = book.find('p', class_='instock availability').text.strip()
                

                # Extraire l'URL de l'image
                """ image_tag = book.find('img')
                if image_tag:
                    image_url = "http://books.toscrape.com/" + image_tag['src']  # L'URL complète de l'image
                    if image_url.startswith("../"):
                            image_url = "http://books.toscrape.com/" + image_url[3:]
                    else:
                            image_url = "http://books.toscrape.com/" + image_url
                    download_image(image_url, title)  # Télécharger et sauvegarder l'image
                else:
                    print(f"Aucune image trouvée pour {title}") """

                # Créer le "paquet" d'infos pour ce livre
                book_data = {
                    "titre": title,
                    "prix": price,
                    "Dispo": availability
                }

                # Ajouter ce paquet à notre collection
                all_books.append(book_data)

            # Trouver l'URL de la page suivante
            base_url = "http://books.toscrape.com/catalogue/category/books/sequential-art_5/"
            next_page = soup.find('a', class_='next')
            if next_page:
                next_page_url = next_page.get('href')
                full_url = base_url + next_page_url  # Concaténer avec l'URL de base
                response = requests.get(full_url)
                soup = BeautifulSoup(response.content, 'html.parser')  # Mettre à jour `soup`
                print(next_page_url)
            if not next_page_url.startswith("http"):
                full_url = base_url.rstrip("/") + "/" + next_page_url
            else:
                break

    else:
        print(f"Erreur {response.status_code}: Impossible de récupérer la page.")

    return all_books


# Lancer le scraping
all_books = scrape_book_infos(url)

# Afficher les résultats
for book in all_books:
    print(f"Titre: {book['titre']}")
    print(f"Prix: {book['prix']}")
    print(f"Disponibilité: {book['Dispo']}")
    print("-" * 50)

# Ajouter les informations des dictionnaires, une ligne après l'autre dans le CSV
with open('names.csv', 'w', newline='') as csvfile:
    fieldnames = ['titre', 'prix', 'Dispo']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for book_data in all_books:
        writer.writerow(book_data)


livres_categories_links = scrape_total()
print(livres_categories_links)

for scraping_category_link in livres_categories_links :
    print(scraping_category_link)
    scrape_book_infos(scraping_category_link)

