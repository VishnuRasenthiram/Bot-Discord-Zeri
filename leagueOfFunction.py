import discord
from riotwatcher import LolWatcher, ApiError
from discord.ext import commands
from discord.ui import Select
from discord.app_commands import Choice
import urllib 
from discord.flags import Intents 
from discord import app_commands
import json
from dotenv import load_dotenv
import os
from currentGameImage import *
from baseDeDonne import *
from historiqueImage import *
load_dotenv()

lol_watcher = LolWatcher(os.getenv('RIOT_API'))
version = lol_watcher.data_dragon.versions_for_region("euw1")

def rank_to_emoji(rank,div,lp):
        var = " "
        match rank.lower():
            case "iron":
                var=f"<:Iron:1119544772785340436>  **{rank.lower()} {div}** {lp} lps"
            case "bronze":
                var=f"<:Bronze:1119544771640311818>  **{rank.lower()} {div}** {lp} lps"
            case "silver":
                var=f"<:Silver:1119544769643819148>  **{rank.lower()} {div}** {lp} lps"
            case "gold":
                var=f"<:Gold:1119544768440057866>  **{rank.lower()} {div}** {lp} lps"
            case "platinum":
                var=f"<:Platinum:1131518475496599572>  **{rank.lower()} {div}** {lp} lps"
            case "emerald":
                var=f"<:Emerald:1131518517846474782>  **{rank.lower()} {div}** {lp} lps"
            case "diamond":
                var=f"<:Diamond:1119544764484825098>  **{rank.lower()} {div}** {lp} lps"
            case "master":
                var=f"<:Master:1119544763041992775>  **{rank.lower()} {div}** {lp} lps"
            case "grandmaster":
                var=f"<:Grandmaster:1119544761058074644>  **{rank.lower()} {div}** {lp} lps"
            case "challenger":
                var=f"<:Challenger:1119544759862706216>  **{rank.lower()} {div}** {lp} lps"
            case _:
                var=f"<:Unranked:1119549521182068856> **{rank.lower()}**"

        return var
def regionForRiotId(region:str):
        
        europe=["euw1","eun1","tr1",'ru1']
        amerique=["na1","la1","la2","br1"]
        
        if region in europe:
            return "europe"
        elif region in amerique:
            return "americas"
        else:
            return "asia"
def getPuuidRegion(interaction:discord.Interaction,pseudo:str,tagline:str,region:str):
        
        
        if not(pseudo):
            
            profile=get_player_data(interaction.user.id)
        
            if profile!=None:
                
                if profile[4]==0:
                    return interaction.response.send_message("Vous n'avez pas confirmé le profil !")
                else :
                    puuid = profile[1]
                    region = profile[3]
                    
            else:
                return interaction.response.send_message("Veuillez préciser un nom d'invocateur ou bien sauvegarder votre profil avec la commande : ```/sauvegarder_mon_profil```")
        else:
            if not isinstance(region,Choice):
                region= Choice(name="defaut",value="euw1")
            me = lol_watcher.accountV1.by_riotid(region=regionForRiotId(region.value),summoner_name=pseudo,tagline=tagline)
            puuid=me["puuid"]
            region= region.value

        return puuid,region
