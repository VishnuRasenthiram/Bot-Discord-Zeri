from nasaapi import Client as ClientNasa
from dotenv import load_dotenv
import os
import discord
import requests

load_dotenv()

nasa=ClientNasa(api_key=os.getenv('NASA_API'))

async def imageNasa(channel):
    try :

        embed=discord.Embed(title=nasa.apod()["title"],
                    description=f"🔭 {nasa.apod()['date']}", 
                    color=discord.Color.red()).set_thumbnail(
                    url="https://www.nasa.gov/wp-content/uploads/2023/12/nasainsigniargb150px.png"
                    )
        if "copyright" in nasa.apod():

                    embed.add_field(
                    name="Auteur :", 
                    value=f'{nasa.apod()["copyright"]}', 
                    inline=True
                    )
        if nasa.apod()["media_type"]=="image":

            response = requests.get(nasa.apod()["hdurl"])

            file_name= nasa.apod()["hdurl"].split("/")[-1]

            if response.status_code == 200:
                if not os.path.exists(f"Image/apod/{file_name}"):
                    with open(f"Image/apod/{file_name}", "wb") as file: 
                        file.write(response.content)
            else:
                print("Erreur lors du téléchargement de l'image.")
                return
            
            file = discord.File(f"Image/apod/{file_name}", filename="apod.png")
            embed.set_image(url="attachment://apod.png")
            

        await channel.send(embed=embed,file=file)

        if nasa.apod()["media_type"]=="video":
            await channel.send(nasa.apod()["hdurl"])

    except Exception as e:
        print(e)
        await channel.send("Erreur lors de la récupération de l'image.")