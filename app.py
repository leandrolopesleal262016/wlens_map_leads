
from flask import Flask, render_template, request, send_file, session, Response
import requests
import threading
import webbrowser
import time
import os
import io
from openpyxl import Workbook
from chave import API_KEY as key

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-me")

API_KEY = key

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = []
    if request.method == 'POST':
        termo = request.form.get('termo', '').strip()
        if termo:
            url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
            params = {'query': termo, 'key': API_KEY}
            resposta = requests.get(url, params=params, timeout=30)
            dados = resposta.json()

            for lugar in dados.get('results', []):
                place_id = lugar.get('place_id')
                nome = lugar.get('name')
                lat = lugar['geometry']['location']['lat']
                lng = lugar['geometry']['location']['lng']

                details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
                details_params = {
                    'place_id': place_id,
                    'fields': 'formatted_phone_number',
                    'key': API_KEY
                }
                detalhes = requests.get(details_url, params=details_params, timeout=30).json()
                telefone = detalhes.get('result', {}).get('formatted_phone_number', 'Não informado')

                resultados.append({'nome': nome, 'numero': telefone, 'lat': lat, 'lng': lng})

    session['resultados'] = resultados
    return render_template('index.html', resultados=resultados, key=API_KEY, download_label='Baixar excell')


def _criar_xlsx(linhas):
    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"
    ws.append(["Nome", "Numero"])
    for item in linhas or []:
        ws.append([item.get("nome", ""), item.get("numero", "")])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


@app.route('/baixar_xml', methods=['GET', 'POST'])
def baixar_xml():
    """Compatibilidade de rota: agora retorna XLSX."""
    linhas = None

    if request.method == 'POST':
        linhas = request.get_json(silent=True)
        if not isinstance(linhas, list):
            linhas = session.get('resultados', [])
    else:
        linhas = session.get('resultados', [])

    xlsx_io = _criar_xlsx(linhas)

    # Cria a resposta manualmente para garantir cabeçalhos
    resp = send_file(
        xlsx_io,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='leads.xlsx'
    )
    # Reforça cabeçalhos que alguns navegadores/resvers respeitam
    resp.headers['Content-Transfer-Encoding'] = 'binary'
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@app.route('/sair', methods=['POST'])
def sair():
    os._exit(0)


def abrir_navegador():
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    threading.Thread(target=abrir_navegador).start()
    app.run(debug=False)
