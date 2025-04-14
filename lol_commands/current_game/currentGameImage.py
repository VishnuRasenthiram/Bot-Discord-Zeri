import asyncio
from PIL import Image, ImageDraw, ImageOps, ImageFont
import aiohttp
import requests
from io import BytesIO
from riotwatcher import LolWatcher, ApiError
import os
from dotenv import load_dotenv
import urllib 
import json
from lol_commands.historique.historiqueImage import *
import functools
import pickle
import time
from pathlib import Path

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


@functools.lru_cache(maxsize=128)
def get_cached_api_data(function_name, *args, timeout=3600):
    """Cache les appels à l'API Riot pour éviter les 429"""
    cache_file = CACHE_DIR / f"{function_name}_{hash(str(args))}.pickle"
    

    if cache_file.exists() and time.time() - cache_file.stat().st_mtime < timeout:
        with open(cache_file, 'rb') as f:
            try:
                return pickle.load(f)
            except:
                pass  
    
    return None

def cache_api_data(function_name, data, *args):
    """Sauvegarde les données dans le cache"""
    cache_file = CACHE_DIR / f"{function_name}_{hash(str(args))}.pickle"
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)

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
async def creerImageCG(cg, regionId, region):
    try:
        size = (1920, 1080)
        sizeChamp = (300, 450)
        

        link = f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/data/fr_FR/champion.json'
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                data = await resp.json()
                champ = data["data"]


        imageFond = await asyncio.to_thread(
            lambda: Image.open("Image/Zeri_CG.png").resize(size)
        )

        tasks = []
        for participant in cg["participants"]:
            tasks.append(process_participant(participant, champ, regionId, region, sizeChamp))


        participant_images = await asyncio.gather(*tasks)


        posB, posR = 0, 0
        for img, team_id in participant_images:
            if team_id == 100:
                localisation = ((sizeChamp[0] * posB + 65 * (posB + 1)), 60)
                posB += 1
            else:
                localisation = ((sizeChamp[0] * posR + 65 * (posR + 1)), 570)
                posR += 1
            
            await asyncio.to_thread(
                lambda: imageFond.paste(img, localisation)
            )


        modeDeJeu = getTypePartieFromCode(cg["gameQueueConfigId"])
        await asyncio.to_thread(
            lambda: add_game_mode_text(imageFond, modeDeJeu)
        )

        return imageFond

    except Exception as e:
        if isinstance(e, ApiError) and e.response.status_code == 429:
            pass
        elif isinstance(e, ApiError) and e.response.status_code == 403:
            pass
        else:
            print(f"Erreur dans creerImageCG: {e}")
        raise


def add_game_mode_text(image: Image.Image, mode_text: str):
    """Ajoute le texte du mode de jeu sur l'image"""
    draw = ImageDraw.Draw(image)
    text_width = draw.textlength(mode_text, font=fontMode)
    image_width = image.size[0]
    text_x = (image_width - text_width) // 2
    draw.text((text_x, 10), mode_text, font=fontMode, 
              fill="#F0E6D2", align="center", stroke_width=2, stroke_fill="#010A13")


async def process_participant(participant, champ, regionId, region, sizeChamp):
    """Traitement async d'un participant"""
    try:
        puuid = participant["puuid"]
        champion = next(
            (cle for cle, valeur in champ.items() 
             if int(valeur['key']) == int(participant['championId'])),
            None
        )
        

        results = await asyncio.gather(
            get_mastery_points(region, puuid, participant['championId']),
            get_summoner_info(region, participant['summonerId']),
            get_account_info(region, puuid),
            get_league_info(regionId, puuid),
            asyncio.sleep(0) 
        )
        masteryPTS, summoner_info, account_info, league_info = results[:4]


        spells = [
            get_summoner_name_by_key(summonnerData, participant["spell1Id"]),
            get_summoner_name_by_key(summonnerData, participant["spell2Id"])
        ]
        runes = {
            "primaryId": participant["perks"]["perkStyle"],
            "primaryRune": participant["perks"]["perkIds"][0],
            "secondaryId": participant["perks"]["perkSubStyle"]
        }

        champ_img = await create_champion_image(
            puuid, champion, league_info["gameName"],
            summoner_info.get("tier", "Unranked"),
            summoner_info.get("rank", ""),
            summoner_info.get("leaguePoints", ""),
            spells, masteryPTS, runes, region,
            account_info["summonerLevel"],
            sizeChamp
        )

        return (champ_img, participant["teamId"])

    except Exception as e:
        if isinstance(e, ApiError) and e.response.status_code == 429:
            pass
        elif isinstance(e, ApiError) and e.response.status_code == 403:
            pass
        else:
            print(f"Erreur traitement participant {puuid}: {e}")
        raise



