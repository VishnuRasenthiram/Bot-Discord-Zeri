from PIL import Image, ImageDraw, ImageOps, ImageFont
import requests
from io import BytesIO
from riotwatcher import LolWatcher, ApiError
import os
from dotenv import load_dotenv
import urllib 
import json
from lol_commands.historique.historiqueImage import *

load_dotenv()
lol_watcher = LolWatcher(os.getenv('RIOT_API'))
version = lol_watcher.data_dragon.versions_for_region("euw1")
font = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=25)
fontLvl = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=20)
fontMode= ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=35)
dataRunes=requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version['v']}/data/en_US/runesReforged.json")
dataRunes=dataRunes.json()

with open("dossierJson/summoner_info.json","r") as f:
    summonnerData= json.load(f)

async def creerImageCG(cg,regionId,region):
    
    size = 1920, 1080
    sizeChamp= 308,400
    link =f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/data/fr_FR/champion.json'

    f = urllib.request.urlopen(link)
    myfile = f.read()
    data=json.loads(myfile)
    champ = data["data"]  
    with Image.open(f"Image/Zeri_CG.png") as imageFond:
        imageFond = imageFond.resize(size)
    posB=0
    posR=0
    for i in range ( len(cg["participants"])) :
        puuid=cg["participants"][i]["puuid"]
        mastery = lol_watcher.champion_mastery.by_puuid(region, puuid)
        spellid1=get_summoner_name_by_key(summonnerData,cg["participants"][i]["spell1Id"])
        spellid2=get_summoner_name_by_key(summonnerData,cg["participants"][i]["spell2Id"])
        spells= [spellid1,spellid2]
        runes={"primaryId":cg["participants"][i]["perks"]["perkStyle"], 
               "primaryRune":cg["participants"][i]["perks"]["perkIds"][0],
               "secondaryId":cg["participants"][i]["perks"]["perkSubStyle"]}
        modeDeJeu=cg["gameQueueConfigId"]

        pseudo=lol_watcher.accountV1.by_puuid(regionId,puuid)["gameName"]
        invocateur= lol_watcher.league.by_summoner(region,cg["participants"][i]["summonerId"])
        rank="Unranked"
        div=" "
        lp=" "
        masteryPTS=" "           
        for cle,valeur in champ.items():
            if int(valeur['key'])==int(cg["participants"][i]['championId']):
                champion=cle
                for idMastery in range(len(mastery)):
                    if int(mastery[idMastery]['championId'])==int(cg["participants"][i]['championId']):
                        masteryPTS="{:,.0f}".format(int(mastery[idMastery]['championPoints']))
                        break
                break        
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
        
        imageFond.paste(getChampImage(puuid,champion,pseudo,rank,div,lp,spells,masteryPTS,runes,region),localisation)
        modeDeJeu= getTypePartieFromCode(modeDeJeu)
        draw = ImageDraw.Draw(imageFond)
        text_width = draw.textlength(modeDeJeu, font=fontMode)

        image_width= imageFond.size[0]
        text_x = (image_width - text_width) // 2

        draw.text((text_x,10), modeDeJeu, font=fontMode, fill="#F0E6D2",align="center",stroke_width=2,stroke_fill="#010A13")
                        
    
    return imageFond
    
def get_summoner_name_by_key(summoners_dict, key):
    for summoner_id, summoner_data in summoners_dict["data"].items():
        
        if (int)(summoner_data['key'])==key:
            return summoner_id
            
  

    
