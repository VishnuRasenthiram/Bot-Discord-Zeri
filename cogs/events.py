import discord
from discord.ext import commands
from zeri_features.zeri_economy.zeriMoney import *
from zeri_features.zeri_interactions.interaction import *
from zeri_features.zeri_ia.zeriA import *
from zeri_features.zeri_welcome.welcomeImage import *

import  time

CHAN_BVN =614953541911576692
ROLE_NEANTIN =1079422327391006851
ROLE_FAILLE=1079432006796066816
CHAN_VOC =1071472444562473021
ANNONCE_CHAN=634266557383442432
KARAN_ID=614728233497133076
COOLDOWN=10


class Events(commands.Cog):
    
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.Zeri_money = ZeriMoney(bot)
        self.last_message_time = {}
        
        
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel:
            await channel.send(f"Bienvenue {member.mention} !")

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        guild=self.bot.get_guild(KARAN_ID)
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
        


    @commands.Cog.listener() 
    async def on_message(self,message):
        cheh=["https://tenor.com/view/nelson-monfort-cheh-i-hear-cheh-in-my-oreillette-gif-15977955","https://tenor.com/view/maskey-gif-17974418","https://tenor.com/view/wavesives-waves-ives-waves-ives-waves-cheh-gif-1692370554913806768","https://tenor.com/view/capitaine-groscheh-gros-cheh-cheh-m%C3%A9rit%C3%A9-mange-ton-seum-gif-12396020753961179573","https://tenor.com/view/cheh-bienfaits-duh-gif-12323680"]
        
        if (not message.author == self.bot.user) and (not message.author.bot) :
                
            file = discord.File(f"env/ranked-emblem/PALU.mp4", filename=f"PALU.mp4")
            fileG2 = discord.File(f"env/ranked-emblem/toohless.mp4", filename=f"toohless.mp4")
            file3 = discord.File(f"env/ranked-emblem/junglediff.png", filename=f"junglediff.png")

            if self.bot.user in message.mentions:
                print(f"Message mentionnant le bot : {message.content}")
                message_content = message.content.replace(f"<@{self.bot.user.id}>", "").strip().lower()
                await message.reply(generate_content(message_content, message.author.name))

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
                
            await self.bot.process_commands(message)
            
            if "merci zeri" in message.content.lower():
                
                await message.reply("Derien Bebou <:Eheh:1280080977418260483>")
                
            if "prankex" in message.content.lower().split():
                await message.channel.send("https://tenor.com/view/guuruu-prank-prankex-gif-19025746535426067")
            
            await self.Zeri_money.add_xp(message,self.calculer_xp(message))

         
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
    async def  on_raw_reaction_remove(self,payload):
        #role = discord.utils.get(emoji.member.guild.roles, id=658408130593423371)
        guild = discord.utils.find(lambda g: g.id == payload.guild_id, self.bot.guilds)
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)

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
    async def on_voice_state_update(self,member,before,after):
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

    @commands.Cog.listener() 
    async def on_message_delete(self,message):
        if message.guild.id==KARAN_ID:
            with open("dossierJson/logs.json", "r") as f:
                users = json.load(f)
            msg = message.content
            msgAuthor = str(message.author.id)
            users["dernierMSG"] = {}
            users["dernierMSG"]["MSG"]=[msg,msgAuthor]

            with open("dossierJson/logs.json","w") as f :
                json.dump(users,f)

async def setup(bot):
    await bot.add_cog(Events(bot))