async def get_mastery_points(region, puuid, championId):

    cache_key = f"mastery_{region}_{puuid}"
    cached_data = get_cached_api_data(cache_key, championId)
    if cached_data:
        return cached_data
        
    try:

        await asyncio.sleep(0.5)
        
        mastery = await asyncio.to_thread(
            lol_watcher.champion_mastery.by_puuid, region, puuid
        )

        for m in mastery:
            if int(m['championId']) == int(championId):
                mastery_points = "{:,.0f}".format(int(m['championPoints']))
                cache_api_data(cache_key, mastery_points, championId)
                return mastery_points
                

        return "0"
        
    except ApiError as e:
        if e.response.status_code == 429:
            return "0"
        raise
    except Exception as e:
        print(f"❌ Erreur dans get_mastery_points: {e}")
        return "0"



async def get_summoner_info(region, summonerId):
    try:
        leagues = await asyncio.to_thread(
            lol_watcher.league.by_summoner, region, summonerId
        )
        for league in leagues:
            if league['queueType'] == "RANKED_SOLO_5x5":
                return {
                    "tier": league["tier"],
                    "rank": league["rank"],
                    "leaguePoints": str(league["leaguePoints"])
                }
        return {}
    except ApiError:
        return {}

async def get_account_info(region, puuid):
    return await asyncio.to_thread(
        lol_watcher.summoner.by_puuid, region, puuid
    )

async def get_league_info(regionId, puuid):
    return await asyncio.to_thread(
        lol_watcher.accountV1.by_puuid, regionId, puuid
    )

async def create_champion_image(puuid, champ, pseudo, rank, div, lp, spells, masteryPTS, runes, region, accountLvl, sizeChamp):
    """Version async de getChampImage"""
    try:
        versions = await asyncio.to_thread(
            lol_watcher.data_dragon.versions_for_region, region
        )
        

        tasks = []
        tasks.append(load_champ_image(champ, versions))
        tasks.append(get_rank_icon(puuid, rank, region))
        tasks.append(load_spell_images(spells, versions))
        tasks.append(load_runes_image(runes))
        

        results = await asyncio.gather(*tasks, return_exceptions=True)
        

        champ_img = results[0] if not isinstance(results[0], Exception) else Image.new('RGB', sizeChamp, color='black')
        rank_icon = results[1] if not isinstance(results[1], Exception) else Image.new('RGBA', (200, 240), (0, 0, 0, 0))
        combined_image = results[2] if not isinstance(results[2], Exception) else Image.new('RGB', (96, 48), color='black')
        runes_image = results[3] if not isinstance(results[3], Exception) else Image.new('RGBA', (65, 55), (0, 0, 0, 0))
        

        return await asyncio.to_thread(
            lambda: compose_champ_image(
                champ_img, rank_icon, combined_image, runes_image,
                pseudo, rank, div, lp, masteryPTS, accountLvl, sizeChamp
            )
        )
    except Exception as e:
        print(f"Erreur dans create_champion_image: {e}")
        return Image.new('RGB', sizeChamp, color='gray')

async def load_champ_image( champ, versions):
    try:
        url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ}_0.jpg"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                img_data = await resp.read()
                return Image.open(BytesIO(img_data))
    except Exception as e:
        print(f"Erreur dans load_champ_image: {e}")


async def get_rank_icon(puuid, rank, region):
    try:

        await asyncio.sleep(0.2)
        account = await asyncio.to_thread(
            lol_watcher.summoner.by_puuid, region, puuid
        )
        
        return await asyncio.to_thread(
            getRankIcon, account, rank, region
        )
    except ApiError as e:
        if isinstance(e, ApiError) and e.response.status_code == 429:
            pass
        elif isinstance(e, ApiError) and e.response.status_code == 403:
            pass
        else:
            print(f"Erreur dans load_rank_icon: {e}")

        account = {"profileIconId": 1}
        return await asyncio.to_thread(
            getRankIcon, account, "Unranked", region
        )
    except Exception as e:
        print(f"Erreur inattendue dans load_rank_icon: {e}")
        return Image.new('RGBA', (200, 240), (0, 0, 0, 0))

