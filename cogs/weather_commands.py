#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
氣象測站查詢指令
提供查詢中央氣象署無人氣象測站基本資料的功能
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import json
import asyncio
import logging
from typing import Optional, List, Dict, Tuple
import urllib.parse
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherCommands(commands.Cog):
    """氣象測站查詢相關指令"""
    
    def __init__(self, bot):
        self.bot = bot
        self.cwa_api_base = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
        
        # 從環境變數讀取 CWA API 密鑰
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.authorization = os.getenv('CWA_API_KEY')
        if not self.authorization:
            logger.error("❌ 錯誤: 找不到 CWA_API_KEY 環境變數")
            logger.info("請在 .env 檔案中設定 CWA_API_KEY=您的中央氣象署API密鑰")
        
        self.station_data_cache = {}  # 快取測站資料
        self.cache_timestamp = 0
        self.cache_duration = 3600  # 快取 1 小時
        
    async def fetch_station_data(self) -> Dict:
        """從 CWA API 獲取無人氣象測站基本資料"""
        try:
            # 檢查快取
            current_time = asyncio.get_event_loop().time()
            if (self.station_data_cache and 
                current_time - self.cache_timestamp < self.cache_duration):
                return self.station_data_cache
            
            # 構建 API URL
            endpoint = "C-B0074-002"
            url = f"{self.cwa_api_base}/{endpoint}"
            
            params = {
                "Authorization": self.authorization,
                "format": "JSON"
            }
            
            logger.info(f"正在從 CWA API 獲取測站資料: {url}")
            
            if hasattr(self.bot, 'connector') and self.bot.connector:
                connector = self.bot.connector
            else:
                connector = aiohttp.TCPConnector(ssl=False)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 更新快取
                        self.station_data_cache = data
                        self.cache_timestamp = current_time
                        
                        logger.info("成功獲取測站資料")
                        return data
                    else:
                        logger.error(f"API 請求失敗，狀態碼: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"獲取測站資料時發生錯誤: {str(e)}")
            return None
    
    def parse_station_data(self, data: Dict) -> List[Dict]:
        """解析測站資料"""
        try:
            if not data or not data.get('success') == 'true':
                logger.error("API 回應格式錯誤或請求失敗")
                return []
            
            stations = data.get('records', {}).get('data', {}).get('stationStatus', {}).get('station', [])
            if not stations:
                logger.error("無法找到測站資料")
                return []
            
            # 整理測站資料
            processed_stations = []
            for station in stations:
                processed_station = {
                    'id': station.get('StationID', ''),
                    'name': station.get('StationName', ''),
                    'name_en': station.get('StationNameEN', ''),
                    'altitude': station.get('StationAltitude', 0),
                    'longitude': station.get('StationLongitude', 0),
                    'latitude': station.get('StationLatitude', 0),
                    'county': station.get('CountyName', ''),
                    'location': station.get('Location', ''),
                    'start_date': station.get('StationStartDate', ''),
                    'end_date': station.get('StationEndDate', ''),
                    'status': station.get('status', ''),
                    'notes': station.get('Notes', ''),
                    'original_id': station.get('OriginalStationID', ''),
                    'new_id': station.get('NewStationID', '')
                }
                processed_stations.append(processed_station)
            
            logger.info(f"成功解析 {len(processed_stations)} 個測站資料")
            return processed_stations
            
        except Exception as e:
            logger.error(f"解析測站資料時發生錯誤: {str(e)}")
            return []
    
    def search_stations(self, stations: List[Dict], query: str) -> List[Dict]:
        """搜尋測站"""
        query = query.strip().lower()
        if not query:
            return []
        
        matches = []
        
        for station in stations:
            # 搜尋條件：測站ID、測站名稱、縣市名稱、位置
            searchable_fields = [
                station.get('id', '').lower(),
                station.get('name', '').lower(),
                station.get('county', '').lower(),
                station.get('location', '').lower(),
                station.get('name_en', '').lower()
            ]
            
            # 檢查是否有任何欄位包含查詢字串
            if any(query in field for field in searchable_fields):
                matches.append(station)
        
        # 按照測站狀態排序（現存測站優先）
        matches.sort(key=lambda x: (x.get('status') != '現存測站', x.get('name', '')))
        
        return matches
    
    def create_station_embed(self, station: Dict) -> discord.Embed:
        """創建測站詳細資訊的 Embed"""
        # 根據測站狀態設定顏色
        if station.get('status') == '現存測站':
            color = discord.Color.green()
            status_emoji = "🟢"
        elif station.get('status') == '已撤銷':
            color = discord.Color.red()
            status_emoji = "🔴"
        else:
            color = discord.Color.yellow()
            status_emoji = "🟡"
        
        embed = discord.Embed(
            title=f"{status_emoji} {station.get('name', '未知測站')} ({station.get('id', 'N/A')})",
            color=color
        )
        
        # 基本資訊
        embed.add_field(
            name="📍 基本資訊",
            value=(
                f"**測站名稱：** {station.get('name', 'N/A')}\n"
                f"**英文名稱：** {station.get('name_en', 'N/A')}\n"
                f"**測站編號：** {station.get('id', 'N/A')}\n"
                f"**狀態：** {status_emoji} {station.get('status', 'N/A')}"
            ),
            inline=False
        )
        
        # 地理位置
        embed.add_field(
            name="🗺️ 地理位置",
            value=(
                f"**縣市：** {station.get('county', 'N/A')}\n"
                f"**詳細位置：** {station.get('location', 'N/A')}\n"
                f"**海拔高度：** {station.get('altitude', 0)} 公尺\n"
                f"**經度：** {station.get('longitude', 0)}\n"
                f"**緯度：** {station.get('latitude', 0)}"
            ),
            inline=False
        )
        
        # 運作時間
        start_date = station.get('start_date', '')
        end_date = station.get('end_date', '')
        if not end_date:
            end_date = "至今"
        
        embed.add_field(
            name="⏰ 運作時間",
            value=(
                f"**啟用日期：** {start_date if start_date else 'N/A'}\n"
                f"**結束日期：** {end_date}"
            ),
            inline=True
        )
        
        # 其他資訊
        if station.get('original_id') or station.get('new_id'):
            embed.add_field(
                name="🔄 測站變更",
                value=(
                    f"**原測站編號：** {station.get('original_id', 'N/A')}\n"
                    f"**新測站編號：** {station.get('new_id', 'N/A')}"
                ),
                inline=True
            )
        
        # 備註
        if station.get('notes'):
            notes = station.get('notes', '')
            if len(notes) > 200:
                notes = notes[:200] + "..."
            embed.add_field(
                name="📝 備註",
                value=notes,
                inline=False
            )
        
        # 地圖連結
        if station.get('latitude') and station.get('longitude'):
            lat = station.get('latitude')
            lng = station.get('longitude')
            google_maps_url = f"https://www.google.com/maps?q={lat},{lng}"
            embed.add_field(
                name="🗺️ 地圖位置",
                value=f"[在 Google 地圖上查看]({google_maps_url})",
                inline=False
            )
        
        embed.set_footer(text="資料來源：中央氣象署開放資料平臺")
        return embed
    
    def create_list_embed(self, stations: List[Dict], query: str, page: int = 1, per_page: int = 10) -> Tuple[discord.Embed, int]:
        """創建測站列表的 Embed"""
        total_stations = len(stations)
        total_pages = (total_stations + per_page - 1) // per_page
        
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_stations)
        page_stations = stations[start_idx:end_idx]
        
        embed = discord.Embed(
            title=f"🏞️ 無人氣象測站查詢結果",
            description=f"搜尋關鍵字：`{query}`\n找到 {total_stations} 個測站",
            color=discord.Color.blue()
        )
        
        if not page_stations:
            embed.add_field(
                name="🔍 查詢結果",
                value="未找到符合條件的測站",
                inline=False
            )
            return embed, total_pages
        
        # 顯示測站列表
        station_list = []
        for i, station in enumerate(page_stations, start=start_idx + 1):
            status_emoji = "🟢" if station.get('status') == '現存測站' else "🔴" if station.get('status') == '已撤銷' else "🟡"
            station_list.append(
                f"{i}. {status_emoji} **{station.get('name', 'N/A')}** ({station.get('id', 'N/A')})\n"
                f"   📍 {station.get('county', 'N/A')} - {station.get('location', 'N/A')[:50]}{'...' if len(station.get('location', '')) > 50 else ''}"
            )
        
        embed.add_field(
            name=f"📋 測站列表 (第 {page}/{total_pages} 頁)",
            value="\n\n".join(station_list),
            inline=False
        )
        
        if total_pages > 1:
            embed.add_field(
                name="📄 翻頁提示",
                value=f"使用 `/weather_station 查詢字串 頁數:{page+1}` 查看下一頁",
                inline=False
            )
        
        # 添加查看詳細資訊的提示
        if total_stations == 1:
            embed.add_field(
                name="💡 查看詳細資訊",
                value=f"使用 `/weather_station {query} detailed:True` 查看詳細資訊",
                inline=False
            )
        elif total_stations > 1:
            embed.add_field(
                name="💡 查看詳細資訊",
                value="使用 `/weather_station_info 測站編號` 查看特定測站的詳細資訊",
                inline=False
            )
        
        embed.set_footer(text=f"第 {page}/{total_pages} 頁 | 資料來源：中央氣象署開放資料平臺")
        return embed, total_pages
    
    async def fetch_weather_observation_data(self) -> Dict:
        """從 CWA API 獲取實際天氣觀測資料"""
        try:
            # 構建 API URL
            endpoint = "O-A0001-001"  # 自動氣象測站資料
            url = f"{self.cwa_api_base}/{endpoint}"
            
            params = {
                "Authorization": self.authorization,
                "format": "JSON"
            }
            
            logger.info(f"正在從 CWA API 獲取天氣觀測資料: {url}")
            
            # 設定 SSL 上下文
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success') == 'true':
                            return data
                        else:
                            logger.error(f"API 回應失敗: {data}")
                            return {}
                    else:
                        logger.error(f"API 請求失敗，狀態碼: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"獲取天氣觀測資料時發生錯誤: {str(e)}")
            return {}

    def search_weather_stations(self, stations: List[Dict], query: str) -> List[Dict]:
        """搜尋天氣測站"""
        if not query:
            return stations[:10]  # 如果沒有查詢條件，返回前10個
        
        query_lower = query.lower()
        matches = []
        
        for station in stations:
            # 搜尋測站名稱
            station_name = station.get('StationName', '').lower()
            if query_lower in station_name:
                matches.append(station)
        
        return matches

    def format_weather_data_embed(self, stations: List[Dict], query: str = "") -> discord.Embed:
        """格式化天氣資料為 Discord Embed"""
        if not stations:
            embed = discord.Embed(
                title="❌ 未找到天氣資料",
                description=f"無法找到符合 '{query}' 的天氣測站資料。",
                color=discord.Color.red()
            )
            embed.add_field(
                name="💡 建議",
                value="請嘗試使用不同的關鍵字，如：板橋、淡水、桃園、新竹等。",
                inline=False
            )
            return embed
        
        # 限制顯示數量
        display_stations = stations[:5]
        
        if query:
            title = f"🌤️ '{query}' 的天氣資訊"
        else:
            title = "🌤️ 天氣觀測資料"
        
        embed = discord.Embed(
            title=title,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for i, station in enumerate(display_stations, 1):
            station_name = station.get('StationName', 'N/A')
            station_id = station.get('StationId', 'N/A')
            obs_time = station.get('ObsTime', {}).get('DateTime', 'N/A')
            
            # 解析天氣要素
            weather_elements = station.get('WeatherElement', {})
            
            # 獲取主要天氣資訊
            temp = weather_elements.get('AirTemperature', 'N/A')
            humidity = weather_elements.get('RelativeHumidity', 'N/A')
            pressure = weather_elements.get('AirPressure', 'N/A')
            wind_speed = weather_elements.get('WindSpeed', 'N/A')
            wind_dir = weather_elements.get('WindDirection', 'N/A')
            
            # 降雨量資訊
            rainfall_now = 'N/A'
            rainfall_info = weather_elements.get('Now', {})
            if rainfall_info and 'Precipitation' in rainfall_info:
                rainfall_now = rainfall_info.get('Precipitation', 'N/A')
            
            # 建立天氣資訊文字
            weather_info = []
            
            if temp != 'N/A':
                weather_info.append(f"🌡️ **氣溫:** {temp}°C")
            if humidity != 'N/A':
                weather_info.append(f"💧 **濕度:** {humidity}%")
            if pressure != 'N/A':
                weather_info.append(f"📊 **氣壓:** {pressure} hPa")
            if wind_speed != 'N/A':
                weather_info.append(f"💨 **風速:** {wind_speed} m/s")
            if wind_dir != 'N/A':
                weather_info.append(f"🧭 **風向:** {wind_dir}°")
            if rainfall_now != 'N/A':
                weather_info.append(f"🌧️ **降雨量:** {rainfall_now} mm")
            
            # 觀測時間
            if obs_time != 'N/A':
                try:
                    # 格式化時間顯示
                    dt = datetime.fromisoformat(obs_time.replace('+08:00', ''))
                    formatted_time = dt.strftime('%m/%d %H:%M')
                    weather_info.append(f"⏰ **觀測時間:** {formatted_time}")
                except:
                    weather_info.append(f"⏰ **觀測時間:** {obs_time}")
            
            field_value = '\n'.join(weather_info) if weather_info else "無天氣資料"
            
            embed.add_field(
                name=f"{i}. {station_name} ({station_id})",
                value=field_value,
                inline=True
            )
        
        # 如果有更多結果，顯示提示
        if len(stations) > 5:
            embed.add_field(
                name="📝 注意",
                value=f"找到 {len(stations)} 個測站，僅顯示前 5 個結果。",
                inline=False
            )
        
        embed.set_footer(text="資料來源：中央氣象署")
        
        return embed

    @app_commands.command(name="weather_stations", description="查詢中央氣象署無人氣象測站基本資料")
    @app_commands.describe(
        query="搜尋關鍵字（測站名稱、編號、縣市或位置）",
        page="頁數（預設為第1頁）",
        detailed="是否顯示詳細資訊（預設為簡化列表）"
    )
    async def weather_station(self, interaction: discord.Interaction, query: str, page: int = 1, detailed: bool = False):
        """查詢無人氣象測站資料"""
        await interaction.response.defer()
        
        try:
            # 獲取測站資料
            data = await self.fetch_station_data()
            if not data:
                embed = discord.Embed(
                    title="❌ 資料獲取失敗",
                    description="無法從中央氣象署獲取測站資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 解析測站資料
            stations = self.parse_station_data(data)
            if not stations:
                embed = discord.Embed(
                    title="❌ 資料解析失敗",
                    description="無法解析測站資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 搜尋測站
            matching_stations = self.search_stations(stations, query)
            
            if not matching_stations:
                embed = discord.Embed(
                    title="🔍 未找到結果",
                    description=f"未找到包含 `{query}` 的測站。\n請嘗試使用測站名稱、編號、縣市名稱或位置關鍵字搜尋。",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="💡 搜尋提示",
                    value=(
                        "• 使用測站名稱：`台北`、`板橋`\n"
                        "• 使用測站編號：`C0A940`\n"
                        "• 使用縣市名稱：`新北市`、`台北市`\n"
                        "• 使用位置關鍵字：`學校`、`公園`"
                    ),
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 根據用戶選擇決定顯示格式
            if detailed and len(matching_stations) == 1:
                # 用戶明確要求詳細資訊且只有一個結果
                embed = self.create_station_embed(matching_stations[0])
                await interaction.followup.send(embed=embed)
                return
            
            # 預設顯示簡化列表格式，即使只有一個結果
            # 確保用戶看到的是簡化列表而非詳細資料
            if page < 1:
                page = 1
            
            embed, total_pages = self.create_list_embed(matching_stations, query, page)
            
            if page > total_pages:
                embed = discord.Embed(
                    title="❌ 頁數超出範圍",
                    description=f"查詢結果共有 {total_pages} 頁，請輸入 1-{total_pages} 之間的頁數。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"查詢測站資料時發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 系統錯誤",
                description=f"查詢過程中發生錯誤：{str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="county_weather_stations", description="按縣市查詢無人氣象測站")
    @app_commands.describe(
        county="縣市名稱（如：台北市、新北市）",
        status="測站狀態篩選",
        page="頁數（預設為第1頁）"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="全部", value="all"),
        app_commands.Choice(name="現存測站", value="現存測站"),
        app_commands.Choice(name="已撤銷", value="已撤銷")
    ])
    async def weather_station_by_county(self, interaction: discord.Interaction, county: str, status: str = "all", page: int = 1):
        """按縣市查詢無人氣象測站"""
        await interaction.response.defer()
        
        try:
            # 獲取測站資料
            data = await self.fetch_station_data()
            if not data:
                embed = discord.Embed(
                    title="❌ 資料獲取失敗",
                    description="無法從中央氣象署獲取測站資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 解析測站資料
            stations = self.parse_station_data(data)
            if not stations:
                embed = discord.Embed(
                    title="❌ 資料解析失敗",
                    description="無法解析測站資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 篩選縣市
            county_stations = [s for s in stations if county.lower() in s.get('county', '').lower()]
            
            # 篩選狀態
            if status != "all":
                county_stations = [s for s in county_stations if s.get('status') == status]
            
            if not county_stations:
                embed = discord.Embed(
                    title="🔍 未找到結果",
                    description=f"在 `{county}` 未找到符合條件的測站。",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 按測站名稱排序
            county_stations.sort(key=lambda x: x.get('name', ''))
            
            # 創建列表 embed
            query_text = f"{county}"
            if status != "all":
                query_text += f" ({status})"
            
            embed, total_pages = self.create_list_embed(county_stations, query_text, page)
            
            if page > total_pages:
                embed = discord.Embed(
                    title="❌ 頁數超出範圍",
                    description=f"查詢結果共有 {total_pages} 頁，請輸入 1-{total_pages} 之間的頁數。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"按縣市查詢測站資料時發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 系統錯誤",
                description=f"查詢過程中發生錯誤：{str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="station_details", description="查詢特定測站的詳細資訊")
    @app_commands.describe(station_id="測站編號（如：C0A940）")
    async def weather_station_info(self, interaction: discord.Interaction, station_id: str):
        """查詢特定測站的詳細資訊"""
        await interaction.response.defer()
        
        try:
            # 獲取測站資料
            data = await self.fetch_station_data()
            if not data:
                embed = discord.Embed(
                    title="❌ 資料獲取失敗",
                    description="無法從中央氣象署獲取測站資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 解析測站資料
            stations = self.parse_station_data(data)
            if not stations:
                embed = discord.Embed(
                    title="❌ 資料解析失敗",
                    description="無法解析測站資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 搜尋指定測站
            station = None
            for s in stations:
                if s.get('id', '').upper() == station_id.upper():
                    station = s
                    break
            
            if not station:
                embed = discord.Embed(
                    title="🔍 未找到測站",
                    description=f"未找到測站編號 `{station_id}` 的資料。\n請確認測站編號是否正確。",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="💡 提示",
                    value="可以使用 `/weather_station` 指令搜尋測站名稱或位置來找到正確的測站編號。",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 顯示詳細資訊
            embed = self.create_station_embed(station)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"查詢測站詳細資訊時發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 系統錯誤",
                description=f"查詢過程中發生錯誤：{str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="weather", description="查詢台灣天氣觀測資訊")
    @app_commands.describe(location="要查詢的地點名稱（如：板橋、淡水、桃園）")
    async def weather(self, interaction: discord.Interaction, location: str = ""):
        """查詢天氣觀測資訊"""
        await interaction.response.defer()
        
        try:
            logger.info(f"用戶 {interaction.user} 查詢天氣: {location}")
            
            # 獲取天氣觀測資料
            data = await self.fetch_weather_observation_data()
            
            if not data:
                embed = discord.Embed(
                    title="❌ 無法獲取天氣資料",
                    description="目前無法連接到氣象署 API，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 解析測站資料
            stations = data.get('records', {}).get('Station', [])
            
            if not stations:
                embed = discord.Embed(
                    title="❌ 無天氣資料",
                    description="目前沒有可用的天氣觀測資料。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 搜尋符合條件的測站
            if location:
                matching_stations = self.search_weather_stations(stations, location)
            else:
                # 如果沒有指定地點，顯示一些熱門測站
                popular_locations = ["板橋", "淡水", "桃園", "新竹", "台中"]
                matching_stations = []
                for loc in popular_locations:
                    matches = self.search_weather_stations(stations, loc)
                    if matches:
                        matching_stations.extend(matches[:1])  # 每個地點取1個
                
                if not matching_stations:
                    matching_stations = stations[:5]  # 如果都沒有，取前5個
            
            # 格式化並發送結果
            embed = self.format_weather_data_embed(matching_stations, location)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"天氣查詢指令執行錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 指令執行錯誤",
                description="執行天氣查詢時發生錯誤，請稍後再試。",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """載入 Cog"""
    await bot.add_cog(WeatherCommands(bot))
    logger.info('WeatherCommands cog 已載入')
