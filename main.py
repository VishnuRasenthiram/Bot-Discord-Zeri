import discord
from riotwatcher import LolWatcher, ApiError
from discord.ext import *
from discord.ui import Select
import asyncio
from datetime import date, datetime
from datetime import timedelta
from discord.flags import Intents 
from discord import app_commands
import urllib
import requests
from datetime import datetime
import json
import random
from nasaapi import Client
import re
import pytz
from dotenv import load_dotenv
import os
from threading import Thread
import subprocess
import sched, time
from discord.ext import tasks, commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from leagueOfFunction import *
from welcomeImage import *
from currentGameImage import *
from baseDeDonne import *
from tenorApi import *
import hashlib  
load_dotenv()
##########################################################################

#API

nasa=Client(api_key=os.getenv('NASA_API'))
lol_watcher = LolWatcher(os.getenv('RIOT_API'))



##########################################################################

default_intents = discord.Intents.all()
client = discord.Client(intents=default_intents)
bot = commands.Bot(command_prefix = "-", description = "Bot de Vishnu",intents=discord.Intents.all(), case_insensitive=True,help_command=None)

pays = "Europe/Paris"

now2 = datetime.now(pytz.timezone(pays))
now = datetime.now()
current_day= now.strftime("%d/%m/%Y")
currect_daay=now2.strftime("%A")
current_time = now2.strftime("%H:%M")
print(currect_daay)


version = lol_watcher.data_dragon.versions_for_region("euw1")
##########################################################################
#CONSTANTES


CHAN_GEN =833833047454515223
CHAN_BVN =614953541911576692
ROLE_NEANTIN =1079422327391006851
ROLE_FAILLE=1079432006796066816
CHAN_VOC =1071472444562473021
CHAN_INFO=634136239804514344
CHAN_REGLEMENT=657946471022329860
MESSAGE_AUTO_ROLE=11111
CHAN_LOLDLE=1091280421192474694
CHAN_FLAME=332580555872927746
ANNONCE_CHAN=634266557383442432
KARAN_ID=614728233497133076
SALON_NASA=1317082270875652180

##################################################################################################################################
##################################################################################################################################


##################################################################################################################################
##################################################################################################################################




##########################################################################
#MAIN
print(current_time)



@bot.event
async def on_ready():
    scheduler.start()
    print("le bot est pret")
    try:
        synced= await bot.tree.sync()
        print(f"Synced {synced} commands")
    except Exception as e:
        print(e)
    periodic_check.start()

   
    
@tasks.loop(seconds=60)
async def periodic_check():
    await verif_game_en_cours()
    
async def changementIconeServeur():
    with open("env/ranked-emblem/Karan_nuit.png", 'rb') as n,open("env/ranked-emblem/Karan_jour.png", 'rb') as j:
        iconNuit = n.read()
        iconJour = j.read()
    
    guild=bot.get_guild(KARAN_ID)
    pays = "Europe/Paris"
    now2 = datetime.now(pytz.timezone(pays))
    current_time = now2.strftime("%H:%M")
    if current_time>"22:00" or current_time<"10:00": 
        await guild.edit(name ="Karan 🌙")
        await guild.edit(icon=iconNuit)
    else:
        await apodAut()
        await guild.edit(name="Karan 🍁")
        await guild.edit(icon=iconJour)
            
       
    
scheduler = AsyncIOScheduler()
scheduler.add_job(changementIconeServeur, CronTrigger(hour=10, minute=1))
scheduler.add_job(changementIconeServeur, CronTrigger(hour=22, minute=1))
##########################################################################



@bot.tree.command(name="ping")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message("Pong! Latence: {}ms".format(round(bot.latency * 1000, 1)))

