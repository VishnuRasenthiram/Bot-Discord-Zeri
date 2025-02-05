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
from nasaapi import Client as ClientNasa
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
from zeriMoney import *
from sauvegardeProfil   import *
from suivitProfil import *
from interaction import *
from imposteur import *
from ladderLol import *
from typing import Union
from zeriA import *
load_dotenv()
##########################################################################

#API



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

Zeri_Money=ZeriMoney(bot)

lol_watcher = LolWatcher(os.getenv('RIOT_API'))
nasa=ClientNasa(api_key=os.getenv('NASA_API'))

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
GUURUU_ID=1282820405626671164
CHANNEL_SUIVIT=1283540354523463701
CHANNEL_SUIVIT_GUURUU=1320482473217490975

##################################################################################################################################
##################################################################################################################################


##################################################################################################################################
##################################################################################################################################

def getBot():
    return bot


##########################################################################
#MAIN


verif_lock = asyncio.Lock()

@tasks.loop(minutes=5)
async def periodic_check():
    async with verif_lock:
        try:
            await verif_game_en_cours()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                print("Service indisponible, attente...")
                await asyncio.sleep(60)
            else:
                print(f"Erreur HTTP: {e}")
        except Exception as e:
            print(f"Erreur: {e}")

verif_lock_ladder = asyncio.Lock()
@tasks.loop(minutes=60)
async def periodic_check_ladder():
    async with verif_lock_ladder:
        try:
            await update_ladder()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                print("Service indisponible, attente...")
                await asyncio.sleep(60)
            else:
                print(f"Erreur HTTP: {e}")
        except Exception as e:
            print(f"Erreur: {e}")
            
            
async def verif_game_en_cours():
        liste = get_player_liste()
        gameDejaSend = []
        if liste is None:
            return

        for gameId in liste:
            gameDejaSend.append(int(gameId[3]))

        for player in liste:
            puuid, region = player[1], player[2]

            for _ in range(3):
                try:
                    cg = lol_watcher.spectator.by_puuid(region, puuid)
                    if cg["gameId"] not in gameDejaSend and cg["gameQueueConfigId"] != 1700:
                        gameDejaSend.append(cg["gameId"])
                        player_data = {"puuid": puuid, "derniereGame": cg["gameId"]}
                        update_derniereGame(player_data)

                        regionId = LOF.regionForRiotId(region)
                        image = await creer_image_avec_reessai(cg, regionId, region)

                        img_bytes = BytesIO()
                        image.save(img_bytes, format="PNG")
                        img_bytes.seek(0)
                        file = discord.File(img_bytes, filename="Partie_En_Cours.png")

                        channelListe = list(get_player_listeChannel(puuid))
                        for channelId in channelListe:
                            channel = bot.get_channel(int(channelId))
                            if channel:
                                img_copy = BytesIO(img_bytes.getvalue()) 
                                await channel.send(file=discord.File(img_copy, filename="Partie_En_Cours.png"))
                    break
                except ApiError as e:
                    if e.response.status_code == 404:
                        break
                except Exception as er:
                    print(f"Erreur inattendue : {er}")
                    break
##########################################################################
async def update_ladder():
    ladder = get_listChannelLadder()

    for channel in ladder:
        channel_id = int(channel[0])
        channel = bot.get_channel(channel_id)
        if channel:
            listeJoueur= get_ladder_profile(channel_id)
            if listeJoueur:
                try:
                    message = await channel.fetch_message(get_messageId_listChannelLadder(channel_id))
                    await message.edit(embed=await create_ladder(listeJoueur))
                except discord.errors.NotFound:
                    message = await channel.send(embed=await create_ladder(listeJoueur))
                    update_messageId_listChannelLadder(channel_id, message.id)
                
    
                    

                    






@bot.event
async def on_ready():
    print(current_time)
    scheduler.start()
    try:
        periodic_check.start()
        periodic_check_ladder.start()
        synced= await bot.tree.sync()
    except Exception as e:
        print(e)
    print("le bot est pret")
    