async def load_spell_images(spells, versions):
    try:
        combined_image = Image.new('RGB', (128, 64), color='black')
        
        for i, spell in enumerate(spells):
            url = f'https://ddragon.leagueoflegends.com/cdn/{versions["v"]}/img/spell/{spell}.png'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    spell_img = Image.open(BytesIO(await resp.read()))
                    

                    spell_img = spell_img.resize((48, 48))
                    slot = Image.open("Image/empty_summ_slot.png")
                    slot.paste(spell_img, (8, 8))
                    

                    combined_image.paste(slot, (i * 64, 0))
        
        return combined_image.resize((96, 48))
    except Exception as e:
        print(f"Erreur dans load_spell_images: {e}")

        return Image.new('RGB', (96, 48), color='black')

async def load_runes_image(runes):
    try:

        primary_url = get_rune_by_PrimaryId(runes["primaryId"], runes["primaryRune"])
        secondary_url = get_rune_by_SecondaryId(runes["secondaryId"])

        async with aiohttp.ClientSession() as session:
            async with session.get(primary_url) as resp1:
                primary_data = await resp1.read()
            async with session.get(secondary_url) as resp2:
                secondary_data = await resp2.read()
        

        image1 = Image.open(BytesIO(primary_data)).convert("RGBA")
        image2 = Image.open(BytesIO(secondary_data)).convert("RGBA")

        result = await asyncio.to_thread(
            lambda: create_runes_image(image1, image2)
        )
        
        return result
    except Exception as e:
        print(f"Erreur dans load_runes_image: {e}")

        return Image.new('RGBA', (65, 55), (0, 0, 0, 0))