class ViewValidator(discord.ui.View):
    @discord.ui.button( # the decorator that lets you specify the properties of the select menu
        style=discord.ButtonStyle.gray,
        emoji='✅'
    )
    async def select_callback(self,interaction, select): # the function called when the user is done selecting options
        await interaction.channel.send("Bien reçu, je vais procédé à la vérification")
        
    
        profile=get_player_data(interaction.user.id)
                
                
        meIcon=lol_watcher.summoner.by_puuid(region=profile[3],encrypted_puuid=profile[1])
            
        icone =f'http://ddragon.leagueoflegends.com/cdn/{version["v"]}/img/profileicon/{meIcon["profileIconId"]}.png'
        if profile[4]==0:
            if profile[2]==icone:
                await interaction.response.send_message("Votre compte est lié !")
                update_player_statut(interaction.user.id,1)
            else :
                await interaction.response.send_message("Vous n'avez pas la bonne icône !")
                await interaction.channel.send("Valider ici :", view=ViewValidator())
                
        else :
            await interaction.response.send_message("Votre compte a déjà été confirmé !")
        


choixRegion=[app_commands.Choice(name="EUW", value="euw1"),
    app_commands.Choice(name="EUN", value="eun1"),
    app_commands.Choice(name="TR", value="tr1"),           
    app_commands.Choice(name="RU", value="ru"),
    app_commands.Choice(name="NA", value="na1"),
    app_commands.Choice(name="LA1", value="la1"),
    app_commands.Choice(name="LA2", value="la2"),
    app_commands.Choice(name="BR", value="br1"),
    app_commands.Choice(name="JP", value="jp1"),
    app_commands.Choice(name="KR", value="kr"),
    app_commands.Choice(name="OC", value="oc1"),
    app_commands.Choice(name="PH", value="ph2"),
    app_commands.Choice(name="SG", value="sg2"),
    app_commands.Choice(name="TH", value="th2"),
    app_commands.Choice(name="TW", value="tw2"),
    app_commands.Choice(name="VN", value="vn2"),]   
    
@bot.tree.command(name="sauvegarder_mon_profil")
@app_commands.choices(region=choixRegion)
async def set_profile(interaction:discord.Interaction,pseudo:str,tagline:str,region:app_commands.Choice[str]):
   
        try:
            me = lol_watcher.accountV1.by_riotid(region=LOF.regionForRiotId(region.value),summoner_name=pseudo,tagline=tagline)
        except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 await interaction.response.send_message("Le compte avec ce pseudo n'existe pas !",ephemeral=True)
            else:
                raise
        iconId=random.randint(0,28)
        icon=f'http://ddragon.leagueoflegends.com/cdn/{version["v"]}/img/profileicon/{iconId}.png'
        profile=get_player_data(interaction.user.id)
        
        if profile == None:    
            
            player_data={
                "id":interaction.user.id,
                "puuid": me['puuid'],
                "icon":icon,
                "region":region.value,
                "statut":0
            }
            insert_player_data(player_data)
            await interaction.user.send("Profile Trouvé !")
            await LOF.profileLeagueOfLegends(interaction,pseudo,tagline,region)
            await interaction.user.send("Veuillez confirmer votre compte en modifiant votre icone par celui ci : ")
            await interaction.user.send(icon)
            await interaction.user.send("Valider ici:", view=ViewValidator())
        else :
            if profile[4]==0:
                await interaction.user.send("Vous avez déjà un compte en train d'être lié !")
                await interaction.user.send(profile[str(interaction.user.id)]["icon"])
                await interaction.user.send("Valider ici :", view=ViewValidator())
            else:
                await interaction.response.send_message("Vous avez déjà un compte lié !",ephemeral=True)
            
        
            
@bot.tree.command(name="supprimer_mon_profil")
async def del_profile(interaction:discord.Interaction):
    etat=delete_player_data(interaction.user.id)
    if etat==0:
        await interaction.response.send_message("Vous n'avez pas lié de compte !",ephemeral=True)
    else :
        
        await interaction.response.send_message("Votre compte a bien été supprimé !",ephemeral=True)