async def changementIconeServeur():

    clear_history()

    if not hasattr(changementIconeServeur, "iconNuit"):
        with open("env/ranked-emblem/Karan_nuit.png", 'rb') as n:
            changementIconeServeur.iconNuit = n.read()
    if not hasattr(changementIconeServeur, "iconJour"):
        with open("env/ranked-emblem/Karan_jour.png", 'rb') as j:
            changementIconeServeur.iconJour = j.read()

    guild = bot.get_guild(KARAN_ID)
    pays = "Europe/Paris"
    now2 = datetime.now(pytz.timezone(pays))
    current_time = now2.strftime("%H:%M")
    if current_time > "22:00" or current_time < "10:00":
        await guild.edit(name="Karan 🌙")
        await guild.edit(icon=changementIconeServeur.iconNuit)
    else:
        await apodAut()
        await guild.edit(name="Karan 🍁")
        await guild.edit(icon=changementIconeServeur.iconJour)
       
    
scheduler = AsyncIOScheduler()
scheduler.add_job(changementIconeServeur, CronTrigger(hour=10, minute=1))
scheduler.add_job(changementIconeServeur, CronTrigger(hour=22, minute=1))
scheduler.add_job(Zeri_Money.update_daily, CronTrigger(hour=0, minute=0))
##########################################################################



@bot.tree.command(name="ping")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message("Pong! Latence: {}ms".format(round(bot.latency * 1000, 1)))
    
@bot.tree.command(name="sauvegarder_mon_profil")
@app_commands.choices(region=choixRegion)
async def sauvegarderProfil(interaction:discord.Interaction,pseudo:str,region:app_commands.Choice[str]="euw1"):
       await  set_profile(interaction,pseudo,region)
                 
@bot.tree.command(name="supprimer_mon_profil")
async def supprimerProfil(interaction:discord.Interaction):
    await del_profile(interaction)

@bot.tree.command(name="suivre_profil")
@app_commands.choices(region=choixRegion)
async def suivreProfil(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
        await add_profile_liste(interaction,pseudo,channel,region)

@suivreProfil.autocomplete("channel")
async def type_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=choice.name, value=choice.value) for choice in generate_choices() if current.lower() in choice.name.lower()]

@bot.tree.command(name="suppr_profil_suivit")
@app_commands.choices(region=choixRegion)
async def supprimerProfilSuivit(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
       await  del_profile_liste(interaction,pseudo,channel,region)

@supprimerProfilSuivit.autocomplete("channel")
async def type_autocomplete(interaction: discord.Interaction, current: str):
    pseudo = interaction.namespace.pseudo
    if not pseudo:
        return []

    pseudo, tagline = await verifFormatRiotId(None, pseudo)
    if not pseudo:
        return []

    me, region = await getMe(None, pseudo, tagline, None)
    puuid = me["puuid"]
    chan = [app_commands.Choice(name="All", value="all")]

    channel_list_id = get_player_listeChannel(puuid)
    if not channel_list_id:
        return chan

    channel_list = []
    for id in channel_list_id:
        channel = bot.get_channel(int(id))
        if channel:
            channel_list.append(app_commands.Choice(name=channel.name, value=str(channel.id)))

    return [choice for choice in channel_list if current.lower() in choice.name.lower()]

@bot.tree.command(name="ajouter_channel_suivit")
async def ajouterChannelSuivit(interaction: discord.Interaction, channel:Union[discord.threads.Thread,discord.channel.TextChannel]):
    await addChannel(interaction,channel)


@bot.tree.command(name="suppr_channel_suivit")
async def supprimerChannelSuivit(interaction: discord.Interaction, channel:str):
   await delChannel(interaction,channel)
    
@supprimerChannelSuivit.autocomplete("channel")
async def type_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=choice.name, value=choice.value) for choice in generate_choices() if current.lower() in choice.name.lower()]

