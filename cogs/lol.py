import discord
from discord.ext import commands
from discord import app_commands
from typing import Union, Optional
from riotwatcher import LolWatcher
import os
from zeri_features.zeri_interactions.tenorApi import *
from lol_commands.profile.sauvegardeProfil   import *
from lol_commands.profile.suivitProfil import *
from lol_commands.leagueOfFunction import *
from zeri_features.zeri_interactions.interaction import *
from zeri_features.imposteur.imposteur import *
from lol_commands.classement.ladderLol import *


class LoLCommands(commands.Cog):
    def __init__(self, bot: discord.Client):
        try:
            self.bot = bot
            self.lol_watcher = LolWatcher(os.getenv('RIOT_API'))
            self.choixRegion = choixRegion
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du cog LoL: {str(e)}")
            raise

    # Commandes d'information
    @app_commands.command(name="profil_lol", description="Affiche le profil d'un joueur LoL")
    @app_commands.choices(region=choixRegion)
    async def profil_lol(self, interaction: discord.Interaction, pseudo: Optional[str] = None, region: app_commands.Choice[str] = "euw1"):
        """Affiche un profil LoL"""
        puuid, region = await getPuuidRegion(interaction, pseudo, region)
        await LOF.profileLeagueOfLegends(interaction, puuid, region)

    @app_commands.command(name="historique", description="Affiche l'historique des parties")
    @app_commands.choices(region=choixRegion)
    async def historique(self, interaction: discord.Interaction, pseudo: Optional[str] = None, region: app_commands.Choice[str] = "euw1"):
        """Affiche l'historique des parties"""
        puuid, region = await getPuuidRegion(interaction, pseudo, region)
        await LOF.historiqueLeagueOfLegends(interaction, puuid, region)

    @app_commands.command(name="partie_en_cours", description="Affiche la partie en cours")
    @app_commands.choices(region=choixRegion)
    async def partie_en_cours(self, interaction: discord.Interaction, pseudo: Optional[str] = None, region: app_commands.Choice[str] = "euw1"):
        """Affiche la partie en cours"""
        puuid, region = await getPuuidRegion(interaction, pseudo, region)
        await LOF.partieEnCours(interaction, puuid, region)

  

async def setup(bot):
    try:
        await bot.add_cog(LoLCommands(bot))
    except Exception as e:
        print(f"❌ Erreur lors du chargement du cog LoL: {str(e)}")
        raise