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
import aiohttp
from leagueOfFunction import *
from typing import Union

lol_watcher = LolWatcher(os.getenv('RIOT_API'))
version = lol_watcher.data_dragon.versions_for_region("euw1")
def generate_choices_liste_playerLadder(puuid):
    liste_channel= get_player_listeChannel(puuid)
    return [app_commands.Choice(name=f"{i[1]}", value=f"{i[0]}") for i in liste_channel ]
def generate_choicesLadder():
    liste_channel= get_listChannelLadder()
    return [app_commands.Choice(name=f"{i[1]}", value=f"{i[0]}") for i in liste_channel ]


async def addChannelLadder(interaction: discord.Interaction, channel:str):
    if not interaction.user.id==517231233235812353:
        await interaction.followup.send(
            "Demandez à <@517231233235812353> pour faire cela!", ephemeral=True
        )
    await interaction.response.defer()
    dataChannel = {
        "id": channel.id,
        "nom": channel.name
    }

    insert_listChannelLadder(dataChannel)

    await interaction.followup.send(f"Le channel {channel} a été ajouté à la liste des channels de ladder",ephemeral=True)
    
async def delChannelLadder(interaction: discord.Interaction, channel:str):
    
    if not interaction.user.id==517231233235812353:
        await interaction.response.send_message(
            "Demandez à <@517231233235812353> pour faire cela!", ephemeral=True
        )
    await interaction.response.defer()
    delete_listChannelLadder(channel)
    await interaction.followup.send("Channel supprimé avec succès !", ephemeral=True)


async def add_profile_listeLadder(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
        try:
            pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
            me,region=await getMe(interaction,pseudo,tagline,region)
            puuid=me["puuid"]
        except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 await interaction.response.send_message("Le compte avec ce pseudo n'existe pas !",ephemeral=True)
        liste = get_ladder_liste()
        trouvé = True
        
        if liste:
            for puuidL in liste:
                if puuidL[0] == puuid and channel in puuidL[1]:
                    trouvé = False
                    break
        
       
        
        if trouvé:
            data={
                "puuid": puuid,
                "channel": channel,
                "region": region,
            }
            insert_ladder(data)
            await interaction.response.send_message("Profil ajouté !", ephemeral=True)
        else:
            await interaction.response.send_message("Ce profil est déjà dans le classement !", ephemeral=True)  
           

async def del_profile_listeLadder(interaction:discord.Interaction,pseudo:str,channel:str,region:app_commands.Choice[str]="euw1"):
    pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
    me,region=await getMe(interaction,pseudo,tagline,region)
    puuid=me["puuid"]
    data={
        "puuid": puuid,
        "channel": channel,
        "region": region,
    }
    etat=delete_ladder(data)
    if etat==0:
        await interaction.response.send_message("Ce profil n'est pas dans la base de donnée!",ephemeral=True)
    else :
        await interaction.response.send_message("Ce profil a bien été supprimé !",ephemeral=True)
rank_order = {
    "CHALLENGER": 0,
    "GRANDMASTER": 1,
    "MASTER": 2,
    "DIAMOND": 3,
    "EMERALD": 4,
    "PLATINUM": 5,
    "GOLD": 6,
    "SILVER": 7,
    "BRONZE": 8,
    "IRON": 9,
    "Unranked": 10
}

division_order = {
    "I": 0,
    "II": 1,
    "III": 2,
    "IV": 3,
    "Unranked": 4
}   

async def create_ladder(liste_joueur):

    embed = discord.Embed(
        title="Classement",
        description="Voici le classement des joueurs",
        color=discord.Color.red()
    )
    classement = []
    for joueur in liste_joueur:
        puuid = joueur[0]
        region = joueur[2]
        versions = lol_watcher.data_dragon.versions_for_region(region)
        try:
            myAccount = lol_watcher.summoner.by_puuid(region, puuid)
            me1 = lol_watcher.league.by_summoner(region, myAccount["id"])
            icone = f'http://ddragon.leagueoflegends.com/cdn/{versions["v"]}/img/profileicon/{myAccount["profileIconId"]}.png'
        except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            else:
                print(err)
        regionRiotId = regionForRiotId(region)
        nom=lol_watcher.accountV1.by_puuid(regionRiotId,puuid)["gameName"]
        if not me1:
            rank  = div = "Unranked"
            lp = 0
        else:
            isSolo = True

            for i in range(len(me1)):
                if me1[i]['queueType'] == "RANKED_SOLO_5x5":
                    rank = me1[i]["tier"]
                    div = me1[i]["rank"]
                    lp = me1[i]["leaguePoints"]
                    isSolo = False
                    break
            if isSolo:
                rank = div  = "Unranked"
                lp = 0

        classement.append((nom,rank,div,lp,icone))

    classement.sort(key=lambda x: (rank_order[x[1]], division_order[x[2]], - int(x[3])))

    for i in range(len(classement),25):
        joueur = classement[i]
        
        embed.add_field(name=f"{i+1}. {joueur[0]}", value=rank_to_emoji(joueur[1],joueur[2],joueur[3]), inline=False)
        if i ==0:
            embed.set_thumbnail(url=joueur[4])
    return embed

