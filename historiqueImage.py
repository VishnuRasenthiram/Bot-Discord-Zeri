from PIL import Image, ImageDraw, ImageOps, ImageFont
import requests
from io import BytesIO
from riotwatcher import LolWatcher, ApiError
import os
from dotenv import load_dotenv
import urllib 
import json

load_dotenv()
lol_watcher = LolWatcher(os.getenv('RIOT_API'))
version = lol_watcher.data_dragon.versions_for_region("euw1")

def creeImageHistorique(puuid,region):
    histo= lol_watcher.match.matchlist_by_puuid(region,puuid)
    with Image.open(f"Image/currentGame.png") as imageFond:
        imageFond
    with open("dossierJson/input.json","r") as numPartie:
            data = json.load(numPartie)    
                
        
        
    list={}
    list2=[]
    wins=0
    
    numPartie=1
    for i in range(20):
    
        matchs=lol_watcher.match.by_id(region, histo[i])
        
        indiceJoueur=0
        for i in matchs['metadata']['participants']:
            if i==puuid:
                positionJoueur=indiceJoueur
            else :
                indiceJoueur+=1
                
        informationPartie=matchs["info"]["participants"][positionJoueur]
        creeBandeauStat(informationPartie)
    
        informationTypePartie=matchs["info"]["queueId"]
        
        
        for i in range (len(data)):
            if str(informationTypePartie).startswith("18"):
                informationTypePartie=18
            if data[i]['queueId']==informationTypePartie:     
                list2.append(data[i]["description"])

        nomChamp=informationPartie['championName']

        if informationTypePartie==18 :
            nomChamp=nomChamp.replace("Strawberry_","")
            
        kill=str(informationPartie["kills"])
        death=str(informationPartie["deaths"])
        assist=str(informationPartie["assists"])
        
            
           
        if informationPartie['win']:
            list[numPartie]=[nomChamp,f'- {kill}/{death}/{assist} <:V:1119547366404526180>']
            wins+=1             
        else:
            list[numPartie]=[nomChamp,f'- {kill}/{death}/{assist}  <:D:1119546988795539497> ']
        numPartie+=1

        
    
    wr=(wins/20)*100
        
    chainePartie=""
    chaineTypePartie=""
    for key ,value in list.items():
        chainePartie += str(key)+": "+' '.join(str(elem) for elem in value)+"\n"         
    for key  in list2:
        chaineTypePartie += str(key)+"\n"    
    chaineTypePartie =chaineTypePartie.replace('5v5',' ').replace('Pick',' ').replace('games',' ')

def creeBandeauItem(informationPartie):
    
    total_width = 448
    combined_image = Image.new('RGB', (total_width, 64), color='black')
    for i in range (7):
        slot = create_empty_slot()
        if informationPartie[f'item{i}'] !=0:
            slot = add_item_to_slot(slot,f'https://ddragon.leagueoflegends.com/cdn/14.16.1/img/item/{informationPartie[f'item{i}']}.png')
        combined_image.paste(slot, (i * 64, 0))
            
    return combined_image

    
    
def create_empty_slot():
    # Créer l'image de base (slot vide)
    slot_image = Image.new('RGB', (64, 64), color="#1E282D")
    draw = ImageDraw.Draw(slot_image)

    # Définir les couleurs
    gold_color = "#C89B3C"  # Couleur dorée
    dark_border_color = "#1E282D"  # Couleur foncée pour le bord

    # Dessiner le cadre
    draw.rectangle([0, 0, 63, 63], outline=dark_border_color, width=1)
    draw.rectangle([2, 2, 61, 61], outline=gold_color, width=2)

    return slot_image
def add_item_to_slot(slot_image, item_image_path):
    # Charger l'image de l'item
    
    response = requests.get(item_image_path)
    img_data = response.content
    item_image= Image.open(BytesIO(img_data))
    item_image=item_image.convert('RGBA')

    # Redimensionner l'image pour qu'elle tienne à l'intérieur du slot (par exemple, 48x48 pixels)
    item_image = item_image.resize((48, 48))

    # Calculer la position pour centrer l'image dans le slot
    pos_x = (64 - 48) // 2
    pos_y = (64 - 48) // 2

    # Coller l'image à l'intérieur du slot vide
    slot_image.paste(item_image, (pos_x, pos_y), item_image)

    return slot_image


def creeBandeauStat(informationPartie):
    # Définir les dimensions du bandeau
    bandeauWidth, bandeauHeight = 900, 200
    
    # Créer une image de base pour le bandeau
    bandeau = Image.new('RGB', (bandeauWidth, bandeauHeight), color="#3C3C41")
    
    # Créer l'image de l'item à coller sur le bandeau
    bandeau_item = creeBandeauItem(informationPartie)
    
    # Vérifier la taille de l'image du bandeau_item
  
    
    # Coller l'image de l'item sur le bandeau à la position (10, 10)
    bandeau.paste(bandeau_item, (10, 10))
    
    # Sauvegarder l'image résultante
    bandeau.save("test.png")
    print("Image sauvegardée sous 'test.png'.")

creeImageHistorique("zRjDt32ZFw-wWT-8-g4o6XW24plv8zPqnyVu35z08dcioqxNMI047LShzsoIIKxzWqnkuJd_A7Rowg","euw1")
