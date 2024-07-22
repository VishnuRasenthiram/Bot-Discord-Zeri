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
        with open("dossierJson/profile.json","r") as f :
            profile = json.load(f)
        
        if not(pseudo):
            estDansListe=False
            for id in profile:
                if interaction.user.id==int(id):
                    estDansListe=True
                    if profile[str(interaction.user.id)]["statut"]==0:
                        return interaction.response.send_message("Vous n'avez pas confirmé le profil !")
                    else :
                        puuid = profile[str(interaction.user.id)]["puuid"]
                        region = profile[str(interaction.user.id)]["region"]
                    
            if not estDansListe:
                return interaction.response.send_message("Veuillez préciser un nom d'invocateur ou bien définir votre profil avec la commande : ```/sauvegarder_mon_profil```")
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
                
            with open("dossierJson/input.json","r") as numPartie:
                data = json.load(numPartie)    
                
        
            histo= lol_watcher.match.matchlist_by_puuid(region,puuid)
            
            
            
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

            embed=discord.Embed(title="Historique League Of Legends",
            description=f'Voici l\'historique league of legends sur les 20 dernieres games de {pseudo} :', 
            color=discord.Color.purple()
            ).add_field(
                name="Historique :",value=chainePartie
            ).add_field(
                name="Mode de jeu",value=chaineTypePartie
            ).add_field(
                name="WinRate :",value=f'{round(wr,2)}% ')
            
            await interaction.followup.send(embed=embed)   
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
            link =f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/data/fr_FR/champion.json'

            f = urllib.request.urlopen(link)
            myfile = f.read()
            data=json.loads(myfile)
            champ = data["data"]   
            
            regionId= LOF.regionForRiotId(region)
            
            cg= lol_watcher.spectator.by_puuid(region,puuid)
            
            blue=""
            red =""
            
            for i in range ( len(cg["participants"])) :
                
                
                pseudo=lol_watcher.accountV1.by_puuid(regionId,cg["participants"][i]["puuid"])["gameName"]
                invocateur= lol_watcher.league.by_summoner(region,cg["participants"][i]["summonerId"])
                rank="Unranked"
                div=" "
                lp=" "
                if cg["participants"][i]["teamId"]==100:

                    for cle,valeur in champ.items():
                        if int(valeur['key'])==int(cg["participants"][i]['championId']):
                            blue+=f'``{cle}`` **-** \t'

                    for i in range(len(invocateur)):
                        if invocateur[i]['queueType']=="RANKED_SOLO_5x5":
                            rank=invocateur[i]["tier"]
                            div=invocateur[i]["rank"]
                            lp=invocateur[i]["leaguePoints"]
                            

                    var=rank_to_emoji(rank,div,lp)  
                            
                    blue+=f'``{pseudo }``\t**|**\t{var}\n'          
                        
                else :
                    
                    for cle,valeur in champ.items():
                        if int(valeur['key'])==int(cg["participants"][i]['championId']):
                            red+=f'``{cle}`` **-** \t'
     

                    for i in range(len(invocateur)):
                        if invocateur[i]['queueType']=="RANKED_SOLO_5x5":
                            rank=invocateur[i]["tier"]
                            div=invocateur[i]["rank"]
                            lp=invocateur[i]["leaguePoints"]
                            

                    var=rank_to_emoji(rank,div,lp)
                    red+=f'``{pseudo}``\t**|**\t{var}\n' 
            
            embed=discord.Embed(title='Match en cours :' ,color=discord.Color.yellow())
            embed.add_field(name="Blue side :",value=blue,inline=False
            ).add_field(name="Red side :",value=red )         
            await interaction.followup.send(embed=embed)    
                
            
            
                    
            
        except ApiError as err :
                
                if err.response.status_code == 429 :
                    print("Quota de requête dépassé")
                elif err.response.status_code == 404:
                    await interaction.followup.send("Le compte avec ce pseudo n'existe pas ou le joueur n'est pas dans une partie!")
                else:
                    raise
    