@bot.tree.command(name="suivre_profil")
@app_commands.choices(region=choixRegion)
async def add_profile_liste(interaction:discord.Interaction,pseudo:str,tagline:str,region:app_commands.Choice[str]):
   
        try:
            lol_watcher.accountV1.by_riotid(region=LOF.regionForRiotId(region.value),summoner_name=pseudo,tagline=tagline)
        except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 await interaction.response.send_message("Le compte avec ce pseudo n'existe pas !",ephemeral=True)
            else:
                raise
        
        liste=get_player_liste()
        trouvé=False
        if liste != None:
            for pseudoL in liste:
                if pseudoL==pseudo :
                    trouvé=True
            
        if trouvé==False :    
            
            player_data={
                "pseudo":pseudo,
                "tagline":tagline,
                "region":region.value,

            }
            insert_player_liste(player_data)
            await interaction.response.send_message("Profil ajouté !",ephemeral=True)
          
       
        else :
                await interaction.response.send_message("Ce profil est déjà suivit !",ephemeral=True)

@bot.tree.command(name="suppr_profil_suivit")
@app_commands.choices(region=choixRegion)
async def del_profile_liste(interaction:discord.Interaction,pseudo:str,tagline:str,region:app_commands.Choice[str]):
    player_data={
                "pseudo":pseudo,
                "tagline":tagline,
                "region":region.value,
    }
    etat=delete_player_liste(player_data)
    if etat==0:
        await interaction.response.send_message("Ce profil n'est pas dans la base de donnée!",ephemeral=True)
    else :
        
        await interaction.response.send_message("Ce profil a bien été supprimé !",ephemeral=True)

async def verif_game_en_cours():
    liste = get_player_liste()
    guild = bot.get_guild(KARAN_ID)
    guildGuuruu=bot.get_guild(1282820405626671164)
    salon = guild.get_channel(1283540354523463701)
    salonGuuruu=guildGuuruu.get_channel(1320482473217490975)
    gameDejaSend = []

    for gameId in liste:
        gameDejaSend.append((int)(gameId[4]))
    if liste is None:
        return
    
    for i in liste:
        puuid, region = getPuuidRegion(None, i[1], i[2], i[3])
        try:
            cg = lol_watcher.spectator.by_puuid(region, puuid)

            
            if (cg["gameId"] not in gameDejaSend) and (cg["gameQueueConfigId"] != 1700) :
                gameDejaSend.append(cg["gameId"])
                player_data = {
                    "pseudo": i[1],
                    "tagline": i[2],
                    "derniereGame": cg["gameId"],
                }

                update_derniereGame(player_data)
                regionId = LOF.regionForRiotId(region)
                image = await creer_image_avec_reessai(cg, regionId, region)
                img_bytes = BytesIO()
                image.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                await salon.send(file=discord.File(img_bytes, filename="Partie_En_Cours.png"))
                await salonGuuruu.send(file=discord.File(img_bytes, filename="Partie_En_Cours.png"))
        except ApiError as err:
            status_code = err.response.status_code
            if status_code == 429:
                print("Quota de requête dépassé")
            else:
                pass
            
         
def getCode(cg):
    liste=[]
    for i in range ( len(cg["participants"])) :
        liste.append(str(cg["participants"][i]["summonerId"])+str(cg["participants"][i]["championId"]))   
    liste.sort()
    id=','.join(liste)
    hash_object = hashlib.sha256(id.encode('utf-8'))
    unique_id = int(hash_object.hexdigest(), 16)
    return unique_id % (10**8)

@bot.tree.command(name="profil")
@app_commands.choices(region=choixRegion)
async def lolp(interaction: discord.Interaction, pseudo: str = None, tagline: str = "euw", region: app_commands.Choice[str] = "euw1"):
    await LOF.profileLeagueOfLegends(interaction,pseudo,tagline,region)


@bot.tree.command(name="historique")
@app_commands.choices(region=choixRegion)
async def histo(interaction: discord.Interaction, pseudo: str = None, tagline: str = "euw", region: app_commands.Choice[str] = "euw1"):
   await  LOF.historiqueLeagueOfLegends(interaction,pseudo,tagline,region)

@bot.tree.command(name="partie_en_cours")
@app_commands.choices(region=choixRegion)
async def partieEnCours(interaction: discord.Interaction, pseudo: str = None, tagline: str = "euw", region: app_commands.Choice[str] = None):

    await LOF.partieEnCours(interaction, pseudo, tagline, region)

