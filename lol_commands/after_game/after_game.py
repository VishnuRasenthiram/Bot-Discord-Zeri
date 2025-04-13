import asyncio
import json
import os
from PIL import Image, ImageDraw,ImageOps, ImageFont
from dotenv import load_dotenv
import requests
from io import BytesIO

import urllib
from riotwatcher import LolWatcher, ApiError

from lol_commands.historique.historiqueImage import add_item_to_slot, creeBandeauItem, getLevelTimerKda, getStats, positionToIcon

from lol_commands.current_game.currentGameImage import get_summoner_name_by_key

load_dotenv()
lol_watcher = LolWatcher(os.getenv('RIOT_API'))
font = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=25)
fontLvl = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=20)
fontMode= ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=35)

try:

    versions = lol_watcher.data_dragon.versions_for_region("euw1")
    current_version = versions["v"] if versions else "13.24.1"  
    
    dataRunes = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{current_version}/data/en_US/runesReforged.json")
    dataRunes = dataRunes.json()
    
    champion_url = f"https://ddragon.leagueoflegends.com/cdn/{current_version}/data/fr_FR/champion.json"
    response = requests.get(champion_url)
    champ = response.json()["data"]

    with open("dossierJson/summoner_info.json","r") as f:
        summonerData = json.load(f)
    
except Exception as e:
    print(f"Erreur lors de l'initialisation: {e}")
    raise




class Joueur :
    def __init__(self, player, queue_id, region):

        self.pseudo=player["riotIdGameName"]
        self.puuid=player["puuid"]
        self.champ=player["championName"]
        self.queue_id=queue_id
        self.team=player["teamId"]
        self.position=player["individualPosition"]
        self.items=creeBandeauItem(player)

        self.rank,self.div,self.lp,self.masteryPTS=get_data(player,region)

        
        self.runes={"primaryId":player["perks"]["styles"][0]["style"], 
            "primaryRune":player["perks"]["styles"][0]["selections"][0]["perk"],
            "secondaryId":player["perks"]["styles"][1]["style"]}


        self.spell1 = player["summoner1Id"]
        self.spell2 = player["summoner2Id"]

        self.region=region
        self.player=player

        self.kda=f"{player["kills"]}/{player["deaths"]}/{player["assists"]}"
        self.level=player["champLevel"]

        

position_order = {
    "TOP": 0,
    "JUNGLE": 1,
    "MIDDLE": 2,
    "BOTTOM": 3,
    "UTILITY": 4,
    "":-1
}

fontAfter = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=40)
def get_data(player,region):
    invocateur= lol_watcher.league.by_summoner(region,player["summonerId"])
    rank="Unranked"
    div=" "
    lp=" "
    masteryPTS=" "
    
    mastery = lol_watcher.champion_mastery.by_puuid(region, player["puuid"])      
    for cle,valeur in champ.items():
        if int(valeur['key'])==int(player['championId']):
            for idMastery in range(len(mastery)):
                if int(mastery[idMastery]['championId'])==int(player['championId']):
                    masteryPTS="{:,.0f}".format(int(mastery[idMastery]['championPoints']))
                    break
            break        
    for j in range(len(invocateur)):
        if invocateur[j]['queueType']=="RANKED_SOLO_5x5":
            rank=invocateur[j]["tier"]
            div=invocateur[j]["rank"]
            lp=invocateur[j]["leaguePoints"]

    return rank,div,lp,masteryPTS

