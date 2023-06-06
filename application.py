# application.py

from db import *
from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
import os.path
from amutil_cloud import AmAwsS3Helper

HTML_FILE_ELEMENT_NAME = "nameFiles" #notice the plural

# Nome do Bucket para o qual é feito o upload
DESTINATION_BUCKET_NAME = "proto-test1"

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "" #do NOT start nor end with /
app.config["AWS_FOLDER"] = ".aws"

# Chave secreta utilizada para proteger a sessão
app.secret_key = "Trabalho_CN"

# Para estabelecer uma conexão com a BD MySQL Local
"""
theConnection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
)
"""
# Para estabelecer uma conexão com a BD MySQL da AWS
theConnection = mysql.connector.connect(
    host="db-cn-trabalho.csnnr3s2quau.us-east-1.rds.amazonaws.com",
    user="root",
    password="passtrabalhocn",
)


if(theConnection):
    # Criação de um objeto "cursor" associado à conexão estabelecida com a BD MySQL
    cursor = theConnection.cursor()

    stCreateDB = getCreateDBSt()
    print("Will exec: ", stCreateDB)
    # Para executar uma instrução SQL na BD utilizando o objeto "cursor", neste caso é a instrução de criação da BD dbTrabalhoCN
    executeResultIsAlwaysNone = cursor.execute(stCreateDB)
    # Para confirmar as alterações feitas na BD
    theConnection.commit()
    print(executeResultIsAlwaysNone)

    stCreateTable = getCreateTableSt()
    print("Will exec: ", stCreateTable)
    # Para executar uma instrução SQL na BD utilizando o objeto "cursor", neste caso é a instrução de criação da tabela dos utilizadores
    executeResultIsAlwaysNone = cursor.execute(stCreateTable)
    # Para confirmar as alterações feitas na BD
    theConnection.commit()
    print(executeResultIsAlwaysNone)

    # Para fechar o objeto cursor e libertar os recursos associados a ele
    cursor.close()
#if

# Função para verificar na BD se existe um utilizador com um determinado nome e password
def checkUser(pUsername, pPassword):
    # Criação de um objeto "cursor" associado à conexão estabelecida com a BD MySQL
    cursor = theConnection.cursor()
    # Para definir o nome da BD da conexão estabelecida
    theConnection.database = getDBName()
    # Instrução que faz um select do username e da password à tabela dos utilizadores
    # onde o username tem o valor do parâmetro pUsername e onde a password tem o valor do parâmetro pPassword
    query = "SELECT username, password FROM tUsers WHERE username=%s and password=%s"
    # Para executar uma instrução SQL na BD utilizando o objeto "cursor", neste caso é a instrução de select da tabela dos utilizadores
    cursor.execute(query, (pUsername, pPassword))
    # Para obter todos os resultados do select anterior em forma de lista
    result = cursor.fetchall()
    print(type(result))
    if result:
        return True
    else:
        return False
# def checkUser

# Função para verificar na BD se existe um utilizador com um determinado nome
def checkUserRegister(pUsername):
    # Criação de um objeto "cursor" associado à conexão estabelecida com a BD MySQL
    cursor = theConnection.cursor()
    # Para definir o nome da BD da conexão estabelecida
    theConnection.database = getDBName()
    # Instrução que faz um select do username à tabela dos utilizadores onde o username tem o valor do parâmetro pUsername
    query = "SELECT username FROM tUsers WHERE username=%s"
    # Para executar uma instrução SQL na BD utilizando o objeto "cursor", neste caso é a instrução de select da tabela dos utilizadores
    cursor.execute(query, (pUsername,))
    # Para obter todos os resultados do select anterior em forma de lista
    result = cursor.fetchall()
    print(type(result))
    if result:
        return True
    else:
        return False

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Relacionado com a página inicial
@app.route("/")
def index():
    # É feito o render da página do login
    return render_template("login.html")
