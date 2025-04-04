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
            print("🔄 Initialisation du LolWatcher...")
            self.lol_watcher = LolWatcher(os.getenv('RIOT_API'))
            print("✅ LolWatcher initialisé")
            self.choixRegion = choixRegion
            print("✅ Cog LoL initialisé avec succès")
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

    # Système ladder
    @app_commands.command(name="ajouter_channel_ladder", description="Ajoute un channel au ladder")
    async def ajouter_channel_ladder(self, interaction: discord.Interaction, channel: Union[discord.Thread, discord.TextChannel]):
        """Ajoute un channel ladder"""
        await addChannelLadder(interaction, channel)

    @app_commands.command(name="supprimer_channel_ladder", description="Retire un channel du ladder")
    async def supprimer_channel_ladder(self, interaction: discord.Interaction, channel: str):
        """Retire un channel ladder"""
        await delChannelLadder(interaction, channel)

    @app_commands.command(name="add_to_ladder", description="Ajoute un joueur au ladder")
    @app_commands.choices(region=choixRegion)
    async def ajouter_ladder(self, interaction: discord.Interaction, pseudo: str, channel: str, region: app_commands.Choice[str] = "euw1"):
        """Ajoute un joueur au ladder"""
        await add_profile_listeLadder(interaction, pseudo, channel, region)

    @app_commands.command(name="delete_from_ladder", description="Supprime un joueur du ladder")
    async def supprimer_profil_ladder(self, interaction: discord.Interaction, pseudo: str, channel: str, region: app_commands.Choice[str] = "euw1"):
        """Supprime un joueur du ladder"""
        await del_profile_listeLadder(interaction, pseudo, channel, region)
    

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

    @supprimer_channel_ladder.autocomplete("channel")
    async def type_autocomplete(self,interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=choice.name, value=choice.value) for choice in generate_choicesLadder() if current.lower() in choice.name.lower()]
    
    @supprimer_profil_ladder.autocomplete("channel")
    async def type_autocomplete(self,interaction: discord.Interaction, current: str):
        pseudo = interaction.namespace.pseudo
        if not pseudo:
            return []

        pseudo, tagline = await verifFormatRiotId(None, pseudo)
        if not pseudo:
            return []

        me, region = await getMe(None, pseudo, tagline, None)
        puuid = me["puuid"]
        chan = [app_commands.Choice(name="All", value="all")]

        channel_list_id = get_liste_channel_ladder_joueur(puuid)

        if not channel_list_id:
            return chan

        channel_list = []
        for id in channel_list_id:

            channel = self.bot.get_channel(int(id[0]))
            if channel:
                channel_list.append(app_commands.Choice(name=channel.name, value=str(channel.id)))      
        return [choice for choice in channel_list if current.lower() in choice.name.lower()]


async def setup(bot):
    try:
        print("🔄 Chargement du cog LoL...")
        await bot.add_cog(LoLCommands(bot))
        print("✅ Cog LoL chargé avec succès")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du cog LoL: {str(e)}")
        raise