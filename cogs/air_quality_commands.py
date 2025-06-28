#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空氣品質查詢指令
提供查詢環保署空氣品質監測資料的功能
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import json
import asyncio
import logging
import ssl
from typing import Optional, List, Dict, Tuple
import urllib.parse
from datetime import datetime

logger = logging.getLogger(__name__)

class AirQualityCommands(commands.Cog):
    """空氣品質查詢相關指令"""
    
    def __init__(self, bot):
        self.bot = bot
        # 主要 API 端點
        self.epa_api_base = "https://data.epa.gov.tw/api/v2/aqx_p_432"
        # 備援 API 端點
        self.backup_apis = [
            "https://data.moenv.gov.tw/api/v2/aqx_p_432",  # 環境部新域名
            "https://opendata.epa.gov.tw/api/v2/aqx_p_432",  # 開放資料平台
        ]
        self.api_key = "94650864-6a80-4c58-83ce-fd13e7ef0504"
        self.air_quality_cache = {}  # 快取空氣品質資料
        self.cache_timestamp = 0
        self.cache_duration = 1800  # 快取 30 分鐘
        
        # 設定 SSL 上下文 - 更寬鬆的設定
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        # 加入更多 SSL 選項
        self.ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        
        # DNS 設定
        self.dns_servers = ['8.8.8.8', '1.1.1.1', '168.95.1.1']
        
        # 台灣縣市列表
        self.taiwan_counties = [
            "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
            "基隆市", "新竹市", "嘉義市",
            "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣",
            "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"
        ]
        
        # AQI 等級定義
        self.aqi_levels = [
            {"min": 0, "max": 50, "level": "良好", "color": 0x00FF00, "emoji": "🟢", "description": "空氣品質為良好，對一般大眾的健康沒有影響"},
            {"min": 51, "max": 100, "level": "普通", "color": 0xFFFF00, "emoji": "🟡", "description": "空氣品質為普通，對敏感族群可能造成輕微影響"},
            {"min": 101, "max": 150, "level": "對敏感族群不健康", "color": 0xFF7F00, "emoji": "🟠", "description": "敏感族群可能出現健康影響，一般大眾較不受影響"},
            {"min": 151, "max": 200, "level": "對所有族群不健康", "color": 0xFF0000, "emoji": "🔴", "description": "所有人都可能開始出現健康影響"},
            {"min": 201, "max": 300, "level": "非常不健康", "color": 0x800080, "emoji": "🟣", "description": "所有人都可能出現嚴重健康影響"},
            {"min": 301, "max": 999, "level": "危害", "color": 0x800000, "emoji": "🟤", "description": "所有人都會受到嚴重健康影響"}
        ]
        
    async def fetch_air_quality_data(self) -> Dict:
        """從環保署 API 獲取空氣品質資料，支援多端點備援"""
        try:
            # 檢查快取
            current_time = asyncio.get_event_loop().time()
            if (self.air_quality_cache and 
                current_time - self.cache_timestamp < self.cache_duration):
                return self.air_quality_cache
            
            # 構建 API 參數
            params = {
                "api_key": self.api_key,
                "limit": 1000,
                "sort": "ImportDate desc",
                "format": "JSON"
            }
            
            # 嘗試的 API 端點列表
            api_endpoints = [self.epa_api_base] + self.backup_apis
            
            for i, api_url in enumerate(api_endpoints):
                try:
                    logger.info(f"正在嘗試第 {i+1} 個 API 端點: {api_url}")
                    
                    # 設定連接器 - 每次嘗試都使用新的設定
                    connector = aiohttp.TCPConnector(
                        ssl=self.ssl_context,
                        limit=10,
                        force_close=True,
                        enable_cleanup_closed=True,
                        use_dns_cache=False,  # 禁用 DNS 快取
                        family=0,  # 允許 IPv4 和 IPv6
                        local_addr=None
                    )
                    
                    timeout = aiohttp.ClientTimeout(
                        total=30,
                        connect=10,
                        sock_read=10
                    )
                    
                    async with aiohttp.ClientSession(
                        connector=connector, 
                        timeout=timeout,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    ) as session:
                        async with session.get(api_url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # 更新快取
                                self.air_quality_cache = data
                                self.cache_timestamp = current_time
                                
                                logger.info(f"✓ 成功從第 {i+1} 個端點獲取空氣品質資料，共 {len(data.get('records', []))} 筆記錄")
                                return data
                            else:
                                logger.warning(f"✗ 第 {i+1} 個端點回應異常: HTTP {response.status}")
                                
                except asyncio.TimeoutError:
                    logger.warning(f"✗ 第 {i+1} 個端點請求超時")
                except aiohttp.ClientConnectorError as e:
                    logger.warning(f"✗ 第 {i+1} 個端點連線錯誤: {e}")
                except Exception as e:
                    logger.warning(f"✗ 第 {i+1} 個端點發生錯誤: {e}")
                
                # 等待一下再嘗試下一個端點
                if i < len(api_endpoints) - 1:
                    await asyncio.sleep(1)
            
            # 所有端點都失敗
            logger.error("✗ 所有空氣品質 API 端點都無法連線")
            return {}
                        
        except Exception as e:
            logger.error(f"獲取空氣品質資料時發生嚴重錯誤: {e}")
            return {}
    
    def get_aqi_info(self, aqi_value: int) -> Dict:
        """根據 AQI 值獲取等級資訊"""
        for level in self.aqi_levels:
            if level["min"] <= aqi_value <= level["max"]:
                return level
        return self.aqi_levels[-1]  # 如果超出範圍，返回最高等級
    
    def search_sites_by_keyword(self, records: List[Dict], keyword: str) -> List[Dict]:
        """根據關鍵字搜尋測站"""
        keyword = keyword.lower()
        results = []
        
        for record in records:
            site_name = record.get('sitename', '').lower()
            county = record.get('county', '').lower()
            
            if keyword in site_name or keyword in county:
                results.append(record)
        
        return results
    
    def search_sites_by_county(self, records: List[Dict], county: str) -> List[Dict]:
        """根據縣市搜尋測站"""
        results = []
        county = county.replace('台', '臺')  # 處理台/臺差異
        
        for record in records:
            record_county = record.get('county', '')
            if county in record_county or record_county in county:
                results.append(record)
        
        return results
    
    def create_site_embed(self, site_data: Dict) -> discord.Embed:
        """建立測站詳細資訊 Embed"""
        site_name = site_data.get('sitename', '未知測站')
        county = site_data.get('county', '未知縣市')
        aqi_str = site_data.get('aqi', '0')
        
        try:
            aqi_value = int(aqi_str) if aqi_str and aqi_str != '' else 0
        except (ValueError, TypeError):
            aqi_value = 0
        
        aqi_info = self.get_aqi_info(aqi_value)
        
        # 建立 Embed
        embed = discord.Embed(
            title=f"{aqi_info['emoji']} {site_name} 空氣品質",
            description=f"📍 {county}",
            color=aqi_info['color']
        )
        
        # AQI 主要資訊
        embed.add_field(
            name="🌡️ AQI 指數",
            value=f"**{aqi_value}** - {aqi_info['level']}",
            inline=True
        )
        
        # 各項污染物資料
        pollutants = [
            ("PM2.5", "pm2.5", "μg/m³"),
            ("PM10", "pm10", "μg/m³"),
            ("O₃", "o3", "ppb"),
            ("CO", "co", "ppm"),
            ("SO₂", "so2", "ppb"),
            ("NO₂", "no2", "ppb")
        ]
        
        pollutant_values = []
        for name, key, unit in pollutants:
            value = site_data.get(key, 'N/A')
            if value and value != '' and value != 'N/A':
                pollutant_values.append(f"{name}: {value} {unit}")
        
        if pollutant_values:
            embed.add_field(
                name="🧪 污染物濃度",
                value="\n".join(pollutant_values[:3]),  # 前三個
                inline=True
            )
            
            if len(pollutant_values) > 3:
                embed.add_field(
                    name="📊 其他污染物",
                    value="\n".join(pollutant_values[3:]),
                    inline=True
                )
        
        # 健康建議
        embed.add_field(
            name="💡 健康建議",
            value=aqi_info['description'],
            inline=False
        )
        
        # 更新時間
        import_date = site_data.get('importdate', site_data.get('ImportDate', ''))
        if import_date:
            embed.add_field(
                name="⏰ 更新時間",
                value=import_date,
                inline=True
            )
        
        # 測站狀態
        status = site_data.get('status', '')
        if status:
            embed.add_field(
                name="📡 測站狀態",
                value=status,
                inline=True
            )
        
        embed.set_footer(text="資料來源：行政院環境保護署")
        
        return embed
    
    def create_list_embed(self, sites: List[Dict], page: int, total_pages: int, query_info: str) -> discord.Embed:
        """建立測站列表 Embed"""
        embed = discord.Embed(
            title="🌬️ 空氣品質查詢結果",
            description=f"📍 {query_info}",
            color=discord.Colour.blue()
        )
        
        # 分頁資訊
        embed.add_field(
            name="📊 查詢結果",
            value=f"找到 {len(sites)} 個測站 | 📄 第 {page}/{total_pages} 頁",
            inline=False
        )
        
        # 測站列表
        site_list = []
        per_page = 10
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_sites = sites[start_idx:end_idx]
        
        for i, site in enumerate(page_sites, start_idx + 1):
            site_name = site.get('sitename', '未知測站')
            county = site.get('county', '未知縣市')
            aqi_str = site.get('aqi', '0')
            
            try:
                aqi_value = int(aqi_str) if aqi_str and aqi_str != '' else 0
            except (ValueError, TypeError):
                aqi_value = 0
            
            aqi_info = self.get_aqi_info(aqi_value)
            
            site_list.append(f"{i}. {aqi_info['emoji']} **{site_name}** ({county}) - AQI: {aqi_value}")
        
        if site_list:
            embed.add_field(
                name="📋 測站列表",
                value="\n".join(site_list),
                inline=False
            )
        
        if total_pages > 1:
            embed.add_field(
                name="💡 翻頁提示",
                value=f"使用 `page:{page + 1}` 查看下一頁",
                inline=False
            )
        
        embed.set_footer(text="點擊下方按鈕查看測站詳細資訊 | 資料來源：環保署")
        
        return embed
    
    def get_sites_page(self, sites: List[Dict], page: int, per_page: int = 10) -> List[Dict]:
        """獲取指定頁面的測站資料"""
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        return sites[start_idx:end_idx]
    
    def calculate_total_pages(self, total_items: int, per_page: int = 10) -> int:
        """計算總頁數"""
        return (total_items + per_page - 1) // per_page
    
    @app_commands.command(name="air_quality", description="查詢空氣品質資訊")
    @app_commands.describe(
        query="搜尋關鍵字（測站名稱、縣市等）",
        page="頁數（預設為第1頁）"
    )
    async def air_quality(self, interaction: discord.Interaction, query: str, page: Optional[int] = 1):
        """查詢空氣品質"""
        await interaction.response.defer()
        
        try:
            # 獲取空氣品質資料
            data = await self.fetch_air_quality_data()
            
            if not data or 'records' not in data:
                await interaction.followup.send("❌ 無法獲取空氣品質資料，請稍後再試。")
                return
            
            records = data['records']
            
            # 搜尋測站
            results = self.search_sites_by_keyword(records, query)
            
            if not results:
                await interaction.followup.send(f"❌ 找不到與「{query}」相關的測站。")
                return
            
            # 檢查頁數
            total_pages = self.calculate_total_pages(len(results))
            if page < 1 or page > total_pages:
                await interaction.followup.send(f"❌ 頁數超出範圍！總共只有 {total_pages} 頁。")
                return
            
            # 建立回應
            embed = self.create_list_embed(results, page, total_pages, f"查詢: {query}")
            
            # 建立按鈕視圖
            view = AirQualityView(self, results, page, total_pages, query)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"查詢空氣品質時發生錯誤: {e}")
            await interaction.followup.send("❌ 查詢過程中發生錯誤，請稍後再試。")
    
    @app_commands.command(name="air_quality_county", description="按縣市查詢空氣品質")
    @app_commands.describe(
        county="選擇縣市",
        page="頁數（預設為第1頁）"
    )
    @app_commands.choices(county=[
        app_commands.Choice(name="臺北市", value="臺北市"),
        app_commands.Choice(name="新北市", value="新北市"),
        app_commands.Choice(name="桃園市", value="桃園市"),
        app_commands.Choice(name="臺中市", value="臺中市"),
        app_commands.Choice(name="臺南市", value="臺南市"),
        app_commands.Choice(name="高雄市", value="高雄市"),
        app_commands.Choice(name="基隆市", value="基隆市"),
        app_commands.Choice(name="新竹市", value="新竹市"),
        app_commands.Choice(name="嘉義市", value="嘉義市"),
        app_commands.Choice(name="新竹縣", value="新竹縣"),
        app_commands.Choice(name="苗栗縣", value="苗栗縣"),
        app_commands.Choice(name="彰化縣", value="彰化縣"),
        app_commands.Choice(name="南投縣", value="南投縣"),
        app_commands.Choice(name="雲林縣", value="雲林縣"),
        app_commands.Choice(name="嘉義縣", value="嘉義縣"),
        app_commands.Choice(name="屏東縣", value="屏東縣"),
        app_commands.Choice(name="宜蘭縣", value="宜蘭縣"),
        app_commands.Choice(name="花蓮縣", value="花蓮縣"),
        app_commands.Choice(name="臺東縣", value="臺東縣"),
        app_commands.Choice(name="澎湖縣", value="澎湖縣"),
        app_commands.Choice(name="金門縣", value="金門縣"),
        app_commands.Choice(name="連江縣", value="連江縣")
    ])
    async def air_quality_county(self, interaction: discord.Interaction, county: str, page: Optional[int] = 1):
        """按縣市查詢空氣品質"""
        await interaction.response.defer()
        
        try:
            # 獲取空氣品質資料
            data = await self.fetch_air_quality_data()
            
            if not data or 'records' not in data:
                await interaction.followup.send("❌ 無法獲取空氣品質資料，請稍後再試。")
                return
            
            records = data['records']
            
            # 搜尋測站
            results = self.search_sites_by_county(records, county)
            
            if not results:
                await interaction.followup.send(f"❌ 找不到「{county}」的空氣品質測站。")
                return
            
            # 檢查頁數
            total_pages = self.calculate_total_pages(len(results))
            if page < 1 or page > total_pages:
                await interaction.followup.send(f"❌ 頁數超出範圍！總共只有 {total_pages} 頁。")
                return
            
            # 建立回應
            embed = self.create_list_embed(results, page, total_pages, f"縣市: {county}")
            
            # 建立按鈕視圖
            view = AirQualityView(self, results, page, total_pages, county)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"查詢縣市空氣品質時發生錯誤: {e}")
            await interaction.followup.send("❌ 查詢過程中發生錯誤，請稍後再試。")
    
    @app_commands.command(name="air_quality_site", description="查詢特定測站的詳細空氣品質資訊")
    @app_commands.describe(
        site_name="測站名稱"
    )
    async def air_quality_site(self, interaction: discord.Interaction, site_name: str):
        """查詢特定測站詳細資訊"""
        await interaction.response.defer()
        
        try:
            # 獲取空氣品質資料
            data = await self.fetch_air_quality_data()
            
            if not data or 'records' not in data:
                await interaction.followup.send("❌ 無法獲取空氣品質資料，請稍後再試。")
                return
            
            records = data['records']
            
            # 尋找指定測站
            found_site = None
            for record in records:
                if site_name.lower() in record.get('sitename', '').lower():
                    found_site = record
                    break
            
            if not found_site:
                await interaction.followup.send(f"❌ 找不到測站「{site_name}」。")
                return
            
            # 建立詳細資訊 Embed
            embed = self.create_site_embed(found_site)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"查詢測站詳細資訊時發生錯誤: {e}")
            await interaction.followup.send("❌ 查詢過程中發生錯誤，請稍後再試。")

class AirQualityView(discord.ui.View):
    """空氣品質查詢結果視圖"""
    
    def __init__(self, cog: AirQualityCommands, sites: List[Dict], page: int, total_pages: int, query: str):
        super().__init__(timeout=300)  # 5分鐘超時
        self.cog = cog
        self.sites = sites
        self.page = page
        self.total_pages = total_pages
        self.query = query
        
        # 添加測站詳細資訊按鈕
        page_sites = self.cog.get_sites_page(sites, page)
        for i, site in enumerate(page_sites[:5]):  # 最多顯示5個按鈕
            site_name = site.get('sitename', f'測站{i+1}')
            button = SiteDetailButton(site, site_name[:20])  # 限制按鈕標籤長度
            self.add_item(button)

class SiteDetailButton(discord.ui.Button):
    """測站詳細資訊按鈕"""
    
    def __init__(self, site_data: Dict, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, emoji="🔍")
        self.site_data = site_data
    
    async def callback(self, interaction: discord.Interaction):
        # 獲取 Cog 實例
        cog = interaction.client.get_cog("AirQualityCommands")
        if cog:
            embed = cog.create_site_embed(self.site_data)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ 系統錯誤，請稍後再試。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AirQualityCommands(bot))
