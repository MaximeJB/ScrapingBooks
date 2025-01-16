import requests
from bs4 import BeautifulSoup

# URL de la page à scraper
url = "https://books.toscrape.com/catalogue/the-past-never-ends_942/index.html"

# Envoyer une requête GET pour récupérer le contenu de la page
response = requests.get(url)

# Vérifier que la requête a réussi
if response.status_code == 200:
    # Parse le contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extraire le titre du livre
    title = soup.find('h1').text
    
    # Extraire le prix
    price = soup.find('p', class_='price_color').text
    
    # Extraire la disponibilité
    availability = soup.find('p', class_='instock availability').text.strip()
    
    # Extraire la description (si disponible)
    description = soup.find('meta', attrs={'name': 'description'})
    if description:
        description = description['content'].strip()
    else:
        description = "Description non disponible."
    
    # Afficher les résultats
    print(f"Titre: {title}")
    print(f"Prix: {price}")
    print(f"Disponibilité: {availability}")
    print(f"Description: {description}")
else:
    print(f"Erreur {response.status_code}: Impossible de récupérer la page.")

    def get_book_urls(category_url):

    #Récupère toutes les URLs des livres pour une catégorie donnée.
    book_urls = []
    while category_url:
        response = requests.get(category_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver tous les liens vers les livres
        for link in soup.find_all('h3'):
            book_urls.append("https://books.toscrape.com/catalogue/" + link.a['href'])

        # Vérifier la présence du lien "next"
        next_page = soup.find('li', class_='next')
        if next_page:
            next_link = next_page.a['href']
            category_url = category_url.rsplit('/', 1)[0] + '/' + next_link
        else:
            category_url = None

    return book_urls


def main():
    # URL de la catégorie choisie
    category_url = "https://books.toscrape.com/catalogue/category/books/science_22/index.html"
    
    # Étape 1 : Récupérer toutes les URLs des livres
    print("Récupération des URLs des livres...")
    book_urls = get_book_urls(category_url)
    print(f"{len(book_urls)} livres trouvés.")
    
    # Étape 2 : Scraper les données des livres
    print("Scraping des données des livres...")
    books_data = []
    for book_url in book_urls:
        books_data.append(scrape_book_data(book_url))
    
    # Étape 3 : Enregistrer dans un fichier CSV
    print("Enregistrement des données dans un fichier CSV...")
    save_to_csv(books_data, "books_data.csv")
    print("Les données ont été enregistrées dans 'books_data.csv'.")

if __name__ == "__main__":
    main()

#