#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雷達圖查詢指令
提供查詢中央氣象署雷達圖整合無地形的功能
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import json
import asyncio
import logging
import ssl
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class RadarCommands(commands.Cog):
    """雷達圖查詢相關指令"""
    
    def __init__(self, bot):
        self.bot = bot
        # 原始雷達圖 API (台灣鄰近地區)
        self.cwa_radar_api = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-003"
        # 大範圍雷達圖 API (台灣較大範圍)
        self.cwa_large_radar_api = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-001"
        
        # 降雨雷達 API 配置
        self.rainfall_radar_apis = {
            "樹林": {
                "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-001",
                "code": "O-A0084-001",
                "location": "新北樹林",
                "description": "單雷達合成回波圖-樹林_無地形"
            },
            "南屯": {
                "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-002", 
                "code": "O-A0084-002",
                "location": "台中南屯",
                "description": "單雷達合成回波圖-南屯_無地形"
            },
            "林園": {
                "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-003",
                "code": "O-A0084-003", 
                "location": "高雄林園",
                "description": "單雷達合成回波圖-林園_無地形"
            }
        }
        
        # 從環境變數讀取 CWA API 密鑰
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.authorization = os.getenv('CWA_API_KEY')
        if not self.authorization:
            logger.error("❌ 錯誤: 找不到 CWA_API_KEY 環境變數")
            logger.info("請在 .env 檔案中設定 CWA_API_KEY=您的中央氣象署API密鑰")
        
        self.radar_cache = {}  # 快取雷達圖資料
        self.large_radar_cache = {}  # 快取大範圍雷達圖資料
        self.rainfall_radar_cache = {}  # 快取降雨雷達圖資料
        self.cache_timestamp = 0
        self.large_cache_timestamp = 0
        self.rainfall_cache_timestamp = {}  # 各雷達站的快取時間戳
        self.cache_duration = 300  # 快取 5 分鐘（雷達圖更新頻繁）
        
        # 初始化降雨雷達快取時間戳
        for station in self.rainfall_radar_apis.keys():
            self.rainfall_cache_timestamp[station] = 0
        
        # 設定 SSL 上下文
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def _add_timestamp_to_url(self, url):
        """為雷達圖片 URL 加上時間戳避免快取"""
        if not url:
            return url
        
        import time
        timestamp = int(time.time())
        
        # 檢查URL是否已經有參數
        if '?' in url:
            return f"{url}&_t={timestamp}"
        else:
            return f"{url}?_t={timestamp}"
        
    async def fetch_radar_data(self) -> Dict:
        """從中央氣象署 API 獲取雷達圖資料"""
        try:
            # 檢查快取
            current_time = asyncio.get_event_loop().time()
            if (self.radar_cache and 
                current_time - self.cache_timestamp < self.cache_duration):
                return self.radar_cache
            
            # 構建 API 參數
            params = {
                "Authorization": self.authorization,
                "downloadType": "WEB",
                "format": "JSON"
            }
            
            logger.info(f"正在從中央氣象署 API 獲取雷達圖資料: {self.cwa_radar_api}")
            
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(self.cwa_radar_api, params=params) as response:
                    if response.status == 200:
                        # 處理 MIME 類型問題，強制讀取為文本並解析 JSON
                        try:
                            response_text = await response.text()
                            data = json.loads(response_text)
                        except json.JSONDecodeError:
                            # 如果 JSON 解析失敗，嘗試直接使用 response.json()
                            data = await response.json(content_type=None)
                        
                        # 更新快取
                        self.radar_cache = data
                        self.cache_timestamp = current_time
                        
                        logger.info("成功獲取雷達圖資料")
                        return data
                    else:
                        logger.error(f"雷達圖 API 請求失敗: HTTP {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"獲取雷達圖資料時發生錯誤: {e}")
            return {}
    
    async def fetch_large_radar_data(self) -> Dict:
        """從中央氣象署 API 獲取大範圍雷達圖資料"""
        try:
            # 檢查快取
            current_time = asyncio.get_event_loop().time()
            if (self.large_radar_cache and 
                current_time - self.large_cache_timestamp < self.cache_duration):
                return self.large_radar_cache
            
            # 構建 API 參數
            params = {
                "Authorization": self.authorization,
                "downloadType": "WEB",
                "format": "JSON"
            }
            
            logger.info(f"正在從中央氣象署 API 獲取大範圍雷達圖資料: {self.cwa_large_radar_api}")
            
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(self.cwa_large_radar_api, params=params) as response:
                    if response.status == 200:
                        # 處理 MIME 類型問題，強制讀取為文本並解析 JSON
                        try:
                            response_text = await response.text()
                            data = json.loads(response_text)
                        except json.JSONDecodeError:
                            # 如果 JSON 解析失敗，嘗試直接使用 response.json()
                            data = await response.json(content_type=None)
                        
                        # 更新快取
                        self.large_radar_cache = data
                        self.large_cache_timestamp = current_time
                        
                        logger.info("成功獲取大範圍雷達圖資料")
                        return data
                    else:
                        logger.error(f"大範圍雷達圖 API 請求失敗: HTTP {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"獲取大範圍雷達圖資料時發生錯誤: {e}")
            return {}
    
    async def fetch_rainfall_radar_data(self, station: str) -> Dict:
        """從中央氣象署 API 獲取降雨雷達圖資料"""
        if station not in self.rainfall_radar_apis:
            logger.error(f"未知的降雨雷達站: {station}")
            return {}
        
        try:
            # 檢查快取
            current_time = asyncio.get_event_loop().time()
            if (station in self.rainfall_radar_cache and 
                current_time - self.rainfall_cache_timestamp.get(station, 0) < self.cache_duration):
                return self.rainfall_radar_cache[station]
            
            station_info = self.rainfall_radar_apis[station]
            
            # 構建 API 參數
            params = {
                "Authorization": self.authorization,
                "downloadType": "WEB",
                "format": "JSON"
            }
            
            logger.info(f"正在從中央氣象署 API 獲取 {station_info['location']} 降雨雷達圖資料: {station_info['api_url']}")
            
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(station_info['api_url'], params=params) as response:
                    if response.status == 200:
                        # 處理 MIME 類型問題，強制讀取為文本並解析 JSON
                        try:
                            response_text = await response.text()
                            data = json.loads(response_text)
                        except json.JSONDecodeError:
                            # 如果 JSON 解析失敗，嘗試直接使用 response.json()
                            data = await response.json(content_type=None)
                        
                        # 更新快取
                        self.rainfall_radar_cache[station] = data
                        self.rainfall_cache_timestamp[station] = current_time
                        
                        logger.info(f"成功獲取 {station_info['location']} 降雨雷達圖資料")
                        return data
                    else:
                        logger.error(f"{station_info['location']} 降雨雷達圖 API 請求失敗: HTTP {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"獲取 {station} 降雨雷達圖資料時發生錯誤: {e}")
            return {}
    
    def parse_radar_data(self, data: Dict) -> Dict:
        """解析雷達圖資料"""
        try:
            if 'cwaopendata' not in data:
                return {}
            
            cwa_data = data['cwaopendata']
            dataset = cwa_data.get('dataset', {})
            
            # 解析基本資訊
            radar_info = {
                'identifier': cwa_data.get('identifier', ''),
                'sent': cwa_data.get('sent', ''),
                'datetime': dataset.get('DateTime', ''),
                'description': '',
                'image_url': '',
                'radar_names': '',
                'coverage': {},
                'dimension': ''
            }
            
            # 解析資料集資訊
            dataset_info = dataset.get('datasetInfo', {})
            if dataset_info:
                radar_info['description'] = dataset_info.get('datasetDescription', '雷達整合回波圖')
                
                parameter_set = dataset_info.get('parameterSet', {})
                if parameter_set:
                    parameter = parameter_set.get('parameter', {})
                    if parameter:
                        radar_info['radar_names'] = parameter.get('radarName', '')
                    
                    radar_info['coverage'] = {
                        'longitude': parameter_set.get('LongitudeRange', ''),
                        'latitude': parameter_set.get('LatitudeRange', '')
                    }
                    radar_info['dimension'] = parameter_set.get('ImageDimension', '')
            
            # 解析資源資訊
            resource = dataset.get('resource', {})
            if resource:
                radar_info['image_url'] = resource.get('ProductURL', '')
                radar_info['description'] = resource.get('resourceDesc', radar_info['description'])
            
            return radar_info
            
        except Exception as e:
            logger.error(f"解析雷達圖資料時發生錯誤: {e}")
            return {}
    
    def parse_rainfall_radar_data(self, data: Dict) -> Dict:
        """解析降雨雷達圖資料"""
        try:
            if 'cwaopendata' not in data:
                return {}
            
            cwa_data = data['cwaopendata']
            dataset = cwa_data.get('dataset', {})
            
            # 解析基本資訊
            radar_info = {
                'identifier': cwa_data.get('identifier', ''),
                'sent': cwa_data.get('sent', ''),
                'datetime': dataset.get('DateTime', ''),
                'description': '',
                'image_url': '',
                'dimension': ''
            }
            
            # 解析資料集資訊
            dataset_info = dataset.get('datasetInfo', {})
            if dataset_info:
                radar_info['description'] = dataset_info.get('datasetDescription', '降雨雷達合成回波圖')
                
                parameter_set = dataset_info.get('parameterSet', {})
                if parameter_set:
                    radar_info['dimension'] = parameter_set.get('ImageDimension', '')
            
            # 解析資源資訊
            resource = dataset.get('resource', {})
            if resource:
                radar_info['image_url'] = resource.get('ProductURL', '')
                radar_info['description'] = resource.get('resourceDesc', radar_info['description'])
            
            return radar_info
            
        except Exception as e:
            logger.error(f"解析降雨雷達圖資料時發生錯誤: {e}")
            return {}
    
    def format_datetime(self, datetime_str: str) -> str:
        """格式化日期時間字符串"""
        try:
            if not datetime_str:
                return "未知時間"
            
            # 解析 ISO 格式時間
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            
            # 轉換為台灣時間格式
            return dt.strftime('%Y年%m月%d日 %H:%M')
            
        except Exception as e:
            logger.error(f"格式化時間時發生錯誤: {e}")
            return datetime_str
    
    def create_radar_embed(self, radar_info: Dict) -> discord.Embed:
        """建立雷達圖資訊 Embed"""
        # 根據是否有圖片選擇顏色
        color = discord.Colour.blue() if radar_info.get('image_url') else discord.Colour.red()
        
        embed = discord.Embed(
            title="🌩️ 台灣雷達圖整合 (無地形)",
            description="中央氣象署雷達回波整合圖像",
            color=color
        )
        
        # 觀測時間
        datetime_str = self.format_datetime(radar_info.get('datetime', ''))
        embed.add_field(
            name="⏰ 觀測時間",
            value=datetime_str,
            inline=True
        )
        
        # 發布時間
        sent_time = self.format_datetime(radar_info.get('sent', ''))
        embed.add_field(
            name="📡 發布時間",
            value=sent_time,
            inline=True
        )
        
        # 雷達站資訊
        radar_names = radar_info.get('radar_names', '')
        if radar_names:
            embed.add_field(
                name="📍 雷達站",
                value=radar_names,
                inline=False
            )
        
        # 覆蓋範圍
        coverage = radar_info.get('coverage', {})
        if coverage:
            longitude = coverage.get('longitude', '')
            latitude = coverage.get('latitude', '')
            if longitude and latitude:
                embed.add_field(
                    name="🗺️ 覆蓋範圍",
                    value=f"經度: {longitude}°\n緯度: {latitude}°",
                    inline=True
                )
        
        # 圖像規格
        dimension = radar_info.get('dimension', '')
        if dimension:
            embed.add_field(
                name="📐 圖像尺寸",
                value=f"{dimension} 像素",
                inline=True
            )
        
        # 說明
        description = radar_info.get('description', '')
        if description:
            embed.add_field(
                name="📝 說明",
                value=description,
                inline=False
            )
        
        # 圖片
        image_url = radar_info.get('image_url', '')
        if image_url:
            # 為雷達圖片 URL 加上時間戳避免快取
            timestamped_url = self._add_timestamp_to_url(image_url)
            embed.set_image(url=timestamped_url)
            embed.add_field(
                name="🔗 圖片連結",
                value=f"[點擊查看原始圖片]({timestamped_url})",
                inline=False
            )
        else:
            embed.add_field(
                name="❌ 圖片狀態",
                value="目前無法取得雷達圖片",
                inline=False
            )
        
        # 資料來源
        embed.set_footer(text="資料來源：中央氣象署 | 雷達圖每10分鐘更新")
        
        return embed
    
    def create_large_radar_embed(self, radar_info: Dict) -> discord.Embed:
        """建立大範圍雷達圖資訊 Embed"""
        # 根據是否有圖片選擇顏色
        color = discord.Colour.green() if radar_info.get('image_url') else discord.Colour.red()
        
        embed = discord.Embed(
            title="🌍 台灣大範圍雷達圖整合 (無地形)",
            description="中央氣象署雷達回波整合圖像 - 較大覆蓋範圍",
            color=color
        )
        
        # 觀測時間
        datetime_str = self.format_datetime(radar_info.get('datetime', ''))
        embed.add_field(
            name="⏰ 觀測時間",
            value=datetime_str,
            inline=True
        )
        
        # 發布時間
        sent_time = self.format_datetime(radar_info.get('sent', ''))
        embed.add_field(
            name="📡 發布時間",
            value=sent_time,
            inline=True
        )
        
        # 雷達站資訊
        radar_names = radar_info.get('radar_names', '')
        if radar_names:
            embed.add_field(
                name="📍 雷達站",
                value=radar_names,
                inline=False
            )
        
        # 覆蓋範圍 (突出大範圍特色)
        coverage = radar_info.get('coverage', {})
        if coverage:
            longitude = coverage.get('longitude', '')
            latitude = coverage.get('latitude', '')
            if longitude and latitude:
                embed.add_field(
                    name="🗺️ 覆蓋範圍 (大範圍)",
                    value=f"經度: {longitude}°\n緯度: {latitude}°\n📏 涵蓋更廣的鄰近海域",
                    inline=True
                )
        
        # 圖像規格
        dimension = radar_info.get('dimension', '')
        if dimension:
            embed.add_field(
                name="📐 圖像尺寸",
                value=f"{dimension} 像素",
                inline=True
            )
        
        # 說明
        description = radar_info.get('description', '')
        if description:
            embed.add_field(
                name="📝 說明",
                value=f"{description}\n🌊 此為大範圍版本，可觀察更多鄰近海域天氣",
                inline=False
            )
        
        # 圖片
        image_url = radar_info.get('image_url', '')
        if image_url:
            # 為大範圍雷達圖片 URL 加上時間戳避免快取
            timestamped_url = self._add_timestamp_to_url(image_url)
            embed.set_image(url=timestamped_url)
            embed.add_field(
                name="🔗 圖片連結",
                value=f"[點擊查看原始圖片]({timestamped_url})",
                inline=False
            )
        else:
            embed.add_field(
                name="❌ 圖片狀態",
                value="目前無法取得大範圍雷達圖片",
                inline=False
            )
        
        # 資料來源
        embed.set_footer(text="資料來源：中央氣象署 | 大範圍雷達圖每10分鐘更新")
        
        return embed
    
    def create_rainfall_radar_embed(self, radar_info: Dict, station: str) -> discord.Embed:
        """建立降雨雷達圖資訊 Embed"""
        # 根據是否有圖片選擇顏色
        color = discord.Colour.orange() if radar_info.get('image_url') else discord.Colour.red()
        
        station_name = self.rainfall_radar_apis[station]['location']
        
        embed = discord.Embed(
            title=f"🌧️ {station_name} 降雨雷達圖 (無地形)",
            description="中央氣象署降雨雷達回波圖像",
            color=color
        )
        
        # 觀測時間
        datetime_str = self.format_datetime(radar_info.get('datetime', ''))
        embed.add_field(
            name="⏰ 觀測時間",
            value=datetime_str,
            inline=True
        )
        
        # 發布時間
        sent_time = self.format_datetime(radar_info.get('sent', ''))
        embed.add_field(
            name="📡 發布時間",
            value=sent_time,
            inline=True
        )
        
        # 雷達站資訊
        embed.add_field(
            name="📍 雷達站",
            value=station_name,
            inline=False
        )
        
        # 圖像規格
        dimension = radar_info.get('dimension', '')
        if dimension:
            embed.add_field(
                name="📐 圖像尺寸",
                value=f"{dimension} 像素",
                inline=True
            )
        
        # 說明
        description = radar_info.get('description', '')
        if description:
            embed.add_field(
                name="📝 說明",
                value=description,
                inline=False
            )
        
        # 圖片
        image_url = radar_info.get('image_url', '')
        if image_url:
            # 為降雨雷達圖片 URL 加上時間戳避免快取
            timestamped_url = self._add_timestamp_to_url(image_url)
            embed.set_image(url=timestamped_url)
            embed.add_field(
                name="🔗 圖片連結",
                value=f"[點擊查看原始圖片]({timestamped_url})",
                inline=False
            )
        else:
            embed.add_field(
                name="❌ 圖片狀態",
                value="目前無法取得雷達圖片",
                inline=False
            )
        
        # 資料來源
        embed.set_footer(text="資料來源：中央氣象署 | 降雨雷達圖每10分鐘更新")
        
        return embed
    
    def create_info_embed(self) -> discord.Embed:
        """建立雷達圖說明 Embed"""
        embed = discord.Embed(
            title="🌩️ 雷達圖功能說明",
            description="台灣雷達圖整合功能介紹",
            color=discord.Colour.green()
        )
        
        embed.add_field(
            name="📡 雷達站覆蓋",
            value="五分山、花蓮、七股、墾丁、樹林、南屯、林園雷達",
            inline=False
        )
        
        embed.add_field(
            name="🗺️ 整合雷達圖範圍比較",
            value="""
            **一般範圍** (`/radar`):
            • 經度: 118.0° - 124.0°
            • 緯度: 20.5° - 26.5°
            • 涵蓋: 台灣本島及鄰近海域
            
            **大範圍** (`/radar_large`):
            • 經度: 115.0° - 126.5°
            • 緯度: 17.75° - 29.25°
            • 涵蓋: 台灣及更廣泛的鄰近海域
            """,
            inline=False
        )
        
        embed.add_field(
            name="📍 單雷達降雨圖",
            value="""
            **樹林雷達** (`/rainfall_radar 樹林`):
            • 位置: 新北樹林
            • 特色: 精細觀測北部地區降雨
            
            **南屯雷達** (`/rainfall_radar 南屯`):
            • 位置: 台中南屯
            • 特色: 精細觀測中部地區降雨
            
            **林園雷達** (`/rainfall_radar 林園`):
            • 位置: 高雄林園
            • 特色: 精細觀測南部地區降雨
            """,
            inline=False
        )
        
        embed.add_field(
            name="⏱️ 更新頻率",
            value="整合雷達圖: 每10分鐘\n單雷達降雨圖: 每6分鐘",
            inline=True
        )
        
        embed.add_field(
            name="🎨 圖像特色",
            value="所有雷達圖均為無地形遮蔽版本",
            inline=True
        )
        
        embed.add_field(
            name="🌈 回波強度說明",
            value="""
            **藍色**: 微弱降雨 (0-10 dBZ)
            **綠色**: 輕度降雨 (10-20 dBZ)
            **黃色**: 中度降雨 (20-30 dBZ)
            **橙色**: 強烈降雨 (30-40 dBZ)
            **紅色**: 劇烈降雨 (40+ dBZ)
            """,
            inline=False
        )
        
        embed.add_field(
            name="📱 可用指令",
            value="""
            **整合雷達圖:**
            • `/radar` - 一般範圍雷達圖
            • `/radar_large` - 大範圍雷達圖
            
            **單雷達降雨圖:**
            • `/rainfall_radar` - 選擇特定雷達站
            
            **說明:**
            • `/radar_info` - 功能說明
            """,
            inline=False
        )
        
        embed.add_field(
            name="💡 使用提示",
            value="""
            • **整合雷達圖**：適合觀察大範圍天氣系統
            • **單雷達降雨圖**：適合精細觀測特定區域降雨
            • **智慧切換**：可在不同雷達圖間一鍵切換
            """,
            inline=False
        )
        
        embed.set_footer(text="資料來源：中央氣象署")
        
        return embed
    
    @app_commands.command(name="radar", description="查詢台灣雷達圖整合 (無地形)")
    async def radar(self, interaction: discord.Interaction):
        """查詢雷達圖"""
        await interaction.response.defer()
        
        try:
            # 獲取雷達圖資料
            data = await self.fetch_radar_data()
            
            if not data:
                await interaction.followup.send("❌ 無法獲取雷達圖資料，請稍後再試。")
                return
            
            # 解析資料
            radar_info = self.parse_radar_data(data)
            
            if not radar_info:
                await interaction.followup.send("❌ 雷達圖資料解析失敗，請稍後再試。")
                return
            
            # 建立回應
            embed = self.create_radar_embed(radar_info)
            
            # 建立視圖（包含重新整理和說明按鈕）
            view = RadarView(self)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"查詢雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 查詢過程中發生錯誤，請稍後再試。")
    
    @app_commands.command(name="radar_info", description="雷達圖功能說明")
    async def radar_info(self, interaction: discord.Interaction):
        """雷達圖功能說明"""
        await interaction.response.defer()
        
        try:
            embed = self.create_info_embed()
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"顯示雷達圖說明時發生錯誤: {e}")
            await interaction.followup.send("❌ 顯示說明時發生錯誤，請稍後再試。")
    
    @app_commands.command(name="large_radar", description="查詢台灣大範圍雷達圖整合 (無地形)")
    async def radar_large(self, interaction: discord.Interaction):
        """查詢大範圍雷達圖"""
        await interaction.response.defer()
        
        try:
            # 獲取大範圍雷達圖資料
            data = await self.fetch_large_radar_data()
            
            if not data:
                await interaction.followup.send("❌ 無法獲取大範圍雷達圖資料，請稍後再試。")
                return
            
            # 解析資料
            radar_info = self.parse_radar_data(data)
            
            if not radar_info:
                await interaction.followup.send("❌ 大範圍雷達圖資料解析失敗，請稍後再試。")
                return
            
            # 建立回應
            embed = self.create_large_radar_embed(radar_info)
            
            # 建立視圖（包含重新整理和說明按鈕）
            view = LargeRadarView(self)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"查詢大範圍雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 查詢過程中發生錯誤，請稍後再試。")
    
    @app_commands.command(name="rainfall_radar", description="查詢降雨雷達圖 (樹林/南屯/林園)")
    @app_commands.describe(station="選擇雷達站：樹林(新北)、南屯(台中)、林園(高雄)")
    @app_commands.choices(station=[
        app_commands.Choice(name="🏢 新北樹林", value="樹林"),
        app_commands.Choice(name="🏭 台中南屯", value="南屯"),
        app_commands.Choice(name="🏗️ 高雄林園", value="林園")
    ])
    async def rainfall_radar(self, interaction: discord.Interaction, station: str):
        """查詢降雨雷達圖"""
        await interaction.response.defer()
        
        try:
            # 驗證雷達站
            if station not in self.rainfall_radar_apis:
                available_stations = list(self.rainfall_radar_apis.keys())
                await interaction.followup.send(f"❌ 無效的雷達站。可用選項：{', '.join(available_stations)}")
                return
            
            # 獲取降雨雷達圖資料
            data = await self.fetch_rainfall_radar_data(station)
            
            if not data:
                station_info = self.rainfall_radar_apis[station]
                await interaction.followup.send(f"❌ 無法獲取 {station_info['location']} 降雨雷達圖資料，請稍後再試。")
                return
            
            # 解析資料
            radar_info = self.parse_rainfall_radar_data(data)
            
            if not radar_info:
                station_info = self.rainfall_radar_apis[station]
                await interaction.followup.send(f"❌ {station_info['location']} 降雨雷達圖資料解析失敗，請稍後再試。")
                return
            
            # 建立回應
            embed = self.create_rainfall_radar_embed(radar_info, station)
            
            # 建立視圖（包含重新整理和切換按鈕）
            view = RainfallRadarView(self, station)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"查詢 {station} 降雨雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 查詢過程中發生錯誤，請稍後再試。")

