import asyncio
from datetime import timedelta
import json
import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from dotenv import load_dotenv
from zeri_features.imposteur.imposteur import fi, impo
from riotwatcher import LolWatcher
import urllib
from zeri_features.zeri_interactions.zeri_nasa import imageNasa
load_dotenv()

lol_watcher = LolWatcher(os.getenv('RIOT_API'))
version = lol_watcher.data_dragon.versions_for_region("euw1")


KARAN_ID=614728233497133076
class DiversCommands(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    
    @commands.command()
    async def pick(self,ctx):
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

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def snipe(self,ctx):
        if ctx.guild.id==KARAN_ID:
            with open("dossierJson/logs.json", "r") as f:
                users = json.load(f)
            
            await ctx.message.channel.send(f'Le dernier message supprimé est : **"{users["dernierMSG"]["MSG"][0]}"** You got sniped bro <@!{users["dernierMSG"]["MSG"][1]}>')
            await ctx.message.channel.send("https://tenor.com/view/stewie-gun-sniper-gif-14401284")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def spam(self,ctx):
            
            msg =int(ctx.message.content.split()[1])
            if msg<=100:
                await ctx.message.delete()
                spam =str(" ".join(ctx.message.content.split()[2:]))
                for msg in range(msg):
                    await ctx.message.channel.send(spam)

                await ctx.message.channel.send("https://tenor.com/view/jigm%C3%A9-hearthstone-travail-termin%C3%A9-mdr-mecredi-des-r%C3%A9ponse-gif-17412853")
            else:
                await ctx.message.channel.send("https://tenor.com/view/mister-v-encore-beaucoup-talking-still-thats-a-lot-there-right-gif-16825265")
        

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def say(self,ctx):
            mesg = str(" ".join(ctx.message.content.split()[1:]))
            await ctx.message.delete()
            await ctx.message.channel.send(mesg)





    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cat(self,ctx):
        link ="https://api.thecatapi.com/v1/images/search"
        f = urllib.request.urlopen(link)
        myfile = f.read()
        foto=json.loads(myfile)
        await ctx.message.channel.send(foto[0]["url"])


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dog(self,ctx):
        link ="https://api.thedogapi.com/v1/images/search"
        f = urllib.request.urlopen(link)
        myfile = f.read()
        foto=json.loads(myfile)
        await ctx.message.channel.send(foto[0]["url"])

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def apod(self,ctx):
        await imageNasa(ctx.message.channel)
'''
    
    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def imposteur(ctx):
        impo(ctx)
            
    @commands.command()
    async def fin(ctx):
        fi(ctx)
                
    
        
        
    @commands.command()
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

    @commands.command()
    async def checkpoll(self,id):
        try:
            print(id)
            channel= self.bot.get_channel(615128656049864734)
            message = await channel.fetch_message(id)
            poll = message.poll
            if poll.is_finalised():
                await channel.send(poll.get_answer(1).vote_count)
        except Exception as e :
            print(e)
'''

async def setup(bot):
    await bot.add_cog(DiversCommands(bot))