def create_runes_image(image1, image2):

    new_size = (130, 130)
    image2 = image2.resize(new_size)
    

    circle1_size = (image1.size[0] + 50, image1.size[1] + 50)
    circle2_size = (image2.size[0] + 50, image2.size[1] + 50)
    
    circle1 = Image.new("RGBA", circle1_size, (0, 0, 0, 0))
    draw1 = ImageDraw.Draw(circle1)
    draw1.ellipse((0, 0, circle1_size[0], circle1_size[1]), 
                  outline="#C89B3C", fill="#1E282D", width=10)
    
    circle2 = Image.new("RGBA", circle2_size, (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(circle2)
    draw2.ellipse((0, 0, circle2_size[0], circle2_size[1]), 
                  outline="#C89B3C", fill="#1E282D", width=10)
    

    circle1.paste(image1, (25, 25), image1)
    circle2.paste(image2, (25, 25), image2)

    output_image = Image.new("RGBA", (450, 350), (255, 255, 255, 0))
    output_image.paste(circle1, (0, 0), circle1)
    output_image.paste(circle2, (265, 130), circle2)
    
    return output_image.resize((65, 55)).convert('RGBA')

def get_summoner_name_by_key(summoners_dict, key):
    for summoner_id, summoner_data in summoners_dict["data"].items():
        
        if (int)(summoner_data['key'])==key:
            return summoner_id
            
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
def compose_champ_image( champ_img, rank_icon, spells_img, runes_img,
                       pseudo, rank, div, lp, masteryPTS, accountLvl, sizeChamp):
    """Version synchrone de la composition finale de l'image du champion"""

    final_img = champ_img.resize(sizeChamp).convert('RGBA')
    final_img.paste(rank_icon, (50, 150), rank_icon)
    final_img.paste(spells_img, (5, 400))
    final_img.paste(runes_img, (230, 397), runes_img)
    
    draw = ImageDraw.Draw(final_img)
    

    if rank == "Unranked":
        rankdivlp = "Unranked"
    else:
        rankdivlp = f'{rank} {div} {lp} lp'


    text_bbox = draw.textbbox((0, 0), pseudo, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    
    rank_bbox = draw.textbbox((0, 0), rankdivlp, font=font)
    rank_width = rank_bbox[2] - rank_bbox[0]
    rank_height = rank_bbox[3] - rank_bbox[1]

    mastery_bbox = draw.textbbox((0, 0), masteryPTS, font=font)
    mastery_width = mastery_bbox[2] - mastery_bbox[0]

    level_bbox = draw.textbbox((0, 0), f"{accountLvl}", font=fontLvl)
    level_width = level_bbox[2] - level_bbox[0]
    level_height = level_bbox[3] - level_bbox[1]
    
    text_position = (((sizeChamp[0] - text_width) // 2), 5)
    divLp_position = (((sizeChamp[0] - rank_width) // 2), (sizeChamp[1] - rank_height) // 2 + 150)
    mastery_position = (((sizeChamp[0] - mastery_width) // 2), 225)
    level_position = (((sizeChamp[0] - level_width) // 2), 40)
    background_position = (level_position[0] - 5, level_position[1] + 2)

    text_color = "#F0E6D2"
    border_color = "#010A13"
    border_width = 2
    background_size = (level_width + 10, level_height + 10)
    corner_radius = 10


    background = Image.new('RGBA', background_size, "#0A1428")
    mask = Image.new('L', background_size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([(0, 0), background_size], corner_radius, fill=255)
    
    border_size = (background_size[0] + 2 * border_width, background_size[1] + 2 * border_width)
    border_img = Image.new('RGBA', border_size, "#010A13")
    border_mask = Image.new('L', border_size, 0)
    border_draw = ImageDraw.Draw(border_mask)
    border_draw.rounded_rectangle([(0, 0), border_size], corner_radius + border_width, fill=255)
    border_img.putalpha(border_mask)
    background.putalpha(mask)


    final_img.paste(border_img, 
                   (background_position[0] - border_width, background_position[1] - border_width), 
                   border_img)
    final_img.paste(background, background_position, background)

    draw.text(text_position, pseudo, font=font, fill=text_color,
             align="center", stroke_width=border_width, stroke_fill=border_color)
    draw.text(divLp_position, rankdivlp, font=font, fill=text_color,
             align="center", stroke_width=border_width, stroke_fill=border_color)
    draw.text(mastery_position, masteryPTS, font=font, fill=text_color,
             align="center", stroke_width=border_width, stroke_fill=border_color)
    draw.text(level_position, f"{accountLvl}", font=fontLvl, fill=text_color,
             align="center", stroke_width=border_width, stroke_fill=border_color)
    
    return final_img
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

async def api_call_with_retry(func, *args, max_retries=3, initial_backoff=1.0):
    """Exécute un appel d'API avec système de retentatives et backoff exponentiel"""
    retries = 0
    backoff = initial_backoff
    
    while True:
        try:
            return await asyncio.to_thread(func, *args)
        except ApiError as e:
            if e.response.status_code == 429:
                retries += 1
                if retries > max_retries:
                    print(f"⚠️ Limite de retentatives atteinte pour {func.__name__}")
                    raise
                    
                retry_after = int(e.response.headers.get('Retry-After', backoff))
                print(f"🕒 Rate limit atteint. Attente de {retry_after}s avant réessai...")
                
                await asyncio.sleep(retry_after)
                backoff *= 2  
            else:
                raise
        except Exception as e:
            print(f"❌ Erreur dans {func.__name__}: {e}")
            raise
'''
if __name__ == "__main__":
    try:
       
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_file = os.path.join(current_dir, "test.json")
        
        
        if os.path.exists(test_file):
            print(f"✅ Fichier test.json trouvé: {test_file}")
            with open(test_file, "r") as f:
                cg = json.load(f)
                
            
            async def run_test():
                try:
                    image = await creerImageCG(cg, "europe", "euw1")
                    image.save(os.path.join(current_dir, "test.png"))
                    print("✅ Image de test créée avec succès : test.png")
                except ApiError as e:
                    if e.response.status_code == 429:
                        pass
                    else:
                        raise
                
            asyncio.run(run_test())
        else:
            print(f"❌ Le fichier {test_file} n'existe pas. Test ignoré.")
            print("💡 Voici où Python cherche le fichier:")
            print(f"   Répertoire de travail actuel: {os.getcwd()}")
            print(f"   Répertoire du script: {current_dir}")
            print("💡 Pour tester, créez un fichier test.json dans l'un de ces répertoires.")
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback
        traceback.print_exc()
'''



