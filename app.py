from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from libs.users import users
import requests
from libs.transformationData import *
from bs4 import BeautifulSoup


app = Flask(__name__)

# Configuração básica do JWT
app.config['JWT_SECRET_KEY'] = 'mykey'  # Troque para algo mais seguro em produção1
jwt = JWTManager(app)


@app.route('/',methods = ['POST'])
def index():
    return "GET INDEX, infomações"


@app.route('/login', methods=['POST'])
def login():

    loginInfo = request.authorization
    username = loginInfo['username']
    password = loginInfo['password']

    # Verifique se as credenciais são válidas (consulte seu banco de dados)
    
    for _ , value in users.items():

        if (username == value["username"]) and (password == value["password"]):
            access_token = create_access_token(username)
            return jsonify({'access_token': access_token}), 200
    
    return jsonify({'error': 'Credenciais inválidas'}), 401


@app.route('/producao', methods = ['GET'])
@jwt_required()
def producao():
    
    queryString = ""
    ano = request.args.get("ano", default=None)
    
    if ano is not None:
        queryString = f"ano={ano}"

    response = requests.get(f"http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02&{queryString}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('table')[4]
    
    df = pd.read_html(str(table))[0]  
    
    try:
        df = df[["Produto", "Quantidade (L.)"]]    
        
        for index, row in df.iterrows():
            value:str = row["Quantidade (L.)"]
            result = value.split(".")
            
            if result[0].isdigit():
                continue
            else:
                df.drop(index, inplace=True)
                
        jsonData = df.to_json(orient='records', lines=False)  # Use 'records' for a different format
        jsonData:dict = json.loads(jsonData)

    except Exception as ex:
        print(ex)    

    return jsonify(jsonData)


@app.route('/processamento', methods = ['GET'])
@jwt_required()
def processamento():

    jsonResult = {}
    queryString = ""
    ano = request.args.get("ano", default=None)
    
    if ano is not None:
        queryString = f"ano={ano}"

    links = {
        "Processamento_Viníferas ":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_03&{queryString}",
        "Processamento_Americanas":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_03&{queryString}",
        "Processamento_Uvas_De_Mesa":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_03&{queryString}",
        "Sem_Classificacao":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_03&{queryString}"
        }
    
    for key, link in links.items():
        
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all('table')[4]
        
        df = pd.read_html(str(table))[0]  
        
        try:
            df = df[["Cultivar", "Quantidade (Kg)"]]    
            
            for index, row in df.iterrows():
                value:str = row['Quantidade (Kg)']
                result = value.split(".")
                
                if result[0].isdigit():
                    continue
                else:
                    df.drop(index, inplace=True)
                    
            jsonData = df.to_json(orient='records', lines=False)  # Use 'records' for a different format
            jsonData:dict = json.loads(jsonData)
            
            jsonResult[key] = jsonData
 
        except Exception as ex:
            print(ex)    

    return jsonify(jsonResult)


@app.route('/comercializacao', methods = ['GET'])
@jwt_required()
def comercializacao():
    
    queryString = ""
    ano = request.args.get("ano", default=None)
    
    if ano is not None:
        queryString = f"ano={ano}"

    response = requests.get(f"http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04&{queryString}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('table')[4]
    
    df = pd.read_html(str(table))[0]  
    
    try:
        df = df[["Produto", "Quantidade (L.)"]]    
        
        for index, row in df.iterrows():
            value:str = row["Quantidade (L.)"]
            result = value.split(".")
            
            if result[0].isdigit() or (result[0]=="-"):
                continue
            else:
                df.drop(index, inplace=True)
                
        jsonData = df.to_json(orient='records', lines=False)  # Use 'records' for a different format
        jsonData:dict = json.loads(jsonData)

    except Exception as ex:
        print(ex)    

    return jsonify(jsonData)

@app.route('/importacao', methods = ['GET'])
@jwt_required()
def importacao():

    jsonResult = {}
    queryString = ""
    ano = request.args.get("ano", default=None)
    
    if ano is not None:
        queryString = f"ano={ano}"

    links = {
        "Vinhos_De_Mesa":f"http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05&{queryString}",
        "Espumantes":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_05&{queryString}",
        "Uvas_Frescas":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_05&{queryString}",
        "Uvas_Passas":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_05&{queryString}",
        "Suco_De_Uva":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_05&opcao=opt_05&{queryString}"
        
        }
    
    for key, link in links.items():
        
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all('table')[4]
        
        df = pd.read_html(str(table))[0]  
        
        try:
            df = df[["Países", "Quantidade (Kg)", "Valor (US$)"]]    
            
            for index, row in df.iterrows():
                value:str = row['Quantidade (Kg)']
                result = value.split(".")
                
                if result[0].isdigit() or (result[0]=="-"):
                    continue
                else:
                    df.drop(index, inplace=True)
                    
            jsonData = df.to_json(orient='records', lines=False)  # Use 'records' for a different format
            jsonData:dict = json.loads(jsonData)
            
            jsonResult[key] = jsonData
 
        except Exception as ex:
            print(ex)    

    return jsonify(jsonResult)


@app.route('/exportacao', methods = ['GET'])
@jwt_required()
def exportacao():

    jsonResult = {}
    queryString = ""
    ano = request.args.get("ano", default=None)
    
    if ano is not None:
        queryString = f"ano={ano}"

    links = {
        
        "Vinhos_De_Mesa":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_06&{queryString}",
        "Espumantes":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_06&{queryString}",
        "Uvas_Frescas":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_06&{queryString}",
        "Suco_De_Uva":f"http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_06&{queryString}",
        }
    
    for key, link in links.items():
        
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all('table')[4]
        
        df = pd.read_html(str(table))[0]  
        
        try:
            df = df[["Países", "Quantidade (Kg)", "Valor (US$)"]]    
            
            for index, row in df.iterrows():
                value:str = row['Quantidade (Kg)']
                result = value.split(".")
                
                if result[0].isdigit() or (result[0]=="-"):
                    continue
                else:
                    df.drop(index, inplace=True)
                    
            jsonData = df.to_json(orient='records', lines=False)  # Use 'records' for a different format
            jsonData:dict = json.loads(jsonData)
            
            jsonResult[key] = jsonData
 
        except Exception as ex:
            print(ex)    

    return jsonify(jsonResult)






app.run(host='0.0.0.0')