@bot.tree.command(name="ajouter_channel_ladder")
async def ajouterChannelLadder(interaction: discord.Interaction, channel:Union[discord.threads.Thread,discord.channel.TextChannel]):
    await addChannelLadder(interaction,channel)


@bot.tree.command(name="suppr_channel_ladder")
async def supprimerChannelLadder(interaction: discord.Interaction, channel:str):
   await delChannelLadder(interaction,channel)
    
@supprimerChannelLadder.autocomplete("channel")
async def type_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=choice.name, value=choice.value) for choice in generate_choicesLadder() if current.lower() in choice.name.lower()]

@bot.tree.command(name="add_to_ladder")
@app_commands.choices(region=choixRegion)
async def ajouterLadder(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
        await add_profile_listeLadder(interaction,pseudo,channel,region)

@ajouterLadder.autocomplete("channel")
async def type_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=choice.name, value=choice.value) for choice in generate_choicesLadder() if current.lower() in choice.name.lower()]

@bot.tree.command(name="delete_from_ladder")
@app_commands.choices(region=choixRegion)
async def supprimerProfilLadder(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
       await  del_profile_listeLadder(interaction,pseudo,channel,region)

@supprimerProfilLadder.autocomplete("channel")
async def type_autocomplete(interaction: discord.Interaction, current: str):
    pseudo = interaction.namespace.pseudo
    if not pseudo:
        return []

    pseudo, tagline = await verifFormatRiotId(None, pseudo)
    if not pseudo:
        return []

    me, region = await getMe(None, pseudo, tagline, None)
    puuid = me["puuid"]
    chan = [app_commands.Choice(name="All", value="all")]

    channel_list_id = get_liste_channel_ladder_joueur(puuid)

    if not channel_list_id:
        return chan

    channel_list = []
    for id in channel_list_id:

        channel = bot.get_channel(int(id[0]))
        if channel:
            channel_list.append(app_commands.Choice(name=channel.name, value=str(channel.id)))      
    return [choice for choice in channel_list if current.lower() in choice.name.lower()]
@bot.tree.command(name="profil_lol")
@app_commands.choices(region=choixRegion)
async def lolp(interaction: discord.Interaction, pseudo: str = None, region: app_commands.Choice[str] = "euw1"):  
    puuid,region=await getPuuidRegion(interaction,pseudo,region)
    await LOF.profileLeagueOfLegends(interaction,puuid,region)


@bot.tree.command(name="historique")
@app_commands.choices(region=choixRegion)
async def histo(interaction: discord.Interaction, pseudo: str = None, region: app_commands.Choice[str] = "euw1"):
    puuid,region=await getPuuidRegion(interaction,pseudo,region)
    await  LOF.historiqueLeagueOfLegends(interaction,puuid,region)

@bot.tree.command(name="partie_en_cours")
@app_commands.choices(region=choixRegion)
async def partieEnCours(interaction: discord.Interaction, pseudo: str = None, region: app_commands.Choice[str] = None):
    puuid,region=await getPuuidRegion(interaction,pseudo,region)
    await LOF.partieEnCours(interaction,puuid, region)



@bot.event
async def on_message(message):
    cheh=["https://tenor.com/view/nelson-monfort-cheh-i-hear-cheh-in-my-oreillette-gif-15977955","https://tenor.com/view/maskey-gif-17974418","https://tenor.com/view/wavesives-waves-ives-waves-ives-waves-cheh-gif-1692370554913806768","https://tenor.com/view/capitaine-groscheh-gros-cheh-cheh-m%C3%A9rit%C3%A9-mange-ton-seum-gif-12396020753961179573","https://tenor.com/view/cheh-bienfaits-duh-gif-12323680"]
    
    if (not message.author == bot.user) and (not message.author.bot) :
            
        file = discord.File(f"env/ranked-emblem/PALU.mp4", filename=f"PALU.mp4")
        fileG2 = discord.File(f"env/ranked-emblem/toohless.mp4", filename=f"toohless.mp4")
        file3 = discord.File(f"env/ranked-emblem/junglediff.png", filename=f"junglediff.png")

        if bot.user in message.mentions:
            message_content = message.content.replace(f"<@{bot.user.id}>", "").strip().lower()
            await message.reply(send_message_with_memory(message.author.name,message_content))

        if "g2 win" in message.content.lower():
            await message.channel.send(file=fileG2)

        if "palu"in message.content.lower().split():
            await message.channel.send(file=file)

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
        
        await Zeri_Money.add_xp(message,calculer_xp(message))

last_message_time = {}
COOLDOWN = 10      
def calculer_xp(message):
    user_id = message.author.id
    current_time = time.time()
    
    if user_id in last_message_time:
        elapsed_time = current_time - last_message_time[user_id]
        if elapsed_time < COOLDOWN:
            return 0 
    
    last_message_time[user_id] = current_time
    
    longueur_message = len(str(message.content.lower()).lstrip())
    coef = math.log(longueur_message + 1) * 10
    return min(int(coef), 100)

@bot.tree.command(name="profil",description="Affiche le profil de l'utilisateur")
async def profil( interaction: discord.Interaction):
    await interaction.response.defer()
    await Zeri_Money.profile(interaction)

@bot.tree.command(name="leaderboard", description="Affiche le classement des utilisateurs en fonction de leur solde")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    await Zeri_Money.leaderboard(interaction)
@bot.tree.command(name="leaderboard_level", description="Affiche le classement des utilisateurs en fonction de leur niveau")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    await Zeri_Money.leaderboard_level(interaction)

@bot.tree.command(name="daily", description="Réclame votre récompense quotidienne")
async def daily(interaction: discord.Interaction):
    await interaction.response.defer()
    await Zeri_Money.daily(interaction)

@bot.tree.command(name="balance", description="Affiche le solde de l'utilisateur")
async def balance( interaction: discord.Interaction):
    await interaction.response.defer()
    await Zeri_Money.balance(interaction)


choixPOF=[app_commands.Choice(name="Pile", value="Pile"),
    app_commands.Choice(name="Face", value="Face")]
@bot.tree.command(name="pile_ou_face")
@app_commands.choices(choix=choixPOF)
async def pile_ou_face(interaction: discord.Interaction, mise: int, choix: app_commands.Choice[str]):
    await interaction.response.defer()
    await Zeri_Money.pile_ou_face(interaction, mise, choix.value)

@bot.event
async def on_member_update(before,after):
    guild=bot.get_guild(KARAN_ID)
    annonce =guild.get_channel(ANNONCE_CHAN)
    dansMonServ=False
    for i in guild.members:
        if i.id==after.id:
            dansMonServ = True
            break
            

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

 



@bot.tree.command(name="interaction")
@app_commands.choices(type=choixInteraction)
async def interaction(interaction: discord.Interaction, type:app_commands.Choice[str], membre: discord.Member):
    await interaction.response.defer()
    embed= discord.Embed(description=generate_interaction_text(type.value, interaction.user.mention, membre.mention), color=discord.Color.random())
    embed.set_image(url=getRandomGIf(type.value))
    await interaction.delete_original_response()
    await interaction.channel.send(membre.mention,embed=embed)

@bot.tree.command(name="action")
@app_commands.choices(type=choixAction)
async def interaction(interaction: discord.Interaction, type:app_commands.Choice[str]):
    await interaction.response.defer()
    embed= discord.Embed(description=generate_interaction_text(type.value, interaction.user.mention,None), color=discord.Color.random())
    embed.set_image(url=getRandomGIf(type.value))
    await interaction.delete_original_response()
    await interaction.channel.send(embed=embed)
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
    impo(ctx)
        
@bot.command()
async def fin(ctx):
    fi(ctx)
                
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

 