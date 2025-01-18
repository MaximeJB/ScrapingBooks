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
    
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Scraping des livres sur la page actuelle
            books = soup.find_all('article', class_='product_pod')
            print(f"Scraping {len(books)} livres sur {url}")
            
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
                # On extrait la base de l'URL jusqu'au dernier '/'
                base_url = url.rsplit('/', 1)[0]
                full_url = base_url + '/' + next_page_url
                print(f"URL de la page suivante: {full_url}")
                url = full_url
            else:
                break
        else:
            print(f"Erreur {response.status_code}: Impossible de récupérer la page.")
            break

    return all_books


# Lancer le scraping
all_books = scrape_book_infos(url)
print("je scrape")

# Afficher les résultats
for book in all_books:
    print(f"Titre: {book['titre']}")
    print(f"Prix: {book['prix']}")
    print(f"Disponibilité: {book['Dispo']}")
    print("-" * 50)
print("j'ajoute !")

# Ajouter les informations des dictionnaires, une ligne après l'autre dans le CSV
with open('names.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['titre', 'prix', 'Dispo']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for book_data in all_books:
        writer.writerow(book_data)



livres_categories_links = scrape_total()
print(livres_categories_links)

all_books = []
for scraping_category_link in livres_categories_links :
    print(scraping_category_link)
    all_books.extend(scrape_book_infos(scraping_category_link))

