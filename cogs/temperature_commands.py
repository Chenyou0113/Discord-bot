#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
溫度分布查詢指令
提供查詢中央氣象署溫度分布的功能
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import json
import asyncio
import logging
import ssl
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class TemperatureCommands(commands.Cog):
    """溫度分布查詢相關指令"""
    
    def __init__(self, bot):
        self.bot = bot
        # 溫度分布 API
        self.temperature_api = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0038-001"
        self.authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
        
        # 快取設定
        self.temperature_cache = {}
        self.cache_timestamp = 0
        self.cache_duration = 1800  # 快取 30 分鐘
        
        # SSL 設定
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def fetch_temperature_data(self) -> Dict:
        """從中央氣象署 API 獲取溫度分布資料"""
        try:
            # 檢查快取
            current_time = asyncio.get_event_loop().time()
            if (self.temperature_cache and 
                current_time - self.cache_timestamp < self.cache_duration):
                return self.temperature_cache
            
            # 構建 API 參數
            params = {
                "Authorization": self.authorization,
                "downloadType": "WEB",
                "format": "JSON"
            }
            
            logger.info(f"正在從中央氣象署 API 獲取溫度分布資料: {self.temperature_api}")
            
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(self.temperature_api, params=params) as response:
                    if response.status == 200:
                        # 處理 MIME 類型問題，使用雙重解析機制
                        try:
                            response_text = await response.text()
                            data = json.loads(response_text)
                        except json.JSONDecodeError:
                            # 如果 JSON 解析失敗，嘗試直接使用 response.json()
                            data = await response.json(content_type=None)
                        
                        # 更新快取
                        self.temperature_cache = data
                        self.cache_timestamp = current_time
                        
                        logger.info("成功獲取溫度分布資料")
                        return data
                    else:
                        logger.error(f"溫度分布 API 請求失敗: HTTP {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"獲取溫度分布資料時發生錯誤: {e}")
            return {}
    
    def parse_temperature_data(self, data: Dict) -> Dict:
        """解析溫度分布資料"""
        try:
            if 'cwaopendata' not in data:
                return {}
            
            cwa_data = data['cwaopendata']
            dataset = cwa_data.get('dataset', {})
            
            # 解析基本資訊
            temp_info = {
                'identifier': cwa_data.get('identifier', ''),
                'sent': cwa_data.get('sent', ''),
                'datetime': dataset.get('DateTime', ''),
                'description': '',
                'image_url': '',
                'locations': [],
                'stats': {
                    'total_stations': 0,
                    'max_temp': None,
                    'min_temp': None,
                    'avg_temp': None,
                    'max_station': '',
                    'min_station': ''
                }
            }
            
            # 解析資料集資訊
            dataset_info = dataset.get('datasetInfo', {})
            if dataset_info:
                temp_info['description'] = dataset_info.get('datasetDescription', '溫度分布')
                
                # 查找圖片 URL
                parameter_set = dataset_info.get('parameterSet', {})
                if parameter_set:
                    parameters = parameter_set.get('parameter', [])
                    if isinstance(parameters, list):
                        for param in parameters:
                            param_value = param.get('parameterValue', '')
                            if isinstance(param_value, str) and ('http' in param_value or 'www' in param_value):
                                temp_info['image_url'] = param_value
                                break
                    elif isinstance(parameters, dict):
                        param_value = parameters.get('parameterValue', '')
                        if isinstance(param_value, str) and ('http' in param_value or 'www' in param_value):
                            temp_info['image_url'] = param_value
            
            # 如果在 datasetInfo 中沒找到圖片，嘗試在 Resource 中查找
            if not temp_info['image_url']:
                resource = dataset.get('Resource', {})
                if resource:
                    product_url = resource.get('ProductURL', '')
                    if product_url and isinstance(product_url, str) and ('http' in product_url):
                        temp_info['image_url'] = product_url
                        logger.info(f"找到溫度分布圖片URL: {product_url}")
            
            # 如果還是沒找到，嘗試構建標準的溫度分布圖URL
            if not temp_info['image_url']:
                # 使用中央氣象署標準的溫度分布圖URL
                temp_info['image_url'] = "https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0038-001.jpg"
                logger.info("使用標準溫度分布圖片URL")
            
            # 解析位置資料
            locations = dataset.get('location', [])
            if not isinstance(locations, list):
                locations = [locations]
            
            temperatures = []
            
            for location in locations:
                location_name = location.get('locationName', '')
                lon = location.get('lon', '')
                lat = location.get('lat', '')
                
                # 解析觀測資料
                station_obs_times = location.get('stationObsTimes', {})
                obs_time_list = station_obs_times.get('stationObsTime', [])
                
                if not isinstance(obs_time_list, list):
                    obs_time_list = [obs_time_list]
                
                for obs_time in obs_time_list:
                    obs_datetime = obs_time.get('DateTime', '')
                    
                    weather_elements = obs_time.get('weatherElements', {})
                    elements = weather_elements.get('weatherElement', [])
                    
                    if not isinstance(elements, list):
                        elements = [elements]
                    
                    # 提取溫度資料
                    temperature_data = {}
                    for element in elements:
                        element_name = element.get('elementName', '')
                        element_value = element.get('elementValue', '')
                        
                        if element_name and element_value:
                            temperature_data[element_name] = element_value
                    
                    if temperature_data:
                        location_info = {
                            'name': location_name,
                            'longitude': lon,
                            'latitude': lat,
                            'datetime': obs_datetime,
                            'temperature_data': temperature_data
                        }
                        temp_info['locations'].append(location_info)
                        
                        # 統計溫度資料（假設有氣溫欄位）
                        for key, value in temperature_data.items():
                            if '溫' in key or 'temp' in key.lower():
                                try:
                                    temp_value = float(value)
                                    temperatures.append((temp_value, location_name))
                                except (ValueError, TypeError):
                                    pass
            
            # 計算統計資料
            if temperatures:
                temp_values = [t[0] for t in temperatures]
                temp_info['stats']['total_stations'] = len(temperatures)
                temp_info['stats']['max_temp'] = max(temp_values)
                temp_info['stats']['min_temp'] = min(temp_values)
                temp_info['stats']['avg_temp'] = round(sum(temp_values) / len(temp_values), 1)
                
                # 找出最高和最低溫的測站
                max_temp_station = [t[1] for t in temperatures if t[0] == temp_info['stats']['max_temp']]
                min_temp_station = [t[1] for t in temperatures if t[0] == temp_info['stats']['min_temp']]
                
                temp_info['stats']['max_station'] = max_temp_station[0] if max_temp_station else ''
                temp_info['stats']['min_station'] = min_temp_station[0] if min_temp_station else ''
            
            return temp_info
            
        except Exception as e:
            logger.error(f"解析溫度分布資料時發生錯誤: {e}")
            return {}
    
    def create_temperature_embed(self, temp_info: Dict) -> discord.Embed:
        """創建溫度分布 Embed"""
        try:
            # 基本資訊
            title = "🌡️ 台灣溫度分布"
            description = temp_info.get('description', '溫度分布資料')
            
            # 建立 Embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=0xFF6B6B,  # 暖色調
                timestamp=datetime.now()
            )
            
            # 統計資訊
            stats = temp_info.get('stats', {})
            if stats.get('total_stations', 0) > 0:
                stats_text = f"""
📊 **統計資訊**
• 測站總數：{stats.get('total_stations', 'N/A')} 個
• 最高溫：{stats.get('max_temp', 'N/A')}°C ({stats.get('max_station', 'N/A')})
• 最低溫：{stats.get('min_temp', 'N/A')}°C ({stats.get('min_station', 'N/A')})
• 平均溫：{stats.get('avg_temp', 'N/A')}°C
"""
                embed.add_field(name="📈 溫度統計", value=stats_text, inline=False)
            
            # 部分測站資料
            locations = temp_info.get('locations', [])
            if locations:
                location_text = ""
                for i, location in enumerate(locations[:10]):  # 只顯示前10個
                    name = location.get('name', 'N/A')
                    temp_data = location.get('temperature_data', {})
                    
                    # 找出溫度值
                    temp_value = 'N/A'
                    for key, value in temp_data.items():
                        if '溫' in key or 'temp' in key.lower():
                            temp_value = f"{value}°C"
                            break
                    
                    location_text += f"🌡️ {name}：{temp_value}\n"
                
                if len(locations) > 10:
                    location_text += f"\n... 還有 {len(locations) - 10} 個測站"
                
                embed.add_field(name="📍 測站溫度", value=location_text, inline=False)
            
            # 時間資訊
            sent_time = temp_info.get('sent', '')
            if sent_time:
                try:
                    dt = datetime.fromisoformat(sent_time.replace('Z', '+00:00'))
                    time_text = dt.strftime('%Y-%m-%d %H:%M:%S')
                    embed.add_field(name="⏰ 資料時間", value=time_text, inline=True)
                except:
                    embed.add_field(name="⏰ 資料時間", value=sent_time, inline=True)
            
            # 圖片顯示
            image_url = temp_info.get('image_url', '')
            if image_url:
                try:
                    # 設定圖片
                    embed.set_image(url=image_url)
                    embed.add_field(
                        name="🖼️ 溫度分布圖", 
                        value=f"[點擊查看完整圖片]({image_url})", 
                        inline=True
                    )
                    logger.info(f"已設定溫度分布圖片: {image_url}")
                except Exception as e:
                    logger.warning(f"設定圖片時發生錯誤: {e}")
                    # 如果設定圖片失敗，至少提供連結
                    embed.add_field(
                        name="🖼️ 溫度分布圖", 
                        value=f"[查看圖片]({image_url})", 
                        inline=True
                    )
            else:
                # 如果沒有圖片URL，提供說明
                embed.add_field(
                    name="🖼️ 溫度分布圖", 
                    value="暫無圖片資料", 
                    inline=True
                )
            
            # footer
            embed.set_footer(text="資料來源：中央氣象署")
            
            return embed
            
        except Exception as e:
            logger.error(f"創建溫度分布 Embed 時發生錯誤: {e}")
            # 回傳錯誤 embed
            error_embed = discord.Embed(
                title="❌ 錯誤",
                description="建立溫度分布資訊時發生錯誤",
                color=0xFF0000
            )
            return error_embed
    
    @app_commands.command(name="temperature", description="查詢台灣溫度分布狀態")
    async def temperature_distribution(self, interaction: discord.Interaction):
        """查詢台灣溫度分布狀態"""
        await interaction.response.defer()
        
        try:
            # 獲取溫度分布資料
            data = await self.fetch_temperature_data()
            
            if not data:
                await interaction.followup.send("❌ 無法獲取溫度分布資料，請稍後再試。")
                return
            
            # 解析資料
            temp_info = self.parse_temperature_data(data)
            
            if not temp_info:
                await interaction.followup.send("❌ 溫度分布資料解析失敗，請稍後再試。")
                return
            
            # 建立 Embed
            embed = self.create_temperature_embed(temp_info)
            
            # 建立重新整理按鈕
            view = TemperatureView(self)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"查詢溫度分布時發生錯誤: {e}")
            await interaction.followup.send("❌ 查詢過程中發生錯誤，請稍後再試。")

