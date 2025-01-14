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
from zeriMoney import *
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

Zeri_Money=ZeriMoney(bot)

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




##########################################################################
#MAIN
print(current_time)

verif_lock = asyncio.Lock()

@tasks.loop(seconds=60)
async def periodic_check():
    async with verif_lock:
        try:
            await verif_game_en_cours()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                await asyncio.sleep(1)
            else:
                raise e

@periodic_check.before_loop
async def before_periodic_check():
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    scheduler.start()
    print("le bot est pret")
    try:
        periodic_check.start()
        synced= await bot.tree.sync()
    except Exception as e:
        print(e)
    
    

   
    




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
scheduler.add_job(Zeri_Money.update_daily, CronTrigger(hour=0, minute=0))
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
        
async def getMe(interaction:discord.Interaction,pseudo,tagline,region):
    if not isinstance(region,Choice):
            region= Choice(name="defaut",value="euw1")
    try:
        me,region =lol_watcher.accountV1.by_riotid(region=regionForRiotId(region.value),summoner_name=pseudo,tagline=tagline),region.value
        return me,region
    
    except ApiError as err:
        if err.response.status_code == 429 :
                print("Quota de requête dépassé")
        elif err.response.status_code == 404:
            await interaction.response.send_message("Le compte avec ce pseudo n'existe pas !",ephemeral=True)

async def verifFormatRiotId(interaction:discord.Interaction,pseudo:str):
    tagline=None
    if pseudo!=None and pseudo.find("#")!=-1:
        pseudo,tagline=pseudo.lower().split("#")[0],pseudo.lower().split("#")[1]
    
    else:
        await interaction.response.send_message("Veuillez entrer votre pseudo avec le # !",ephemeral=True)
    return pseudo,tagline
async def getPuuidRegion(interaction:discord.Interaction,pseudo:str,region:str):
        if pseudo:
            pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
        if not(pseudo):
            
            profile=get_player_data(interaction.user.id)
        
            if profile!=None:
                
                if profile[4]==0:
                    await interaction.response.send_message("Vous n'avez pas confirmé le profil !",ephemeral=True)
                else :
                    puuid = profile[1]
                    region = profile[3]
                    
            else:
                await interaction.response.send_message("Veuillez entrer votre Riot ID comme ceci : Pseudo#0000\nVous avez la possibilité de lié votre compte via la commande : **/sauvegarder_mon_profil**",ephemeral=True)
        else:
            me,region=await getMe(interaction,pseudo,tagline,region)
            puuid=me["puuid"]


        return puuid,region            


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
async def set_profile(interaction:discord.Interaction,pseudo:str,region:app_commands.Choice[str]="euw1"):
   
        try:
            pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
            me,region=await getMe(interaction,pseudo,tagline,region)
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
                "region":region,
                "statut":0
            }
            insert_player_data(player_data)
            await interaction.response.send_message("Profile Trouvé !")
            await interaction.user.send("Veuillez confirmer votre compte en modifiant votre icone par celui ci : ")
            await interaction.user.send(icon)
            await interaction.user.send("Valider ici:", view=ViewValidator())
            await interaction.user.send("Pour annuler utilisez la commande : **/supprimer_mon_profil** ")
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
async def add_profile_liste(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
   
        try:
            pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
            me,region=await getMe(interaction,pseudo,tagline,region)
            puuid=me["puuid"]
        except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 await interaction.response.send_message("Le compte avec ce pseudo n'existe pas !",ephemeral=True)
        liste = get_player_liste()
        trouvé = True
        
        if liste:
            for puuidL in liste:
                if puuidL[1] == puuid and channel in ast.literal_eval(puuidL[4]):
                    trouvé = False
                    break
        
        if trouvé:
            for i in liste:
                if i[1] == puuid:
                    listeChan = list(ast.literal_eval(i[4]))
                    listeChan.append(channel)
                    update_player_listeChannel(puuid, listeChan)
                    trouvé = False
                    break
        
            if trouvé:
                listeChan = [channel]
                player_data = {
                    "puuid": puuid,
                    "region": region,
                    "listeChannel": str(listeChan)
                }
                insert_player_liste(player_data)
        
            await interaction.response.send_message("Profil ajouté !", ephemeral=True)
        else:
            await interaction.response.send_message("Ce profil est déjà suivi !", ephemeral=True)
@add_profile_liste.autocomplete("channel")
async def type_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=choice.name, value=choice.value) for choice in generate_choices() if current.lower() in choice.name.lower()]
 
async def getPuuidRegion(interaction:discord.Interaction,pseudo:str,region:str):
        if pseudo:
            pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
        if not(pseudo):
            
            profile=get_player_data(interaction.user.id)
        
            if profile!=None:
                
                if profile[4]==0:
                    await interaction.response.send_message("Vous n'avez pas confirmé le profil !",ephemeral=True)
                else :
                    puuid = profile[1]
                    region = profile[3]
                    
            else:
                await interaction.response.send_message("Veuillez entrer votre Riot ID comme ceci : Pseudo#0000\nVous avez la possibilité de lié votre compte via la commande : **/sauvegarder_mon_profil**",ephemeral=True)
        else:
            me,region=await getMe(interaction,pseudo,tagline,region)
            puuid=me["puuid"]


        return puuid,region            



