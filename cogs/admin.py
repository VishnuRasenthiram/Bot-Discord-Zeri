import json
import discord
from discord.ext import commands
from discord import app_commands
import random


KARAN_ID=614728233497133076
ROLE_JSON_PATH = 'dossierJson/role.json'

class Admin(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    

    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        await member.ban(reason = reason)
        await ctx.message.channel.send(f'{member} a été ban !') 


    @commands.command()   
    @commands.has_permissions(administrator = True)
    async def liberer(self, ctx, member: discord.Member):
        with open(ROLE_JSON_PATH, 'r') as f:
            users = json.load(f)
        
        role = discord.utils.get(ctx.message.guild.roles, name = "🔗|Prisonnier")
        await member.remove_roles(role)
                
        await ctx.message.channel.send(f'{member.name} a été libéré. ^^')
        
        a = len(users[f'{member.id}']["roles"])    
        for i in range(a):
            b = users[f'{member.id}']["roles"][i]
            roled = discord.utils.get(ctx.message.guild.roles, name = b)
            await member.add_roles(roled)
        with open(ROLE_JSON_PATH, 'w') as f:
            json.dump(users, f)

            
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def prison(self,ctx,member: discord.Member):

        
        with open(ROLE_JSON_PATH, 'r') as f:
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
        with open(ROLE_JSON_PATH, 'w') as f:
                json.dump(users, f)
        await ctx.message.channel.send(f'{member.name} a été envoyé en prison. ^^')
        
    async def add_role(self,users,user,nbrole):
        for i in range(1,nbrole):
            
            users[f'{user.id}']["roles"].append(str(user.roles[i]))

    async def update_data(self,users, user,role):
        if f'{user.id}' not in users:
            users[f'{user.id}'] = {}
            users[f'{user.id}']["roles"] = role



    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def clear(self,ctx , amount=5):
        await ctx.channel.purge(limit=amount + 1)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def filtre(self,ctx , amount=5):
        guild = self.bot.get_guild(KARAN_ID)
        if guild is None:
            await ctx.send("Guild introuvable avec l'ID donné.")
            return
        filtre = guild.get_channel(615128656049864734)
        if filtre is None:
            await ctx.send("Salon introuvable avec l'ID donné.")
            return
        if isinstance(filtre, discord.TextChannel):
            await filtre.purge(limit=amount)
        else:
            await ctx.send("La commande de purge ne peut être utilisée que sur un salon textuel.")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def leave(self,ctx):
        if ctx.author.id==517231233235812353:
            serv = self.bot.get_guild(int(ctx.message.content.split()[1:][0]))
            if serv is not None:
                await serv.leave()
                await ctx.channel.send(f'J\'ai quitté le serveur : {serv}!')
            else:
                await ctx.channel.send("Serveur introuvable ou je ne suis pas membre de ce serveur.")
"""
    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def resetHistory(ctx):
        clear_history()
        await ctx.channel.send("Historique réinitialisé")
"""

        
async def setup(bot):
    await bot.add_cog(Admin(bot))