@bot.event
async def on_message(message):
    cheh=["https://tenor.com/view/nelson-monfort-cheh-i-hear-cheh-in-my-oreillette-gif-15977955","https://tenor.com/view/maskey-gif-17974418","https://tenor.com/view/wavesives-waves-ives-waves-ives-waves-cheh-gif-1692370554913806768","https://tenor.com/view/capitaine-groscheh-gros-cheh-cheh-m%C3%A9rit%C3%A9-mange-ton-seum-gif-12396020753961179573","https://tenor.com/view/cheh-bienfaits-duh-gif-12323680"]
    
    if (not message.author == bot.user) and (not message.author.bot) :
            
        file = discord.File(f"env/ranked-emblem/PALU.mp4", filename=f"PALU.mp4")
        

        if "palu"in message.content.lower().split():
            await message.channel.send(file=file)

        file3 = discord.File(f"env/ranked-emblem/junglediff.png", filename=f"junglediff.png")

        if "jungle diff"in message.content.lower():
            a=await message.channel.send(file=file3)
            await a.add_reaction("✅")
            await a.add_reaction("❌")
            
            
        if "cheh"in message.content.lower().split():
            await message.channel.send(random.choice(cheh))
            
        await bot.process_commands(message)
        
            
        if "merci zeri" in message.content.lower():
            
            await message.reply("Derien Bebou <:Eheh:1280080977418260483>")
            
        if "prankex" in message.content.lower().split():
            await message.channel.send("https://tenor.com/view/guuruu-prank-prankex-gif-19025746535426067")

            

@bot.event
async def on_member_update(before,after):
    guild=bot.get_guild(KARAN_ID)
    annonce =guild.get_channel(ANNONCE_CHAN)
    dansMonServ=False
    for i in guild.members:
        if i.id==after.id:
            dansMonServ = True
            

    if after.activity != None:
        if dansMonServ:
            if after.activity.type==discord.ActivityType.streaming : 
                await annonce.send(f"{before.name} est en live ! \n{after.activity.url}")
        

#CLEAR

 
@bot.command()
@commands.has_permissions(administrator = True)
async def clear(ctx , amount=5):
    await ctx.channel.purge(limit=amount + 1)


@bot.command()
@commands.has_permissions(administrator = True)
async def filtre(ctx , amount=5):
    guild=bot.get_guild(KARAN_ID)
    filtre =guild.get_channel(615128656049864734)
    await filtre.purge(limit=amount )
##########################################################################

#apod

async def apodAut():
    guild=bot.get_guild(KARAN_ID)
    salonNasa =guild.get_channel(SALON_NASA)
    await imageNasa(salonNasa)


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def apod(ctx):
    await imageNasa(ctx.message.channel)

async def imageNasa(channel):
    apod=nasa
    
    
    if apod.apod()["media_type"]=="image":
    
        embed=discord.Embed(title="Photo astronomique du jour !",
                description=f'Voici la photo du jour en astronomie !', 
                color=discord.Color.red()).set_thumbnail(
                url="https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png"
                ).set_image(url=apod.apod()["hdurl"])

        if "copyright" in apod.apod():

                embed.add_field(
                name="Auteur :", 
                value=f'{apod.apod()["copyright"]}', 
                inline=True
                )
        await channel.send(embed=embed)
    elif apod.apod()["media_type"]=="video":
        embed=discord.Embed(title="Vidéo astronomique du jour !",
                description=f'Voici la vidéo du jour en astronomie !', 
                color=discord.Color.red()).set_thumbnail(
                url="https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png"
                )

        if "copyright" in apod.apod():

                embed.add_field(
                name="Auteur :", 
                value=f'{apod.apod()["copyright"]}', 
                inline=True
                )
        
        await channel.send(embed=embed)
        await channel.send(apod.apod()["url"])
    
##########################################################################   


#cat

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def cat(ctx):
    link ="https://api.thecatapi.com/v1/images/search"
    f = urllib.request.urlopen(link)
    myfile = f.read()
    foto=json.loads(myfile)
    await ctx.message.channel.send(foto[0]["url"])
