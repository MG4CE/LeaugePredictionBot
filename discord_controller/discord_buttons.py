import discord

class PredictionButtons(discord.ui.View):
    @discord.ui.button(label="Predict Win", style=discord.ButtonStyle.success)
    async def win_button_callback(self, interaction, button):
        await interaction.response.send_message("You pressed me!")

    @discord.ui.button(label="Predict Loss", style=discord.ButtonStyle.danger)
    async def loss_button_callback(self, interaction, button):
        await interaction.response.send_message("You pressed me!")