def generate_choices_liste_player(puuid):
    liste_channel= get_player_listeChannel(puuid)
    return [app_commands.Choice(name=f"{i[1]}", value=f"{i[0]}") for i in liste_channel ]
#il faut une fonction pour supprimer un channel ou tous les channels et donc la personne de la liste

@bot.tree.command(name="suppr_profil_suivit")
@app_commands.choices(region=choixRegion)
async def del_profile_liste(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
    pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
    me,region=await getMe(interaction,pseudo,tagline,region)
    puuid=me["puuid"]
    player_data={
                "puuid":puuid,
                "region":region,
    }

    if channel=="all":
        etat=delete_player_liste(player_data)
    else:
        channelListe= list(get_player_listeChannel(puuid))
        if str(channel) in channelListe:
            channelListe.remove(channel)
            if len(channelListe)==0:
                delete_player_liste(player_data)
            etat=1
            update_player_listeChannel(player_data["puuid"],channelListe)
        else:
            etat=0
            
                
    if etat==0:
        await interaction.response.send_message("Ce profil n'est pas dans la base de donnée!",ephemeral=True)
    else :
        await interaction.response.send_message("Ce profil a bien été supprimé !",ephemeral=True)
@del_profile_liste.autocomplete("channel")
async def type_autocomplete(interaction: discord.Interaction, current: str):
    pseudo = interaction.namespace.pseudo
    pseudo, tagline = await verifFormatRiotId(None, pseudo)
    me, region = await getMe(None, pseudo, tagline, None)
    puuid = me["puuid"]
    chan = [app_commands.Choice(name="All", value="all")]

    channel_list_id = get_player_listeChannel(puuid)
    if channel_list_id is None:
        return chan
    channel_list = []
    for id in channel_list_id:
        channel = bot.get_channel(int(id))
        if channel:
            channel_list.append(app_commands.Choice(name=channel.name, value=str(channel.id)))

    chan = chan + [
        choice for choice in channel_list if current.lower() in choice.name.lower()
    ]
    return chan
     


async def verif_game_en_cours():
    liste = get_player_liste()
    gameDejaSend = []
    if liste is None:
        return

    for gameId in liste:
        gameDejaSend.append((int)(gameId[3]))
    
    for player in liste:
        puuid, region = player[1], player[2]
        try:
            cg = lol_watcher.spectator.by_puuid(region, puuid)
            if (cg["gameId"] not in gameDejaSend) and (cg["gameQueueConfigId"] != 1700) :
                player_data = {
                    "puuid": puuid,
                    "derniereGame": cg["gameId"],
                }

                regionId = LOF.regionForRiotId(region)
                image = await creer_image_avec_reessai(cg, regionId, region)
                img_bytes = BytesIO()
                image.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                file=discord.File(img_bytes, filename="Partie_En_Cours.png")

                channelListe= list(get_player_listeChannel(puuid))
                for channelId in channelListe:
                    channel=bot.get_channel(int(channelId))
                    await channel.send(file=file)
                    img_bytes.seek(0)
                gameDejaSend.append(cg["gameId"])
                update_derniereGame(player_data)
        except ApiError as err:
            status_code = err.response.status_code
            if status_code == 429:
                print("Quota de requête dépassé")
                pass
            else:
                pass


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

 
def generate_interaction_text(value, M1, M2):
    interaction_texts = {
        "hug anime": f"{M1} fait un câlin chaleureux à {M2} 🫂.",
        "run away anime": f"{M1} fuit {M2} 🏃💨.",
        "kiss anime": f"{M1} donne une bise à {M2} 💋.",
        "kiss romantic anime": f"{M1} embrasse tendrement {M2} ❤️.",
        "hold hands anime": f"{M1} prend doucement la main de {M2} 🤝.",
        "pat anime": f"{M1} tapote la tête de {M2} avec affection 🤗.",
        "warm smile anime": f"{M1} sourit chaleureusement à {M2} 😊.",
        "ignore anime": f"{M1} ignore complètement {M2} 🫥.",
        "punch anime": f"{M1} frappe {M2} de toute ses forces 🤜💥.",
        "push anime": f"{M1} pousse {M2} ✋.",
        "threaten anime": f"{M1} menace {M2} avec un regard intense ⚡.",
        "shout anime": f"{M1} crie en direction de {M2} 😡.",
        "stare anime": f"{M1} fixe {M2} avec insistance 👀.",
        "wink anime": f"{M1} fait un clin d’œil à {M2} 😉.",
        "gun shoot anime": f"{M1} piou piou pan pan pan sur {M2} 🔫.",
        "laught at anime": f"{M1} se fout de la gueule de {M2} 😆.",
        "shy anime": f"{M1} est gêné devant {M2} et rougit timidement 😳.",
        "cry anime": f"{M1} pleure à chaudes larmes devant {M2} 😭.",
        "pout anime": f"{M1} boude {M2} 🙁.",
        "drool anime": f"{M1} bave en regardant {M2} 🤤.",
        "feed anime": f"{M1} donne à manger à {M2} 🍲.",
        "sit anime": f"{M1} s’assoit tranquillement à côté de {M2} 🪑.",
        "sleep with anime": f"{M1} s’endort paisiblement à côté de {M2} 😴."
    }
    interaction_texts_none = {
        "cry anime": f"{M1} pleure à chaudes larmes 😭.",
        "shy anime": f"{M1} est gêné et rougit 😳.",
        "sleep anime": f"{M1} s’endort paisiblement 😴.",
        "bored anime": f"{M1} s’ennuie profondément🥱.",
        "drool anime": f"{M1} bave un peu en rêvassant 🤤.",
        "hungry anime": f"{M1} a faim et se tient le ventre 🍴.",
        "disappear anime": f"{M1} disparaît mystérieusement✨.",
        "depress anime": f"{M1} semble déprimer 😔.",
        "happy anime": f"{M1} est heureux😄.",
        "wake up anime": f"{M1} se réveille en sursaut😯.",
        "sit anime": f"{M1} s’assoit tranquillement, profitant du moment 🪑."
    }
    if M2 == None:
        return interaction_texts_none.get(value, f"Interaction inconnue de {M1} 🤔.")
    return interaction_texts.get(value, f"Interaction inconnue entre {M1} et {M2} 🤔.")
choixInteraction = [
    app_commands.Choice(name="Câlin", value="hug anime"),
    app_commands.Choice(name="Se moquer", value="laught at anime"),
    app_commands.Choice(name="Fuit", value="run away anime"),
    app_commands.Choice(name="Bise", value="kiss anime"),
    app_commands.Choice(name="Embrasse", value="kiss romantic anime"),
    app_commands.Choice(name="Prend par la main", value="hold hands anime"),
    app_commands.Choice(name="Pat", value="pat anime"),
    app_commands.Choice(name="Sourit", value="warm smile anime"),
    app_commands.Choice(name="Ignore", value="ignore anime"),
    app_commands.Choice(name="Frappe", value="punch anime"),
    app_commands.Choice(name="Pousse", value="push anime"),
    app_commands.Choice(name="Menace", value="threaten anime"),
    app_commands.Choice(name="Crie", value="shout anime"),
    app_commands.Choice(name="Fixe avec insistance", value="stare anime"),
    app_commands.Choice(name="Clin d’œil", value="wink anime"),
    app_commands.Choice(name="Tire", value="gun shoot anime"),
    app_commands.Choice(name="Gêné", value="shy anime"),
    app_commands.Choice(name="Pleure", value="cry anime"),
    app_commands.Choice(name="Boude", value="pout anime"),
    app_commands.Choice(name="Donne à manger", value="feed anime"),
    app_commands.Choice(name="S’assoit", value="sit anime"),
    app_commands.Choice(name="Dort", value="sleep with anime")
]

choixAction=[
    app_commands.Choice(name="Gêné", value="shy anime"),
    app_commands.Choice(name="S’ennuie", value="bored anime"),
    app_commands.Choice(name="Pleure", value="cry anime"),
    app_commands.Choice(name="Bave", value="drool anime"),
    app_commands.Choice(name="Affamé", value="hungry anime"),
    app_commands.Choice(name="Disparaît", value="disappear anime"),
    app_commands.Choice(name="Déprimé", value="depress anime"),
    app_commands.Choice(name="Heureux", value="happy anime"),
    app_commands.Choice(name="Dort", value="sleep anime"),
    app_commands.Choice(name="S’assoit", value="sit anime"),
    app_commands.Choice(name="Se reveille", value="wake up anime")
]

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

     

@bot.command()
async def testChann(ctx):

    channel= bot.get_channel(CHANNEL_SUIVIT)  
    print(dir(channel))


@bot.tree.command(name="ajouter_channel_suivit")
async def addChannel(interaction: discord.Interaction, channel:discord.channel.TextChannel):
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Vous devez être administrateur pour utiliser cette commande !", ephemeral=True
        )
    await interaction.response.defer()
    dataChannel = {
        "id": channel.id,
        "nom": channel.name
    }
    insert_listChannelSuivit(dataChannel)
    await interaction.followup.send("Channel ajouté avec succès !", ephemeral=True)
def generate_choices():
    liste_channel= get_listChannelSuivit()
    return [app_commands.Choice(name=f"{i[1]}", value=f"{i[0]}") for i in liste_channel ]

@bot.tree.command(name="suppr_channel_suivit")
async def delChannel(interaction: discord.Interaction, channel:str):
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Vous devez être administrateur pour utiliser cette commande !", ephemeral=True
        )
    await interaction.response.defer()
    delete_listChannelSuivit(channel)
    await interaction.followup.send("Channel supprimé avec succès !", ephemeral=True)
    
@delChannel.autocomplete("channel")
async def type_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=choice.name, value=choice.value) for choice in generate_choices() if current.lower() in choice.name.lower()]
    



if __name__ == "__main__":
    asyncio.run(bot.start(os.getenv('TOKEN')))

 