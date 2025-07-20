#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
縣市監視器指令模組
"""

import asyncio
import aiohttp
import discord
import datetime
import ssl
import logging
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

class CityCameraCommands(commands.Cog):
    """縣市監視器查詢指令"""
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="縣市監視器", description="查詢各縣市道路監視器")
    @app_commands.describe(county="選擇縣市")
    @app_commands.choices(county=[
        app_commands.Choice(name="宜蘭縣", value="YilanCounty"),
        # ... 其他縣市選項
    ])
    async def city_cameras(self, interaction: discord.Interaction, county: str):
        # 實作內容
        pass

async def setup(bot):
    await bot.add_cog(CityCameraCommands(bot))