def getChampImage(puuid,Champ,pseudo,rank,div,lp,spell,masteryPTS,runes,region):
    versions = lol_watcher.data_dragon.versions_for_region(region)
    Account = lol_watcher.summoner.by_puuid(region, puuid)
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{Champ}_0.jpg"
    accountLvl= Account["summonerLevel"]
    sizeChamp= 300,450
    response = requests.get(url)
    img_data = response.content
 
    imgChamp = Image.open(BytesIO(img_data))
    imgChamp=imgChamp.resize(sizeChamp)

    finalImage= imgChamp.convert('RGBA')
    rankIcon=getRankIcon(Account,rank,region)
    finalImage.paste(rankIcon, (50, 150), rankIcon)

    imageSumm=Image.open(f"Image/empty_summ_slot.png")
    combined_image = Image.new('RGB', (128, 64), color='black')
    for summ in range(2): 
        icone = f'https://ddragon.leagueoflegends.com/cdn/{versions["v"]}/img/spell/{spell[summ]}.png'
        slot= add_item_to_slot(imageSumm,icone)
        combined_image.paste(slot, (summ * 64, 0))
        
           
    combined_image =combined_image.resize((96,48))
    runes_image=runesImage(get_rune_by_PrimaryId(runes["primaryId"],runes["primaryRune"]),get_rune_by_SecondaryId(runes["secondaryId"])).resize((65,55)).convert('RGBA')
    finalImage.paste(combined_image,(5,400))
    finalImage.paste(runes_image,(230,397),runes_image)
    imageFond= ImageDraw.Draw(finalImage)

    if rank=="Unranked":
        rankdivlp= "Unranked"
    else:
        rankdivlp= f'{rank} {div} {lp} lp'

    text_bbox = imageFond.textbbox((0, 0), pseudo, font=font)
    text_width = text_bbox[2] - text_bbox[0]


    rank_bbox= imageFond.textbbox((0,0),rankdivlp,font)
    rank_width=rank_bbox[2]-rank_bbox[0]
    rank_height= rank_bbox[3]-rank_bbox[1]

    mastery_bbox=imageFond.textbbox((0,0),masteryPTS,font)
    mastery_width=mastery_bbox[2]-mastery_bbox[0]

    level_bbox = imageFond.textbbox((0, 0), f"{accountLvl}", fontLvl)
    level_width = level_bbox[2] - level_bbox[0]
    level_height = level_bbox[3] - level_bbox[1]
    
    text_position = (((sizeChamp[0] - text_width) // 2), 5)
    divLp_position=(((sizeChamp[0] - rank_width) // 2), (sizeChamp[1] - rank_height) // 2 + 150)
    mastery_position=(((sizeChamp[0] - mastery_width) // 2), 225)
    level_position=(((sizeChamp[0] - level_width)//2), 40)
    background_position = level_position[0] - 5, level_position[1]+2
    text_color = "#F0E6D2"
    border_color = "#010A13"
    border_width = 2 

    
    background_size = (level_width+10, level_height+10)
    corner_radius = 10

    background = Image.new('RGBA', background_size, "#0A1428")
    mask = Image.new('L', background_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), background_size], corner_radius, fill=255)
    border_size = (background_size[0] + 2 * border_width, background_size[1] + 2 * border_width)
    border = Image.new('RGBA', border_size, "#010A13")
    border_mask = Image.new('L', border_size, 0)
    border_draw = ImageDraw.Draw(border_mask)
    border_draw.rounded_rectangle([(0, 0), border_size], corner_radius + border_width, fill=255)
    border.putalpha(border_mask)
    background.putalpha(mask)

    finalImage.paste(border, (background_position[0] - border_width, background_position[1] - border_width), border)

    finalImage.paste(background, background_position, background)
    
    imageFond.text(text_position,f"{pseudo}",font=font,fill=text_color,align="center",stroke_width=border_width,stroke_fill=border_color)
    imageFond.text(divLp_position,rankdivlp,font=font,fill=text_color,align="center",stroke_width=border_width,stroke_fill=border_color)
    imageFond.text(mastery_position,masteryPTS,font=font,fill=text_color,align="center",stroke_width=border_width,stroke_fill=border_color)
    imageFond.text(level_position,f"{accountLvl}",font=fontLvl,fill=text_color,align="center",stroke_width=border_width,stroke_fill=border_color)
    return finalImage.resize(sizeChamp)     


def getRankIcon(Account,rank,region):

    sizeEmblem=200,240
    sizeIcone=65,65
    imgRank=Image.open(f'Image/RANKICON/Wings/{rank}.png')

    versions = lol_watcher.data_dragon.versions_for_region(region)
    
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

    iconeFinal.paste(output,[68,110],mask=output)
    iconeFinal.convert('RGBA')
    
    return iconeFinal




def get_rune_by_PrimaryId(rune_id,secondary_Id):
    for rune in dataRunes:
        if rune["id"]==rune_id:
            rune_liste =rune["slots"][0]["runes"]
            for i in range (len(rune_liste)):
                if rune_liste[i]["id"]==secondary_Id:
                    return "https://ddragon.leagueoflegends.com/cdn/img/"+rune_liste[i]["icon"]
def get_rune_by_SecondaryId(rune_id):
    for rune in dataRunes:
        if rune["id"]==rune_id:
            return "https://ddragon.leagueoflegends.com/cdn/img/"+rune["icon"]


def runesImage(image1_url, image2_url):
    response1 = requests.get(image1_url)
    image1 = Image.open(BytesIO(response1.content)).convert("RGBA")

    response2 = requests.get(image2_url)
    image2 = Image.open(BytesIO(response2.content)).convert("RGBA")


    new_size = (130, 130)
    image2 = image2.resize(new_size)


    circle1_size = (image1.size[0] + 50, image1.size[1] + 50)
    circle2_size = (image2.size[0] + 50, image2.size[1] + 50)

    circle1 = Image.new("RGBA", circle1_size, (0, 0, 0, 0))
    draw1 = ImageDraw.Draw(circle1)
    draw1.ellipse((0, 0, circle1_size[0], circle1_size[1]), outline="#C89B3C",fill="#1E282D", width=10)

    circle2 = Image.new("RGBA", circle2_size, (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(circle2)
    draw2.ellipse((0, 0, circle2_size[0], circle2_size[1]), outline="#C89B3C",fill="#1E282D", width=10)


    circle1.paste(image1, (25, 25), image1)
    circle2.paste(image2, (25, 25), image2)


    output_image = Image.new("RGBA", (450,350), (255, 255, 255, 0))

    output_image.paste(circle1, (0, 0), circle1)
    output_image.paste(circle2, (265, 130), circle2)

    return output_image.convert("RGBA")
"""
with open("1.json","r") as f :
    cg= json.load(f)




image =creerImageCG(cg,"europe","euw1")

image.save("test.png")
"""
class joueur :
    def __init__(self,player,queue_id):
        self.pseudo=player["riotIdGameName"]
        self.champ=player["championName"]
        self.queue_id=queue_id
        self.team=player["teamId"]
        self.position=player["individualPosition"]
        self.items=creeBandeauItem(player)
        self.player=player
        
   

position_order = {
    "TOP": 0,
    "JUNGLE": 1,
    "MIDDLE": 2,
    "BOTTOM": 3,
    "UTILITY": 4,
    "":-1
}

fontAfter = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=40)

async def after_game(region: str, game_id: int):
    try :
        matchs = lol_watcher.match.by_id(region, f"{region.upper()}_{game_id}")
        listeJoueur = [joueur(player,matchs["info"]["queueId"]) for player in matchs["info"]["participants"]]

        # Attribuer les rôles manquants
        listeJoueur.sort(key=lambda x: x.team)
        nb_j = (int)(len(listeJoueur)/2)
        blue = listeJoueur[:nb_j]
        red = listeJoueur[nb_j:]
        if matchs["info"]["gameMode"] == "CLASSIC":
            blue.sort(key=lambda x: (position_order[x.position]))
            red.sort(key=lambda x: (position_order[x.position]))

        imageFond = Image.open(f"Image/Zeri_CG.png")
        size = 1920, 1080
        imageFond = imageFond.resize(size)
        for index,joueurs in enumerate(blue):
            localisation = (10, 50 + 200 * index)
            imageFond.paste(cree_bandeau_joueur(joueurs).resize((950,160)), localisation)
        for index,joueurs in enumerate(red):
            localisation = (970, 50 + 200 * index)
            imageFond.paste(cree_bandeau_joueur(joueurs).resize((950,160)), localisation)

        text=ImageDraw.Draw(imageFond)

        win = blue[0].player["win"]

        if win:
            text.text((480,0),"Victoire",font=fontAfter,fill="#0397AB",stroke_width=1,stroke_fill="black")
            text.text((1400,0),"Défaite",font=fontAfter,fill="#D12B3A",stroke_width=1,stroke_fill="black")
        else:
            text.text((1400,0),"Victoire",font=fontAfter,fill="#0397AB",stroke_width=1,stroke_fill="black")
            text.text((480,0),"Défaite",font=fontAfter,fill="#D12B3A",stroke_width=1,stroke_fill="black")
        return imageFond
    except ApiError as e:
        raise e

def cree_bandeau_joueur(joueur: joueur):
    image = Image.new('RGBA',(800,150), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle([(0, 0), (800,150)], fill="#3C3C41", outline="black", width=6)


    chp=f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/img/champion/{joueur.champ}.png'
    image.paste(Image.open(BytesIO(requests.get(chp).content)).resize((120,120)),(10,20))

    iconPos=positionToIcon(joueur.player)
    image.paste(iconPos,(610,60),iconPos)

    image.paste(joueur.items,(155,45))
    
    text = ImageDraw.Draw(image)

    text.text((155,10),f"{joueur.champ}  -  {joueur.pseudo}",font=font)
    
    image.paste(getLevelTimerKda(joueur.player).resize((300,30)),(155,112))

    image.paste(getStats(joueur.player).resize((140,80)),(650,40))

    return image



#after_game("euw1", 7317366866).save("test.png")