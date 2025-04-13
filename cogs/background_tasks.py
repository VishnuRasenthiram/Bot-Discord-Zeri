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


KARAN_ID=614728233497133076
SALON_NASA=1317082270875652180
class BackgroundTasks(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.economy = ZeriMoney(bot)
        self.scheduler = AsyncIOScheduler()
        self.verif_lock_ladder = asyncio.Lock()
        self.verif_lock = asyncio.Lock()
        self.verif_lock_fini = asyncio.Lock()
        self.lol_watcher = LolWatcher(os.getenv('RIOT_API'))

    async def cog_load(self):
        self.periodic_check.start()
        self.periodic_check_ladder.start()

    async def cog_unload(self):
        self.periodic_check.cancel()
        self.periodic_check_ladder.cancel()

        
 
    @tasks.loop(minutes=5)
    async def periodic_check(self):
        async with self.verif_lock:
            try:
                await self.verif_game_en_cours()
                await self.verif_game_fini()

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503:
                    print("Service indisponible, attente...")
                    await asyncio.sleep(60)
                else:
                    print(f"Erreur HTTP: {e}")
            except Exception as e:
                print(f"Erreur: {e}")

    
      
    @tasks.loop(minutes=60)
    async def periodic_check_ladder(self):
        async with self.verif_lock_ladder:
            try:
                await self.update_ladder()
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503:
                    print("Service indisponible, attente...")
                    await asyncio.sleep(60)
                else:
                    print(f"Erreur HTTP: {e}")
            except Exception as e:
                print(f"Erreur: {e}")
            
   
    async def verif_game_en_cours(self):
        try:
            liste = get_player_liste()
            if not liste:
                return

            gameDejaSend = {int(gameId[3]) for gameId in liste if gameId[3]}

            tasks = []
            for player in liste:
                puuid, region = player[1], player[2]
                tasks.append(self.process_player_game(puuid, region, gameDejaSend))

            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            print(f"Erreur globale verif_game_en_cours: {e}")

    async def process_player_game(self, puuid, region, gameDejaSend):
        try:
            cg = await asyncio.to_thread(
                lambda: self.lol_watcher.spectator.by_puuid(region, puuid)
            )
            
            if cg["gameId"] in gameDejaSend or cg["gameQueueConfigId"] == 1700:
                return

            gameDejaSend.add(cg["gameId"])
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

            # Traitement parallèle
            image_task = asyncio.create_task(after_game(region, game_id))
            messages_task = asyncio.create_task(self.get_existing_messages(player))

            image, message_data = await asyncio.gather(image_task, messages_task)

            # Préparation image
            img_bytes = BytesIO()
            await asyncio.to_thread(lambda: image.save(img_bytes, format="PNG"))
            img_bytes.seek(0)

            # Envoi notifications
            await self.update_game_messages(message_data, img_bytes)

            # Mise à jour BDD
            player_data = {
                "puuid": puuid,
                "derniereGame": game_id,
                "messages_id": player[5],
                "game_fini": game_id
            }
            await asyncio.to_thread(lambda: update_derniereGame(player_data))

        except Exception as e:
            pass

    # Helpers
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