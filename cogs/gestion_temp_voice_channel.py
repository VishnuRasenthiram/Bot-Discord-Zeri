import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from bd.baseDeDonne import (
    add_temp_voice_creator, 
    remove_temp_voice_creator, 
    get_all_temp_voice_creators, 
    is_temp_voice_creator,
    init_temp_voice_creators_table
)

class VoiceChannelManager(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

        self.temp_voice_channels = {} 




    temp_voice_group = app_commands.Group(
        name="tempvoice", 
        description="Gestion des salons vocaux temporaires",
    )

    @temp_voice_group.command(name="add", description="Ajoute un canal comme créateur de salons vocaux temporaires")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_temp_voice(self, interaction: discord.Interaction, channel: discord.VoiceChannel = None):
        """Ajoute un canal comme créateur de salons vocaux temporaires"""
        await interaction.response.defer(ephemeral=True)

        if not channel:
            if isinstance(interaction.channel, discord.VoiceChannel):
                channel = interaction.channel
            else:
                await interaction.followup.send("Vous devez spécifier un canal vocal ou exécuter cette commande dans un canal vocal.", ephemeral=True)
                return
        
        if is_temp_voice_creator(channel.id):
            await interaction.followup.send(f"Le canal {channel.mention} est déjà configuré comme créateur de salons temporaires.", ephemeral=True)
            return
        

        success = add_temp_voice_creator(channel.id)
        
        if success:
            await interaction.followup.send(f"✅ Le canal {channel.mention} est maintenant configuré comme créateur de salons vocaux temporaires.", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Erreur lors de l'ajout du canal {channel.mention}.", ephemeral=True)

    @temp_voice_group.command(name="remove", description="Retire un canal de la liste des créateurs de salons temporaires")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_temp_voice(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Retire un canal de la liste des créateurs de salons temporaires"""
        await interaction.response.defer(ephemeral=True)
        

        if not is_temp_voice_creator(channel.id):
            await interaction.followup.send(f"Le canal {channel.mention} n'est pas configuré comme créateur de salons temporaires.", ephemeral=True)
            return
        

        success = remove_temp_voice_creator(channel.id)
        
        if success:
            await interaction.followup.send(f"✅ Le canal {channel.mention} a été retiré de la liste des créateurs de salons temporaires.", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Erreur lors du retrait du canal {channel.mention}.", ephemeral=True)

    @temp_voice_group.command(name="list", description="Affiche la liste des canaux créateurs de salons temporaires")
    async def list_temp_voice(self, interaction: discord.Interaction):
        """Affiche la liste des canaux créateurs de salons temporaires"""
        await interaction.response.defer(ephemeral=True)
        
        creators = get_all_temp_voice_creators()
        
        if not creators:
            await interaction.followup.send("Aucun canal créateur de salons temporaires n'est configuré.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Canaux créateurs de salons temporaires",
            description="Liste des canaux qui permettent la création de salons vocaux temporaires",
            color=discord.Color.blue()
        )
        
        channels_text = ""
        for channel_id in creators:
            channel = interaction.guild.get_channel(int(channel_id))
            if channel:
                channels_text += f"• {channel.mention} (`{channel.id}`)\n"
            else:
                channels_text += f"• Canal inconnu (`{channel_id}`)\n"
        
        embed.add_field(name="Canaux configurés", value=channels_text or "Aucun canal trouvé")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @commands.Cog.listener() 
    async def on_voice_state_update(self, member, before, after):
        """Gère la création et suppression des salons vocaux temporaires"""

        if after.channel and is_temp_voice_creator(after.channel.id):
            try:

                new_channel = await after.channel.clone(
                    name=f'◜⏳◞{member.display_name}',
                )
                

                self.temp_voice_channels[new_channel.id] = member.id
                

                view = self.create_control_buttons(new_channel.id)
                

                control_message = await new_channel.send(
                    f"**Salon créé par {member.display_name}**\nUtilisez ces boutons pour gérer votre salon vocal.", 
                    view=view
                )
                

                await member.move_to(new_channel)
            except Exception as e:
                print(f"Erreur lors de la création du salon temporaire: {e}")
        

        if before.channel:
                if "◜⏳◞" in before.channel.name :
                    if len(before.channel.members)==0:
                        await before.channel.delete()
    def create_control_buttons(self, channel_id):
        """Crée et retourne une vue avec les boutons de contrôle pour un salon vocal temporaire"""
        view = discord.ui.View(timeout=None)
        
        lock_button = discord.ui.Button(
            label="🔒 Verrouiller le salon", 
            style=discord.ButtonStyle.red, 
            custom_id=f"lock_channel_{channel_id}"
        )

        limit_button = discord.ui.Button(
            label="👥 Définir limite", 
            style=discord.ButtonStyle.blurple, 
            custom_id=f"set_limit_{channel_id}"
        )
        

        async def lock_callback(interaction: discord.Interaction):

            if interaction.user.id != self.temp_voice_channels.get(channel_id):
                await interaction.response.send_message("Seul le créateur du salon peut utiliser cette fonction.", ephemeral=True)
                return

            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                await interaction.response.send_message("Le salon n'existe plus.", ephemeral=True)
                return

            current_perms = channel.overwrites_for(interaction.guild.default_role)
            is_locked = current_perms.connect is False

            new_perms = discord.PermissionOverwrite(**{k: v for k, v in current_perms})
            new_perms.connect = not is_locked
            await channel.set_permissions(interaction.guild.default_role, overwrite=new_perms)

            lock_button.label = "🔓 Déverrouiller le salon" if not is_locked else "🔒 Verrouiller le salon"
            
            await interaction.response.edit_message(view=view)
            await interaction.followup.send(
                f"Le salon est maintenant {'verrouillé' if not is_locked else 'déverrouillé'}.", 
                ephemeral=True
            )
        

        async def limit_callback(interaction: discord.Interaction):

            if interaction.user.id != self.temp_voice_channels.get(channel_id):
                await interaction.response.send_message("Seul le créateur du salon peut utiliser cette fonction.", ephemeral=True)
                return

            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                await interaction.response.send_message("Le salon n'existe plus.", ephemeral=True)
                return
            

            class LimitModal(discord.ui.Modal, title='Définir une limite d\'utilisateurs'):
                limit_input = discord.ui.TextInput(
                    label='Nombre maximum d\'utilisateurs',
                    placeholder='Entrez un nombre entre 1 et 99 (0 = pas de limite)',
                    required=True,
                    min_length=1,
                    max_length=2
                )
                
                async def on_submit(self, modal_interaction: discord.Interaction):
                    try:
                        limit = int(self.limit_input.value)
                        if 0 <= limit <= 99:
                            if limit == 0:
                                await channel.edit(user_limit=0)
                                await modal_interaction.response.send_message("Limite d'utilisateurs supprimée.", ephemeral=True)
                            else:

                                await channel.edit(user_limit=limit)
                                await modal_interaction.response.send_message(f"Limite définie à {limit} utilisateurs.", ephemeral=True)
                        else:
                            await modal_interaction.response.send_message("La limite doit être entre 0 et 99.", ephemeral=True)
                    except ValueError:
                        await modal_interaction.response.send_message("Veuillez entrer un nombre valide.", ephemeral=True)
            
            await interaction.response.send_modal(LimitModal())
        

        lock_button.callback = lock_callback
        limit_button.callback = limit_callback
        

        view.add_item(lock_button)
        view.add_item(limit_button)
        
        return view

    @add_temp_voice.error
    @remove_temp_voice.error
    @list_temp_voice.error
    async def temp_voice_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur est survenue: {error}", ephemeral=True)
            print(f"Erreur dans les commandes tempvoice: {error}")

async def setup(bot):
    await bot.add_cog(VoiceChannelManager(bot))