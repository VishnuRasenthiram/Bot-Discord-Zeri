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


class Profil_lol(commands.Cog):
    def __init__(self, bot: discord.Client):
        try:
            self.bot = bot
            self.lol_watcher = LolWatcher(os.getenv('RIOT_API'))
            self.choixRegion = choixRegion
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du cog LoL: {str(e)}")
            raise


    @app_commands.command(name="sauvegarder_mon_profil", description="Sauvegarde votre profil LoL")
    @app_commands.choices(region=choixRegion)
    async def sauvegarder_profil(self, interaction: discord.Interaction, pseudo: str, region: app_commands.Choice[str] = "euw1"):
        """Sauvegarde un profil LoL"""
        await set_profile(interaction, pseudo, region)

    @app_commands.command(name="supprimer_mon_profil", description="Supprime votre profil sauvegardé")
    async def supprimer_profil(self, interaction: discord.Interaction):
        """Supprime un profil LoL"""
        await del_profile(interaction)

    # Système de suivi
    @app_commands.command(name="suivre_profil", description="Suivre un profil LoL dans un channel")
    @app_commands.choices(region=choixRegion)
    async def suivre_profil(self, interaction: discord.Interaction, pseudo: str, channel: str, region: app_commands.Choice[str] = "euw1"):
        """Ajoute un suivi de profil"""
        await add_profile_liste(interaction, pseudo, channel, region)

    @app_commands.command(name="suppr_profil_suivit", description="Arrêter de suivre un profil")
    @app_commands.choices(region=choixRegion)
    async def supprimer_profil_suivi(self, interaction: discord.Interaction, pseudo: str, channel: str, region: app_commands.Choice[str] = "euw1"):
        """Retire un suivi de profil"""
        await del_profile_liste(interaction, pseudo, channel, region)

    # Gestion des channels
    @app_commands.command(name="ajouter_channel_suivit", description="Ajoute un channel à la liste de suivi")
    async def ajouter_channel_suivi(self, interaction: discord.Interaction, channel: Union[discord.Thread, discord.TextChannel]):
        """Ajoute un channel de suivi"""
        await addChannel(interaction, channel)

    @app_commands.command(name="suppr_channel_suivit", description="Retire un channel de la liste de suivi")
    async def supprimer_channel_suivi(self, interaction: discord.Interaction, channel: str):
        """Retire un channel de suivi"""
        await delChannel(interaction, channel)

   


    # Autocomplétions
    @suivre_profil.autocomplete("channel")
    @supprimer_profil_suivi.autocomplete("channel")
    async def autocomplete_channel(self, interaction: discord.Interaction, current: str):
        """Autocomplétion générique pour les channels"""
        choices = generate_choices()  # À adapter selon votre implémentation
        return [app_commands.Choice(name=c.name, value=c.value) 
                for c in choices 
                if current.lower() in c.name.lower()][:25]

    @supprimer_profil_suivi.autocomplete("channel")
    async def autocomplete_suivi_channel(self, interaction: discord.Interaction, current: str):
        """Autocomplétion spécifique pour les channels de suivi"""
        pseudo = interaction.namespace.pseudo
        if not pseudo:
            return []

        pseudo, tagline = await verifFormatRiotId(None, pseudo)
        if not pseudo:
            return []

        me, region = await getMe(None, pseudo, tagline, None)
        puuid = me["puuid"]
        
        channels = []
        for channel_id in get_player_listeChannel(puuid):
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                channels.append(app_commands.Choice(name=channel.name, value=str(channel.id)))
        
        return [c for c in channels if current.lower() in c.name.lower()][:25]
    

    @supprimer_channel_suivi.autocomplete("channel")
    async def type_autocomplete(self,interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=choice.name, value=choice.value) for choice in generate_choices() if current.lower() in choice.name.lower()]



async def setup(bot):
    try:
        await bot.add_cog(Profil_lol(bot))
    except Exception as e:
        print(f"❌ Erreur lors du chargement du cog LoL: {str(e)}")
        raise