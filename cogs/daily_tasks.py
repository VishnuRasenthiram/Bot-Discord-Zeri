import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
import pytz
import os
from io import BytesIO
from main import KARAN_ID,SALON_NASA
from zeri_features.zeri_interactions.zeri_nasa import imageNasa
from zeri_features.zeri_economy.zeriMoney import ZeriMoney

TIMEZONE_PARIS = "Europe/Paris"

class DailyTasks(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.economy = ZeriMoney(bot)
        self.scheduler = AsyncIOScheduler()
        self.icon_loaded = False


    async def cog_load(self):
        """Exécuté quand le cog est chargé"""
        await self.load_icons()
        self.setup_tasks()
        self.scheduler.start()


    async def load_icons(self):
        """Charge les icônes du serveur"""
        try:
            with open("env/ranked-emblem/Karan_nuit.png", 'rb') as n:
                self.iconNuit = n.read()
            with open("env/ranked-emblem/Karan_jour.png", 'rb') as j:
                self.iconJour = j.read()
            self.icon_loaded = True
        except Exception as e:
            print(f"❌ Erreur chargement icônes: {e}")

    def setup_tasks(self):
        """Configure les tâches planifiées"""
        try:
            self.scheduler.add_job(
                self.changement_icone_serveur,
                CronTrigger(hour=11, minute=1, timezone=TIMEZONE_PARIS)
            )
            self.scheduler.add_job(
                self.changement_icone_serveur,
                CronTrigger(hour=23, minute=1, timezone=TIMEZONE_PARIS)
            )
            self.scheduler.add_job(
                self.execute_daily_update, 
                CronTrigger(hour=0, minute=0, timezone=TIMEZONE_PARIS)
            )
        except Exception as e:
            print(f"❌ Erreur configuration tâches: {e}")

    async def execute_daily_update(self):
        """Wrapper pour exécuter update_daily correctement"""
        try:
            await self.economy.update_daily()
        except Exception as e:
            print(f"❌ Erreur dans update_daily: {e}")

    async def changement_icone_serveur(self):
        """Change l'icône et le nom du serveur"""
        try:

            if not self.icon_loaded:
                await self.load_icons()

            guild = self.bot.get_guild(KARAN_ID)
            if not guild:
                print("❌ Serveur introuvable")
            now = datetime.datetime.now(pytz.timezone(TIMEZONE_PARIS))
            current_hour = now.hour
            now = datetime.datetime.now(pytz.timezone("Europe/Paris"))
            current_hour = now.hour

            if current_hour >= 22 or current_hour < 10:
                await guild.edit(name="Karan 🌙", icon=self.iconNuit) 
            else:
                await guild.edit(name="Karan 🍁", icon=self.iconJour) 
                await self.apod_auto()
        except Exception as e:
            print(f"❌ Erreur changement icône: {e}")

    async def apod_auto(self):
        """Poste automatiquement l'image astronomique du jour"""
        try:
            salon = self.bot.get_channel(SALON_NASA)
            if salon:
                await imageNasa(salon)  
        except Exception as e:
            print(f"❌ Erreur APOD auto: {e}")


async def setup(bot):
    """Fonction obligatoire pour charger le cog"""
    await bot.add_cog(DailyTasks(bot))