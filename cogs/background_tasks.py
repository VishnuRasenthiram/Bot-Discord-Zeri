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
        self.lol_watcher = LolWatcher(os.getenv('RIOT_API'))

    async def cog_load(self):
        self.periodic_check.start()
        self.periodic_check_fini.start()
        self.periodic_check_ladder.start()

    async def cog_unload(self):
        self.periodic_check.cancel()
        self.periodic_check_fini.cancel()
        self.periodic_check_ladder.cancel()

        
 
    @tasks.loop(minutes=5)
    async def periodic_check(self):
        async with self.verif_lock:
            try:
                await self.verif_game_en_cours()

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503:
                    print("Service indisponible, attente...")
                    await asyncio.sleep(60)
                else:
                    print(f"Erreur HTTP: {e}")
            except Exception as e:
                print(f"Erreur: {e}")

    @tasks.loop(minutes=1)
    async def periodic_check_fini(self):
        try:
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
            liste = get_player_liste()
            gameDejaSend = []
            if liste is None:
                return

            for gameId in liste:
                gameDejaSend.append(int(gameId[3]))

            for player in liste:
                puuid, region = player[1], player[2]   
                try:
                    cg = self.lol_watcher.spectator.by_puuid(region, puuid)
                    if cg["gameId"] not in gameDejaSend and cg["gameQueueConfigId"] != 1700:
                        gameDejaSend.append(cg["gameId"])
                        

                        regionId = LOF.regionForRiotId(region)
                        image = await creer_image_avec_reessai(cg, regionId, region)

                        img_bytes = BytesIO()
                        image.save(img_bytes, format="PNG")
                        img_bytes.seek(0)
                        
                        liste_messages = []

                        channelListe = list(get_player_listeChannel(puuid))
                        for channelId in channelListe:
                            channel = self.bot.get_channel(int(channelId))
                            if channel:
                                img_copy = BytesIO(img_bytes.getvalue()) 
                                message = await channel.send(file=discord.File(img_copy, filename="Partie_En_Cours.png"))
                                liste_messages.append(message.id)

                        player_data = {"puuid": puuid, "derniereGame": cg["gameId"],"messages_id": str(liste_messages),"game_fini":0}
                        update_derniereGame(player_data)
                    break
                except ApiError as e:
                    if e.response.status_code == 404:
                        break
                except Exception as er:
                    print(f"Erreur inattendue test : {er}")
                    break

    async def verif_game_fini(self):
        liste = get_player_liste()
        gameDejaSend = []
        if liste is None:
            return

        for gameId in liste:
            if gameId[6] != 0 and gameId[6] != None:
                gameDejaSend.append((int)(gameId[6]))

        for player in liste:
            region = player[2]
            puuid = player[1]
            
            try:
                
                if  (int)(player[3]) not in gameDejaSend and (int)(player[3]) != None:
                    gameDejaSend.append(player[3])
                    
                    image = await after_game(region,player[3])

                    img_bytes = BytesIO()
                    image.save(img_bytes, format="PNG")
                    img_bytes.seek(0)
                    
                    message_liste = list(ast.literal_eval(player[5]))
                    channel_liste = list(ast.literal_eval(player[4]))

                    combined = zip(channel_liste, message_liste)

                    for channel, message_id in combined:
                        channel = self.bot.get_channel(int(channel))
                        
                        if channel:
                            message = await channel.fetch_message(message_id)
                            if message:
                                img_copy = BytesIO(img_bytes.getvalue()) 
                                await message.channel.send(file=discord.File(img_copy, filename="Partie_Fini.png"))
                                await message.delete()
                            
                    
                    player_data = {"puuid": puuid, "derniereGame": player[3],"messages_id": player[5],"game_fini":player[3]}
                    update_derniereGame(player_data)

                
            except ApiError as e:
                if e.response.status_code == 404:
                    pass
                    
            except Exception as er:
                pass

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