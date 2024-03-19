import discord
from riotwatcher import LolWatcher, ApiError
from discord.ext import commands
from discord.ui import Select
import urllib 
from discord.flags import Intents 
from discord import app_commands
import json
from dotenv import load_dotenv
import os
load_dotenv()

lol_watcher = LolWatcher(os.getenv('RIOT_API'))
my_region = 'euw1'
my_regionForId='europe'
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
class LOF:
    def regionForRiotId(region:str):
        regionForRiotId(region)

    def profileLeagueOfLegends(interaction:discord.Interaction,pseudo:str,tagline:str,region:str):
            
        with open("baseDeDonnéeDeWish/profile.json","r") as f :
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
                    
            if not estDansListe:
                return interaction.response.send_message("Veuillez préciser un nom d'invocateur ou bien définir votre profil avec la commande : ```/sauvegarder_mon_profil```")
        else:
            me = lol_watcher.accountV1.by_riotid(region=regionForRiotId(region.value),summoner_name=pseudo,tagline=tagline)
            puuid=me["puuid"]          
        versions = lol_watcher.data_dragon.versions_for_region(region.value)
        champions_version = versions['n']['champion']
        dd=lol_watcher.data_dragon.champions(champions_version)

        try:

            myAccount= lol_watcher.summoner.by_puuid(region.value,puuid)
            mastery=lol_watcher.champion_mastery.by_puuid(region.value,puuid)
            me1=lol_watcher.league.by_summoner(region.value,myAccount["id"])
            icone =f'http://ddragon.leagueoflegends.com/cdn/{version["v"]}/img/profileicon/{myAccount["profileIconId"]}.png'
            if not (me1):
                rank="Unranked"
                rank_flex="Unranked"
                div="Unranked"
                div_flex="Unranked"
                lp="Unranked"
                lp_flex="Unranked"
                win="Unranked"
                loose="Unranked"
                wr="Unranked"
    
            else:
                isSolo=True
                isFlex=True
                
                for i in range(len(me1)):
                    if me1[i]['queueType']=="RANKED_SOLO_5x5":
                        rank=me1[i]["tier"]
                        div=me1[i]["rank"]
                        lp=me1[i]["leaguePoints"]
                        win=me1[i]["wins"]
                        loose=me1[i]["losses"]
                        wr=(win/(win+loose))*100
                        wr=f'{round(wr,2)}%'
                        isSolo=False
                        
                    if me1[i]['queueType']=="RANKED_FLEX_SR":
                        rank_flex=me1[i]["tier"]
                        div_flex=me1[i]["rank"]
                        lp_flex=me1[i]["leaguePoints"]
                        isFlex=False
                        
                if isSolo:
                    rank="Unranked"
                    div="Unranked"
                    lp="Unranked"
                    win="Unranked"
                    loose="Unranked"
                    wr="Unranked"
                    wr="Unranked"
                    
                if isFlex:
                    rank_flex="Unranked"
                    div_flex="Unranked"
                    lp_flex="Unranked"
                          
            file = discord.File(f"env/ranked-emblem/zeri2.gif", filename=f"zeri2.gif")
            
            soloq=rank_to_emoji(rank,div,lp)
            flex=rank_to_emoji(rank_flex,div_flex,lp_flex)
            regionRiotId=regionForRiotId(region.value)
            nom=lol_watcher.accountV1.by_puuid(regionRiotId,puuid)["gameName"]
            tagline=lol_watcher.accountV1.by_puuid(regionRiotId,puuid)["tagLine"]
            embed=discord.Embed(title="Profil League Of Legends",
            description=f'{interaction.user.name} voici le profil de {nom}#{tagline} ', 
            color=discord.Color.blue()).set_thumbnail(
            url=icone
            ).add_field(
            name="Pseudo :", 
            value=nom, 
            inline=True
            ).add_field(
            name="Niveau :",
            value=myAccount["summonerLevel"],
            inline=True
            ).add_field(
            name="Rank :", 
            value=f"Solo/duo : {soloq} \n Flex : {flex}",
            inline=False
            ).add_field(
            name="Wins :", 
            value=win,
            inline=True
            ).add_field(name=" ",value=" "
            ).add_field(name="Winrate :",value=wr
            ).add_field(
            name="Losses :", 
            value=loose ,
            inline=False
            ).set_image(url="attachment://zeri2.gif")
            
            
            test={'1':[],'2':[],'3':[]}
            
            
            
            for i in range(3):
                for j in dd['data']:
                    
                    if int(dd['data'][j]['key'])==int(mastery[i]['championId']):
                        test[str(i+1)].append(dd['data'][j]['id'])
                        test[str(i+1)].append(int(mastery[i]['championPoints']))
            chaine = ""
            for key, value in test.items():
                
                chaine += key + ": " + " - ".join(str(v) for v in value) + " Pts \n"
            lignes = chaine.split("\n")
            for ligne in lignes:
                elements = ligne.split("-")
                if len(elements) > 1:
                    nombre = ''.join(filter(str.isdigit, elements[1].strip()))  # Supprime tous les caractères non numériques de la chaîne
                    nombre_formate = "{:,.0f}".format(int(nombre))
                    chaine = chaine.replace(elements[1].strip(), nombre_formate + " Pts")
            
            embed.add_field(
                name="Mastery :",
                value=chaine
            )
                   
            return interaction.response.send_message(embed=embed,file=file)
        #.set_image(url=f"attachment://emblem-{rank.lower()}.png")
        
        except ApiError as err :
            print(err)
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 return interaction.response.send_message("Le compte avec ce pseudo n'existe pas !")
            else:
                raise





    def historiqueLeagueOfLegends(ctx):
        try:
            
            name =str(" ".join(ctx.message.content.split()[1:]))
            versions = lol_watcher.data_dragon.versions_for_region(my_region)
            
            with open('input.json','r') as f:
                data = json.load(f)    
                
            
                
            
            me = lol_watcher.summoner.by_name(my_region, name)
            histo= lol_watcher.match.matchlist_by_puuid(my_region,me["puuid"])
            
            embed=discord.Embed(title="Historique League Of Legends",
            description=f'{ctx.author.name} voici l\'historique league of legends sur les 20 dernieres games de {name} :', 
            color=discord.Color.purple())
            
            list={}
            list2=[]
            wins=0
            
            
            f=1
            for i in range(20):
            
                matchs=lol_watcher.match.by_id(my_region, histo[i])
                j=0
                for i in matchs['metadata']['participants']:
                    if i==me["puuid"]:
                        pos=j
                    else :
                        j+=1
                        
                info=matchs["info"]["participants"][pos]
                info2=matchs["info"]["queueId"]
                for i in range (len(data)):
                    if data[i]['queueId']==info2:     
                        list2.append(data[i]["description"])
                        
                if info['win']:
                    list[f]=[info['championName'],f'-   {str(info["kills"])}/{str(info["deaths"])}/{str(info["assists"])} <:V:1119547366404526180>']
                    wins+=1             
                else:
                    list[f]=[info['championName'],f'-   {str(info["kills"])}/{str(info["deaths"])}/{str(info["assists"])} <:D:1119546988795539497> ']
                
                f+=1
            
            wr=(wins/20)*100
                
            chaine = ""
            chaine2=""
            for key ,value in list.items():
                # Use join() to concatenate the values without the brackets and quotes
                chaine += str(key)+":"+' '.join(str(elem) for elem in value)+"\n"    
                # Print the formatted key-value pair           
            for key  in list2:
                # Use join() to concatenate the values without the brackets and quotes
                chaine2 += str(key)+"\n"    
                # Print the formatted key-value pair
            chaine2 =chaine2.replace('5v5',' ').replace('Pick',' ').replace('games',' ')
            embed.add_field(name="Historique :",value=chaine
            ).add_field(
                name="Mode de jeu",value=chaine2
            ).add_field(
                name="WinRate :",value=f'{round(wr,2)}% ')
            return ctx.channel.send(embed=embed)    
        except ApiError as err :
                if err.response.status_code == 429 :
                    print("Quota de requête dépassé")
                elif err.response.status_code == 404:
                    return ctx.message.channel.send("Le compte avec ce pseudo n'existe pas !")
                else:
                    raise    


    def partieEnCours(ctx):
        try:
            link =f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/data/fr_FR/champion.json'
            f = urllib.request.urlopen(link)
            myfile = f.read()
            data=json.loads(myfile)
            champ = data["data"]   
            name =str(" ".join(ctx.message.content.split()[1:]))
            me = lol_watcher.summoner.by_name(my_region,name)
            cg= lol_watcher.spectator.by_summoner(my_region,me["id"])
            blue=""
            red =""
            
            for i in range ( len(cg["participants"])) :
                nom = cg["participants"][i]["summonerName"] 
                if cg["participants"][i]["teamId"]==100:
                    
                    me = lol_watcher.summoner.by_name(my_region,cg["participants"][i]["summonerName"] )
                    me1= lol_watcher.league.by_summoner(my_region,me["id"])
                    
                    for cle,valeur in champ.items():
                        if int(valeur['key'])==int(cg["participants"][i]['championId']):
                            blue+=f'``{cle}`` **-** \t'
                    
                    rank="Unranked"
                    div=" "
                    lp=" "
        
                    for i in range(len(me1)):
                        if me1[i]['queueType']=="RANKED_SOLO_5x5":
                            rank=me1[i]["tier"]
                            div=me1[i]["rank"]
                            lp=me1[i]["leaguePoints"]
                            

                    var=rank_to_emoji(rank,div,lp)
                        
                            
                    blue+=f'``{nom }``\t**|**\t{var}\n'          
                        
                else :
                    me = lol_watcher.summoner.by_name(my_region,cg["participants"][i]['summonerName'])
                    me1= lol_watcher.league.by_summoner(my_region,me["id"])
                    
                    for cle,valeur in champ.items():
                        if int(valeur['key'])==int(cg["participants"][i]['championId']):
                            red+=f'``{cle}`` **-** \t'
                    
                    rank="Unranked"
                    div=" "
                    lp=" "

                    for i in range(len(me1)):
                        if me1[i]['queueType']=="RANKED_SOLO_5x5":
                            rank=me1[i]["tier"]
                            div=me1[i]["rank"]
                            lp=me1[i]["leaguePoints"]
                            

                    var=rank_to_emoji(rank,div,lp)
                    
                        
                    red+=f'``{nom}``\t**|**\t{var}\n' 
        
            embed=discord.Embed(title='Match en cours :' ,color=discord.Color.yellow())
            embed.add_field(name="Blue side :",value=blue,inline=False
            ).add_field(name="Red side :",value=red )         
            return ctx.channel.send(embed=embed)   
                
            
            
                    
            
        except ApiError as err :
                
                if err.response.status_code == 429 :
                    print("Quota de requête dépassé")
                elif err.response.status_code == 404:
                    return  ctx.message.channel.send("Le compte avec ce pseudo n'existe pas ! ou bien l'utilisateur n'est pas en game !")
                else:
                    raise
    