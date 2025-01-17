from discord import *
from discord.ext import *
import asyncio
import json
import random




async def impo(ctx):
    from main import getBot

    bot = getBot()
    with open('dossierJson/imposteur.json','r') as f :
        users = json.load(f)
    users[f'{ctx.author.id}']={"game":"true"}
    roles=["Imposteur","Droide","Serpentin","Double-face","Super-héros"]
    task=[
            "Flash dans le vide",
            "Back",
            "Dive l'ennemi le plus proche",
            "Va voler le buff de ton jungle (le canon d'un de tes laners si tu es jungler)",
            "Prend un fight en utilisant aucun sort !",
            "Doit aller sur une lane ( split push )",
            "Doit revendre un objet et en acheter un autre",
            "Tu n'as plus le droit de prendre les cs range ( si tu es jg tu n'as plus le droit de prendre tes loups et corbin )",
            "Engage un fight et te plaindre de la team apres",
            "Reste caché dans un buisson pendant 30 secondes",
            "Suivre l'ennemi jusqu’à sa base",
            "Ne pas toucher aux sbires canon",
            "Prends des items totalement inutiles pour ton champion",
            "Pose une ward dans ta propre base",
            "Essayez d'aider un ennemi",
            "Dodge les compétences de tes alliés",
            "Insta-back après avoir quitté la base"
           
        ]
    doubleface=["Gentil","Imposteur"]
    if len(ctx.message.raw_mentions)==5:
        for i in ctx.message.raw_mentions:
            role =random.choice(roles)
            roles.remove(role)
            user= bot.get_user(i)
            users[f'{ctx.author.id}'][role]=user.id
            match role:
                case "Imposteur":
                    await user.send(f'{user.name} Vous êtes {role} \n Faire perdre la game sans se faire démasquer ')
                case "Droide":
                    await user.send(f'{user.name} Vous êtes {role} \n Gagner la game en suivant les instructions reçues ')
                case "Serpentin":
                    await user.send(f'{user.name} Vous êtes {role} \n Gagner la game en ayant le plus de morts et de dégâts de sa team')
                case "Double-face":
                    await user.send(f'{user.name} Vous êtes {role} \n Change de rôle aléatoirement. Doit gagner la game en tant que gentil ou perdre en imposteur')
                case "Super-héros":
                    await user.send(f'{user.name} Vous êtes {role} \n Gagner la game en ayant le plus de dégâts, d\'assistances et de kills.')
                case _:
                    await user.send("Feur")
        with open('dossierJson/imposteur.json','w') as f :
            json.dump(users,f)
        
        with open('dossierJson/imposteur.json','r') as f :
            jeu = json.load(f)
        boucle=jeu[str(ctx.author.id)]["game"]
        await asyncio.sleep(300)
        while(boucle=="true"):
            with open('dossierJson/imposteur.json','r') as f :
                jeu = json.load(f)
            boucle=jeu[str(ctx.author.id)]["game"]
            if jeu[str(ctx.author.id)]["game"]=="true":
                user= bot.get_user(jeu[str(ctx.author.id)]["Droide"])
                user2= bot.get_user(jeu[str(ctx.author.id)]["Double-face"])
                await user2.send(random.choice(doubleface))
                await user.send(random.choice(task))
                timer = random.randint(180,300)
                await asyncio.sleep(timer)
        
         
    else :
        await ctx.channel.send("Le nombre de participant n'est pas valide (5)")  

async def fi(ctx):
    from main import getBot

    bot = getBot()
    with open('dossierJson/imposteur.json','r') as f :
        jeu = json.load(f)
    jeu[str(ctx.author.id)]["game"]="false"
    with open('dossierJson/imposteur.json','w') as f :
            json.dump(jeu,f)
    await ctx.channel.send("La partie est terminé voici la liste des roles : ")
    for key,value in jeu[str(ctx.author.id)].items():
        
        if key!="game":
            user= bot.get_user(jeu[str(ctx.author.id)][key])
            await ctx.channel.send(f'{user.name} : {key}')
    jeu[str(ctx.author.id)].clear()
    jeu[str(ctx.author.id)]["game"]="false"
    with open('dossierJson/imposteur.json','w') as f :
            json.dump(jeu,f)