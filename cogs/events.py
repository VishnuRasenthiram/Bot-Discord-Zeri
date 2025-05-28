from io import BytesIO
import json
import math
import discord
from discord.ext import commands
from zeri_features.zeri_economy.zeriMoney import ZeriMoney # Replace 'Interaction' with the actual names you use from this module
from zeri_features.zeri_ia.zeriA import get_response_from_ai
from zeri_features.zeri_welcome.welcomeImage import creerImageBVN

import  time

CHAN_BVN =614953541911576692
ROLE_NEANTIN =1079422327391006851
ROLE_FAILLE=1079432006796066816
CHAN_VOC =1071472444562473021
ANNONCE_CHAN=634266557383442432
KARAN_ID=614728233497133076
COOLDOWN=10
BASE_PATH="env/ranked-emblem/"

class Events(commands.Cog):
    
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.Zeri_money = ZeriMoney(bot)
        self.last_message_time = {}
        self.temp_voice_channels = {}

        
        
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel:
            await channel.send(f"Bienvenue {member.mention} !")

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        guild=self.bot.get_guild(KARAN_ID)
        annonce =guild.get_channel(ANNONCE_CHAN)
        dans_mon_serv = False
        for i in guild.members:
            if i.id == after.id:
                dans_mon_serv = True
                break
                

        if after.activity != None and dans_mon_serv:
            if after.activity.type == discord.ActivityType.streaming: 
                await annonce.send(f"{before.name} est en live ! \n{after.activity.url}")
        


    @commands.Cog.listener() 
    async def on_message(self, message):
        await self.bot.process_commands(message)
        if (message.author == self.bot.user) or message.author.bot:
            return

        await self.handle_ai_mention(message)
        await self.handle_reactions(message)
        await self.handle_random_responses(message)
        await self.Zeri_money.add_xp(message, self.calculer_xp(message))

    async def handle_ai_mention(self, message):
        if self.bot.user in message.mentions:
            try:
                message_content = message.content.replace(f"<@{self.bot.user.id}>", "").strip().lower()
                await message.reply(get_response_from_ai(message.author.name, message_content))
            except Exception as e:
                print(f"Erreur lors de la réponse au message : {e}")

    async def handle_reactions(self, message):
        if any(phrase in message.content.lower() for phrase in ["fuck", "batclem"]):
            await message.add_reaction("<:pepefkbatclem:1363094839155097711>")

    async def handle_random_responses(self, message):
        import random
        cheh = [
            "https://tenor.com/view/nelson-monfort-cheh-i-hear-cheh-in-my-oreillette-gif-15977955",
            "https://tenor.com/view/maskey-gif-17974418",
            "https://tenor.com/view/wavesives-waves-ives-waves-ives-waves-cheh-gif-1692370554913806768",
            "https://tenor.com/view/capitaine-groscheh-gros-cheh-cheh-m%C3%A9rit%C3%A9-mange-ton-seum-gif-12396020753961179573",
            "https://tenor.com/view/cheh-bienfaits-duh-gif-12323680"
        ]
        BASE_PATH = "env/ranked-emblem/"
        file = discord.File(BASE_PATH + "PALU.mp4", filename="PALU.mp4")
        file_g2 = discord.File(BASE_PATH + "g2_win.mp4", filename="g2_win.mp4")
        file3 = discord.File(BASE_PATH + "junglediff.png", filename="junglediff.png")
        file_clem = discord.File(BASE_PATH + "clem.mp4", filename="clem.mp4")
        file_guuruu = discord.File(BASE_PATH + "guuruu.mp4", filename="guuruu.mp4")

        content_lower = message.content.lower()
        content_split = content_lower.split()

        if random.randrange(0, 4) != 1:
            return

        if any(phrase in content_lower for phrase in ["g2 win", "g2 a gagné", "g2 a win"]):
            await message.channel.send(file=file_g2)
            return

        if "fuck batclem" in content_lower:
            await message.channel.send(file=file_clem)
            return

        if "fuck guuruu" in content_lower:
            await message.channel.send(file=file_guuruu)
            return

        if "palu" in content_split:
            await message.channel.send(file=file)
            return

        if "jungle diff" in content_lower:
            a = await message.channel.send(file=file3)
            await a.add_reaction("✅")
            await a.add_reaction("❌")
            return

        if "cheh" in content_split:
            await message.channel.send(random.choice(cheh))
            return

        if "merci zeri" in content_lower:
            await message.reply("Derien Bebou <:Eheh:1280080977418260483>")
            return

        if "prankex" in content_split:
            await message.channel.send("https://tenor.com/view/guuruu-prank-prankex-gif-19025746535426067")


         
    def calculer_xp(self,message):
        user_id = message.author.id
        current_time = time.time()
        
        if user_id in self.last_message_time:
            elapsed_time = current_time - self.last_message_time[user_id]
            if elapsed_time < COOLDOWN:
                return 0 
        
        self.last_message_time[user_id] = current_time
        
        longueur_message = len(str(message.content.lower()).lstrip())
        coef = math.log(longueur_message + 1) * 10
        return min(int(coef), 100)

    
    @commands.Cog.listener() 
    async def on_member_join(self,member):
        
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
        

    @commands.Cog.listener() 
    async def on_member_remove(self,member):
        if member.guild.id==KARAN_ID:

            image =creerImageBVN(member,"Aurevoir")

            img_bytes=BytesIO()
            image.save(img_bytes,format='PNG')
            img_bytes.seek(0)
            channel=discord.utils.get(member.guild.channels, id=CHAN_BVN)
            await channel.send(file=discord.File(img_bytes, filename='aurevoir.png'))

    @commands.Cog.listener() 
    async def on_message_delete(self,message):
        if message.guild.id==KARAN_ID:
            with open("dossierJson/logs.json", "r") as f:
                users = json.load(f)
            msg = message.content
            msg_author = str(message.author.id)
            users["dernierMSG"] = {}
            users["dernierMSG"]["MSG"]=[msg,msg_author]

            with open("dossierJson/logs.json","w") as f :
                json.dump(users,f)

async def setup(bot):
    await bot.add_cog(Events(bot))