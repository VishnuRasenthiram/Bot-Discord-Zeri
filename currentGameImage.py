from PIL import Image, ImageDraw, ImageOps, ImageFont
import requests
from io import BytesIO
from riotwatcher import LolWatcher, ApiError
import os
from dotenv import load_dotenv
import urllib 
import json
import asyncio
from historiqueImage import add_item_to_slot
load_dotenv()
lol_watcher = LolWatcher(os.getenv('RIOT_API'))
version = lol_watcher.data_dragon.versions_for_region("euw1")
font = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=25)
with open("3.json","r") as f:
    summonnerData= json.load(f)

async def creerImageCG(cg,regionId,region):
    
    size = 1920, 1080
    sizeChamp= 308,400
    link =f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/data/fr_FR/champion.json'

    f = urllib.request.urlopen(link)
    myfile = f.read()
    data=json.loads(myfile)
    champ = data["data"]  
    with Image.open(f"Image/currentGame.png") as imageFond:
        imageFond = imageFond.resize(size)
    posB=0
    posR=0
    for i in range ( len(cg["participants"])) :
        puuid=cg["participants"][i]["puuid"]
        spellid1=get_summoner_name_by_key(summonnerData,cg["participants"][i]["spell1Id"])
        spellid2=get_summoner_name_by_key(summonnerData,cg["participants"][i]["spell2Id"])
        spells= [spellid1,spellid2]
        pseudo=lol_watcher.accountV1.by_puuid(regionId,puuid)["gameName"]
        invocateur= lol_watcher.league.by_summoner(region,cg["participants"][i]["summonerId"])
        rank="Unranked"
        div=" "
        lp=" "
        
            
        for cle,valeur in champ.items():
            if int(valeur['key'])==int(cg["participants"][i]['championId']):
                champion=cle

        for j in range(len(invocateur)):
            if invocateur[j]['queueType']=="RANKED_SOLO_5x5":
                rank=invocateur[j]["tier"]
                div=invocateur[j]["rank"]
                lp=invocateur[j]["leaguePoints"]
                
        if cg["participants"][i]["teamId"]==100:
            localisation= ((sizeChamp[0]*(posB)+65*(posB+1)) ,(60)) 
            posB+=1          
        else :
            localisation= ((sizeChamp[0]*(posR)+65*(posR+1)) ,(570))  
            posR+=1
      
        imageFond.paste(getChampImage(puuid,champion,pseudo,rank,div,lp,spells,region),localisation)
        
                        
    
    return imageFond
    
def get_summoner_name_by_key(summoners_dict, key):
    for summoner_id, summoner_data in summoners_dict["data"].items():
        
        if (int)(summoner_data['key'])==key:
            return summoner_id
            
  

    
def getChampImage(puuid,Champ,pseudo,rank,div,lp,spell,region):
    versions = lol_watcher.data_dragon.versions_for_region(region)
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{Champ}_0.jpg"
    

    sizeChamp= 300,450
    response = requests.get(url)
    img_data = response.content
 
    imgChamp = Image.open(BytesIO(img_data))
    imgChamp=imgChamp.resize(sizeChamp)

    finalImage= imgChamp.convert('RGBA')
    rankIcon=getRankIcon(puuid,rank,region)
    finalImage.paste(rankIcon, (70, 190), rankIcon)

    imageSumm=Image.open(f"Image/empty_summ_slot.png")
    combined_image = Image.new('RGB', (128, 64), color='black')
    for summ in range(2): 
        icone = f'https://ddragon.leagueoflegends.com/cdn/{versions["v"]}/img/spell/{spell[summ]}.png'
        slot= add_item_to_slot(imageSumm,icone)
        combined_image.paste(slot, (summ * 64, 0))
        
           
    combined_image =combined_image.resize((96,48))
    finalImage.paste(combined_image,(5,400))
    imageFond= ImageDraw.Draw(finalImage)


    rankdivlp= f'{rank} {div} {lp} lp'

    text_bbox = imageFond.textbbox((0, 0), pseudo, font=font)
    text_width = text_bbox[2] - text_bbox[0]


    rank_bbox= imageFond.textbbox((0,0),rankdivlp,font)
    rank_width=rank_bbox[2]-rank_bbox[0]
    rank_height= rank_bbox[3]-rank_bbox[1]

    text_position = (((sizeChamp[0] - text_width) // 2), 5)
    divLp_position=(((sizeChamp[0] - rank_width) // 2), (sizeChamp[1] - rank_height) // 2 + 150)
    
    text_color = "#F0E6D2"
    border_color = "#010A13"
    border_width = 1 
            
    
    for x_offset, y_offset in [(-border_width, 0), (border_width, 0), (0, -border_width), (0, border_width)]:
        imageFond.text((text_position[0] + x_offset, text_position[1] + y_offset), pseudo, font=font, fill=border_color)
        imageFond.text((divLp_position[0] + x_offset, divLp_position[1] + y_offset), rankdivlp, font=font, fill=border_color)
    
    
    imageFond.text(text_position,f"{pseudo}",font=font,fill=text_color)
    imageFond.text(divLp_position,rankdivlp,font=font,fill=text_color)
  
    return finalImage.resize(sizeChamp)     


def getRankIcon(puuid,rank,region):

    sizeEmblem= 160,200
    sizeIcone=50,50
    imgRank=Image.open(f'Image/RANKICON/Wings/{rank}.png')

    versions = lol_watcher.data_dragon.versions_for_region(region)
    Account = lol_watcher.summoner.by_puuid(region, puuid)
    icone = f'http://ddragon.leagueoflegends.com/cdn/{versions["v"]}/img/profileicon/{Account["profileIconId"]}.png'
    
    response = requests.get(icone)
    imageIcon= BytesIO(response.content)
    mask = Image.new('L', sizeIcone, 0)
    masque = ImageDraw.Draw(mask)
    masque.ellipse((0, 0, sizeIcone[0], sizeIcone[1]), fill=255)

    imgIcone=Image.open(imageIcon)

    imgIcone=imgIcone.resize(sizeIcone)
    iconeFinal =imgRank.resize(sizeEmblem)

    output = ImageOps.fit(imgIcone,sizeIcone , centering=(0.5, 0.5))
    output.putalpha(mask)
    iconeFinal.paste(output,[54,94],mask=output)
    iconeFinal.convert('RGBA')
    
    return iconeFinal

