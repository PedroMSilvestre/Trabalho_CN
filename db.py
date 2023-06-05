import mysql.connector
from tools import currentDateAndHour

# Nome da BD
DB_NAME = "dbTrabalhoCN"

# Tabela dos utilizadores
TABLE_USERS = "tUsers"

# Statement para criar a BD
CREATE_DB_STATEMENT = "CREATE DATABASE IF NOT EXISTS %s"

# Statement para criar a tabela dos utilizadores
CREATE_TABLE_STATEMENT = "CREATE table if not exists `%s`.`%s` (\
    id int not null auto_increment,\
    username varchar(50),\
    password varchar(50),\
    confirmPassword varchar(50),\
    creationDate datetime not null,\
    primary key (id)\
);"

# Statement para inserir um registo na tabela dos utilizadores
INSERT_RECORD_STATEMENT = "INSERT INTO `%s`.`%s` VALUES (\
    null,\
    '%s',\
    '%s',\
    '%s',\
    '%s'\
);"

# Função para criar a BD
def getCreateDBSt(pDBName:str=DB_NAME)->str:
    st:str=CREATE_DB_STATEMENT%(pDBName)
    return st
#def getCreateDBSt

# Função para criar a tabela dos utilizadores
def getCreateTableSt(pDBName:str=DB_NAME, pTableName:str=TABLE_USERS
)->str:
    st:str=CREATE_TABLE_STATEMENT%(pDBName, pTableName)
    return st
#def getCreateTableSt

# Função para inserir um registo na tabela dos utilizadores
def getInsertUserSt(
    pUsername:str,
    pPassword:str,
    pConfirmPassword:str,
    pDBName:str=DB_NAME,
    pTableName:str=TABLE_USERS,
)->str:
    strNow = currentDateAndHour()
    st:str=INSERT_RECORD_STATEMENT%(
        pDBName,
        pTableName,
        pUsername,
        pPassword,
        pConfirmPassword,
        strNow
    )
    return st
#def getInsertUrlSt

# Função para mostrar o nome da BD
def getDBName():
    dbName = DB_NAME
    return dbName
# def getDBName
