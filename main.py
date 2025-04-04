import discord
from discord.ext import *
import asyncio
from datetime import datetime
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os
from discord.ext import commands
import traceback
load_dotenv()

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


@bot.event
async def on_ready():
    print(current_time)
    await bot.change_presence(activity=discord.Game(name="zzzzz"))
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)
    await load_cogs()
    print("le bot est pret")
    

@bot.event
async def on_command_error(ctx, error):
     if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send('Ahahaha  t\'as pas les perms <:kekw:1079185133573255210>')
        await ctx.channel.send("https://tenor.com/view/counter-i-dont-gived-you-permission-gif-23613918")



@bot.event
async def on_error(event, *args, **kwargs):
    with open("error_log.txt", "a") as f:
        f.write(f"\nErreur détectée : {event}\n")
        f.write(traceback.format_exc())

async def load_cogs():
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'loaded {filename}')
                except Exception as e:
                    print(f'Failed to load {filename}')


async def main():
    async with bot:
        await bot.start(os.getenv('TOKEN')) 
                           
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot arrêté par l'utilisateur")
    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")