class LOF:
    def regionForRiotId(region:str):
     
        return regionForRiotId(region)
    

    async def profileLeagueOfLegends(interaction:discord.Interaction,pseudo:str,tagline:str,region:str):
            
        await interaction.response.defer()

        puuid,region=getPuuidRegion(interaction,pseudo,tagline,region)
        versions = lol_watcher.data_dragon.versions_for_region(region)
        champions_version = versions['n']['champion']
        dd = lol_watcher.data_dragon.champions(champions_version)

        try:
            myAccount = lol_watcher.summoner.by_puuid(region, puuid)
            mastery = lol_watcher.champion_mastery.by_puuid(region, puuid)
            me1 = lol_watcher.league.by_summoner(region, myAccount["id"])
            icone = f'http://ddragon.leagueoflegends.com/cdn/{versions["v"]}/img/profileicon/{myAccount["profileIconId"]}.png'

            if not me1:
                rank = rank_flex = div = div_flex = lp = lp_flex = win = loose = wr = "Unranked"
            else:
                isSolo = isFlex = True

                for i in range(len(me1)):
                    if me1[i]['queueType'] == "RANKED_SOLO_5x5":
                        rank = me1[i]["tier"]
                        div = me1[i]["rank"]
                        lp = me1[i]["leaguePoints"]
                        win = me1[i]["wins"]
                        loose = me1[i]["losses"]
                        wr = (win / (win + loose)) * 100
                        wr = f'{round(wr, 2)}%'
                        isSolo = False

                    if me1[i]['queueType'] == "RANKED_FLEX_SR":
                        rank_flex = me1[i]["tier"]
                        div_flex = me1[i]["rank"]
                        lp_flex = me1[i]["leaguePoints"]
                        isFlex = False

                if isSolo:
                    rank = div = lp = win = loose = wr = "Unranked"
                if isFlex:
                    rank_flex = div_flex = lp_flex = "Unranked"

            file = discord.File("env/ranked-emblem/zeri2.gif", filename="zeri2.gif")
            soloq = rank_to_emoji(rank, div, lp)
            flex = rank_to_emoji(rank_flex, div_flex, lp_flex)
            regionRiotId = LOF.regionForRiotId(region)
            nom=lol_watcher.accountV1.by_puuid(regionRiotId,puuid)["gameName"]
            tagline=lol_watcher.accountV1.by_puuid(regionRiotId,puuid)["tagLine"]
            print(nom,tagline)
            embed = discord.Embed(
                title="Profil League Of Legends",
                description=f'{interaction.user.name} voici le profil de {nom}#{tagline}',
                color=discord.Color.blue()
            ).set_thumbnail(url=icone).add_field(
                name="Pseudo :", value=nom, inline=True
            ).add_field(
                name="Niveau :", value=myAccount["summonerLevel"], inline=True
            ).add_field(
                name="Rank :", value=f"Solo/duo : {soloq} \n Flex : {flex}", inline=False
            ).add_field(
                name="Wins :", value=win, inline=True
            ).add_field(
                name=" ", value=" "
            ).add_field(
                name="Winrate :", value=wr
            ).add_field(
                name="Losses :", value=loose, inline=False
            ).set_image(url="attachment://zeri2.gif")

            test = {'1': [], '2': [], '3': []}

            for i in range(3):
                for j in dd['data']:
                    if int(dd['data'][j]['key']) == int(mastery[i]['championId']):
                        test[str(i + 1)].append(dd['data'][j]['id'])
                        test[str(i + 1)].append(int(mastery[i]['championPoints']))
            
            chaine = ""
            for key, value in test.items():
                chaine += key + ": " + " - ".join(str(v) for v in value) + " Pts \n"
            lignes = chaine.split("\n")
            for ligne in lignes:
                elements = ligne.split("-")
                if len(elements) > 1:
                    nombre = ''.join(filter(str.isdigit, elements[1].strip()))
                    nombre_formate = "{:,.0f}".format(int(nombre))
                    chaine = chaine.replace(elements[1].strip(), nombre_formate + " Pts")

            embed.add_field(name="Mastery :", value=chaine)

            await interaction.followup.send(embed=embed, file=file)
    
        except ApiError as err:
            print(err)
            if err.response.status_code == 429:
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                await interaction.followup.send("Le compte avec ce pseudo n'existe pas !")
            else:
                raise
            


    async def historiqueLeagueOfLegends(interaction:discord.Interaction,pseudo:str,tagline:str,region:str):

        await interaction.response.defer()

        puuid,region=getPuuidRegion(interaction,pseudo,tagline,region)
        
        try:
                image =creeImageHistorique(puuid,region)
                img_bytes=BytesIO()
                image.save(img_bytes,format='PNG')
                img_bytes.seek(0)
                await interaction.followup.send(file=discord.File(img_bytes,filename="Historique.png"))
        except ApiError as err :
                if err.response.status_code == 429 :
                    print("Quota de requête dépassé")
                elif err.response.status_code == 404:
                    await interaction.followup.send("Le compte avec ce pseudo n'existe pas !")
                else:
                    print(err)
                    raise    


    async def partieEnCours(interaction:discord.Interaction,pseudo:str,tagline:str,region:str):
        await interaction.response.defer()
        puuid,region=getPuuidRegion(interaction,pseudo,tagline,region)
        try:
            regionId= LOF.regionForRiotId(region)
            cg=lol_watcher.spectator.by_puuid(region,puuid)
            image=await creer_image_avec_reessai(cg, regionId, region)
            img_bytes=BytesIO()
            image.save(img_bytes,format='PNG')
            img_bytes.seek(0)
                   
            await interaction.followup.send(file=discord.File(img_bytes,filename="Partie_En_Cours.png"))    
      
            
        except ApiError as err :
                
                if err.response.status_code == 429 :
                    print("Quota de requête dépassé")
                elif err.response.status_code == 404:
                    await interaction.followup.send("Le compte avec ce pseudo n'existe pas ou le joueur n'est pas dans une partie!")
                else:
                    print(err)
                    raise


async def creer_image_avec_reessai(cg, regionId, region):
    attempt = True
    while attempt :
        try:
            image = await creerImageCG(cg, regionId, region)
            attempt =False
            return image 
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                await asyncio.sleep(1) 
            else:
                raise e
    raise Exception("Échec après plusieurs tentatives : le service reste indisponible.")