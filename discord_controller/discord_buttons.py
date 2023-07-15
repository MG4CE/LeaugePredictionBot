from typing import Optional
import discord
from controller.controller import Controller

class PredictionButtons(discord.ui.View):

    def __init__(self, controller: Controller, *, timeout: Optional[float] = 180.0):
        self.controller = controller
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Predict Win", style=discord.ButtonStyle.success)
    async def win_button_callback(self, interaction: discord.interactions.Interaction, button):
        self.controller.process_prediction_selection_button_command(True, interaction)

    @discord.ui.button(label="Predict Loss", style=discord.ButtonStyle.danger)
    async def loss_button_callback(self, interaction: discord.interactions.Interaction, button):
        self.controller.process_prediction_selection_button_command(False, interaction)
