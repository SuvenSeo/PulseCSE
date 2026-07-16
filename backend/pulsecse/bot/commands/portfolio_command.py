"""
This module contains the implementation of the portfolio command for the PulseCSE bot.
"""

import discord
from discord.ext import commands
from backend.pulsecse.bot import bot
from backend.pulsecse.models import User, Portfolio

class PortfolioCommand(commands.Cog):
    """
    This class represents the portfolio command.
    """

    def __init__(self, bot):
        """
        Initializes the portfolio command.

        Args:
            bot (commands.Bot): The PulseCSE bot instance.
        """
        self.bot = bot

    @commands.command(name="portfolio")
    async def portfolio(self, ctx):
        """
        Displays the user's portfolio.

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        user_id = ctx.author.id
        user = User.get_user(user_id)

        if user is None:
            await ctx.send("You do not have a portfolio.")
            return

        portfolio = Portfolio.get_portfolio(user_id)

        if portfolio is None:
            await ctx.send("You do not have a portfolio.")
            return

        embed = discord.Embed(title="Portfolio", description="Your current portfolio:")
        embed.add_field(name="Stocks", value=portfolio.stocks, inline=False)
        embed.add_field(name="Bonds", value=portfolio.bonds, inline=False)
        embed.add_field(name="Cash", value=portfolio.cash, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="add_stock")
    async def add_stock(self, ctx, stock_symbol: str, quantity: int):
        """
        Adds a stock to the user's portfolio.

        Args:
            ctx (commands.Context): The context of the command invocation.
            stock_symbol (str): The symbol of the stock to add.
            quantity (int): The quantity of the stock to add.
        """
        user_id = ctx.author.id
        user = User.get_user(user_id)

        if user is None:
            await ctx.send("You do not have a portfolio.")
            return

        portfolio = Portfolio.get_portfolio(user_id)

        if portfolio is None:
            portfolio = Portfolio.create_portfolio(user_id)

        portfolio.add_stock(stock_symbol, quantity)
        await ctx.send(f"Added {quantity} {stock_symbol} to your portfolio.")

    @commands.command(name="remove_stock")
    async def remove_stock(self, ctx, stock_symbol: str, quantity: int):
        """
        Removes a stock from the user's portfolio.

        Args:
            ctx (commands.Context): The context of the command invocation.
            stock_symbol (str): The symbol of the stock to remove.
            quantity (int): The quantity of the stock to remove.
        """
        user_id = ctx.author.id
        user = User.get_user(user_id)

        if user is None:
            await ctx.send("You do not have a portfolio.")
            return

        portfolio = Portfolio.get_portfolio(user_id)

        if portfolio is None:
            await ctx.send("You do not have a portfolio.")
            return

        portfolio.remove_stock(stock_symbol, quantity)
        await ctx.send(f"Removed {quantity} {stock_symbol} from your portfolio.")

def setup(bot):
    """
    Sets up the portfolio command.

    Args:
        bot (commands.Bot): The PulseCSE bot instance.
    """
    bot.add_cog(PortfolioCommand(bot))