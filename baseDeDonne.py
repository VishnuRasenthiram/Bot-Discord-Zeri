import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL=os.getenv('DATABASE_URL')


def initDataBase():

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

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
            pseudo VARCHAR(128),
            tagline VARCHAR(64),
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
        INSERT INTO liste_player(pseudo,tagline,region,derniereGame)
        VALUES (%s, %s,%s,%s)
    """, (data['pseudo'], data['tagline'],data['region'],"Null"))
    conn.commit()
    cur.close()
    conn.close()

def delete_player_liste(data):
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("DELETE FROM liste_player WHERE pseudo = %s AND tagline =%s AND region=%s" , (data["pseudo"],data["tagline"],data["region"]))
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
        WHERE pseudo=%s and tagline=%s;
    """, (data["derniereGame"],data['pseudo'], data['tagline']))
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
