import json
import discord
from discord.ext import commands
from discord import app_commands
import random

KARAN_ID=614728233497133076

class ProfilCommands(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @app_commands.command(name="pp", description="Affiche la photo de profil actuelle")
    async def pp(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        target = user if user else interaction.user
        await interaction.followup.send(target.display_avatar)

    @app_commands.command(name="ppdebase", description="Affiche la photo de profil de base")
    async def ppdebase(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        target = user if user else interaction.user
        await interaction.followup.send(target.avatar)

    @app_commands.command(name="ppserv", description="Affiche l'icône du serveur")
    async def ppserv(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(interaction.guild.icon)

    @app_commands.command(name="banner", description="Affiche la bannière d'un utilisateur")
    async def banner(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        target = user if user else interaction.user
        
        usez = await self.bot.fetch_user(target.id)
        if usez.banner is None:
            await interaction.followup.send("N'a pas de bannière")
        else:
            await interaction.followup.send(usez.banner)

async def setup(bot):
    await bot.add_cog(ProfilCommands(bot))