class TemperatureView(discord.ui.View):
    """溫度分布互動視圖"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)  # 5分鐘超時
        self.cog = cog
    
    @discord.ui.button(label="🔄 重新整理", style=discord.ButtonStyle.primary)
    async def refresh_temperature(self, interaction: discord.Interaction, button: discord.ui.Button):
        """重新整理溫度分布資料"""
        await interaction.response.defer()
        
        try:
            # 清除快取，強制重新獲取
            self.cog.temperature_cache = {}
            
            # 獲取最新資料
            data = await self.cog.fetch_temperature_data()
            
            if not data:
                await interaction.followup.send("❌ 無法獲取最新溫度分布資料。", ephemeral=True)
                return
            
            # 解析資料
            temp_info = self.cog.parse_temperature_data(data)
            
            if not temp_info:
                await interaction.followup.send("❌ 溫度分布資料解析失敗。", ephemeral=True)
                return
            
            # 建立新的 Embed
            embed = self.cog.create_temperature_embed(temp_info)
            
            # 更新訊息
            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            logger.error(f"重新整理溫度分布時發生錯誤: {e}")
            await interaction.followup.send("❌ 重新整理時發生錯誤。", ephemeral=True)
    
    async def on_timeout(self):
        """當視圖超時時禁用所有按鈕"""
        for item in self.children:
            item.disabled = True

async def setup(bot):
    await bot.add_cog(TemperatureCommands(bot))