class RadarView(discord.ui.View):
    """雷達圖查詢結果視圖"""
    
    def __init__(self, cog: RadarCommands):
        super().__init__(timeout=300)  # 5分鐘超時
        self.cog = cog
    
    @discord.ui.button(label="🔄 重新整理", style=discord.ButtonStyle.primary)
    async def refresh_radar(self, interaction: discord.Interaction, button: discord.ui.Button):
        """重新整理雷達圖"""
        await interaction.response.defer()
        
        try:
            # 清除快取，強制重新獲取
            self.cog.radar_cache = {}
            
            # 獲取最新資料
            data = await self.cog.fetch_radar_data()
            
            if not data:
                await interaction.followup.send("❌ 無法獲取最新雷達圖資料。", ephemeral=True)
                return
            
            # 解析資料
            radar_info = self.cog.parse_radar_data(data)
            
            if not radar_info:
                await interaction.followup.send("❌ 雷達圖資料解析失敗。", ephemeral=True)
                return
            
            # 建立新的 Embed
            embed = self.cog.create_radar_embed(radar_info)
            
            # 更新原始訊息
            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            logger.error(f"重新整理雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 重新整理時發生錯誤。", ephemeral=True)
    
    @discord.ui.button(label="ℹ️ 說明", style=discord.ButtonStyle.secondary)
    async def show_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """顯示雷達圖說明"""
        embed = self.cog.create_info_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🌍 大範圍", style=discord.ButtonStyle.success)
    async def switch_to_large(self, interaction: discord.Interaction, button: discord.ui.Button):
        """切換到大範圍雷達圖"""
        await interaction.response.defer()
        
        try:
            # 獲取大範圍雷達圖資料
            data = await self.cog.fetch_large_radar_data()
            
            if not data:
                await interaction.followup.send("❌ 無法獲取大範圍雷達圖資料。", ephemeral=True)
                return
            
            # 解析資料
            radar_info = self.cog.parse_radar_data(data)
            
            if not radar_info:
                await interaction.followup.send("❌ 大範圍雷達圖資料解析失敗。", ephemeral=True)
                return
            
            # 建立大範圍的 Embed
            embed = self.cog.create_large_radar_embed(radar_info)
            
            # 切換到大範圍視圖
            view = LargeRadarView(self.cog)
            
            # 更新原始訊息
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"切換到大範圍雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 切換時發生錯誤。", ephemeral=True)
    
    @discord.ui.button(label="📍 降雨雷達", style=discord.ButtonStyle.secondary)
    async def switch_to_rainfall(self, interaction: discord.Interaction, button: discord.ui.Button):
        """顯示降雨雷達選擇"""
        embed = discord.Embed(
            title="📍 選擇降雨雷達站",
            description="請選擇要查看的單雷達降雨圖",
            color=discord.Colour.blue()
        )
        
        embed.add_field(
            name="🏢 新北樹林",
            value="精細觀測北部地區降雨",
            inline=True
        )
        
        embed.add_field(
            name="🏭 台中南屯",
            value="精細觀測中部地區降雨",
            inline=True
        )
        
        embed.add_field(
            name="🏗️ 高雄林園",
            value="精細觀測南部地區降雨",
            inline=True
        )
        
        embed.add_field(
            name="💡 提示",
            value="單雷達降雨圖提供特定區域的精細降雨觀測，更新頻率為每6分鐘",
            inline=False
        )
        
        # 建立降雨雷達選擇視圖
        view = RainfallRadarSelectView(self.cog)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class LargeRadarView(discord.ui.View):
    """大範圍雷達圖查詢結果視圖"""
    
    def __init__(self, cog: RadarCommands):
        super().__init__(timeout=300)  # 5分鐘超時
        self.cog = cog
    
    @discord.ui.button(label="🔄 重新整理", style=discord.ButtonStyle.primary)
    async def refresh_large_radar(self, interaction: discord.Interaction, button: discord.ui.Button):
        """重新整理大範圍雷達圖"""
        await interaction.response.defer()
        
        try:
            # 清除快取，強制重新獲取
            self.cog.large_radar_cache = {}
            
            # 獲取最新資料
            data = await self.cog.fetch_large_radar_data()
            
            if not data:
                await interaction.followup.send("❌ 無法獲取最新大範圍雷達圖資料。", ephemeral=True)
                return
            
            # 解析資料
            radar_info = self.cog.parse_radar_data(data)
            
            if not radar_info:
                await interaction.followup.send("❌ 大範圍雷達圖資料解析失敗。", ephemeral=True)
                return
            
            # 建立新的 Embed
            embed = self.cog.create_large_radar_embed(radar_info)
            
            # 更新原始訊息
            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            logger.error(f"重新整理大範圍雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 重新整理時發生錯誤。", ephemeral=True)
    
    @discord.ui.button(label="ℹ️ 說明", style=discord.ButtonStyle.secondary)
    async def show_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """顯示雷達圖說明"""
        embed = self.cog.create_info_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🌩️ 一般範圍", style=discord.ButtonStyle.success)
    async def switch_to_normal(self, interaction: discord.Interaction, button: discord.ui.Button):
        """切換到一般範圍雷達圖"""
        await interaction.response.defer()
        
        try:
            # 獲取一般範圍雷達圖資料
            data = await self.cog.fetch_radar_data()
            
            if not data:
                await interaction.followup.send("❌ 無法獲取一般範圍雷達圖資料。", ephemeral=True)
                return
            
            # 解析資料
            radar_info = self.cog.parse_radar_data(data)
            
            if not radar_info:
                await interaction.followup.send("❌ 一般範圍雷達圖資料解析失敗。", ephemeral=True)
                return
            
            # 建立一般範圍的 Embed
            embed = self.cog.create_radar_embed(radar_info)
            
            # 切換到一般範圍視圖
            view = RadarView(self.cog)
            
            # 更新原始訊息
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"切換到一般範圍雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 切換時發生錯誤。", ephemeral=True)
    
    @discord.ui.button(label="📍 降雨雷達", style=discord.ButtonStyle.secondary)
    async def switch_to_rainfall(self, interaction: discord.Interaction, button: discord.ui.Button):
        """顯示降雨雷達選擇"""
        embed = discord.Embed(
            title="📍 選擇降雨雷達站",
            description="請選擇要查看的單雷達降雨圖",
            color=discord.Colour.green()
        )
        
        embed.add_field(
            name="🏢 新北樹林",
            value="精細觀測北部地區降雨",
            inline=True
        )
        
        embed.add_field(
            name="🏭 台中南屯",
            value="精細觀測中部地區降雨",
            inline=True
        )
        
        embed.add_field(
            name="🏗️ 高雄林園",
            value="精細觀測南部地區降雨",
            inline=True
        )
        
        embed.add_field(
            name="💡 提示",
            value="單雷達降雨圖提供特定區域的精細降雨觀測，更新頻率為每6分鐘",
            inline=False
        )
        
        # 建立降雨雷達選擇視圖
        view = RainfallRadarSelectView(self.cog)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class RainfallRadarView(discord.ui.View):
    """降雨雷達圖查詢結果視圖"""
    
    def __init__(self, cog: RadarCommands, current_station: str):
        super().__init__(timeout=300)  # 5分鐘超時
        self.cog = cog
        self.current_station = current_station
        
        # 為當前雷達站設置不同的按鈕樣式
        self.station_styles = {
            "樹林": discord.ButtonStyle.primary,
            "南屯": discord.ButtonStyle.success,
            "林園": discord.ButtonStyle.danger
        }
    
    @discord.ui.button(label="🔄 重新整理", style=discord.ButtonStyle.secondary)
    async def refresh_rainfall_radar(self, interaction: discord.Interaction, button: discord.ui.Button):
        """重新整理降雨雷達圖"""
        await interaction.response.defer()
        
        try:
            # 清除快取，強制重新獲取
            if self.current_station in self.cog.rainfall_radar_cache:
                del self.cog.rainfall_radar_cache[self.current_station]
            
            # 獲取最新資料
            data = await self.cog.fetch_rainfall_radar_data(self.current_station)
            
            if not data:
                station_info = self.cog.rainfall_radar_apis[self.current_station]
                await interaction.followup.send(f"❌ 無法獲取最新 {station_info['location']} 降雨雷達圖資料。", ephemeral=True)
                return
            
            # 解析資料
            radar_info = self.cog.parse_rainfall_radar_data(data)
            
            if not radar_info:
                station_info = self.cog.rainfall_radar_apis[self.current_station]
                await interaction.followup.send(f"❌ {station_info['location']} 降雨雷達圖資料解析失敗。", ephemeral=True)
                return
            
            # 建立新的 Embed
            embed = self.cog.create_rainfall_radar_embed(radar_info, self.current_station)
            
            # 更新原始訊息
            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            logger.error(f"重新整理 {self.current_station} 降雨雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 重新整理時發生錯誤。", ephemeral=True)
    
    @discord.ui.button(label="🏢 樹林", style=discord.ButtonStyle.primary)
    async def switch_to_shulin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """切換到樹林雷達站"""
        if self.current_station == "樹林":
            await interaction.response.send_message("ℹ️ 目前已在查看樹林雷達站。", ephemeral=True)
            return
        
        await self._switch_station(interaction, "樹林")
    
    @discord.ui.button(label="🏭 南屯", style=discord.ButtonStyle.success)
    async def switch_to_nantun(self, interaction: discord.Interaction, button: discord.ui.Button):
        """切換到南屯雷達站"""
        if self.current_station == "南屯":
            await interaction.response.send_message("ℹ️ 目前已在查看南屯雷達站。", ephemeral=True)
            return
        
        await self._switch_station(interaction, "南屯")
    
    @discord.ui.button(label="🏗️ 林園", style=discord.ButtonStyle.danger)
    async def switch_to_linyuan(self, interaction: discord.Interaction, button: discord.ui.Button):
        """切換到林園雷達站"""
        if self.current_station == "林園":
            await interaction.response.send_message("ℹ️ 目前已在查看林園雷達站。", ephemeral=True)
            return
        
        await self._switch_station(interaction, "林園")
    
    @discord.ui.button(label="🌩️ 整合雷達", style=discord.ButtonStyle.secondary)
    async def switch_to_integrated(self, interaction: discord.Interaction, button: discord.ui.Button):
        """切換到整合雷達圖"""
        await interaction.response.defer()
        
        try:
            # 獲取整合雷達圖資料
            data = await self.cog.fetch_radar_data()
            
            if not data:
                await interaction.followup.send("❌ 無法獲取整合雷達圖資料。", ephemeral=True)
                return
            
            # 解析資料
            radar_info = self.cog.parse_radar_data(data)
            
            if not radar_info:
                await interaction.followup.send("❌ 整合雷達圖資料解析失敗。", ephemeral=True)
                return
            
            # 建立整合雷達圖的 Embed
            embed = self.cog.create_radar_embed(radar_info)
            
            # 切換到整合雷達圖視圖
            view = RadarView(self.cog)
            
            # 更新原始訊息
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"切換到整合雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 切換時發生錯誤。", ephemeral=True)
    
    async def _switch_station(self, interaction: discord.Interaction, target_station: str):
        """切換雷達站的內部方法"""
        await interaction.response.defer()
        
        try:
            # 獲取目標雷達站資料
            data = await self.cog.fetch_rainfall_radar_data(target_station)
            
            if not data:
                station_info = self.cog.rainfall_radar_apis[target_station]
                await interaction.followup.send(f"❌ 無法獲取 {station_info['location']} 降雨雷達圖資料。", ephemeral=True)
                return
            
            # 解析資料
            radar_info = self.cog.parse_rainfall_radar_data(data)
            
            if not radar_info:
                station_info = self.cog.rainfall_radar_apis[target_station]
                await interaction.followup.send(f"❌ {station_info['location']} 降雨雷達圖資料解析失敗。", ephemeral=True)
                return
            
            # 建立新的 Embed
            embed = self.cog.create_rainfall_radar_embed(radar_info, target_station)
            
            # 切換到目標雷達站視圖
            view = RainfallRadarView(self.cog, target_station)
            
            # 更新原始訊息
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"切換到 {target_station} 降雨雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 切換時發生錯誤。", ephemeral=True)

