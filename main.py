import discord
from riotwatcher import LolWatcher, ApiError
from discord.ext import commands
import asyncio
from datetime import date, datetime
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

load_dotenv()
##########################################################################

#API

nasa=Client(api_key=os.getenv('NASA_API'))
lol_watcher = LolWatcher(os.getenv('RIOT_API'))


##########################################################################

default_intents = discord.Intents.all()
client = discord.Client(intents=default_intents)
bot = commands.Bot(command_prefix = "-", description = "Bot d'Aladdin",intents=discord.Intents.all(), case_insensitive=True,help_command=None)

pays = "Europe/Paris"

now2 = datetime.now(pytz.timezone(pays))
now = datetime.now()
current_day= now.strftime("%d/%m/%Y")
currect_daay=now2.strftime("%A")
current_time = now2.strftime("%H:%M")
print(currect_daay)

my_region = 'euw1'
version = lol_watcher.data_dragon.versions_for_region("euw1")
##########################################################################
#CONSTANTES

antifeur=[133228507873411072,300928722939281409,688997212113600586,320579380390658048]
antispam=[133228507873411072,632906154003136512]
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
FLAMEID=0
GUURUUID=185191654255362048
ALADID=517231233235812353
##########################################################################
#MAIN
print(current_time)

@bot.event
async def on_ready():
    guild=bot.get_guild(614728233497133076)
    karantest =guild.get_channel(615128656049864734)
    guildguuruu=bot.get_guild(332580555872927746)
    guuruuchan=guildguuruu.get_channel(CHAN_LOLDLE)
    guuruuchanflame=guildguuruu.get_channel(CHAN_FLAME)
    print("le bot est pret")
    try:
        synced= await bot.tree.sync()
        print(f"Synced {synced} commands")
    except Exception as e:
        print(e)
    
    
	
    while True:
       
        
        pays = "Europe/Paris"

        now2 = datetime.now(pytz.timezone(pays))
        now = datetime.now()
        current_day= now.strftime("%d/%m/%Y")
        currect_daay=now2.strftime("%A")
        current_time = now2.strftime("%H:%M")
        
            
        
        if current_time>"22:00" or current_time<"10:00": 
            await guild.edit(name ="Karan 🌙")
        else:
            await guild.edit(name="Karan 🍁")
            
        if current_time>="04:00"and current_time <"04:05" :
            await guuruuchan.send("N'oubliez pas de faire votre Loldle du jour !")
            await guuruuchan.send("https://loldle.net/")
        if currect_daay in ["Monday","Tuesday","Wednesday","Thursday"] and (current_time>="20:00" and current_time<"20:05"):
            msg = await guuruuchanflame.send("Alors,@Guuruu#2278 t'es allé à la salle ?")
            global FLAMEID
            FLAMEID=msg.id
            await msg.add_reaction(":white_check_mark:")
            await msg.add_reaction(":x:")
        await asyncio.sleep(300)
	
##########################################################################

@bot.tree.command(name="ping")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message("Pong! Latence: {}ms".format(round(bot.latency * 1000, 1)))


@bot.event
async def on_message(message):
    cheh=["https://tenor.com/view/vilebrequin-cheh-levy-gif-19953300","https://tenor.com/view/maskey-gif-17974418"]
    
    if (not message.author == bot.user) and (not message.author.bot) :
            
        file = discord.File(f"env/ranked-emblem/PALU.mp4", filename=f"PALU.mp4")
        if not message.author.id in antispam:

            if "palu"in message.content.lower().split():
                await message.channel.send(file=file)
            file2 = discord.File(f"env/ranked-emblem/ratio.png", filename=f"ratio.png")
            ISMENTIONED =False
            if message.mentions !=None:
                
                for i in range(len(message.mentions)):
                    if message.mentions[i].id == 517231233235812353:
                        ISMENTIONED=True
                    
            if ISMENTIONED==False:    
                if ("ratio"in message.content.lower().split())and(not "aladdin"in message.content.lower().split())  :
                    
                    await message.channel.send(file=file2)

            file3 = discord.File(f"env/ranked-emblem/junglediff.png", filename=f"junglediff.png")

            if "jungle diff"in message.content.lower():
                a=await message.channel.send(file=file3)
                await a.add_reaction("✅")
                await a.add_reaction("❌")
                
                
            if "cheh"in message.content.lower().split():
                await message.channel.send(random.choice(cheh))
                
            await bot.process_commands(message)
            
            if "guuruu"in message.content.lower().split():
                await message.add_reaction("<:GuuruuW:1091852794568396810>")
                
                
            if "merci zeri" in message.content.lower():
                await message.reply("Derien frérot/e <:Shock:1089628155133820938>")
                
                
            if "zebi" in message.content.lower().split():
                await message.add_reaction("<:Zebi:1092526109192618074>")
                
                
            if "bonne nuit" in message.content.lower():
                await message.channel.send("Bonne nuit Bg/Blg! Repose toi bien !")
                
                
            if "prankex" in message.content.lower().split():
                await message.channel.send("https://tenor.com/view/guuruu-prank-prankex-gif-19025746535426067")

            