#dog

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def dog(ctx):
    link ="https://api.thedogapi.com/v1/images/search"
    f = urllib.request.urlopen(link)
    myfile = f.read()
    foto=json.loads(myfile)
    await ctx.message.channel.send(foto[0]["url"])

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def pat(ctx):
    
    await ctx.message.channel.send(getRandomGIf("pat pat"))
##########################################################################
#SAY


@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def say(ctx):
    
        mesg = str(" ".join(ctx.message.content.split()[1:]))
        await ctx.message.delete()
        await ctx.message.channel.send(mesg)
##########################################################################


@bot.command()
async def pp(ctx):
    
   
    if  len(ctx.message.mentions)>0:
        user=ctx.message.mentions[0]
        await ctx.message.channel.send(user.display_avatar)

    else:
        
        await ctx.message.channel.send(ctx.author.display_avatar)
@bot.command()
async def ppdebase(ctx):
    
   
    if  len(ctx.message.mentions)>0:
        user=ctx.message.mentions[0]
        await ctx.message.channel.send(user.avatar)

    else:
        
        await ctx.message.channel.send(ctx.author.avatar)

@bot.command()
async def ppserv(ctx):
    await ctx.channel.send(ctx.guild.icon)

@bot.command()
async def banner(ctx):
    
   
    if  len(ctx.message.mentions)>0:
        user=ctx.message.mentions[0]
        usez =await bot.fetch_user(user.id)
        if usez.banner==None:
            await ctx.channel.send("N'a pas de banniere")
        else:
            await ctx.message.channel.send(usez.banner)

    else:
        usez =await bot.fetch_user(ctx.author.id)
        if usez.banner==None:
            await ctx.channel.send("N'a pas de banniere")
        else:
            await ctx.message.channel.send(usez.banner)


        
##########################################################################        

         
#SPAM

        
@bot.command()
@commands.has_permissions(administrator = True)

async def spam(ctx):
        
        
        msg =int(ctx.message.content.split()[1])
        if msg<=100:
            await ctx.message.delete()
            spam =str(" ".join(ctx.message.content.split()[2:]))
            for msg in range(msg):
                await ctx.message.channel.send(spam)

            await ctx.message.channel.send("https://tenor.com/view/jigm%C3%A9-hearthstone-travail-termin%C3%A9-mdr-mecredi-des-r%C3%A9ponse-gif-17412853")
        else:
            await ctx.message.channel.send("https://tenor.com/view/mister-v-encore-beaucoup-talking-still-thats-a-lot-there-right-gif-16825265")
    



##########################################################################

#BAN UNBAN

        
@bot.command()
@commands.has_permissions(administrator = True)
async def prison(ctx,member: discord.Member):

    
    with open('dossierJson/role.json', 'r') as f:
        users = json.load(f)

    nbrole= len(member.roles)

    await update_data(users, member,[])
    await add_role(users, member,nbrole)

    nbrole2= nbrole-1
    while(nbrole2>=1) :
        await member.remove_roles(member.roles[nbrole2])
        nbrole2=nbrole2-1
    role = discord.utils.get(ctx.message.guild.roles, name = "🔗|Prisonnier")
    await member.add_roles(role)    
    with open('dossierJson/role.json', 'w') as f:
            json.dump(users, f)
    await ctx.message.channel.send(f'{member.name} a été envoyé en prison. ^^')
    
async def add_role(users,user,nbrole):
    for i in range(1,nbrole):
        
        users[f'{user.id}']["roles"].append(str(user.roles[i]))

async def update_data(users, user,role):
    if not f'{user.id}' in users:
        users[f'{user.id}'] = {}
        users[f'{user.id}']["roles"] = role



@bot.command()   
@commands.has_permissions(administrator = True)
async def liberer(ctx, member: discord.Member):
    with open('dossierJson/role.json', 'r') as f:
        users = json.load(f)
      
    role = discord.utils.get(ctx.message.guild.roles, name = "🔗|Prisonnier")
    await member.remove_roles(role)
              
    await ctx.message.channel.send(f'{member.name} a été libéré. ^^')
    
    a=len(users[f'{member.id}']["roles"])    
    for i in range(a):
        b= users[f'{member.id}']["roles"][i]
        roled = discord.utils.get(ctx.message.guild.roles, name = b)
        await member.add_roles(roled)
    users[f'{member.id}']["roles"].clear()
    with open('dossierJson/role.json', 'w') as f:
            json.dump(users, f)
