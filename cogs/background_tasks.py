import discord
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import asyncio
from io import BytesIO
import ast
import requests
from lol_commands.leagueOfFunction import LOF, creer_image_avec_reessai
from riotwatcher import LolWatcher
from riotwatcher.exceptions import ApiError
from zeri_features.zeri_economy.zeriMoney import ZeriMoney
from bd.baseDeDonne import (
    get_ladder_profile,
    get_player_liste, 
    get_player_listeChannel, 
    update_derniereGame
)
from lol_commands.classement.ladderLol import (
    create_ladder, 
    get_listChannelLadder,
    get_messageId_listChannelLadder, 
    update_messageId_listChannelLadder
)

from lol_commands.after_game.after_game import after_game


import shutil
import datetime
import pickle
import time as time_module
from pathlib import Path
import logging

KARAN_ID=614728233497133076
SALON_NASA=1317082270875652180
class BackgroundTasks(commands.Cog):
    CACHE_PICKLE_PATTERN = '*.pickle'

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.economy = ZeriMoney(bot)
        

        self.logger = logging.getLogger('zeribot.cache')
        self.logger.setLevel(logging.DEBUG)
        
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        

        self.scheduler = AsyncIOScheduler()
        self.verif_lock_ladder = asyncio.Lock()
        self.verif_lock = asyncio.Lock()
        self.verif_lock_fini = asyncio.Lock()
        riot_api_key = os.getenv('RIOT_API')
        if not riot_api_key:
            raise ValueError("RIOT_API environment variable is not set.")
        self.lol_watcher = LolWatcher(riot_api_key)

        self.CACHE_DIR = Path("cache")
        self.CACHE_DIR.mkdir(exist_ok=True)
        self.CACHE_MAX_AGE = 86400  # 24 heures en secondes
        self.CACHE_MAX_SIZE = 500 * 1024 * 1024  # 500 MB
        

        self._setup_cache_system()
        

    def _setup_cache_system(self):
        """Configure le système de cache et planifie son nettoyage"""
        self.scheduler.add_job(self.clean_old_cache_files, 'interval', hours=12)
        self.scheduler.add_job(self.clean_cache_if_full, 'interval', hours=3)
        self.logger.info("Système de cache configuré")

    def get_cache_size(self):
        """Calcule la taille totale du cache en octets"""
        total_size = 0
        for path in self.CACHE_DIR.glob('**/*'):
            if path.is_file():
                total_size += path.stat().st_size
        return total_size

    def clean_old_cache_files(self):
        """Supprime les fichiers de cache plus anciens que CACHE_MAX_AGE"""
        try:
            now = time_module.time()
            count = 0
            for file_path in self.CACHE_DIR.glob(self.CACHE_PICKLE_PATTERN):
                if now - file_path.stat().st_mtime > self.CACHE_MAX_AGE:
                    file_path.unlink()
                    count += 1
            self.logger.info(f"Nettoyage du cache: {count} fichiers supprimés")
        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage du cache: {e}")

    def clean_cache_if_full(self):
        """Nettoie le cache s'il dépasse la taille maximale"""
        if self.get_cache_size() > self.CACHE_MAX_SIZE:
            self.logger.warning("Cache plein, nettoyage en cours...")
            files = [(f, f.stat().st_mtime) for f in self.CACHE_DIR.glob(self.CACHE_PICKLE_PATTERN)]
            files.sort(key=lambda x: x[1])
            files = [(f, f.stat().st_mtime) for f in self.CACHE_DIR.glob('*.pickle')]
            files.sort(key=lambda x: x[1])
            

            target_size = self.CACHE_MAX_SIZE * 0.7  
            while files and self.get_cache_size() > target_size:
                if files:
                    oldest_file = files.pop(0)[0]
                    oldest_file.unlink()
                    
            self.logger.info(f"Cache réduit à {self.get_cache_size() / 1024 / 1024:.2f} MB")
    
    def cache_api_data(self, function_name, data, *args, max_age=3600):
        """Sauvegarde les données dans le cache avec un temps d'expiration"""
        cache_file = self.CACHE_DIR / f"{function_name}_{hash(str(args))}.pickle"
        with open(cache_file, 'wb') as f:
            expiry_time = time_module.time() + max_age
            cache_data = {
                'data': data,
                'expires': expiry_time
            }
            pickle.dump(cache_data, f)
        

        if self.get_cache_size() > self.CACHE_MAX_SIZE:
            self.clean_cache_if_full()
    
    def get_cached_api_data(self, function_name, *args, timeout=3600):
        """Cache les appels à l'API Riot pour éviter les 429"""
        cache_file = self.CACHE_DIR / f"{function_name}_{hash(str(args))}.pickle"
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)

                if time_module.time() < cache_data.get('expires', 0):
                    return cache_data['data']
                else:

                    cache_file.unlink(missing_ok=True)
        
        return None

    async def cog_load(self):

        self.periodic_check_ladder.start()
        self.scheduler.start()
        self.logger.info("Background tasks et planificateur démarrés")

    async def cog_unload(self):

        self.periodic_check_ladder.cancel()
        self.scheduler.shutdown()
        self.logger.info("Background tasks et planificateur arrêtés")

    @tasks.loop(minutes=5)
    async def periodic_check(self):
        """Vérifie périodiquement les parties en cours et terminées"""
        try:
            async with self.verif_lock:
                await self.verif_game_en_cours()
                
            async with self.verif_lock_fini:
                await self.verif_game_fini()
        except Exception as e:
            self.logger.error(f"Erreur dans la vérification périodique: {str(e)}")

    @tasks.loop(minutes=15)
    async def periodic_check_ladder(self):
        """Met à jour périodiquement les classements"""
        try:
            async with self.verif_lock_ladder:
                await self.update_ladder()
        except Exception as e:
            self.logger.error(f"Erreur dans la mise à jour des classements: {str(e)}")

    @commands.command(name="clear_cache")
    @commands.is_owner() 
    async def clear_cache_command(self, ctx):
        """Commande permettant de nettoyer le cache manuellement"""
        try:
            before_size = self.get_cache_size() / 1024 / 1024  # Taille en MB
            
            if self.CACHE_DIR.exists():
                shutil.rmtree(self.CACHE_DIR)
            self.CACHE_DIR.mkdir(exist_ok=True)
            
            await ctx.send(f"✅ Cache vidé ! ({before_size:.2f} MB libérés)")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du nettoyage du cache: {e}")
    
    @commands.command(name="cache_status")
    @commands.is_owner()
    async def cache_status_command(self, ctx):
        """Affiche des statistiques sur l'utilisation du cache"""
        try:
            file_count = len(list(self.CACHE_DIR.glob(self.CACHE_PICKLE_PATTERN)))
            
            files = [(f, f.stat().st_mtime) for f in self.CACHE_DIR.glob(self.CACHE_PICKLE_PATTERN)]
            files.sort(key=lambda x: x[1], reverse=True)
            recent_files = files[:5] if files else []
            files.sort(key=lambda x: x[1], reverse=True)
            recent_files = files[:5] if files else []
            
            cache_size = self.get_cache_size() / 1024 / 1024  # Taille en MB

            embed = discord.Embed(
                title="Statistiques du Cache",
                description="État actuel du système de cache",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Taille du cache", value=f"{cache_size:.2f} MB / {self.CACHE_MAX_SIZE/1024/1024} MB", inline=False)
            embed.add_field(name="Nombre de fichiers", value=str(file_count), inline=True)
            embed.add_field(name="Max âge", value=f"{self.CACHE_MAX_AGE/3600} heures", inline=True)
            
            if recent_files:
                recent = "\n".join([f"{Path(f[0].name).stem} ({datetime.datetime.fromtimestamp(f[1]).strftime('%H:%M:%S')})" for f in recent_files])
                embed.add_field(name="Fichiers récents", value=recent, inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
            

    async def process_player_game(self, puuid, region, game_deja_send):
        try:

            cache_key = f"spectator_{region}_{puuid}"
            cached_data = self.get_cached_api_data(cache_key, timeout=120) 
            
            if cached_data:
                cg = cached_data
                self.logger.info(f"Données de spectator récupérées du cache pour {puuid}")
            else:

                cg = await asyncio.to_thread(
                    lambda: self.lol_watcher.spectator.by_puuid(region, puuid)
                )
                self.cache_api_data(cache_key, cg, max_age=120)

            if cg["gameId"] in game_deja_send or cg["gameQueueConfigId"] == 1700:
                return

            game_deja_send.add(cg["gameId"])
            regionId = LOF.regionForRiotId(region)
            

            image_task = asyncio.create_task(creer_image_avec_reessai(cg, regionId, region))
            channels_task = asyncio.create_task(self.get_channels_to_notify(puuid))
            
            image, channel_ids = await asyncio.gather(image_task, channels_task)


            img_bytes = BytesIO()
            await asyncio.to_thread(lambda: image.save(img_bytes, format="PNG"))
            img_bytes.seek(0)

            message_ids = await self.send_notifications(channel_ids, img_bytes)


            player_data = {
                "puuid": puuid,
                "derniereGame": cg["gameId"],
                "messages_id": str(message_ids),
                "game_fini": 0
            }
            await asyncio.to_thread(lambda: update_derniereGame(player_data))

        except ApiError as e:
            if e.response.status_code != 404 and e.response.status_code != 403 and e.response.status_code != 429:
                print(f"API Error for {puuid}: {e}")
        except Exception as e:
            print(f"Error processing player {puuid}: {e}")

    async def verif_game_en_cours(self):
        try:
            liste = get_player_liste()
            if not liste:
                return

            game_deja_send = {int(gameId[3]) for gameId in liste if gameId[3]}

            tasks = []
            for player in liste:
                puuid, region = player[1], player[2]
                tasks.append(self.process_player_game(puuid, region, game_deja_send))

            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            print(f"Erreur globale verif_game_en_cours: {e}")

    async def verif_game_fini(self):
        try:
            liste = get_player_liste()
            if not liste:
                return

            gameDejaSend = {int(gameId[6]) for gameId in liste if gameId[6]}

            tasks = []
            for player in liste:
                if player[3] and int(player[3]) not in gameDejaSend:
                    tasks.append(self.process_finished_game(player, gameDejaSend))

            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            print(f"Erreur globale verif_game_fini: {e}")

    async def process_finished_game(self, player, gameDejaSend):
        try:
            puuid, region, game_id = player[1], player[2], player[3]
            gameDejaSend.add(game_id)


            image_task = asyncio.create_task(after_game(region, game_id))
            messages_task = asyncio.create_task(self.get_existing_messages(player))

            image, message_data = await asyncio.gather(image_task, messages_task)


            img_bytes = BytesIO()
            await asyncio.to_thread(lambda: image.save(img_bytes, format="PNG"))
            img_bytes.seek(0)


            await self.update_game_messages(message_data, img_bytes)

            player_data = {
                "puuid": puuid,
                "derniereGame": game_id,
                "messages_id": player[5],
                "game_fini": game_id
            }
            await asyncio.to_thread(lambda: update_derniereGame(player_data))

        except Exception as e:
            pass

    async def get_channels_to_notify(self, puuid):
        return list(get_player_listeChannel(puuid))

    async def send_notifications(self, channel_ids, img_bytes):
        message_ids = []
        for channel_id in channel_ids:
            try:
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    img_copy = BytesIO(img_bytes.getvalue())
                    msg = await channel.send(file=discord.File(img_copy, "Partie_En_Cours.png"))
                    message_ids.append(msg.id)
            except Exception as e:
                print(f"Error sending to channel {channel_id}: {e}")
        return message_ids

    async def get_existing_messages(self, player):
        try:
            return list(zip(
                ast.literal_eval(player[4]),
                ast.literal_eval(player[5])
            ))
        except Exception as e:
            print(f"Error parsing message data: {e}")
            return []

    async def update_game_messages(self, message_data, img_bytes):
        for channel_id, message_id in message_data:
            try:
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    message = await channel.fetch_message(int(message_id))
                    if message:
                        img_copy = BytesIO(img_bytes.getvalue())
                        await message.channel.send(file=discord.File(img_copy, "Partie_Fini.png"))
                        await message.delete()
            except Exception as e:
                print(f"Error updating message {message_id}: {e}")

    async def update_ladder(self):
        ladder = get_listChannelLadder()
        for channel in ladder:
            channel_id = int(channel[0])    
            channel = self.bot.get_channel(channel_id)
            if channel:
                listeJoueur= get_ladder_profile(channel_id)
                if listeJoueur:
                    try:
                        message = await channel.fetch_message(get_messageId_listChannelLadder(channel_id))
                        await message.edit(embed=await create_ladder(listeJoueur))
                    except discord.errors.NotFound:
                        message = await channel.send(embed=await create_ladder(listeJoueur))
                        update_messageId_listChannelLadder(channel_id, message.id)
           
    
                    

async def setup(bot):
    await bot.add_cog(BackgroundTasks(bot))