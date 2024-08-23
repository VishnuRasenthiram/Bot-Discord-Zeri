from PIL import Image, ImageDraw, ImageOps, ImageFont
import requests
from io import BytesIO
from riotwatcher import LolWatcher, ApiError
import os
from dotenv import load_dotenv
import urllib 
import json
from math import *

load_dotenv()
lol_watcher = LolWatcher(os.getenv('RIOT_API'))
version = lol_watcher.data_dragon.versions_for_region("euw1")
font = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=25)

bandeauWidth, bandeauHeight = 900, 200
masque = Image.new('L', (bandeauWidth, bandeauHeight), 0)
draw = ImageDraw.Draw(masque)
radius = 50  

draw.rounded_rectangle([(0, 0), (bandeauWidth, bandeauHeight)], radius=radius, fill=255)

def creeImageHistorique(puuid,region):
    histo= lol_watcher.match.matchlist_by_puuid(region,puuid)
    imageFond= Image.open(f"Image/historiqueImage.png")

    for indicePartie in range(10):
    
        matchs=lol_watcher.match.by_id(region, histo[indicePartie])
        
        indiceJoueur=0
        for i in matchs['metadata']['participants']:
            if i==puuid:
                positionJoueur=indiceJoueur
                break
            else :
                indiceJoueur+=1               
        informationPartie=matchs["info"]["participants"][positionJoueur]
        informationTypePartie=matchs["info"]["queueId"]
        bandeau=creeBandeauStat(informationPartie,informationTypePartie).resize((2000,400))
        imageFond.paste(bandeau,(0,indicePartie*400),bandeau)

    return imageFond
    

def creeBandeauItem(informationPartie):
    
    total_width = 448
    combined_image = Image.new('RGB', (total_width, 64), color='black')
    slot = Image.open("Image/empty_slot.png")
    for i in range (7):
        if informationPartie[f'item{i}'] !=0:
            slot = add_item_to_slot(slot,f'https://ddragon.leagueoflegends.com/cdn/14.16.1/img/item/{informationPartie[f'item{i}']}.png')
            combined_image.paste(slot, (i * 64, 0))
            
    return combined_image

def getTypePartieFromCode(informationTypePartie):
    with open("dossierJson/input.json","r") as numPartie:
            data = json.load(numPartie)  
    for i in range (len(data)):
        if str(informationTypePartie).startswith("18"):
            informationTypePartie=18
        if data[i]['queueId']==informationTypePartie:     
            return data[i]["description"] 
    
def create_empty_slot():
    
    slot_image = Image.new('RGB', (64, 64), color="#1E282D")
    draw = ImageDraw.Draw(slot_image)

   
    gold_color = "#C89B3C"  
    dark_border_color = "#1E282D"  


    draw.rectangle([0, 0, 63, 63], outline=dark_border_color, width=1)
    draw.rectangle([2, 2, 61, 61], outline=gold_color, width=2)

    return slot_image
def add_item_to_slot(slot_image, item_image_path):

    
    response = requests.get(item_image_path)
    img_data = response.content
    item_image= Image.open(BytesIO(img_data)).convert('RGBA')

    item_image = item_image.resize((48, 48))

    pos_x = 8
    pos_y = 8

    slot_image.paste(item_image, (pos_x, pos_y), item_image)

    return slot_image



def getChampIcon(informationPartie):
    champ_image_path=f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/img/champion/{informationPartie['championName']}.png'
    response = requests.get(champ_image_path)
    img_data = response.content
    champ_image= Image.open(BytesIO(img_data)).convert('RGBA')

    return champ_image

def creeTemplateStats():

    imageGold=Image.open('Image/gold.png').resize((50,50)).convert('RGBA')
    imageCs=Image.open('Image/minion.png').resize((50,50)).convert('RGBA')
    imageDamage=Image.open('Image/damage.png').resize((50,45)).convert('RGBA')
    imageVision=Image.open('Image/vision.png').resize((50,40)).convert('RGBA')

    statsBand=Image.new('RGBA', (220, 120), color="#3C3C41")

    draw= ImageDraw.Draw(statsBand)
    draw.rectangle([0, 0, 219, 119], outline="#C89B3C", width=2)

    statsBand.paste(imageCs,(10,10),imageCs)
    statsBand.paste(imageGold,(10,60),imageGold)
    statsBand.paste(imageDamage,(110,12),imageDamage)
    statsBand.paste(imageVision,(110,65),imageVision)

    statsBand.save("Image/statsBand.png")

