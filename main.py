from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///NFT_database.db'

db = SQLAlchemy()
db.init_app(app)

@app.route('/')
def home():
    return render_template('NFTSearch.html')

@app.route('/info', methods = ['POST', 'GET'])
def info():
    NFTaddress = request.form['NFTaddress']
    urlSolana = f'https://solana-gateway.moralis.io/nft/mainnet/{NFTaddress}/metadata'
    headers = {
        "accept": "application/json",
        "X-API-Key": "0h6h4XzjIoBFefiJpgJjtMGYbuB0UbGzGBhlDxzaEmPwET4c9B6SmO1HWWIR3tZt"
    }
    r = requests.get(urlSolana, headers = headers)

    dbFind = NFTdatabase.query.filter_by(mint = NFTaddress).first()
    if dbFind is not None:
        return render_template('NFTInfo.html', officialName= dbFind.name, icon=dbFind.icon, mint=dbFind.mint, name=dbFind.name,
                               symbol=dbFind.symbol, description=dbFind.description,
                               colName=dbFind.colName, colFamily=dbFind.colFamily)
    else:
        if r.status_code == 200:
            name = r.json()['name']
            metaplexUrl = r.json()['metaplex']['metadataUri']
            icon = requests.get(metaplexUrl).json()['image']
            mint = r.json()['mint']
            symbol = requests.get(metaplexUrl).json()['symbol']
            description = requests.get(metaplexUrl).json()['description']
            colName = ''
            colFamily = ''
            collection = []
            for i in requests.get(metaplexUrl).json():
                collection.append(i)
            checkCollection = False
            for i in collection:
                if i == 'collection':
                    checkCollection = True
                else:
                    checkCollection = False
            if checkCollection:
                colName = requests.get(metaplexUrl).json()['collection']['name']
                colFamily = requests.get(metaplexUrl).json()['collection']['family']
            addressToDB = ''
            if checkCollection:
                addressToDB = NFTdatabase(mint = mint, name = name, symbol = symbol, description = description, colName = colName, colFamily = colFamily, icon = icon)
            else:
                addressToDB = NFTdatabase(mint=mint, name=name, symbol=symbol, description=description, colName = 'None', colFamily = 'None', icon=icon)
            db.session.add(addressToDB)
            db.session.commit()
            if checkCollection:
                return render_template('NFTInfo.html', officialName=name, icon=icon, mint=mint, name=name,
                                       symbol=symbol, description=description,
                                       colName=colName, colFamily=colFamily)
            else:
                return render_template('NFTInfo.html', officialName=name, icon=icon, mint=mint, name=name,
                                       symbol=symbol, description=description, colName='None', colFamily='None')
        else:
            return render_template('NotFound.html')

class NFTdatabase(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mint = db.Column(db.String, unique = True, nullable = True)
    name = db.Column(db.String)
    symbol = db.Column(db.String)
    description = db.Column(db.String)
    colName = db.Column(db.String)
    colFamily = db.Column(db.String)
    icon = db.Column(db.String)

#with app.app_context():
  #  db.create_all()


if __name__ == '__main__':
    app.run(debug = True)