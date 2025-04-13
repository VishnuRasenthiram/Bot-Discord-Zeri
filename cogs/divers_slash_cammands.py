import discord
from discord.ext import commands
from discord import app_commands
import random
from zeri_features.zeri_interactions.interaction import *
from zeri_features.zeri_interactions.tenorApi import *


class DiversSlashCommands(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @app_commands.command(name="roll", description="Lance un dé (1-100 par défaut)")
    async def roll(self, interaction: discord.Interaction, max: int = 100):
        """Lance un dé (1-100 par défaut)"""
        await interaction.response.send_message(f"🎲 Résultat : {random.randint(1, max)}")


    @app_commands.command(name="ping", description="Vérifie la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        """Commande ping améliorée"""
        await interaction.response.send_message(f"Pong! Latence: {round(self.bot.latency * 1000, 1)}ms")
            
    
    @app_commands.command(name="interaction", description="Fait une interaction avec un membre")
    @app_commands.choices(type=choixInteraction)
    async def interaction(self,interaction: discord.Interaction, type:app_commands.Choice[str], membre: discord.Member):
        """Fait une interaction avec un membre"""
        await interaction.response.defer()
        embed= discord.Embed(description=generate_interaction_text(type.value, interaction.user.mention, membre.mention), color=discord.Color.random())
        embed.set_image(url=getRandomGIf(type.value))
        await interaction.delete_original_response()
        await interaction.channel.send(membre.mention,embed=embed)


    @app_commands.command(name="action", description="Fait une action")
    @app_commands.choices(type=choixAction)
    async def action(self,interaction: discord.Interaction, type:app_commands.Choice[str]):
        """Fait une action"""
        await interaction.response.defer()
        embed= discord.Embed(description=generate_interaction_text(type.value, interaction.user.mention,None), color=discord.Color.random())
        embed.set_image(url=getRandomGIf(type.value))
        await interaction.delete_original_response()
        await interaction.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DiversSlashCommands(bot))