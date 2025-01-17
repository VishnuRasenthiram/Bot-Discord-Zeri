from discord import *
choixInteraction = [
    app_commands.Choice(name="Câlin", value="hug anime"),
    app_commands.Choice(name="Se moquer", value="laught at anime"),
    app_commands.Choice(name="Fuit", value="run away anime"),
    app_commands.Choice(name="Bise", value="kiss anime"),
    app_commands.Choice(name="Embrasse", value="kiss romantic anime"),
    app_commands.Choice(name="Prend par la main", value="hold hands anime"),
    app_commands.Choice(name="Pat", value="pat anime"),
    app_commands.Choice(name="Sourit", value="warm smile anime"),
    app_commands.Choice(name="Ignore", value="ignore anime"),
    app_commands.Choice(name="Frappe", value="punch anime"),
    app_commands.Choice(name="Pousse", value="push anime"),
    app_commands.Choice(name="Menace", value="threaten anime"),
    app_commands.Choice(name="Crie", value="shout anime"),
    app_commands.Choice(name="Fixe avec insistance", value="stare anime"),
    app_commands.Choice(name="Clin d’œil", value="wink anime"),
    app_commands.Choice(name="Tire", value="gun shoot anime"),
    app_commands.Choice(name="Gêné", value="shy anime"),
    app_commands.Choice(name="Pleure", value="cry anime"),
    app_commands.Choice(name="Boude", value="pout anime"),
    app_commands.Choice(name="Donne à manger", value="feed anime"),
    app_commands.Choice(name="S’assoit", value="sit anime"),
    app_commands.Choice(name="Dort", value="sleep with anime")
]

choixAction=[
    app_commands.Choice(name="Gêné", value="shy anime"),
    app_commands.Choice(name="S’ennuie", value="bored anime"),
    app_commands.Choice(name="Pleure", value="cry anime"),
    app_commands.Choice(name="Bave", value="drool anime"),
    app_commands.Choice(name="Affamé", value="hungry anime"),
    app_commands.Choice(name="Disparaît", value="disappear anime"),
    app_commands.Choice(name="Déprimé", value="depress anime"),
    app_commands.Choice(name="Heureux", value="happy anime"),
    app_commands.Choice(name="Dort", value="sleep anime"),
    app_commands.Choice(name="S’assoit", value="sit anime"),
    app_commands.Choice(name="Se reveille", value="wake up anime")
]





def generate_interaction_text(value, M1, M2):
    interaction_texts = {
        "hug anime": f"{M1} fait un câlin chaleureux à {M2} 🫂.",
        "run away anime": f"{M1} fuit {M2} 🏃💨.",
        "kiss anime": f"{M1} donne une bise à {M2} 💋.",
        "kiss romantic anime": f"{M1} embrasse tendrement {M2} ❤️.",
        "hold hands anime": f"{M1} prend doucement la main de {M2} 🤝.",
        "pat anime": f"{M1} tapote la tête de {M2} avec affection 🤗.",
        "warm smile anime": f"{M1} sourit chaleureusement à {M2} 😊.",
        "ignore anime": f"{M1} ignore complètement {M2} 🫥.",
        "punch anime": f"{M1} frappe {M2} de toute ses forces 🤜💥.",
        "push anime": f"{M1} pousse {M2} ✋.",
        "threaten anime": f"{M1} menace {M2} avec un regard intense ⚡.",
        "shout anime": f"{M1} crie en direction de {M2} 😡.",
        "stare anime": f"{M1} fixe {M2} avec insistance 👀.",
        "wink anime": f"{M1} fait un clin d’œil à {M2} 😉.",
        "gun shoot anime": f"{M1} piou piou pan pan pan sur {M2} 🔫.",
        "laught at anime": f"{M1} se fout de la gueule de {M2} 😆.",
        "shy anime": f"{M1} est gêné devant {M2} et rougit timidement 😳.",
        "cry anime": f"{M1} pleure à chaudes larmes devant {M2} 😭.",
        "pout anime": f"{M1} boude {M2} 🙁.",
        "drool anime": f"{M1} bave en regardant {M2} 🤤.",
        "feed anime": f"{M1} donne à manger à {M2} 🍲.",
        "sit anime": f"{M1} s’assoit tranquillement à côté de {M2} 🪑.",
        "sleep with anime": f"{M1} s’endort paisiblement à côté de {M2} 😴."
    }
    interaction_texts_none = {
        "cry anime": f"{M1} pleure à chaudes larmes 😭.",
        "shy anime": f"{M1} est gêné et rougit 😳.",
        "sleep anime": f"{M1} s’endort paisiblement 😴.",
        "bored anime": f"{M1} s’ennuie profondément🥱.",
        "drool anime": f"{M1} bave un peu en rêvassant 🤤.",
        "hungry anime": f"{M1} a faim et se tient le ventre 🍴.",
        "disappear anime": f"{M1} disparaît mystérieusement✨.",
        "depress anime": f"{M1} semble déprimer 😔.",
        "happy anime": f"{M1} est heureux😄.",
        "wake up anime": f"{M1} se réveille en sursaut😯.",
        "sit anime": f"{M1} s’assoit tranquillement, profitant du moment 🪑."
    }
    if M2 == None:
        return interaction_texts_none.get(value, f"Interaction inconnue de {M1} 🤔.")
    return interaction_texts.get(value, f"Interaction inconnue entre {M1} et {M2} 🤔.")