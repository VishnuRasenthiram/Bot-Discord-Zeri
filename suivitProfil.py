import discord
from riotwatcher import LolWatcher, ApiError
from discord.ext import *
from discord.ui import Select
import asyncio
from datetime import date, datetime
from datetime import timedelta
from discord.flags import Intents 
from discord import app_commands
import urllib
import requests
from datetime import datetime
import json
import random
from nasaapi import Client
import re
import pytz
from dotenv import load_dotenv
import os
from threading import Thread
import subprocess
import sched, time
from discord.ext import tasks, commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from leagueOfFunction import *
from welcomeImage import *
from currentGameImage import *
from baseDeDonne import *
from tenorApi import *
import hashlib  
from zeriMoney import *
import aiohttp
from leagueOfFunction import *
from typing import Union

def generate_choices_liste_player(puuid):
    liste_channel= get_player_listeChannel(puuid)
    return [app_commands.Choice(name=f"{i[1]}", value=f"{i[0]}") for i in liste_channel ]
def generate_choices():
    liste_channel= get_listChannelSuivit()
    return [app_commands.Choice(name=f"{i[1]}", value=f"{i[0]}") for i in liste_channel ]

async def add_profile_liste(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
        try:
            pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
            me,region=await getMe(interaction,pseudo,tagline,region)
            puuid=me["puuid"]
        except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 await interaction.response.send_message("Le compte avec ce pseudo n'existe pas !",ephemeral=True)
        liste = get_player_liste()
        trouvé = True
        
        if liste:
            for puuidL in liste:
                if puuidL[1] == puuid and channel in ast.literal_eval(puuidL[4]):
                    trouvé = False
                    break
        
        if trouvé:
            for i in liste:
                if i[1] == puuid:
                    listeChan = list(ast.literal_eval(i[4]))
                    listeChan.append(channel)
                    update_player_listeChannel(puuid, listeChan)
                    trouvé = False
                    break
        
            if trouvé:
                listeChan = [channel]
                player_data = {
                    "puuid": puuid,
                    "region": region,
                    "listeChannel": str(listeChan)
                }
                insert_player_liste(player_data)
        
            await interaction.response.send_message("Profil ajouté !", ephemeral=True)
        else:
            await interaction.response.send_message("Ce profil est déjà suivi !", ephemeral=True)


async def del_profile_liste(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
    pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
    me,region=await getMe(interaction,pseudo,tagline,region)
    puuid=me["puuid"]
    player_data={
                "puuid":puuid,
                "region":region,
    }

    if channel=="all":
        etat=delete_player_liste(player_data)
    else:
        channelListe= list(get_player_listeChannel(puuid))
        if str(channel) in channelListe:
            channelListe.remove(channel)
            if len(channelListe)==0:
                delete_player_liste(player_data)
            etat=1
            update_player_listeChannel(player_data["puuid"],channelListe)
        else:
            etat=0
            
                
    if etat==0:
        await interaction.response.send_message("Ce profil n'est pas dans la base de donnée!",ephemeral=True)
    else :
        await interaction.response.send_message("Ce profil a bien été supprimé !",ephemeral=True)



async def addChannel(interaction: discord.Interaction, channel:Union[discord.threads.Thread,discord.channel.TextChannel]):
    
    if not interaction.user.id==517231233235812353:
        await interaction.response.send_message(
            "Demandez à <@517231233235812353> pour faire cela!", ephemeral=True
        )
    await interaction.response.defer()
    dataChannel = {
        "id": channel.id,
        "nom": channel.name
    }
    insert_listChannelSuivit(dataChannel)
    await interaction.followup.send("Channel ajouté avec succès !", ephemeral=True)

async def delChannel(interaction: discord.Interaction, channel:str):
    
    if not interaction.user.id==517231233235812353:
        await interaction.response.send_message(
            "Demandez à <@517231233235812353> pour faire cela!", ephemeral=True
        )
    await interaction.response.defer()
    delete_listChannelSuivit(channel)
    await interaction.followup.send("Channel supprimé avec succès !", ephemeral=True)