class RainfallRadarSelectView(discord.ui.View):
    """降雨雷達選擇視圖"""
    
    def __init__(self, cog: RadarCommands):
        super().__init__(timeout=180)  # 3分鐘超時
        self.cog = cog
    
    @discord.ui.button(label="🏢 新北樹林", style=discord.ButtonStyle.primary)
    async def select_shulin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """選擇樹林雷達站"""
        await self._select_station(interaction, "樹林")
    
    @discord.ui.button(label="🏭 台中南屯", style=discord.ButtonStyle.success)
    async def select_nantun(self, interaction: discord.Interaction, button: discord.ui.Button):
        """選擇南屯雷達站"""
        await self._select_station(interaction, "南屯")
    
    @discord.ui.button(label="🏗️ 高雄林園", style=discord.ButtonStyle.danger)
    async def select_linyuan(self, interaction: discord.Interaction, button: discord.ui.Button):
        """選擇林園雷達站"""
        await self._select_station(interaction, "林園")
    
    async def _select_station(self, interaction: discord.Interaction, station: str):
        """選擇雷達站的內部方法"""
        await interaction.response.defer()
        
        try:
            # 獲取降雨雷達圖資料
            data = await self.cog.fetch_rainfall_radar_data(station)
            
            if not data:
                station_info = self.cog.rainfall_radar_apis[station]
                await interaction.followup.send(f"❌ 無法獲取 {station_info['location']} 降雨雷達圖資料。", ephemeral=True)
                return
            
            # 解析資料
            radar_info = self.cog.parse_rainfall_radar_data(data)
            
            if not radar_info:
                station_info = self.cog.rainfall_radar_apis[station]
                await interaction.followup.send(f"❌ {station_info['location']} 降雨雷達圖資料解析失敗。", ephemeral=True)
                return
            
            # 建立降雨雷達圖的 Embed
            embed = self.cog.create_rainfall_radar_embed(radar_info, station)
            
            # 建立降雨雷達圖視圖
            view = RainfallRadarView(self.cog, station)
            
            # 發送新的降雨雷達圖訊息
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"選擇 {station} 降雨雷達圖時發生錯誤: {e}")
            await interaction.followup.send("❌ 選擇時發生錯誤。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RadarCommands(bot))
