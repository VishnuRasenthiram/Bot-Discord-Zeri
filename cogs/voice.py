import json
import discord
from discord.ext import commands
from discord import app_commands
import random
from discord import FFmpegPCMAudio
from discord.utils import get
from youtube_search_music import YoutubeMusicSearch
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

load_dotenv()




voice_clients = {}
yt_dlp_options = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                'restrictfilenames': True,
                'noplaylist': True,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'logtostderr': False,
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch',
                'source_address': '0.0.0.0',
            }
YTDL = yt_dlp.YoutubeDL(yt_dlp_options)

FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }

KARAN_ID=614728233497133076

class Voice(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.playlist = []
        self.boucle = False
        self.current_song = 0

        

    @app_commands.command(name="play", description="rejoint le vocal")
    async def play(self, interaction: discord.Interaction, titre: str):
        """Rejoint le vocal"""

        await interaction.response.defer()
        
        try:

            if not interaction.user.voice:
                await interaction.followup.send("Vous n'êtes pas dans un salon vocal !")
                return
            
            channel = interaction.user.voice.channel
            already_connected = False
            for voice_client in self.bot.voice_clients:
                if voice_client.channel == channel:
                    already_connected = True
                    voice = voice_client
                    await interaction.followup.send(f"musique ajouté a la playlist!")

            if not already_connected:
                voice = await channel.connect()
                await interaction.followup.send(f"Je rejoins le vocal {channel.name}, préparation de l'audio...")
                
            self.playlist.append({
                    interaction.user.id: titre
                })

            
        

            try:

                song = self.playlist[self.current_song]

                results = YoutubeMusicSearch(os.getenv('API_GOOGLE')).search(song.values())
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(
                    None, 
                    lambda: YTDL.extract_info("https://www.youtube.com/watch?v="+results["items"][0]["id"]["videoId"], download=False)
                )
                

                if voice.is_connected() :
                    song_url = data['url']
                    voice.play(discord.FFmpegPCMAudio(song_url, **FFMPEG_OPTIONS))
                    await interaction.channel.send(f"🎵 Lecture!")

                self.current_song += 1
                if self.boucle and self.current_song >= len(self.playlist):
                    self.current_song = 0
                    
                    
            except Exception as e:
                await interaction.channel.send(f"❌ Erreur lors de la lecture audio : {e}")

            
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {e}")
   
    @app_commands.command(name="leave", description="rejoint le vocal")
    async def leave(self, interaction: discord.Interaction):
        """Rejoint le vocal"""
        try:
            channel = interaction.user.voice.channel
            
            
            if channel is not None:
                for voice_protocol in self.bot.voice_clients:
                    if voice_protocol.channel == interaction.user.voice.channel:
                        await voice_protocol.disconnect(force=True)
                        break
                await interaction.response.send_message(f"Je quitte le vocal {channel.name}")
                
            else:
                await interaction.response.send_message("Vous n'êtes pas dans un salon vocal !")

            
        except Exception as e:
            await interaction.response.send_message(f"Erreur : {e}")    

    @app_commands.command(name="playlist", description="affiche la playlist")
    async def playlist(self, interaction: discord.Interaction):

        try:
            
                
            await interaction.response.defer()
            await interaction.followup.send("Voici la playlist :"+str(self.playlist))

            
        except Exception as e:
            await interaction.response.send_message(f"Erreur : {e}")
        
#async def setup(bot):
#    await bot.add_cog(Voice(bot))