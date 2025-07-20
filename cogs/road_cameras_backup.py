#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import aiohttp
import ssl
import logging
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict
import datetime

logger = logging.getLogger(__name__)

class RoadCameraCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.provincial_api_url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
        self.national_api_url = "https://tisvcloud.freeway.gov.tw/history/motc20/CCTV.xml"

    async def _fetch_xml_data(self, url: str) -> Optional[ET.Element]:
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        return ET.fromstring(xml_content)
                    else:
                        logger.error(f"HTTP {response.status} 獲取資料失敗")
                        return None
        except Exception as e:
            logger.error(f"獲取 XML 資料錯誤: {str(e)}")
            return None

    @app_commands.command(name="省道監視器", description="查詢省道監視器")
    async def provincial_cameras(self, interaction: discord.Interaction, road_number: Optional[str] = None):
        await interaction.response.defer()
        
        try:
            root = await self._fetch_xml_data(self.provincial_api_url)
            if not root:
                await interaction.followup.send(" 無法獲取省道監視器資料")
                return
            
            cameras_count = len(root.findall('.//CCTV'))
            
            embed = discord.Embed(
                title=" 省道監視器查詢",
                description=f"共找到 {cameras_count} 個省道監視器",
                color=0x0099ff,
                timestamp=datetime.datetime.now()
            )
            
            if road_number:
                embed.add_field(name="道路編號", value=road_number, inline=True)
            
            embed.add_field(name="功能狀態", value=" 基本功能已就緒", inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"查詢省道監視器錯誤: {str(e)}")
            await interaction.followup.send(f" 查詢錯誤: {str(e)}")

    @app_commands.command(name="國道監視器", description="查詢國道監視器")
    async def national_cameras(self, interaction: discord.Interaction, highway: Optional[str] = None):
        await interaction.response.defer()
        
        try:
            root = await self._fetch_xml_data(self.national_api_url)
            if not root:
                await interaction.followup.send(" 無法獲取國道監視器資料")
                return
            
            cameras_count = len(root.findall('.//CCTV'))
            
            embed = discord.Embed(
                title=" 國道監視器查詢",
                description=f"共找到 {cameras_count} 個國道監視器",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            
            if highway:
                embed.add_field(name="國道編號", value=highway, inline=True)
            
            embed.add_field(name="功能狀態", value=" 基本功能已就緒", inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"查詢國道監視器錯誤: {str(e)}")
            await interaction.followup.send(f" 查詢錯誤: {str(e)}")

async def setup(bot):
    await bot.add_cog(RoadCameraCommands(bot))