##########################################################################

#SNIPE

@bot.event
async def on_message_delete(message):
    if message.guild.id==KARAN_ID:
        with open("dossierJson/logs.json", "r") as f:
            users = json.load(f)
        msg = message.content
        msgAuthor = str(message.author.id)
        users["dernierMSG"] = {}
        users["dernierMSG"]["MSG"]=[msg,msgAuthor]

        with open("dossierJson/logs.json","w") as f :
            json.dump(users,f)


@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def snipe(ctx):
    if ctx.guild.id==KARAN_ID:
        with open("dossierJson/logs.json", "r") as f:
            users = json.load(f)
        
        await ctx.message.channel.send(f'Le dernier message supprimé est : **"{users["dernierMSG"]["MSG"][0]}"** You got sniped bro <@!{users["dernierMSG"]["MSG"][1]}>')
        await ctx.message.channel.send("https://tenor.com/view/stewie-gun-sniper-gif-14401284")

##########################################################################

#BAN

@bot.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.message.channel.send(f'{member} a été ban !') 
##########################################################################





            
        
        
#VOICE CHANNEL

@bot.event
async def on_voice_state_update(member,before,after):
    if not after.channel==None:

        if after.channel.id ==CHAN_VOC or after.channel.id==1235199112257994792 :
            if after.channel.id ==CHAN_VOC:
                chan = await after.channel.clone(name=f'◜⏳◞{member.display_name}')
            else :
                chan = await after.channel.clone(name=f'◜⏳◞Gaming Session')
            await member.move_to(chan)


    if before.channel:
            if "◜⏳◞" in before.channel.name :
                if len(before.channel.members)==0:
                    await before.channel.delete()
#help
##########################################################################
@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def help(ctx):
    file = discord.File(f"env/ranked-emblem/zeri3.gif", filename=f"zeri3.gif")
    embed=discord.Embed(title="Help Menu Zeri",
    description=f'{ctx.author.name} voici toutes les commandes disponibles avec Zeri ! ', 
    color=discord.Color.green()).add_field(
    name="-apod", 
    value="Vous envoie la derniere photo astronomique du jour !", 
    inline=False
    ).add_field(
    name="-cat", 
    value="Envoie une image aléatoire de chat.",
    inline=False
    ).add_field(
    name="-dog", 
    value="Envoie une image aléatoire de chien." ,
    inline=False
    ).add_field(
    name="-snipe", 
    value="Permet de snipe le dernier message supprimer par n'importe quel utilisateur." ,
    inline=False
    ).add_field(
    name="-lolp [Pseudo]", 
    value="Renvoie le profile League of legends." ,
    inline=False
    ).add_field(
    name="-histo [Pseudo]", 
    value="Renvoie l'historique des 20 dernières partie de League of legends." ,
    inline=False
    ).add_field(
    name="-prison [pseudo] (admin)", 
    value="Envoie en prison la personne." ,
    inline=False
    ).add_field(
    name="-liberer [pseudo] (admin)", 
    value="Libere la personne de la prison." ,
    inline=False
    ).add_field(
    name="-ban [pseudo] (admin)",
    value="Vous permet de ban la peronne.",
    inline=False
    ).add_field(
    name="-clear [X] (admin)",
    value="Vous permet de supprimer X nombres de messages.",
    inline=False
    ).add_field(
    name="-spam [X] [message] (admin)",
    value="Vous permet de spam X nombres de messages.",
    inline=False
    ).add_field(
    name="-say [MESSAGE] (admin)", 
    value="Permet de parler a travers le bot !",
    inline=False
    ).set_image(url="attachment://zeri3.gif")

    await ctx.message.channel.send(embed=embed,file=file)
##########################################################################

