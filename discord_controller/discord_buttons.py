from typing import Optional
import discord
from typing import Callable

class PredictionButtons(discord.ui.View):

    def __init__(self, callback: Callable, *, timeout: Optional[float] = 180.0):
        self.callback = callback
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Predict Win", style=discord.ButtonStyle.success)
    async def win_button_callback(self, interaction: discord.interactions.Interaction, button):
        self.callback(True, interaction)

    @discord.ui.button(label="Predict Loss", style=discord.ButtonStyle.danger)
    async def loss_button_callback(self, interaction: discord.interactions.Interaction, button):
        self.callback(False, interaction)
