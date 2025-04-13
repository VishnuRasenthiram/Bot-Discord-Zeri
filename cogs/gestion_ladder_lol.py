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


class Ladder_lol(commands.Cog):
    def __init__(self, bot: discord.Client):
        try:
            self.bot = bot
            self.lol_watcher = LolWatcher(os.getenv('RIOT_API'))
            self.choixRegion = choixRegion
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du cog LoL: {str(e)}")
            raise


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
    


    # Autocomplétions
   
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
        await bot.add_cog(Ladder_lol(bot))
    except Exception as e:
        print(f"❌ Erreur lors du chargement du cog LoL: {str(e)}")
        raise