# def index

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Relacionado com a página para o utilizador fazer o registo
@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirmPassword = request.form["confirm_password"]

        print(checkUserRegister(username))
        # Para guardar o valor da função (True ou False)
        user = checkUserRegister(username)

        # Se existir ligação com a BD o utilizador é registado na mesma
        if(theConnection):
            # Criação de um objeto "cursor" associado à conexão estabelecida com a BD MySQL
            cursor = theConnection.cursor()
            # Caso o nome do utilizador não exista na BD e a password e a confirm password forem iguais
            if not user and password == confirmPassword:
                stInsert = getInsertUserSt(
                    pUsername= username,
                    pPassword= password,
                    pConfirmPassword= confirmPassword
                )
            else:
                # Caso o nome do utilizador já exista na BD
                if user:
                    # Mensagem para alertar que nome de utilizador já existe
                    warning_message = "Username already exists!!"
                    # É feito o render da página de registo e é passada a variável warning_message para a página
                    return render_template("register.html", warning_message=warning_message)
                # Caso a password e o confirm password não coincidam
                elif password != confirmPassword:
                    # Mensagem para alertar que a password e o confirm password não coincidem
                    warning_message = "Password and Confirm Password don't match!!"
                    # É feito o render da página de registo e é passada a variável warning_message para a página
                    return render_template("register.html", warning_message=warning_message)
            cursor.execute(stInsert)
            theConnection.commit()
            cursor.close()
            # theConnection.close()
        #if
        # Após ser registado é redirecionado para a página inicial
        return redirect(url_for("index"))
    else:
        # Caso o método não seja POST é feito o render outra vez da página de registo
        return render_template("register.html")
    #if
# def register

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Relacionado com a página para o utilizador fazer o login
@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        print(checkUser(username, password))

        # Caso o utilizador esteja presente na BD
        if checkUser(username, password):
            # Para armazenar uma variável de sessão chamada username com o valor username
            session["username"] = username
            # É feito o redirecionamento para a página home
            return redirect(url_for("home"))
        # Caso o utilizador não esteja presente na BD
        else:
            # return redirect(url_for("index"))
            # Mensagem para alertar que as credenciais são inválidas
            warning_message="Invalid Credentials!!"
            # É feito o render da  página de login e é passada a variável warning_message para a página
            return render_template("login.html", warning_message=warning_message)
        # É feito o redirecionamento para a página inicial
        return redirect(url_for("index"))
    # if
# def login

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Relacionado com o logout
@app.route("/logout")
def logout():
    # Para limpar a sessão
    session.clear()
    # É feito o redirecionamento para a página inicial
    return redirect(url_for("index"))
# def logout

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Relacionado com a página home
@app.route("/home", methods=["POST", "GET"])
def home():
    # Caso a sessão tenha a variável username
    if "username" in session:
        # É feito o render da página home e é passada a variável username para a página
        return render_template("home.html", username=session["username"])
    # Caso a sessão não tenha a variável username
    else:
        # É feito o redirecionamento para a página inicial
        return redirect(url_for("index"))
# def home

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Relacionado com a página Random Image Generator
@app.route("/imgen", methods=["POST","GET"])
def imgen():
    # É feito o render da página do Gerador de Imagens
    return render_template("imgen.html")
# def imgen

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Relacionado com o upload do(s) ficheiro(s) para o bucket
@app.route(rule="/upload", methods=['POST'])
def saveFilesToBucketAndFileSystem():
    strFeedback = ""

    # Inicializa a classe AmAwsS3Helper para obter as chaves de acesso e a região
    amS3 = AmAwsS3Helper(
        pStrCredentialsFilePath=app.config["AWS_FOLDER"] + "/credentials_for_iam_user_boto3_with_policy_AmazonS3FullAccess.txt",
        pStrConfigFilePath=app.config["AWS_FOLDER"] + "/config_for_region_eu_west2.txt"
    )

    # Recebe os ficheiros e envia para o bucket
    dictUploadResults =\
        amS3.saveFlaskUploadedPluralFilesToS3Bucket(
            pStrBucketName=DESTINATION_BUCKET_NAME,
            pHtmlFileElementName=HTML_FILE_ELEMENT_NAME,
            pStrCloudBucketDestinationPath=app.config["UPLOAD_FOLDER"]
        )

    # Verifica o estado de cada upload
    for strSecureFilename in dictUploadResults.keys():
        bSaveResult = dictUploadResults[strSecureFilename]

        if(bSaveResult):
            strFeedback += "SUCCESS: File {} uploaded to bucket.".format(strSecureFilename)
        else:
            strFeedback += "FAILURE: File {} NOT uploaded to bucket.".format(strSecureFilename)
        #else

        strFeedback+="\n"
    #for

    # É feito o render da página home, mas com os estados do upload
    return render_template('home.html', username=session["username"], strFeedback=strFeedback)
#def saveFilesToBucketAndFileSystem

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(
        debug=True
    )
# if