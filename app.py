from flask import Flask, render_template, request, make_response
import requests
import xml.etree.ElementTree as ET
import threading
import webbrowser
import time
import os
from chave import API_KEY as key

app = Flask(__name__)

API_KEY = key

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = []
    if request.method == 'POST':
        termo = request.form['termo']
        url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
        params = {
            'query': termo,
            'key': API_KEY
        }

        resposta = requests.get(url, params=params)
        dados = resposta.json()

        for lugar in dados.get('results', []):
            place_id = lugar.get('place_id')
            nome = lugar.get('name')
            lat = lugar['geometry']['location']['lat']
            lng = lugar['geometry']['location']['lng']

            # Busca telefone do lugar via detalhes
            details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
            details_params = {
                'place_id': place_id,
                'fields': 'formatted_phone_number',
                'key': API_KEY
            }
            detalhes = requests.get(details_url, params=details_params).json()
            telefone = detalhes.get('result', {}).get('formatted_phone_number', 'Não informado')

            resultados.append({
                'nome': nome,
                'numero': telefone,
                'lat': lat,
                'lng': lng
            })

    return render_template('index.html', resultados=resultados, key=API_KEY)


@app.route('/baixar_xml', methods=['POST'])
def baixar_xml():
    dados = request.get_json()

    # Criar estrutura XML
    root = ET.Element('Leads')
    for item in dados:
        lead = ET.SubElement(root, 'Lead')
        ET.SubElement(lead, 'Nome').text = item['nome']
        ET.SubElement(lead, 'Numero').text = item['numero']

    xml_str = ET.tostring(root, encoding='utf-8', method='xml')
    response = make_response(xml_str)
    response.headers.set('Content-Type', 'application/xml')
    response.headers.set('Content-Disposition', 'attachment', filename='leads.xml')
    return response

@app.route('/sair', methods=['POST'])
def sair():
    os._exit(0)

def abrir_navegador():
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    threading.Thread(target=abrir_navegador).start()
    app.run(debug=False)
