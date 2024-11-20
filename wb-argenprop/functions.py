import requests
from bs4 import BeautifulSoup


def get_property_details(url_propiedad):
    response = requests.get(url_propiedad)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        item_owner_id = soup.find('p', {'class': 'property-code'})
        item_owner_id = item_owner_id.text.strip().split(":")[1].strip() if item_owner_id else None

        item_address = soup.find('p', {'class': 'location-container'})
        item_address_op = soup.find('h2', {'class': 'titlebar__title'})
        item_address = item_address.text.strip() if item_address else item_address_op.text.strip()

        item_price = soup.find('div', {'class': 'titlebar__price-mobile'}).find('p')
        item_price = item_price.text.strip() if item_price else None

        item_name = soup.find('p',{'class':'form-details-heading'})
        item_name = item_name.text.strip() if item_name else None


        item_features = soup.find('ul', {'class': 'property-features'})
        if item_features:
            features = {}
            for li in item_features.find_all('li'):
                feature_name = li.find('p').contents[0].strip()
                feature_value = li.find('strong').text.strip()
                features[feature_name] = feature_value
        else:
            print("")

        item_description = ', '.join([f"{key}{value}" for key, value in features.items()])

        return {
            'owner_id': item_owner_id,
            'address': item_address,
            'price': item_price,
            'description': item_description,
            'name': item_name
        }

    except Exception as e:
        print(f"Error procesando {url_propiedad}: {e}")
        return None
