import discord
from discord.ext import commands
from discord import app_commands
from zeri_features.zeri_economy.zeriMoney import *

choixPOF = [
            app_commands.Choice(name="Pile", value="Pile"),
            app_commands.Choice(name="Face", value="Face")
        ]
class Economy(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.Zeri_Money = ZeriMoney()


    @app_commands.command(name="profil", description="Affiche le profil de l'utilisateur")
    async def profil(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.Zeri_Money.profile(interaction)

    @app_commands.command(name="leaderboard", description="Affiche le classement des utilisateurs en fonction de leur solde")
    async def leaderboard_money(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.Zeri_Money.leaderboard(interaction)

    @app_commands.command(name="leaderboard_level", description="Affiche le classement des utilisateurs en fonction de leur niveau")
    async def leaderboard_level(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.Zeri_Money.leaderboard_level(interaction)

    @app_commands.command(name="daily", description="Réclame votre récompense quotidienne")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.Zeri_Money.daily(interaction)

    @app_commands.command(name="balance", description="Affiche le solde de l'utilisateur")
    async def balance(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.Zeri_Money.balance(interaction)

    @app_commands.command(name="pile_ou_face", description="Jouer à pile ou face")
    @app_commands.choices(choix=choixPOF)
    async def pile_ou_face(self, interaction: discord.Interaction, mise: int, choix: app_commands.Choice[str]):
        await interaction.response.defer()
        await self.Zeri_Money.pile_ou_face(interaction, mise, choix.value)

    

async def setup(bot):
    await bot.add_cog(Economy(bot))