async def after_game(region: str, game_id: int):
    try:

        matchs = await asyncio.to_thread(
            lol_watcher.match.by_id, region, f"{region.upper()}_{game_id}"
        )

        listeJoueur = await asyncio.to_thread(
            lambda: [Joueur(player, matchs["info"]["queueId"], matchs["info"]["platformId"]) 
                    for player in matchs["info"]["participants"]]
        )


        nb_j = len(listeJoueur) // 2
        blue = listeJoueur[:nb_j]
        red = listeJoueur[nb_j:]
        
        if matchs["info"]["gameMode"] == "CLASSIC":
            await asyncio.to_thread(
                lambda: (blue.sort(key=lambda x: position_order[x.position]),
                        red.sort(key=lambda x: position_order[x.position]))
            )

        imageFond = await asyncio.to_thread(
            lambda: Image.open(f"Image/Zeri_CG.png").resize((1920, 1080))
        )
        
        win = blue[0].player["win"]
        cadre_b = "victory" if win else "defeat"
        cadre_r = "defeat" if win else "victory"
        
        image_cadre_b = await asyncio.to_thread(
            lambda: Image.open(f"Image/{cadre_b}_cadre.png")
        )
        image_cadre_r = await asyncio.to_thread(
            lambda: Image.open(f"Image/{cadre_r}_cadre.png")
        )

        tasks = []
        for index, joueurs in enumerate(blue):
            tasks.append(process_player_image(joueurs, imageFond, image_cadre_b, index, is_blue=True))
        
        for index, joueurs in enumerate(red):
            tasks.append(process_player_image(joueurs, imageFond, image_cadre_r, index, is_blue=False))
        
        await asyncio.gather(*tasks)

        return imageFond
        
    except Exception as e:
        if isinstance(e, ApiError) and e.response.status_code == 429:
            pass
        elif isinstance(e, FileNotFoundError):
            pass
        else:
            print(f"Erreur dans after_game: {e}")
        raise

async def process_player_image(joueur, base_image, cadre_image, index, is_blue):
    """Helper pour traiter un joueur de manière asynchrone"""
    try:
        y_pos = 40 if is_blue else 590
        localisation = (10 + 400 * index, y_pos)
        
  
        champ_img = await asyncio.to_thread(getChampImage, joueur)
        champ_img = await asyncio.to_thread(lambda: champ_img.resize((300, 450)))
        

        await asyncio.to_thread(
            lambda: (
                base_image.paste(champ_img, localisation),
                base_image.paste(joueur.items.resize((300, 40)), (localisation[0], localisation[1]+450)),
                base_image.paste(cadre_image, (localisation[0], localisation[1]-40), cadre_image),
                kda_level(joueur, base_image, localisation)
            )
        )
    except Exception as e:
        print(f"Error processing player {joueur.pseudo}: {e}")

def kda_level(joueur: Joueur, imageFond: Image.Image, localisation: tuple[int, int]):
    imageFond = ImageDraw.Draw(imageFond)
    imageFond.text((localisation[0]+100,localisation[1]-35),f"{joueur.kda}",font=font,fill="#F0E6D2",align="center",stroke_width=2,stroke_fill="#010A13")
    imageFond.text((localisation[0]+10,localisation[1]-35),f"{joueur.level}",font=font,fill="#F0E6D2",align="center",stroke_width=2,stroke_fill="#010A13")

def getChampImage(joueur: Joueur):
    region = joueur.region
    puuid = joueur.puuid
    Champ = joueur.champ
    runes = joueur.runes
    rank = joueur.rank
    div = joueur.div
    lp = joueur.lp
    masteryPTS = joueur.masteryPTS
    spells = [ get_summoner_name_by_key(summonerData,joueur.spell1), get_summoner_name_by_key(summonerData,joueur.spell2)]


    

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
        icone = f'https://ddragon.leagueoflegends.com/cdn/{versions["v"]}/img/spell/{spells[summ]}.png'
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

    text_bbox = imageFond.textbbox((0, 0), joueur.pseudo, font=font)
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
    
    imageFond.text(text_position,f"{joueur.pseudo}",font=font,fill=text_color,align="center",stroke_width=border_width,stroke_fill=border_color)
    imageFond.text(divLp_position,rankdivlp,font=font,fill=text_color,align="center",stroke_width=border_width,stroke_fill=border_color)
    imageFond.text(mastery_position,masteryPTS,font=font,fill=text_color,align="center",stroke_width=border_width,stroke_fill=border_color)
    imageFond.text(level_position,f"{accountLvl}",font=fontLvl,fill=text_color,align="center",stroke_width=border_width,stroke_fill=border_color)
    return finalImage.resize(sizeChamp)     


def getRankIcon(Account,rank,region):

    sizeEmblem=200,240
    sizeIcone=65,65
    imgRank=Image.open(f'Image/RANKICON/Wings/{rank}.png')


    
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
    iconeFinal = iconeFinal.convert('RGBA')
    
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


#after_game("euw1", 7364256303).save("test.png")