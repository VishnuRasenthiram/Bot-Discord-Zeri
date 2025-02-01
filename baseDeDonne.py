import psycopg2
import os
from dotenv import load_dotenv
import ast
load_dotenv()
DATABASE_URL=os.getenv('DATABASE_URL')


def initDataBase():

    conn = psycopg2.connect(
        host="localhost",          # ou l'adresse IP du serveur si nécessaire
        database="zeribot",        # nom de la base de données
        user="postgres",           # utilisateur PostgreSQL
        port="5432"                # port par défaut de PostgreSQL
    )

    # Créer un curseur pour exécuter des commandes SQL
    cur = conn.cursor()

    # Création de la table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_data (
            id BIGINT PRIMARY KEY,
            puuid VARCHAR(128),
            icon TEXT,
            region VARCHAR(10),
            statut INT
        )
    """)

    # Valider les modifications
    conn.commit()

    # Fermer le curseur et la connexion
    cur.close()
    conn.close()


def insert_player_data(data):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO player_data (id, puuid, icon, region, statut)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (data['id'], data['puuid'], data['icon'], data['region'], data['statut']))
    conn.commit()
    cur.close()
    conn.close()


def get_player_data(player_id):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT * FROM player_data WHERE id = %s", (player_id,))
    player = cur.fetchone()
    cur.close()
    conn.close()
    return player

def update_player_statut(player_id, new_statut):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        UPDATE player_data
        SET statut = %s
        WHERE id = %s
    """, (new_statut, player_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_player_data(player_id):
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("DELETE FROM player_data WHERE id = %s", (player_id,))
    conn.commit()
    if cur.rowcount == 0:
            etat =0
    else:
            etat =1
    cur.close()
    conn.close()

    return etat





def initTableListePlayer():

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    # Créer un curseur pour exécuter des commandes SQL
    cur = conn.cursor()

    # Création de la table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS liste_player (
            id SERIAL PRIMARY KEY,
            puuid VARCHAR(128),
            region VARCHAR(64),
            derniereGame VARCHAR(128)
           
        )
    """)

    # Valider les modifications
    conn.commit()

    # Fermer le curseur et la connexion
    cur.close()
    conn.close()

def insert_player_liste(data):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO liste_player(puuid,region,derniereGame,listeChannel)
        VALUES (%s,%s,%s,%s)
    """, (data['puuid'],data['region'],"0",data['listeChannel']))
    conn.commit()
    cur.close()
    conn.close()

def delete_player_liste(data):
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("DELETE FROM liste_player WHERE puuid = %sAND region=%s" , (data["puuid"],data["region"]))
    conn.commit()
    if cur.rowcount == 0:
            etat =0
    else:
            etat =1
    cur.close()
    conn.close()

    return etat    

def update_derniereGame(data):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        UPDATE liste_player 
        SET derniereGame=%s
        WHERE puuid=%s ;
    """, (data["derniereGame"],data['puuid']))
    conn.commit()
    cur.close()
    conn.close()



def get_player_liste():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT * FROM liste_player ")
    player_liste = cur.fetchall()
    cur.close()
    conn.close()
    return player_liste

def clear_player_liste():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("DELETE FROM liste_player")
    conn.commit()
    cur.close()
    conn.close()
    
def drop_player_table():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS liste_player")
    conn.commit()
    cur.close()
    conn.close()

def alterTableListePlayer():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("ALTER TABLE liste_player ADD COLUMN listeChannel VARCHAR(255) DEFAULT '[]'")
    conn.commit()
    cur.close()
    conn.close()

def get_player_listeChannel(puuid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT listeChannel FROM liste_player WHERE puuid = %s", (puuid,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    return ast.literal_eval(result[0])

    
def update_player_listeChannel(puuid, listeChannel):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        UPDATE liste_player 
        SET listeChannel = %s
        WHERE puuid = %s ;
    """, (str(listeChannel), puuid,))
    conn.commit()
    cur.close()
    conn.close()

def init_listChannelSuivit_table():

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS liste_Channel_Suivit (
            id varchar(255) PRIMARY KEY,
            nom VARCHAR(255)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

def insert_listChannelSuivit(data):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO liste_Channel_Suivit (id, nom)
        VALUES (%s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (data['id'], data['nom']))
    conn.commit()
    cur.close()
    conn.close()
def delete_listChannelSuivit(id):    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("DELETE FROM liste_Channel_Suivit WHERE id = %s" , (id,))
    conn.commit()
    if cur.rowcount == 0:
            etat =0
    else:
            etat =1
    cur.close()
    conn.close()

    return etat

def get_listChannelSuivit():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT * FROM liste_Channel_Suivit ")
    liste_channel = cur.fetchall()
    cur.close()
    conn.close()
    return liste_channel

def init_user_table():

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id BIGINT PRIMARY KEY,
            money INT,
            level INT,
            xp INT,
            daily INT, 
            nb_daily INT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

def insert_user_profile(data):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_profile (id, money, level, xp, daily, nb_daily)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (data['id'], data['money'], data['level'], data['xp'], data['daily'], data['nb_daily']))
    conn.commit()
    cur.close()
    conn.close()    
