import discord
from discord.ext import *
import asyncio
import random
from bd.baseDeDonne import *
import math

class ZeriMoney:

    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def update_daily(self):

        userListe=get_user_liste()

        for user in userListe:
            if user[4] == 0:
                update_user_profile(user[0],user[1],user[2],user[3],user[4],0)
                
            else:
                update_user_profile(user[0],user[1],user[2],user[3],0,user[5])
                
    async def daily(self,interaction: discord.Interaction):
        id= interaction.user.id
        user=get_user_profile(id)
        if user==None:
           await  self.register(id)
        if user[4] == 0:
            if user[5]==7:
                newDaily=5
                newMoney=user[1]+(500*newDaily)+1000
            else:
                newDaily=user[5]+1
                newMoney=user[1]+(500*newDaily)
            
            update_user_profile(user[0],newMoney,user[2],user[3],1,newDaily)  
            await interaction.followup.send("Vous avez réclamé votre récompense quotidienne.")
        else:
            await interaction.followup.send("Vous avez déjà réclamé votre récompense quotidienne.")
        

    async def balance(self,interaction: discord.Interaction):
        id= interaction.user.id
        user=get_user_profile(id)
        if user==None:
           await  self.register(id)
        await interaction.followup.send(f"Balance: {user[1]} <:Zcoins:1357324573120397543> ")

    async def register(self,id):
        user=get_user_profile(id)
        if user==None:
            user={
                "id":id,
                "money":0,
                "level":0,
                "xp":0,
                "daily":0,
                "nb_daily" : 0
            }
            insert_user_profile(user)
            


    async def leaderboard(self,interaction: discord.Interaction):
        
        userListe=get_user_liste()
        userListe.sort(key=lambda x: x[1], reverse=True)
        embed=discord.Embed(
            title="Leaderboard",
            description="Top 10",
            color=discord.Color.blue()
        )
        taille=len(userListe)
        if(taille>10):
            taille=10

        for i in range(taille):
            if i<len(userListe):
                embed.add_field(
                    name=f"{i+1}. {self.bot.get_user(userListe[i][0])}",
                    value=f"Balance : {userListe[i][1]}",
                    inline=False
                )

        await interaction.followup.send(embed=embed)


    async def leaderboard_level(self,interaction: discord.Interaction):
        
        userListe=get_user_liste()
        userListe.sort(key=lambda x: x[2], reverse=True)
        embed=discord.Embed(
            title="Leaderboard",
            description="Top 10",
            color=discord.Color.blue()
        )
        taille=len(userListe)
        if(taille>10):
            taille=10

        for i in range(taille):
            if i<len(userListe):
                embed.add_field(
                    name=f"{i+1}. {self.bot.get_user(userListe[i][0])}",
                    value=f"Level : {userListe[i][2]}",
                    inline=False
                )

        await interaction.followup.send(embed=embed)
    async def profile(self,interaction: discord.Interaction):
        id= interaction.user.id
        user=get_user_profile(id)
        if user==None:
            await self.register(id)
        if user[4] == 0:
            claimed = "📫"
        else:
            claimed = "📪"
        embed=discord.Embed(
            title="Profile",
            description=f"{interaction.user.name} voici votre profil",
            color=discord.Color.blue()
        ).set_thumbnail(
            url=interaction.user.display_avatar.url
        ).add_field(
            name="Balance",
            value=f"{user[1]} ZC <:Zcoins:1357324573120397543> ",
            inline=True
        ).add_field(
            name="Level",
            value=user[2],
            inline=True
        ).add_field(
            name="XP",
            value=f"{user[3]}/{await self.xp_requis_pour_level(user[2]+1)}",
            inline=True
        ).add_field(
            name="Daily",
            value=claimed,
            inline=True
        ).add_field(
            name="Daily count",
            value=f"{user[5]}/7",
            inline=True
        )
        await interaction.followup.send(embed=embed)

        
    
    async def xp_requis_pour_level(self, level: int):
        base_xp = 100
        scaling_factor = 1.2
        return int(base_xp * (level ** scaling_factor) * math.log(level + 1))
    
    async def verif_level_up(self,message):
        id= message.author.id
        user=get_user_profile(id)
        if user==None:
           await  self.register(id)
        xp_requis = await self.xp_requis_pour_level(user[2])
        if user[3] >= xp_requis:
            newLevel = user[2] + 1
            newXP = user[3] - xp_requis
            update_user_profile(user[0],user[1]+newLevel*100,newLevel,newXP,user[4],user[5])

      
    async def add_xp(self,message, xp: int):
        id= message.author.id
        user=get_user_profile(id)
        if user==None:
           await self.register(id)
        newXP = user[3] + xp
        update_user_profile(user[0],user[1],user[2],newXP,user[4],user[5])
        await self.verif_level_up(message)
    
    async def pile_ou_face(self,interaction: discord.Interaction, mise: int, choix: str):
        id= interaction.user.id
        user=get_user_profile(id)
        if user==None:
           await self.register(id)
        if user[1] < mise:
            await interaction.followup.send("Vous n'avez pas assez d'argent pour miser cette somme.")
            return
        if mise < 0:
            await interaction.followup.send("Vous ne pouvez pas miser une somme négative.")
            return
        if mise<100:
            await interaction.followup.send("Vous devez miser au moins 100 ZC.")
            return
        if mise>10000:
            await interaction.followup.send("Vous ne pouvez pas miser plus de 10000 ZC.")
            return
        message =await interaction.followup.send(f"Vous avez misé {mise} ZC sur {choix}. La pièce est lancée...<:Zcoins:1357324573120397543> ")
        message = await interaction.channel.fetch_message(message.id)
        await asyncio.sleep(4)  
        if random.randint(0, 1) == 0:
            resultat = "Pile"
        else:
            resultat = "Face"
        await message.edit(content=f"Vous avez misé {mise} ZC sur {choix}. Résultat: {resultat}")  

        if resultat == choix:
            newMoney = user[1] + mise
            await interaction.followup.send(f"{interaction.user.mention} vous avez gagné {mise} ZC! <:Zcoins:1357324573120397543> ")
        else:
            newMoney = user[1] - mise
            await interaction.followup.send(f"{interaction.user.mention} vous avez perdu {mise} ZC. <:Zcoins:1357324573120397543> ")
        update_user_profile(user[0],newMoney,user[2],user[3],user[4],user[5])