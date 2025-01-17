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

class ViewValidator(discord.ui.View):
    @discord.ui.button( # the decorator that lets you specify the properties of the select menu
        style=discord.ButtonStyle.gray,
        emoji='✅'
    )
    async def select_callback(self,interaction, select): # the function called when the user is done selecting options
        await interaction.channel.send("Bien reçu, je vais procédé à la vérification")
        
    
        profile=get_player_data(interaction.user.id)
                
                
        meIcon=lol_watcher.summoner.by_puuid(region=profile[3],encrypted_puuid=profile[1])
            
        icone =f'http://ddragon.leagueoflegends.com/cdn/{version["v"]}/img/profileicon/{meIcon["profileIconId"]}.png'
        if profile[4]==0:
            if profile[2]==icone:
                await interaction.response.send_message("Votre compte est lié !")
                update_player_statut(interaction.user.id,1)
            else :
                await interaction.response.send_message("Vous n'avez pas la bonne icône !")
                await interaction.channel.send("Valider ici :", view=ViewValidator())
                
        else :
            await interaction.response.send_message("Votre compte a déjà été confirmé !")
        
       





async def set_profile(interaction:discord.Interaction,pseudo:str,region:app_commands.Choice[str]="euw1"):
   
        try:
            pseudo,tagline=await verifFormatRiotId(interaction,pseudo)
            me,region=await getMe(interaction,pseudo,tagline,region)
        except ApiError as err :
            if err.response.status_code == 429 :
                print("Quota de requête dépassé")
            elif err.response.status_code == 404:
                 await interaction.response.send_message("Le compte avec ce pseudo n'existe pas !",ephemeral=True)
            else:
                raise
        iconId=random.randint(0,28)
        icon=f'http://ddragon.leagueoflegends.com/cdn/{version["v"]}/img/profileicon/{iconId}.png'
        profile=get_player_data(interaction.user.id)
        
        if profile == None:    
            
            player_data={
                "id":interaction.user.id,
                "puuid": me['puuid'],
                "icon":icon,
                "region":region,
                "statut":0
            }
            insert_player_data(player_data)
            await interaction.response.send_message("Profile Trouvé !")
            await interaction.user.send("Veuillez confirmer votre compte en modifiant votre icone par celui ci : ")
            await interaction.user.send(icon)
            await interaction.user.send("Valider ici:", view=ViewValidator())
            await interaction.user.send("Pour annuler utilisez la commande : **/supprimer_mon_profil** ")
        else :
            if profile[4]==0:
                await interaction.user.send("Vous avez déjà un compte en train d'être lié !")
                await interaction.user.send(profile[str(interaction.user.id)]["icon"])
                await interaction.user.send("Valider ici :", view=ViewValidator())
            else:
                await interaction.response.send_message("Vous avez déjà un compte lié !",ephemeral=True)


async def del_profile(interaction:discord.Interaction):
    etat=delete_player_data(interaction.user.id)
    if etat==0:
        await interaction.response.send_message("Vous n'avez pas lié de compte !",ephemeral=True)
    else :
        await interaction.response.send_message("Votre compte a bien été supprimé !",ephemeral=True)