def get_user_liste():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_profile ")
    player_liste = cur.fetchall()
    cur.close()
    conn.close()
    return player_liste
def get_user_profile(user_id):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_profile WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def update_user_profile(user_id, new_money, new_level, new_xp, new_daily, new_nb_daily):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        UPDATE user_profile
        SET money = %s, level = %s, xp = %s, daily = %s, nb_daily = %s
        WHERE id = %s
    """, (new_money, new_level, new_xp, new_daily, new_nb_daily, user_id))
    conn.commit()
    cur.close()
    conn.close()
    
def reset_listeChannel():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("UPDATE liste_player SET listeChannel = '[]'")
    conn.commit()
    cur.close()
    conn.close()


#ladder 
def init_listChannelLadder_table():

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS liste_Channel_Ladder (
            id VARCHAR(255) PRIMARY KEY,
            nom VARCHAR(255),
            messageId VARCHAR(255)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

def insert_listChannelLadder(data):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO liste_Channel_Ladder (id, nom, messageId)
        VALUES (%s, %s, 0)
        ON CONFLICT (id) DO NOTHING
    """, (data['id'], data['nom']))
    conn.commit()
    cur.close()
    conn.close()
    
def delete_listChannelLadder(id):    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("DELETE FROM liste_Channel_Ladder WHERE id = %s" , (id,))
    conn.commit()
    if cur.rowcount == 0:
            etat =0
    else:
            etat =1
    cur.close()
    conn.close()

    return etat

def get_listChannelLadder():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT * FROM liste_Channel_Ladder ")
    liste_channel = cur.fetchall()
    cur.close()
    conn.close()
    return liste_channel

def update_messageId_listChannelLadder(id, messageId):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        UPDATE liste_Channel_Ladder
        SET messageId = %s
        WHERE id = %s
    """, (str(messageId), str(id)))
    conn.commit()
    cur.close()
    conn.close()

def get_messageId_listChannelLadder(id):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT messageId FROM liste_Channel_Ladder WHERE id = %s", (str(id),))
    result = cur.fetchone()
    cur.close()
    conn.close()

    return result[0]




def init_ladder_table():
     
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    cur = conn.cursor()

    cur.execute("""
               CREATE TABLE IF NOT EXISTS ladder (
            puuid VARCHAR(128),
            channel varchar(255),
            region VARCHAR(64),
            PRIMARY KEY (puuid, channel),
            FOREIGN KEY (channel) REFERENCES liste_Channel_Ladder(id)
        );
        
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_ladder(data):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ladder (puuid, channel, region)
        VALUES (%s, %s, %s)
        ON CONFLICT (puuid, channel) DO NOTHING
    """, (data['puuid'], data['channel'], data['region']))
    conn.commit()
    cur.close()
    conn.close()

def get_ladder_liste():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT * FROM ladder ")
    player_liste = cur.fetchall()
    cur.close()
    conn.close()
    return player_liste

def get_ladder_profile(channel):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT * FROM ladder WHERE channel = %s", (str(channel),))
    user = cur.fetchall()
    cur.close()
    conn.close()
    return user

def delete_ladder(data):
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("DELETE FROM ladder WHERE puuid = %s AND channel = %s AND region = %s" , (data["puuid"],data["channel"],data["region"]))
    conn.commit()
    if cur.rowcount == 0:
            etat =0
    else:
            etat =1
    cur.close()
    conn.close()

    return etat


def drop_table_liste_channel_ladder():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    cur.execute("DROP TABLE IF EXISTS liste_Channel_Ladder CASCADE")
    
    conn.commit()
    cur.close()
    conn.close()


def drop_table_ladder():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    cur.execute("DROP TABLE IF EXISTS ladder CASCADE")
    
    conn.commit()
    cur.close()
    conn.close()

def get_liste_channel_ladder_joueur(puuid):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT channel FROM ladder WHERE puuid = %s", (puuid,))
    liste_channel = cur.fetchall()
    cur.close()
    conn.close()
    return liste_channel