@bot.event
async def on_member_join(member):
    
    if member.guild.id==KARAN_ID:

        image =creerImageBVN(member,"Bienvenue")
      

        img_bytes=BytesIO()
        image.save(img_bytes,format='PNG')
        img_bytes.seek(0)
     

        channel=discord.utils.get(member.guild.channels, id=CHAN_BVN)
        role = discord.utils.get(member.guild.roles, id=ROLE_NEANTIN)
        role2= discord.utils.get(member.guild.roles, id=ROLE_FAILLE)
      
        await channel.send(file=discord.File(img_bytes, filename='bienvenue.png'))
        await member.add_roles(role)
        await member.add_roles(role2)
       



@bot.event
async def on_member_remove(member):
    if member.guild.id==KARAN_ID:

        image =creerImageBVN(member,"Aurevoir")

        img_bytes=BytesIO()
        image.save(img_bytes,format='PNG')
        img_bytes.seek(0)
        channel=discord.utils.get(member.guild.channels, id=CHAN_BVN)
        await channel.send(file=discord.File(img_bytes, filename='aurevoir.png'))
      

##########################################################################



@bot.event
async def  on_raw_reaction_remove(payload):
    #role = discord.utils.get(emoji.member.guild.roles, id=658408130593423371)
    guild = discord.utils.find(lambda g: g.id == payload.guild_id, bot.guilds)
    member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
##########################################################################    
##########################################################################    
bot.event
async def on_command_error(ctx, error):
	print(error)



        
@bot.command()

async def pick(ctx):
    link =f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/data/fr_FR/champion.json'
    f = urllib.request.urlopen(link)
    myfile = f.read()
    champ=json.loads(myfile)
    
    liste= list(champ["data"].keys())
    nbAleatoire=random.randint(0,len(liste))
    champAleatoire=liste[nbAleatoire]
    
    chp=f'https://ddragon.leagueoflegends.com/cdn/{version["v"]}/img/champion/{champAleatoire}.png'
    
    
    embed = discord.Embed(title="Pick Aléatoire",description='Voici le champion aléatoire :',color=discord.Color.red()).set_thumbnail(url=chp
            ).add_field(name="Nom", value=champAleatoire)
    
    await ctx.message.channel.send(embed=embed)
    
        




    

    



@bot.event
async def on_command_error(ctx, error):
     if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send('Ahahaha  t\'as pas les perms <:kekw:1079185133573255210>')
        await ctx.channel.send("https://tenor.com/view/counter-i-dont-gived-you-permission-gif-23613918")




