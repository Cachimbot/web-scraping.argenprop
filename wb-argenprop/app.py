import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from functions import get_property_details
import json

app = Flask(__name__)

@app.route('/argenprop', methods=['GET', 'POST'])
def argenprop_web_scraper():
    try:
        if request.method == 'POST':
            # Leer datos del cuerpo de la solicitud
            data = json.loads(request.data)
            pais = data.get("pais")
            limite = data.get("limite", None)
        else:  # GET
            # Leer datos desde los parámetros de la URL
            pais = request.args.get("pais")
            limite = request.args.get("limite", type=int)

        # Validaciones
        if not pais:
            return jsonify({"error": "El campo 'pais' es obligatorio"}), 400

        if limite is not None and limite <= 0:
            return jsonify({"error": "El campo 'limite' debe ser un número entero positivo."}), 400

        # Construcción de la URL para scraping
        url = f'https://www.argenprop.com/casas/alquiler/{pais}'
        session = requests.Session()
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        next_page = True
        casas = []
        page_count = 1

        while next_page:
            print(f"Scraping página {page_count}...")
            propiedades = soup.find_all('div', {'class': 'listing__item'})

            for propiedad in propiedades:
                url_pg_propiedad = propiedad.find('a', {'class': 'card'})['href']
                url_propiedad = f'https://www.argenprop.com{url_pg_propiedad}'
                details = get_property_details(url_propiedad)
                if details:
                    casas.append(details)

                # Verificar si se ha alcanzado el límite antes de pasar a la siguiente página
                if limite and len(casas) >= limite:
                    casas = casas[:limite]  # Recortar al límite
                    next_page = False  # Detener el scraping
                    break

            # Verificar si hay una página siguiente solo si no se ha alcanzado el límite
            if next_page:
                next_page_item = soup.find('li', {'class': 'pagination__page-next pagination__page'})
                if next_page_item:
                    next_page_link = next_page_item.find('a')['href']
                    url = f'https://www.argenprop.com{next_page_link}'
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_count += 1
                else:
                    next_page = False
            else:
                break

        # Si no se encontraron propiedades, devolver un mensaje claro
        if not casas:
            return jsonify({"error": "No se encontraron propiedades para el país indicado."}), 404

        return jsonify(casas)

    except json.JSONDecodeError:
        return jsonify({"error": "El cuerpo de la solicitud debe ser un JSON válido."}), 400
    except Exception as e:
        # Manejo genérico de errores
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
