import os
import time
import mysql.connector
from mysql.connector import pooling, errors
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PORT = int(os.getenv("DB_PORT"))
DB_PASSWORD = os.getenv("DB_PASSWORD")

_pool = None


def init_pool(pool_size=5):
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="zeri_pool",
            pool_size=pool_size,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            connect_timeout=10,
            autocommit=True
        )


def get_connection(retries=3, delay=2):
    """Retourne une connexion opérationnelle (ping + retries)."""
    init_pool()
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            conn = _pool.get_connection()
            try:
                conn.ping(reconnect=True, attempts=3, delay=1)
            except Exception:
                conn.close()
                raise
            return conn
        except (errors.InterfaceError, errors.OperationalError, Exception) as e:
            last_exc = e
            print(f"[DB] tentative {attempt} échouée: {e}")
            time.sleep(delay)
    raise last_exc


def execute_query(query, params=None, fetchone=False, fetchall=False):
    """Helper safe: gère connexion, curseur, retries."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(buffered=True)
        cur.execute(query, params or ())
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()
        if not conn.autocommit:
            conn.commit()
        return None
    except Exception as e:
        print(f"[DB] execute_query erreur: {e}")
        raise
    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        try:
            if conn and conn.is_connected():
                conn.close()
        except Exception:
            pass


def initDataBase():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_data (
            id BIGINT PRIMARY KEY,
            puuid VARCHAR(128),
            icon TEXT,
            region VARCHAR(10),
            statut INT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_player_data(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO player_data (id, puuid, icon, region, statut)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE id=id
    """, (data['id'], data['puuid'], data['icon'], data['region'], data['statut']))
    conn.commit()
    cur.close()
    conn.close()