def getStats(informationPartie):

    gold=str(informationPartie["goldEarned"])
    damage=str(informationPartie["totalDamageDealtToChampions"])
    visionScore=str(informationPartie["visionScore"])
    cs=str(informationPartie["totalMinionsKilled"])

    statsBand=Image.open("Image/statsBand.png")

    draw= ImageDraw.Draw(statsBand)
    font = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=20)
    
    draw.text((50,20),cs,font=font)
    draw.text((50,70),gold,font=font)
    draw.text((150,20),damage,font=font)
    draw.text((150,70),visionScore,font=font)

    return statsBand

def creetemplateLTK():
    imageLevel=Image.open('Image/level.png').resize((40,40)).convert('RGBA')
    imageTemps=Image.open('Image/temps.png').resize((40,40)).convert('RGBA')
    statsBand=Image.new('RGBA', (400, 50), color="#3C3C41")

    draw= ImageDraw.Draw(statsBand)
    
    draw.rectangle([0, 0, 399, 49], outline="#C89B3C", width=2)
    statsBand.paste(imageLevel,(10,5),imageLevel)
    statsBand.paste(imageTemps,(250,5),imageTemps)

    statsBand.save("Image/LTKBand.png")

def getLevelTimerKda(informationPartie):
    champLevel=str(informationPartie['champLevel'])
    
    tempsMinute=floor(informationPartie["timePlayed"]/60)
    tempsSeconde=informationPartie["timePlayed"]-(tempsMinute*60)

    kill=str(informationPartie["kills"])
    death=str(informationPartie["deaths"])
    assist=str(informationPartie["assists"])
    LTKBand=Image.open("Image/LTKBand.png")
    
    font = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=20)
    draw= ImageDraw.Draw(LTKBand)

    draw.text((50,10),f"{champLevel}",font=font)
    draw.text((300,10),f"{tempsMinute}:{tempsSeconde}",font=font)
    draw.text((150,10),f"{kill}/{death}/{assist}",font=font)

    return LTKBand


def creeBandeauStat(informationPartie,informationTypePartie):
    typePartie=getTypePartieFromCode(informationTypePartie)

    champNom= informationPartie['championName']

    win=informationPartie['win']
 
    bandeau = Image.new('RGB', (bandeauWidth, bandeauHeight), color="#3C3C41")

    bandeau.paste(getStats(informationPartie),(670,50))
    bandeau.paste(getLevelTimerKda(informationPartie),(150,130))

    iconPos=positionToIcon(informationPartie).resize((74,64))
    bandeau.paste(iconPos,(600,70),iconPos)

    text=ImageDraw.Draw(bandeau)

    if win:
        text.text((500,10),"Victoire",font=font,fill="#0397AB")
    else:
        text.text((500,10),"Défaite",font=font,fill="#D12B3A")
    text.text((150,10),f"{champNom}  -  {typePartie}",font=font)

    bandeau_item = creeBandeauItem(informationPartie)
    
    bandeau.paste(bandeau_item, (150, 50))
    bandeau.paste(getChampIcon(informationPartie),(20,30))
    bandeau.putalpha(masque)
    
    
    return bandeau
    

def positionToIcon(informationPartie):
    lane = informationPartie["individualPosition"]

    match lane:
        case "TOP":
            imageLane=Image.open("Image/TOP.png")
        case "JUNGLE":
            imageLane=Image.open("Image/JUNGLE.png")
        case "MIDDLE":
            imageLane=Image.open("Image/MID.png")
        case "BOTTOM":
            imageLane=Image.open("Image/BOT.png")
        case "UTILITY":
            imageLane=Image.open("Image/SUPPORT.png")
        case _:
            imageLane=Image.open("Image/NOPOS.png")
    return imageLane.convert("RGBA")
    
