#bout de code de l'autre projet (scraping)

 
#extraction basique
Extraire le titre du livre
        title = soup.find('h1').text
        
        # Extraire le prix
        price = soup.find('p', class_='price_color').text
        
        # Extraire la disponibilité
        availability = soup.find('p', class_='instock availability').text.strip()
        