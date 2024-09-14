from PIL import Image, ImageDraw, ImageOps, ImageFont
import requests
from io import BytesIO
from riotwatcher import LolWatcher, ApiError
import os
from dotenv import load_dotenv
import urllib 
import json
import asyncio
load_dotenv()
lol_watcher = LolWatcher(os.getenv('RIOT_API'))
version = lol_watcher.data_dragon.versions_for_region("euw1")
font = ImageFont.truetype("font/BeaufortforLOL-Bold.ttf",size=25)

async def creerImageCG(cg, regionId, region):
    print("1")
    size = 1920, 1080
    print("2")
    sizeChamp = 308, 400
    print("3")
    link = f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/data/fr_FR/champion.json'
    print("4")

    f = urllib.request.urlopen(link)
    print("5")
    myfile = f.read()
    print("6")
    data = json.loads(myfile)
    print("7")
    champ = data["data"]
    print("8")
    
    with Image.open(f"Image/currentGame.png") as imageFond:
        print("9")
        imageFond = imageFond.resize(size)
    print("10")
    
    posB = 0
    print("11")
    posR = 0
    print("12")
    
    for i in range(len(cg["participants"])):
        print(f"13-{i}")
        puuid = cg["participants"][i]["puuid"]
        print(f"14-{i}")
        pseudo = lol_watcher.accountV1.by_puuid(regionId, puuid)["gameName"]
        print(f"15-{i}")
        invocateur = lol_watcher.league.by_summoner(region, cg["participants"][i]["summonerId"])
        print(f"16-{i}")
        rank = "Unranked"
        print(f"17-{i}")
        div = " "
        print(f"18-{i}")
        lp = " "
        print(f"19-{i}")
        
        for cle, valeur in champ.items():
            print(f"20-{i}")
            if int(valeur['key']) == int(cg["participants"][i]['championId']):
                print(f"21-{i}")
                champion = cle

        for j in range(len(invocateur)):
            print(f"22-{i}-{j}")
            if invocateur[j]['queueType'] == "RANKED_SOLO_5x5":
                print(f"23-{i}-{j}")
                rank = invocateur[j]["tier"]
                print(f"24-{i}-{j}")
                div = invocateur[j]["rank"]
                print(f"25-{i}-{j}")
                lp = invocateur[j]["leaguePoints"]
        
        if cg["participants"][i]["teamId"] == 100:
            print(f"26-{i}")
            localisation = ((sizeChamp[0] * (posB) + 65 * (posB + 1)), (60))
            print(f"27-{i}")
            posB += 1
        else:
            print(f"28-{i}")
            localisation = ((sizeChamp[0] * (posR) + 65 * (posR + 1)), (570))
            print(f"29-{i}")
            posR += 1
        
        print(f"30-{i}")
        imageFond.paste(getChampImage(puuid, champion, pseudo, rank, div, lp, region), localisation)
    
    print("31")
    imageFond.save("test.png")


def getChampImage(puuid, Champ, pseudo, rank, div, lp, region):
    print("32")
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{Champ}_0.jpg"
    print("33")
    sizeChamp = 300, 450

    print("34")
    response = requests.get(url)
    print("35")
    img_data = response.content
    print("36")

    imgChamp = Image.open(BytesIO(img_data))
    print("37")
    imgChamp = imgChamp.resize(sizeChamp)
    print("38")

    finalImage = imgChamp.convert('RGBA')
    print("39")

    rankIcon = getRankIcon(puuid, rank, region)
    print("40")
    finalImage.paste(rankIcon, (70, 220), rankIcon)
    
    print("41")
    imageFond = ImageDraw.Draw(finalImage)

    print("42")
    rankdivlp = f'{rank} {div} {lp} lp'

    print("43")
    text_bbox = imageFond.textbbox((0, 0), pseudo, font=font)
    print("44")
    text_width = text_bbox[2] - text_bbox[0]
    print("45")
    text_height = text_bbox[3] - text_bbox[1]

    print("46")
    rank_bbox = imageFond.textbbox((0, 0), rankdivlp, font)
    print("47")
    rank_width = rank_bbox[2] - rank_bbox[0]
    print("48")
    rank_height = rank_bbox[3] - rank_bbox[1]

    print("49")
    text_position = ((sizeChamp[0] - text_width) // 2, 5)
    print("50")
    divLp_position = ((sizeChamp[0] - rank_width) // 2, (sizeChamp[1] - rank_height) // 2 + 190)
    
    print("51")
    text_color = "#F0E6D2"
    print("52")
    border_color = "#010A13"
    print("53")
    border_width = 1 
    
    print("54")
    for x_offset, y_offset in [(-border_width, 0), (border_width, 0), (0, -border_width), (0, border_width)]:
        print("55")
        imageFond.text((text_position[0] + x_offset, text_position[1] + y_offset), pseudo, font=font, fill=border_color)
        print("56")
        imageFond.text((divLp_position[0] + x_offset, divLp_position[1] + y_offset), rankdivlp, font=font, fill=border_color)

    print("57")
    imageFond.text(text_position, f"{pseudo}", font=font, fill=text_color)
    print("58")
    imageFond.text(divLp_position, rankdivlp, font=font, fill=text_color)
  
    print("59")
    return finalImage.resize(sizeChamp)     


def getRankIcon(puuid, rank, region):
    print("60")
    sizeEmblem = 160, 200
    print("61")
    sizeIcone = 50, 50
    print("62")
    imgRank = Image.open(f'Image/RANKICON/Wings/{rank}.png')
    print("63")

    versions = lol_watcher.data_dragon.versions_for_region(region)
    print("64")
    Account = lol_watcher.summoner.by_puuid(region, puuid)
    print("65")
    icone = f'http://ddragon.leagueoflegends.com/cdn/{versions["v"]}/img/profileicon/{Account["profileIconId"]}.png'
    print("66")
    
    response = requests.get(icone)
    print("67")
    imageIcon = BytesIO(response.content)
    print("68")
    mask = Image.new('L', sizeIcone, 0)
    print("69")
    masque = ImageDraw.Draw(mask)
    print("70")
    masque.ellipse((0, 0, sizeIcone[0], sizeIcone[1]), fill=255)

    print("71")
    imgIcone = Image.open(imageIcon)
    print("72")

    imgIcone = imgIcone.resize(sizeIcone)
    print("73")
    iconeFinal = imgRank.resize(sizeEmblem)
    print("74")

    output = ImageOps.fit(imgIcone, sizeIcone, centering=(0.5, 0.5))
    print("75")
    output.putalpha(mask)
    print("76")
    iconeFinal.paste(output, [54, 94], mask=output)
    print("77")
    iconeFinal.convert('RGBA')
    
    print("78")
    return iconeFinal





