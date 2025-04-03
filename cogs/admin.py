import json
import discord
from discord.ext import commands
from discord import app_commands
import random
from main import KARAN_ID
from zeri_features.zeri_ia.zeriA import clear_history



class Admin(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    

    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(ctx, member : discord.Member, *, reason = None):
        await member.ban(reason = reason)
        await ctx.message.channel.send(f'{member} a été ban !') 


    @commands.command()   
    @commands.has_permissions(administrator = True)
    async def liberer(self,ctx, member: discord.Member):
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

            
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def prison(self,ctx,member: discord.Member):

        
        with open('dossierJson/role.json', 'r') as f:
            users = json.load(f)

        nbrole= len(member.roles)

        await self.update_data(users, member,[])
        await self.add_role(users, member,nbrole)

        nbrole2= nbrole-1
        while(nbrole2>=1) :
            await member.remove_roles(member.roles[nbrole2])
            nbrole2=nbrole2-1
        role = discord.utils.get(ctx.message.guild.roles, name = "🔗|Prisonnier")
        await member.add_roles(role)    
        with open('dossierJson/role.json', 'w') as f:
                json.dump(users, f)
        await ctx.message.channel.send(f'{member.name} a été envoyé en prison. ^^')
        
    async def add_role(self,users,user,nbrole):
        for i in range(1,nbrole):
            
            users[f'{user.id}']["roles"].append(str(user.roles[i]))

    async def update_data(self,users, user,role):
        if not f'{user.id}' in users:
            users[f'{user.id}'] = {}
            users[f'{user.id}']["roles"] = role



    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def clear(self,ctx , amount=5):
        await ctx.channel.purge(limit=amount + 1)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def filtre(self,ctx , amount=5):
        guild=self.bot.get_guild(KARAN_ID)
        filtre =guild.get_channel(615128656049864734)
        await filtre.purge(limit=amount )

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def leave(self,ctx):
        if ctx.author.id==517231233235812353:
            serv= self.bot.get_guild(int(ctx.message.content.split()[1:][0]))
            await serv.leave()
            await ctx.channel.send(f'J\'ai quitté le serveur : {serv}!')    

    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def resetHistory(ctx):
        clear_history()
        await ctx.channel.send("Historique réinitialisé")


        
async def setup(bot):
    await bot.add_cog(Admin(bot))