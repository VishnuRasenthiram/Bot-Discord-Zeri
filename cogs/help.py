import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def help(self,ctx):
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


async def setup(bot):
    await bot.add_cog(Help(bot))