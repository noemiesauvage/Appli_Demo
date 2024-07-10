from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import requests
import logging


NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_API_KEY = "secret_3lW3pscXNMTLyVt8ucguorEg8Zrtld5rOo04jLOD43o"
DATABASE_ID = "d6e83d295d2c40548fdc0fa0241a24c4"
NOTION_QUERY_URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"


app = Flask(__name__)

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)

def add_to_notion(data):
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Rep1": {"rich_text": [{"text": {"content": data['en_tant_que']}}]},
            "Rep2": {"rich_text": [{"text": {"content": data['jaimerais']}}]},
            "Rep3": {"rich_text": [{"text": {"content": data['afin_de_parce_que']}}]},
            "Index": {"rich_text": [{"text": {"content": data['Index']}}]}
        }
    }

    response = requests.post(NOTION_API_URL, json=payload, headers=headers)
    
    logging.debug(f"Request payload: {payload}")
    logging.debug(f"Response status code: {response.status_code}")
    logging.debug(f"Response content: {response.content}")
    
    return response.status_code

def fetch_data_from_notion():
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    response = requests.post(NOTION_QUERY_URL, headers=headers)
    data = response.json()

    logging.debug(f"Response status code: {response.status_code}")
    logging.debug(f"Response content: {response.content}")

    rows = []
    for result in data['results']:
        properties = result['properties']
        en_tant_que = properties['Rep1']['rich_text'][0]['text']['content']
        jaimerais = properties['Rep2']['rich_text'][0]['text']['content']
        afin_de_parce_que = properties['Rep3']['rich_text'][0]['text']['content']
        Index = properties['Index']['rich_text'][0]['text']['content']
        rows.append([en_tant_que, jaimerais, afin_de_parce_que, Index])
    
    return rows


@app.route('/')
def index():
    return render_template('form.html', options_en_tant_que=[
        "Exploitants agricoles",
        "Artisans",
        "Commerçants et assimilés",
        "Chefs d'entreprise de 10 salariés ou plus",
        "Professions libérales et assimilées",
        "Cadres de la fonction publique",
        "Professeurs et professions scientifiques",
        "Professions de l'information, des arts et des spectacles",
        "Cadres administratifs et commerciaux d'entreprise",
        "Ingénieurs et cadres techniques d'entreprise",
        "Professions intermédiaires de l'enseignement, de la santé, de la fonction publique et assimilés",
        "Professions intermédiaires administratives et commerciales des entreprises",
        "Techniciens",
        "Contremaîtres, agents de maîtrise",
        "Employés civils et agents de service de la fonction publique",
        "Policiers et militaires",
        "Employés administratifs d'entreprise",
        "Employés de commerce",
        "Personnels des services directs aux particuliers",
        "Ouvriers qualifiés",
        "Ouvriers non qualifiés",
        "Conducteurs de véhicules et du personnel de transport",
        "Retraités",
        "Chômeurs",
        "Etudiants",
        "Autres personnes sans activité professionnelle"
])

@app.route('/save', methods=['POST'])
def save():
    en_tant_que = request.form['en_tant_que']
    jaimerais = request.form['jaimerais']
    afin_de_parce_que = request.form['afin_de_parce_que']

    # Récupérer les données depuis Notion
    rows = fetch_data_from_notion()


    # Convertir les données en DataFrame avec toutes les colonnes nécessaires
    df = pd.DataFrame(rows, columns=['Rep1', 'Rep2', 'Rep3', 'Index'])
    if df['Index'].empty:
        NewIndex = 1
    else:
        # Trouver le numéro le plus grand dans la colonne 'Index'
        max_index = max(df['Index'].astype('int32'))
        print(df['Index'].unique(),max_index)
        # Convertir max_index en entier si ce n'est pas déjà le cas
        max_index = int(max_index) if pd.notnull(max_index) else 0
        # Générer un nouveau numéro qui sera +1 grand
        NewIndex = max_index + 1
    
    Index = str(NewIndex)  # Convertir en chaîne de caractères

    # Envoyer les données à Notion
    notion_data = {
        'en_tant_que': en_tant_que,
        'jaimerais': jaimerais,
        'afin_de_parce_que': afin_de_parce_que,
        'Index': Index  # Assurez-vous que Index est une chaîne de caractères
    }
    status = add_to_notion(notion_data)

    if status == 200:
        return redirect(url_for('confirmation'))
    else:
        return 'Réponse enregistrée mais échec de l\'envoi à Notion.'

@app.route('/confirmation')
def confirmation():
    return """
    <html>
    <head>
    </head>
    <body>
        <p>Votre résultat a été enregistré. Vous pouvez reremplir le formulaire si vous le souhaitez.</p>
        <button onclick="window.location.href='/'">Retourner au formulaire</button>
    </body>
    </html>
    """


if __name__ == '__main__':
    app.run(debug=True)