#CLEAR

 
@bot.command()
@commands.has_permissions(administrator = True)
async def clear(ctx , amount=5):
    
    await ctx.channel.purge(limit=amount + 1)
##########################################################################

#apod


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def apod(ctx):
    apod=nasa
    
    embed=discord.Embed(title="Photo astronomique du jour !",
            description=f'{ctx.author.name} voici la photo du jour en astronomie !', 
            color=discord.Color.red()).set_thumbnail(
            url="https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png"
            ).set_image(url=apod.apod()["hdurl"])

    if "copyright" in apod.apod():

            embed.add_field(
            name="Auteur :", 
            value=f'{apod.apod()["copyright"]}', 
            inline=True
            )
    await ctx.message.channel.send(embed=embed)
    
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
#LOL PROFILE

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def lolp(ctx):
        name =str(" ".join(ctx.message.content.split()[1:]))
        versions = lol_watcher.data_dragon.versions_for_region(my_region)
        champions_version = versions['n']['champion']
        dd=lol_watcher.data_dragon.champions(champions_version)
        
        
            
        
        try:
            me = lol_watcher.summoner.by_name(my_region, name)
            me1= lol_watcher.league.by_summoner(my_region,me["id"])
            mastery=lol_watcher.champion_mastery.by_summoner(my_region, me["id"]) 
           
            
                    
                 
            
              
                
            icone =f'http://ddragon.leagueoflegends.com/cdn/{version["v"]}/img/profileicon/{me["profileIconId"]}.png'
            if not  me1:
                rank="Unranked"
                div=" "
                lp=" "
                win="Unranked"
                loose="Unranked"
                wr="Unranked"
            else:
                if  not "RANKED_FLEX_SR" in me1[0]['queueType']:
                    rank=me1[0]["tier"]
                    div=me1[0]["rank"]
                    lp=me1[0]["leaguePoints"]
                    win=me1[0]["wins"]
                    loose=me1[0]["losses"]
                    wr=(win/(win+loose))*100
                    wr=round(wr,2)
                else :
                    rank=me1[1]["tier"]
                    div=me1[1]["rank"]
                    lp=me1[1]["leaguePoints"]
                    win=me1[1]["wins"]
                    loose=me1[1]["losses"]
                    wr=(win/(win+loose))*100
                    wr=round(wr,2)
                    
            file = discord.File(f"env/ranked-emblem/zeri2.gif", filename=f"zeri2.gif")

            var=""
            match rank.lower():
                case "iron":
                    var=f"<:iron:1070669886700920872>  **{rank.lower()} {div}** {lp} lps"
                case "bronze":
                    var=f"<:bronze:1070670261340352574>  **{rank.lower()} {div}** {lp} lps"
                case "silver":
                    var=f"<:silver:1070670285822505080>  **{rank.lower()} {div}** {lp} lps"
                case "gold":
                    var=f"<:gold:1070670322195509329>  **{rank.lower()} {div}** {lp} lps"
                case "platinum":
                    var=f"<:platinum:1070670342651129966>  **{rank.lower()} {div}** {lp} lps"
                case "diamond":
                    var=f"<:diamond:1070670360267198496>  **{rank.lower()} {div}** {lp} lps"
                case "master":
                    var=f"<:master:1070670398074671114>  **{rank.lower()} {div}** {lp} lps"
                case "grandmaster":
                    var=f"<:grandmaster:1070670415367778327>  **{rank.lower()} {div}** {lp} lps"
                case "challenger":
                    var=f"<:challenger:1070670432107245578>  **{rank.lower()} {div}** {lp} lps"
                case _:
                    var=f"<:HanakoBahYes:811668408637718558> **{rank.lower()} {div}** {lp} lps"


            

            embed=discord.Embed(title="League Profil",
            description=f'{ctx.author.name} voici le profil de {name} ', 
            color=discord.Color.blue()).set_thumbnail(
            url=icone
            ).add_field(
            name="Pseudo :", 
            value=me["name"], 
            inline=True
            ).add_field(
            name="Niveau :",
            value=me["summonerLevel"],
            inline=True
            ).add_field(
            name="Rank :", 
            value=var,
            inline=True
            ).add_field(
            name="Wins :", 
            value=win,
            inline=True
            ).add_field(name=" ",value=" "
            ).add_field(name="Winrate :",value=f'{round(wr,2)}%'
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
            await ctx.message.channel.send(embed=embed,file=file)

#.set_image(url=f"attachment://emblem-{rank.lower()}.png")
        
        except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 await ctx.message.channel.send("Le compte avec ce pseudo n'existe pas !")
            else:
                raise
        
##########################################################################        

         
#SPAM

        
@bot.command()
@commands.has_permissions(administrator = True)

async def spam(ctx):
        
        if ctx.message.author.id!=688997212113600586:
            msg =int(ctx.message.content.split()[1])
            if msg<=100:
                await ctx.message.delete()
                spam =str(" ".join(ctx.message.content.split()[2:]))
                for msg in range(msg):
                    await ctx.message.channel.send(spam)

                await ctx.message.channel.send("https://tenor.com/view/jigm%C3%A9-hearthstone-travail-termin%C3%A9-mdr-mecredi-des-r%C3%A9ponse-gif-17412853")
            else:
                await ctx.message.channel.send("https://tenor.com/view/mister-v-encore-beaucoup-talking-still-thats-a-lot-there-right-gif-16825265")
        else :
            await ctx.message.reply("T'as pas l'age mon con")



##########################################################################

#BAN UNBAN

        
@bot.command()
@commands.has_permissions(administrator = True)
async def prison(ctx,member: discord.Member):

    
    with open('role.json', 'r') as f:
        users = json.load(f)

    nbrole= len(member.roles)

    await update_data(users, member,[])
    await add_role(users, member,nbrole)



    for i in range(1,len(member.roles)) :
        await member.remove_roles(member.roles[i]) 
         
        role = discord.utils.get(ctx.message.guild.roles, name = "🔗|Prisonnier")
        await member.add_roles(role)
    with open('role.json', 'w') as f:
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
    with open('role.json', 'r') as f:
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
    with open('role.json', 'w') as f:
            json.dump(users, f)
##########################################################################

#SNIPE

@bot.event
async def on_message_delete(message):
    if message.guild.id==614728233497133076:
        with open("logs.json", "r") as f:
            users = json.load(f)
        msg = message.content
        msgAuthor = str(message.author.id)
        users["dernierMSG"] = {}
        users["dernierMSG"]["MSG"]=[msg,msgAuthor]

        with open("logs.json","w") as f :
            json.dump(users,f)


@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def snipe(ctx):
    if ctx.guild.id==614728233497133076:
        with open("logs.json", "r") as f:
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

        if after.channel.id ==CHAN_VOC:


            chan = await after.channel.clone(name=f'◜⏳◞{member.name}')
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
    channel=discord.utils.get(member.guild.channels, id=CHAN_BVN)
    role = discord.utils.get(member.guild.roles, id=ROLE_NEANTIN)
    role2= discord.utils.get(member.guild.roles, id=ROLE_FAILLE)
    
    embed=discord.Embed(title="Bienvenue").set_thumbnail(url=member.avatar).add_field(name="Pseudo",value=member.name).add_field(name="Nous a rejoins le :",value=current_day)
    
    await channel.send(embed=embed)
    await member.add_roles(role)
    await member.add_roles(role2)

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def welcome(ctx):
    
    embed=discord.Embed(title="Bienvenue").set_thumbnail(url=ctx.author.avatar).add_field(name="Pseudo",value=ctx.author.name
    ).add_field(name="Nous a rejoins le :",value=current_day)
    
    await ctx.channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    channel=discord.utils.get(member.guild.channels, id=CHAN_BVN)
    embed=discord.Embed(title="Ciao").set_thumbnail(url=member.avatar).add_field(name="Pseudo",value=member.name)
    
    await channel.send(embed=embed)
##########################################################################

#REACTION    
@bot.event
async def on_raw_reaction_add(emoji):
    global FLAMEID
    role = discord.utils.get(emoji.member.guild.roles, id=658408130593423371)
    channel=discord.utils.get(emoji.member.guild.channels, id=emoji.channel_id)        
            
    if emoji.message_id==MESSAGE_AUTO_ROLE:
        if emoji.emoji.id==811668408637718558:
            await emoji.member.add_roles(role)
            await channel.send("")
    with open("logs.json", "r") as f:
            streak = json.load(f)

            streak["streak"]
    

    if emoji.message_id ==FLAMEID:
            if emoji.member.id==GUURUUID:
                if emoji.emoji.name=='❌':
                    
                    await channel.send(f"Oh le bouffon il est pas allé à la salle et en plus il a perdu son streak de {streak['streak'][0]} séances")
                    streak["streak"][0] = 0
                    FLAMEID=0
                elif emoji.emoji.name=='✅':
                    
                    streak['streak'][0]+=1
                    await channel.send('C\'est bien keep going !')
                    await channel.send(f"Tu as fais un streak de {streak['streak'][0]} séances")
                    FLAMEID=0
    with open("logs.json","w") as f :
            json.dump(streak,f)

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
async def histo(ctx):
     
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
                list[f]=[info['championName'],f'-   {str(info["kills"])}/{str(info["deaths"])}/{str(info["assists"])} <:v:1086301650291019777>']
                wins+=1             
            else:
                list[f]=[info['championName'],f'-   {str(info["kills"])}/{str(info["deaths"])}/{str(info["assists"])} <:d:1086301723095740556> ']
            
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
        await ctx.channel.send(embed=embed)    
    except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 await ctx.message.channel.send("Le compte avec ce pseudo n'existe pas !")
            else:
                raise    



@bot.command()
async def cg(ctx):
    try:
        link ="https://ddragon.leagueoflegends.com/cdn/13.8.1/data/en_US/champion.json"
        f = urllib.request.urlopen(link)
        myfile = f.read()
        data=json.loads(myfile)
        champ = data["data"]   
        name =str(" ".join(ctx.message.content.split()[1:]))
        me = lol_watcher.summoner.by_name(my_region,name)
        cg= lol_watcher.spectator.by_summoner(my_region,me["id"])
        blue=""
        red =""
        
        for i in cg["participants"] :
            
            if i["teamId"]==100:
                
                me = lol_watcher.summoner.by_name(my_region,i["summonerName"])
                me1= lol_watcher.league.by_summoner(my_region,me["id"])
                
                for cle,valeur in champ.items():
                    if int(valeur['key'])==int(i['championId']):
                        blue+=f'``{cle}`` **-** \t'
                     
                
                
                
                if not  me1:
                    rank="Unranked"
                    div=" "
                    lp=" "
                
                
                else:
                    if  not "RANKED_FLEX_SR" in me1[0]['queueType']:
                        rank=me1[0]["tier"]
                        div=me1[0]["rank"]
                        lp=me1[0]["leaguePoints"]
                        
                    else :
                        rank=me1[1]["tier"]
                        div=me1[1]["rank"]
                        lp=me1[1]["leaguePoints"]
                        
                        
            

                var=""
                match rank.lower():
                    case "iron":
                        var=f"<:iron:1070669886700920872>  **{rank.lower()} {div}** {lp}"
                    case "bronze":
                        var=f"<:bronze:1070670261340352574>  **{rank.lower()} {div}** {lp} "
                    case "silver":
                        var=f"<:silver:1070670285822505080>  **{rank.lower()} {div}** {lp} "
                    case "gold":
                        var=f"<:gold:1070670322195509329>  **{rank.lower()} {div}** {lp} "
                    case "platinum":
                        var=f"<:platinum:1070670342651129966>  **{rank.lower()} {div}** {lp} "
                    case "diamond":
                        var=f"<:diamond:1070670360267198496>  **{rank.lower()} {div}** {lp} "
                    case "master":
                        var=f"<:master:1070670398074671114>  **{rank.lower()} {div}** {lp} "
                    case "grandmaster":
                        var=f"<:grandmaster:1070670415367778327>  **{rank.lower()} {div}** {lp} "
                    case "challenger":
                        var=f"<:challenger:1070670432107245578>  **{rank.lower()} {div}** {lp} "
                    case _:
                        var=f"<:HanakoBahYes:811668408637718558> **{rank.lower()} {div}** {lp} "    
                        
                blue+=f'``{i["summonerName"]}``\t**|**\t{var}\n'          
                    
            else :
                me = lol_watcher.summoner.by_name(my_region,i["summonerName"])
                me1= lol_watcher.league.by_summoner(my_region,me["id"])
                if not  me1:
                    rank="Unranked"
                    div=" "
                    lp=" "
                for cle,valeur in champ.items():
                    if int(valeur['key'])==int(i['championId']):
                        red+=f'``{cle}`` **-** \t'
                
                else:
                    if  not "RANKED_FLEX_SR" in me1[0]['queueType']:
                        rank=me1[0]["tier"]
                        div=me1[0]["rank"]
                        lp=me1[0]["leaguePoints"]
                        
                    else :
                        rank=me1[1]["tier"]
                        div=me1[1]["rank"]
                        lp=me1[1]["leaguePoints"]
                        
                        
            

                var=""
                match rank.lower():
                    case "iron":
                        var=f"<:iron:1070669886700920872>  **{rank.lower()} {div}** {lp}"
                    case "bronze":
                        var=f"<:bronze:1070670261340352574>  **{rank.lower()} {div}** {lp}"
                    case "silver":
                        var=f"<:silver:1070670285822505080>  **{rank.lower()} {div}** {lp}"
                    case "gold":
                        var=f"<:gold:1070670322195509329>  **{rank.lower()} {div}** {lp}"
                    case "platinum":
                        var=f"<:platinum:1070670342651129966>  **{rank.lower()} {div}** {lp}"
                    case "diamond":
                        var=f"<:diamond:1070670360267198496>  **{rank.lower()} {div}** {lp}"
                    case "master":
                        var=f"<:master:1070670398074671114>  **{rank.lower()} {div}** {lp}"
                    case "grandmaster":
                        var=f"<:grandmaster:1070670415367778327>  **{rank.lower()} {div}** {lp}"
                    case "challenger":
                        var=f"<:challenger:1070670432107245578>  **{rank.lower()} {div}** {lp}"
                    case _:
                        var=f"<:HanakoBahYes:811668408637718558> **{rank.lower()} {div}** {lp}"    
                      
                red+=f'``{i["summonerName"]}``\t**|**\t{var}\n' 
        
        
        
                
                        
        
        
                
        embed=discord.Embed(title='Match en cours :' ,color=discord.Color.yellow())
        embed.add_field(name="Blue side :",value=blue,inline=False
        ).add_field(name="Red side :",value=red )         
        
        await ctx.channel.send(embed=embed)   
            
        
        
                
        
    except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 await ctx.message.channel.send("Le compte avec ce pseudo n'existe pas ! ou bien l'utilisateur n'est pas en game !")
            else:
                raise 


@bot.event
async def on_command_error(ctx, error):
     if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send('Ahahaha Bouffon t\'as pas les perms <:kekw:1079185133573255210>')
        await ctx.channel.send("https://tenor.com/view/counter-i-dont-gived-you-permission-gif-23613918")
    
                
                
bot.run(os.getenv('TOKEN'))

 