def get_player_data(player_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM player_data WHERE id = %s", (player_id,))
    player = cur.fetchone()
    cur.close()
    conn.close()
    return player


def update_player_statut(player_id, new_statut):
    conn = get_connection()
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM player_data WHERE id = %s", (player_id,))
    conn.commit()
    etat = 1 if cur.rowcount > 0 else 0
    cur.close()
    conn.close()
    return etat


def initTableListePlayer():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS liste_player (
            id INT AUTO_INCREMENT PRIMARY KEY,
            puuid VARCHAR(128),
            region VARCHAR(64),
            derniereGame VARCHAR(128),
            listeChannel VARCHAR(255) DEFAULT '[]',
            messages_id VARCHAR(256) DEFAULT '[]',
            game_fini BIGINT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_player_liste(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO liste_player(puuid, region, derniereGame, listeChannel)
        VALUES (%s, %s, %s, %s)
    """, (data['puuid'], data['region'], "0", data['listeChannel']))
    conn.commit()
    cur.close()
    conn.close()


def delete_player_liste(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM liste_player WHERE puuid = %s AND region = %s",
                (data["puuid"], data["region"]))
    conn.commit()
    etat = 1 if cur.rowcount > 0 else 0
    cur.close()
    conn.close()
    return etat


def update_derniereGame(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE liste_player 
        SET derniereGame=%s, messages_id=%s, game_fini=%s
        WHERE puuid=%s
    """, (data["derniereGame"], data["messages_id"], data['game_fini'], data["puuid"]))
    conn.commit()
    cur.close()
    conn.close()


def get_player_liste():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM liste_player")
    player_liste = cur.fetchall()
    cur.close()
    conn.close()
    return player_liste


def clear_player_liste():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM liste_player")
    conn.commit()
    cur.close()
    conn.close()


def drop_player_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS liste_player")
    conn.commit()
    cur.close()
    conn.close()


def alterTableListePlayer():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "ALTER TABLE liste_player ADD COLUMN listeChannel VARCHAR(255) DEFAULT '[]'")
    conn.commit()
    cur.close()
    conn.close()


def get_player_listeChannel(puuid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT listeChannel FROM liste_player WHERE puuid = %s", (puuid,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return ast.literal_eval(result[0]) if result else []


def update_player_listeChannel(puuid, listeChannel):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE liste_player 
        SET listeChannel = %s
        WHERE puuid = %s
    """, (str(listeChannel), puuid))
    conn.commit()
    cur.close()
    conn.close()


def init_listChannelSuivit_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS liste_channel_suivit (
            id VARCHAR(255) PRIMARY KEY,
            nom VARCHAR(255)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_listChannelSuivit(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO liste_channel_suivit (id, nom)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE id=id
    """, (data['id'], data['nom']))
    conn.commit()
    cur.close()
    conn.close()


def delete_listChannelSuivit(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM liste_channel_suivit WHERE id = %s", (id,))
    conn.commit()
    etat = 1 if cur.rowcount > 0 else 0
    cur.close()
    conn.close()
    return etat


def get_listChannelSuivit():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM liste_channel_suivit")
    liste_channel = cur.fetchall()
    cur.close()
    conn.close()
    return liste_channel


def init_user_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id BIGINT PRIMARY KEY,
            money INT,
            level INT,
            xp INT,
            daily INT, 
            nb_daily INT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_user_profile(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_profile (id, money, level, xp, daily, nb_daily)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE id=id
    """, (data['id'], data['money'], data['level'], data['xp'], data['daily'], data['nb_daily']))
    conn.commit()
    cur.close()
    conn.close()


def get_user_liste():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_profile")
    player_liste = cur.fetchall()
    cur.close()
    conn.close()
    return player_liste


def get_user_profile(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_profile WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def update_user_profile(user_id, new_money, new_level, new_xp, new_daily, new_nb_daily):
    conn = get_connection()
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE liste_player SET listeChannel = '[]'")
    conn.commit()
    cur.close()
    conn.close()


# Ladder functions
def init_listChannelLadder_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS liste_channel_ladder (
            id VARCHAR(255) PRIMARY KEY,
            nom VARCHAR(255),
            messageId VARCHAR(255)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_listChannelLadder(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO liste_channel_ladder (id, nom, messageId)
        VALUES (%s, %s, '0')
        ON DUPLICATE KEY UPDATE id=id
    """, (data['id'], data['nom']))
    conn.commit()
    cur.close()
    conn.close()


def delete_listChannelLadder(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM liste_channel_ladder WHERE id = %s", (id,))
    conn.commit()
    etat = 1 if cur.rowcount > 0 else 0
    cur.close()
    conn.close()
    return etat


def get_listChannelLadder():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM liste_channel_ladder")
    liste_channel = cur.fetchall()
    cur.close()
    conn.close()
    return liste_channel


def update_messageId_listChannelLadder(id, messageId):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE liste_channel_ladder
        SET messageId = %s
        WHERE id = %s
    """, (str(messageId), str(id)))
    conn.commit()
    cur.close()
    conn.close()


def get_messageId_listChannelLadder(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT messageId FROM liste_channel_ladder WHERE id = %s", (str(id),))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None


def init_ladder_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ladder (
            puuid VARCHAR(128),
            channel VARCHAR(255),
            region VARCHAR(64),
            PRIMARY KEY (puuid, channel),
            FOREIGN KEY (channel) REFERENCES liste_channel_ladder(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_ladder(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ladder (puuid, channel, region)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE puuid=puuid
    """, (data['puuid'], data['channel'], data['region']))
    conn.commit()
    cur.close()
    conn.close()


def get_ladder_liste():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ladder")
    player_liste = cur.fetchall()
    cur.close()
    conn.close()
    return player_liste


def get_ladder_profile(channel):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ladder WHERE channel = %s", (str(channel),))
    user = cur.fetchall()
    cur.close()
    conn.close()
    return user


def delete_ladder(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ladder WHERE puuid = %s AND channel = %s AND region = %s",
                (data["puuid"], data["channel"], data["region"]))
    conn.commit()
    etat = 1 if cur.rowcount > 0 else 0
    cur.close()
    conn.close()
    return etat


def drop_table_liste_channel_ladder():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS liste_channel_ladder CASCADE")
    conn.commit()
    cur.close()
    conn.close()


def drop_table_ladder():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS ladder CASCADE")
    conn.commit()
    cur.close()
    conn.close()


def get_liste_channel_ladder_joueur(puuid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT channel FROM ladder WHERE puuid = %s", (puuid,))
    liste_channel = cur.fetchall()
    cur.close()
    conn.close()
    return liste_channel


def init_temp_voice_creators_table():
    """Initialise la table qui stocke les IDs des canaux permettant la création de salons vocaux temporaires"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS temp_voice_creators (
            channel_id VARCHAR(255) PRIMARY KEY
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    cur.close()
    conn.close()


def add_temp_voice_creator(channel_id):
    """Ajoute l'ID d'un canal créateur de salons vocaux temporaires"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO temp_voice_creators (channel_id)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE channel_id=channel_id
    """, (str(channel_id),))
    conn.commit()
    cur.close()
    conn.close()
    return True


def remove_temp_voice_creator(channel_id):
    """Supprime l'ID d'un canal créateur de salons vocaux temporaires"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM temp_voice_creators WHERE channel_id = %s", (str(channel_id),))
    conn.commit()
    result = cur.rowcount > 0
    cur.close()
    conn.close()
    return result


def get_all_temp_voice_creators():
    """Récupère tous les IDs des canaux créateurs de salons vocaux temporaires"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT channel_id FROM temp_voice_creators")
    creators = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return creators


def is_temp_voice_creator(channel_id):
    """Vérifie si un canal est un créateur de salon vocal temporaire"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM temp_voice_creators WHERE channel_id = %s", (str(channel_id),))
    result = cur.fetchone() is not None
    cur.close()
    conn.close()
    return result