@bot.command()
@commands.cooldown(1, 900, commands.BucketType.user)
async def imposteur(ctx):
    with open('dossierJson/imposteur.json','r') as f :
        users = json.load(f)
    users[f'{ctx.author.id}']={"game":"true"}
    roles=["Imposteur","Droide","Serpentin","Double-face","Super-héros"]
    task=[
            "Flash dans le vide",
            "Back",
            "Dive l'ennemi le plus proche",
            "Va voler le buff de ton jungle (le canon d'un de tes laners si tu es jungler)",
            "Prend un fight en utilisant aucun sort !",
            "Doit aller sur une lane ( split push )",
            "Doit revendre un objet et en acheter un autre",
            "Tu n'as plus le droit de prendre les cs range ( si tu es jg tu n'as plus le droit de prendre tes loups et corbin )",
            "Engage un fight et te plaindre de la team apres",
            "Reste caché dans un buisson pendant 30 secondes",
            "Suivre l'ennemi jusqu’à sa base",
            "Ne pas toucher aux sbires canon",
            "Prends des items totalement inutiles pour ton champion",
            "Pose une ward dans ta propre base",
            "Essayez d'aider un ennemi",
            "Dodge les compétences de tes alliés",
            "Insta-back après avoir quitté la base"
           
        ]
    doubleface=["Gentil","Imposteur"]
    if len(ctx.message.raw_mentions)==5:
        for i in ctx.message.raw_mentions:
            role =random.choice(roles)
            roles.remove(role)
            user= bot.get_user(i)
            users[f'{ctx.author.id}'][role]=user.id
            match role:
                case "Imposteur":
                    await user.send(f'{user.name} Vous êtes {role} \n Faire perdre la game sans se faire démasquer ')
                case "Droide":
                    await user.send(f'{user.name} Vous êtes {role} \n Gagner la game en suivant les instructions reçues ')
                case "Serpentin":
                    await user.send(f'{user.name} Vous êtes {role} \n Gagner la game en ayant le plus de morts et de dégâts de sa team')
                case "Double-face":
                    await user.send(f'{user.name} Vous êtes {role} \n Change de rôle aléatoirement. Doit gagner la game en tant que gentil ou perdre en imposteur')
                case "Super-héros":
                    await user.send(f'{user.name} Vous êtes {role} \n Gagner la game en ayant le plus de dégâts, d\'assistances et de kills.')
                case _:
                    await user.send("Feur")
        with open('dossierJson/imposteur.json','w') as f :
            json.dump(users,f)
        
        with open('dossierJson/imposteur.json','r') as f :
            jeu = json.load(f)
        boucle=jeu[str(ctx.author.id)]["game"]
        await asyncio.sleep(300)
        while(boucle=="true"):
            with open('dossierJson/imposteur.json','r') as f :
                jeu = json.load(f)
            boucle=jeu[str(ctx.author.id)]["game"]
            if jeu[str(ctx.author.id)]["game"]=="true":
                user= bot.get_user(jeu[str(ctx.author.id)]["Droide"])
                user2= bot.get_user(jeu[str(ctx.author.id)]["Double-face"])
                await user2.send(random.choice(doubleface))
                await user.send(random.choice(task))
                timer = random.randint(180,300)
                await asyncio.sleep(timer)
        
         
    else :
        await ctx.channel.send("Le nombre de participant n'est pas valide (5)")    
        
@bot.command()
async def fin(ctx):
    with open('dossierJson/imposteur.json','r') as f :
        jeu = json.load(f)
    jeu[str(ctx.author.id)]["game"]="false"
    with open('dossierJson/imposteur.json','w') as f :
            json.dump(jeu,f)
    await ctx.channel.send("La partie est terminé voici la liste des roles : ")
    for key,value in jeu[str(ctx.author.id)].items():
        
        if key!="game":
            user= bot.get_user(jeu[str(ctx.author.id)][key])
            await ctx.channel.send(f'{user.name} : {key}')
    jeu[str(ctx.author.id)].clear()
    jeu[str(ctx.author.id)]["game"]="false"
    with open('dossierJson/imposteur.json','w') as f :
            json.dump(jeu,f)
                
@bot.command()
@commands.has_permissions(administrator = True)
async def leave(ctx):
    if ctx.author.id==517231233235812353:
        serv= bot.get_guild(int(ctx.message.content.split()[1:][0]))
        await serv.leave()
        await ctx.channel.send(f'J\'ai quitté le serveur : {serv}!')     
        
        
        
@bot.command()
@commands.has_permissions(administrator = True)
async def poll(ctx, question="Quelle est votre couleur préférée ?"):
    try:
       
       

        poll = discord.Poll(question, duration=timedelta(hours=1))
        poll.add_answer(text="Bleu")
        poll.add_answer(text="Rouge")

        message =await ctx.send(poll=poll)
        print(message.id)
        with open("test.json","w") as f:
            json.dump((str)(message.id),f)
        temps = timedelta(seconds=10)
        sec = timedelta(seconds=1)
        while temps>timedelta(seconds=0):
            await asyncio.sleep(1)
            temps=temps-sec 
            if temps==timedelta(seconds=0):
                await poll.end()

       
        
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la création du sondage : {e}")

@bot.command()
async def checkpoll(id):
    try:
        print(id)
        channel= bot.get_channel(615128656049864734)
        message = await channel.fetch_message(id)
        poll = message.poll
        if poll.is_finalised():
            await channel.send(poll.get_answer(1).vote_count)
    except Exception as e :
        print(e)

if __name__ == "__main__":
    asyncio.run(bot.start(os.getenv('TOKEN')))

 