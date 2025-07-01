#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水庫水情查詢指令 (修復結構版本)
包含水位查詢、監視器查詢等功能
"""

import asyncio
import aiohttp
import discord
import datetime
import json
import ssl
import logging
from discord.ext import commands
from discord import app_commands

# 設定日誌
logger = logging.getLogger(__name__)

class ReservoirCommands(commands.Cog):
    """水庫水情查詢指令"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # 水庫 ID 對應表（部分主要水庫）
        self.reservoir_names = {
            "10501": "石門水庫",
            "10502": "新山水庫", 
            "10804": "翡翠水庫",
            "12101": "鯉魚潭水庫",
            "12102": "德基水庫",
            "12103": "石岡壩",
            "12104": "谷關水庫",
            "12401": "霧社水庫",
            "12402": "日月潭水庫",
            "12901": "湖山水庫",
            "13801": "曾文水庫",
            "13802": "烏山頭水庫",
            "13803": "白河水庫",
            "13804": "尖山埤水庫",
            "13805": "虎頭埤水庫",
            "14101": "阿公店水庫",
            "14102": "澄清湖水庫",
            "14602": "牡丹水庫",
            "14603": "龍鑾潭水庫"
        }
    
    def _extract_county_from_location(self, location_description):
        """從位置描述中提取縣市"""
        county_keywords = {
            '基隆': '基隆市', '台北': '台北市', '新北': '新北市',
            '桃園': '桃園市', '新竹': '新竹市', '苗栗': '苗栗縣',
            '台中': '台中市', '彰化': '彰化縣', '南投': '南投縣',
            '雲林': '雲林縣', '嘉義': '嘉義市', '台南': '台南市',
            '高雄': '高雄市', '屏東': '屏東縣', '宜蘭': '宜蘭縣',
            '花蓮': '花蓮縣', '台東': '台東縣'
        }
        
        for keyword, county in county_keywords.items():
            if keyword in location_description:
                return county
        
        return '未知'

    def _process_camera_url(self, url):
        """處理監視器圖片 URL，確保可以正確顯示"""
        if not url:
            return "N/A"
        
        processed_url = url.strip()
        
        # 如果已經是完整的 HTTP/HTTPS URL，直接加時間戳
        if processed_url.startswith(('http://', 'https://')):
            return self._add_timestamp_to_url(processed_url)
        
        # 如果是以 / 開頭的絕對路徑
        elif processed_url.startswith('/'):
            base_urls = [
                'https://fhy.wra.gov.tw',
                'https://opendata.wra.gov.tw'
            ]
            full_url = base_urls[0] + processed_url
            return self._add_timestamp_to_url(full_url)
        
        # 如果不是以上格式，可能是相對路徑
        else:
            # 檢查是否看起來像檔案名稱或相對路徑
            if '.' in processed_url and any(ext in processed_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                full_url = 'https://alerts.ncdr.nat.gov.tw/' + processed_url
                return self._add_timestamp_to_url(full_url)
            else:
                # 如果不是圖片檔案，返回 N/A
                return "N/A"
    
    def _add_timestamp_to_url(self, url):
        """為URL加上時間戳避免快取"""
        if not url or url == "N/A":
            return url
        
        import time
        timestamp = int(time.time())
        
        # 檢查URL是否已經有參數
        if '?' in url:
            return f"{url}&_t={timestamp}"
        else:
            return f"{url}?_t={timestamp}"

    def _standardize_county_name(self, location_str):
        """標準化縣市名稱"""
        if not location_str:
            return location_str
        
        # 縣市對應表
        county_mapping = {
            '台北': '台北市', '臺北': '台北市',
            '新北': '新北市', '桃園': '桃園市',
            '台中': '台中市', '臺中': '台中市',
            '台南': '台南市', '臺南': '台南市',
            '高雄': '高雄市', '基隆': '基隆市',
            '新竹市': '新竹市', '嘉義市': '嘉義市',
            '新竹縣': '新竹縣', '苗栗': '苗栗縣',
            '彰化': '彰化縣', '南投': '南投縣',
            '雲林': '雲林縣', '嘉義縣': '嘉義縣',
            '屏東': '屏東縣', '宜蘭': '宜蘭縣',
            '花蓮': '花蓮縣', '台東': '台東縣',
            '臺東': '台東縣'
        }
        
        return county_mapping.get(location_str, location_str)

    # === 指令方法 ===
    
    @app_commands.command(name="water_level", description="查詢全台河川水位資料")
    @app_commands.describe(
        city="選擇縣市",
        river="河川名稱",
        station="測站名稱"
    )
    @app_commands.choices(city=[
        app_commands.Choice(name="基隆", value="基隆"),
        app_commands.Choice(name="台北", value="台北"),
        app_commands.Choice(name="新北", value="新北"),
        app_commands.Choice(name="桃園", value="桃園"),
        app_commands.Choice(name="新竹", value="新竹"),
        app_commands.Choice(name="苗栗", value="苗栗"),
        app_commands.Choice(name="台中", value="台中"),
        app_commands.Choice(name="彰化", value="彰化"),
        app_commands.Choice(name="南投", value="南投"),
        app_commands.Choice(name="雲林", value="雲林"),
        app_commands.Choice(name="嘉義", value="嘉義"),
        app_commands.Choice(name="台南", value="台南"),
        app_commands.Choice(name="高雄", value="高雄"),
        app_commands.Choice(name="屏東", value="屏東"),
        app_commands.Choice(name="宜蘭", value="宜蘭"),
        app_commands.Choice(name="花蓮", value="花蓮"),
        app_commands.Choice(name="台東", value="台東"),
        app_commands.Choice(name="澎湖", value="澎湖"),
        app_commands.Choice(name="金門", value="金門"),
        app_commands.Choice(name="連江", value="連江")
    ])
    async def water_level(
        self, 
        interaction: discord.Interaction, 
        city: str = None, 
        river: str = None, 
        station: str = None
    ):
        """查詢河川水位資料"""
        await interaction.response.defer()
        
        try:
            # API 設定
            api_base = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
            endpoint = "E-A0015-001"  # 河川水位即時資料 API
            authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
            
            url = f"{api_base}/{endpoint}"
            params = {
                "Authorization": authorization,
                "format": "JSON"
            }
            
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        await interaction.followup.send(f"❌ API 請求失敗，狀態碼: {response.status}")
                        return
                    
                    data = await response.json()
                    
                    if data.get('success') != 'true':
                        await interaction.followup.send("❌ API 回應格式錯誤")
                        return
                    
                    # 解析資料
                    records = data.get('records', [])
                    if not records:
                        await interaction.followup.send("❌ 無水位資料")
                        return
                    
                    # 篩選資料
                    filtered_records = []
                    
                    for record in records:
                        location_name = record.get('LocationName', '')
                        river_name = record.get('RiverName', '')
                        basin_name = record.get('BasinName', '')
                        
                        # 標準化縣市名稱
                        standardized_location = self._standardize_county_name(location_name)
                        
                        # 篩選條件
                        matches = True
                        
                        if city:
                            city_standard = self._standardize_county_name(city)
                            if city_standard not in standardized_location and city not in location_name:
                                matches = False
                        
                        if river and matches:
                            if river.lower() not in river_name.lower():
                                matches = False
                        
                        if station and matches:
                            if station.lower() not in location_name.lower():
                                matches = False
                        
                        if matches:
                            record['StandardizedLocation'] = standardized_location
                            filtered_records.append(record)
                    
                    if not filtered_records:
                        filter_msg = []
                        if city:
                            filter_msg.append(f"縣市: {city}")
                        if river:
                            filter_msg.append(f"河川: {river}")
                        if station:
                            filter_msg.append(f"測站: {station}")
                        
                        filter_text = "、".join(filter_msg) if filter_msg else "全台"
                        await interaction.followup.send(f"❌ 找不到符合條件的水位資料\n篩選條件: {filter_text}")
                        return
                    
                    # 限制顯示數量
                    display_records = filtered_records[:15]
                    
                    # 建立 embed
                    embed = discord.Embed(
                        title="🌊 河川水位查詢結果",
                        color=0x0099ff,
                        timestamp=datetime.datetime.now()
                    )
                    
                    # 設定篩選資訊
                    filter_info = []
                    if city:
                        filter_info.append(f"縣市: {city}")
                    if river:
                        filter_info.append(f"河川: {river}")
                    if station:
                        filter_info.append(f"測站: {station}")
                    
                    if filter_info:
                        embed.add_field(
                            name="🔍 篩選條件",
                            value=" | ".join(filter_info),
                            inline=False
                        )
                    
                    # 加入水位資料
                    for i, record in enumerate(display_records, 1):
                        location = record.get('LocationName', 'N/A')
                        river_name = record.get('RiverName', 'N/A')
                        water_level = record.get('WaterLevel', 'N/A')
                        obs_time = record.get('ObsTime', 'N/A')
                        standardized_location = record.get('StandardizedLocation', location)
                        
                        # 格式化水位資料
                        if water_level != 'N/A' and water_level is not None:
                            try:
                                water_level_num = float(water_level)
                                water_level_str = f"{water_level_num:.2f} 公尺"
                            except:
                                water_level_str = str(water_level)
                        else:
                            water_level_str = "無資料"
                        
                        # 格式化時間
                        try:
                            if obs_time != 'N/A':
                                dt = datetime.datetime.fromisoformat(obs_time.replace('Z', '+00:00'))
                                # 轉換為台灣時間 (UTC+8)
                                dt_tw = dt + datetime.timedelta(hours=8)
                                time_str = dt_tw.strftime('%m/%d %H:%M')
                            else:
                                time_str = "無資料"
                        except:
                            time_str = str(obs_time)
                        
                        embed.add_field(
                            name=f"{i}. {location}",
                            value=f"🏞️ 河川: {river_name}\n💧 水位: {water_level_str}\n📍 位置: {standardized_location}\n⏰ 時間: {time_str}",
                            inline=True
                        )
                    
                    # 加入統計資訊
                    if len(filtered_records) > len(display_records):
                        embed.add_field(
                            name="📊 資料統計",
                            value=f"總共找到 {len(filtered_records)} 筆資料，顯示前 {len(display_records)} 筆",
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="📊 資料統計",
                            value=f"共 {len(filtered_records)} 筆資料",
                            inline=False
                        )
                    
                    embed.set_footer(text="💡 使用 city/river/station 參數可以縮小搜尋範圍")
                    
                    await interaction.followup.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"查詢河川水位時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢水位資料時發生錯誤: {str(e)}")

    @app_commands.command(name="water_cameras", description="查詢水利防災監控影像")
    @app_commands.describe(county="選擇縣市")
    @app_commands.choices(county=[
        app_commands.Choice(name="基隆市", value="基隆市"),
        app_commands.Choice(name="台北市", value="台北市"),
        app_commands.Choice(name="新北市", value="新北市"),
        app_commands.Choice(name="桃園市", value="桃園市"),
        app_commands.Choice(name="新竹市", value="新竹市"),
        app_commands.Choice(name="新竹縣", value="新竹縣"),
        app_commands.Choice(name="苗栗縣", value="苗栗縣"),
        app_commands.Choice(name="台中市", value="台中市"),
        app_commands.Choice(name="彰化縣", value="彰化縣"),
        app_commands.Choice(name="南投縣", value="南投縣"),
        app_commands.Choice(name="雲林縣", value="雲林縣"),
        app_commands.Choice(name="嘉義市", value="嘉義市"),
        app_commands.Choice(name="嘉義縣", value="嘉義縣"),
        app_commands.Choice(name="台南市", value="台南市"),
        app_commands.Choice(name="高雄市", value="高雄市"),
        app_commands.Choice(name="屏東縣", value="屏東縣"),
        app_commands.Choice(name="宜蘭縣", value="宜蘭縣"),
        app_commands.Choice(name="花蓮縣", value="花蓮縣"),
        app_commands.Choice(name="台東縣", value="台東縣"),
    ])
    async def water_cameras(self, interaction: discord.Interaction, county: str = None):
        """查詢水利防災監控影像"""
        await interaction.response.defer()
        
        try:
            api_url = "https://alerts.ncdr.nat.gov.tw/RssXmlData/Cc_Details.aspx"
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        await interaction.followup.send(f"❌ API 請求失敗，狀態碼: {response.status}")
                        return
                    
                    content = await response.text()
                    
                    # 解析 XML
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(content)
                    
                    cameras = []
                    for item in root.findall('.//item'):
                        title = item.find('title')
                        link = item.find('link')
                        description = item.find('description')
                        
                        if title is not None and link is not None:
                            camera_info = {
                                'title': title.text,
                                'link': link.text,
                                'description': description.text if description is not None else ''
                            }
                            
                            # 從描述中提取位置資訊
                            if description is not None and description.text:
                                desc_text = description.text
                                # 嘗試提取縣市資訊
                                for county_name in ['基隆市', '台北市', '新北市', '桃園市', '新竹市', '新竹縣', 
                                                   '苗栗縣', '台中市', '彰化縣', '南投縣', '雲林縣', '嘉義市',
                                                   '嘉義縣', '台南市', '高雄市', '屏東縣', '宜蘭縣', '花蓮縣', '台東縣']:
                                    if county_name in desc_text or county_name.replace('市', '').replace('縣', '') in desc_text:
                                        camera_info['county'] = county_name
                                        break
                                else:
                                    camera_info['county'] = '未知'
                            else:
                                camera_info['county'] = '未知'
                            
                            cameras.append(camera_info)
                    
                    if not cameras:
                        await interaction.followup.send("❌ 無法取得監視器資料")
                        return
                    
                    # 篩選指定縣市
                    if county:
                        filtered_cameras = [cam for cam in cameras if cam['county'] == county]
                        if not filtered_cameras:
                            await interaction.followup.send(f"❌ 在 {county} 找不到水利防災監視器")
                            return
                    else:
                        filtered_cameras = cameras
                    
                    # 限制顯示數量
                    display_cameras = filtered_cameras[:20]
                    
                    if not display_cameras:
                        await interaction.followup.send("❌ 沒有找到符合條件的監視器")
                        return
                    
                    # 建立 embed
                    embed = discord.Embed(
                        title="🌊 水利防災監控影像",
                        description=f"縣市篩選: {county if county else '全台'}\n共找到 {len(filtered_cameras)} 個監視器，顯示前 {len(display_cameras)} 個",
                        color=0x0099ff,
                        timestamp=datetime.datetime.now()
                    )
                    
                    # 顯示第一個監視器
                    first_camera = display_cameras[0]
                    image_url = self._process_camera_url(first_camera['link'])
                    
                    embed.add_field(
                        name=f"📹 {first_camera['title']}",
                        value=f"📍 位置: {first_camera['county']}\n⏰ 更新時間: {datetime.datetime.now().strftime('%H:%M:%S')}",
                        inline=False
                    )
                    
                    if image_url != "N/A":
                        embed.set_image(url=image_url)
                    
                    if len(display_cameras) > 1:
                        embed.set_footer(text=f"第 1/{len(display_cameras)} 個監視器")
                    
                    await interaction.followup.send(embed=embed)
                        
        except Exception as e:
            logger.error(f"查詢水利防災監控影像時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢監控影像時發生錯誤: {str(e)}")

    @app_commands.command(name="national_highway_cameras", description="查詢國道監視器")
    @app_commands.describe(
        highway="國道編號（例如：1, 3, 5）",
        location="地點關鍵字"
    )
    async def national_highway_cameras(
        self, 
        interaction: discord.Interaction, 
        highway: str = None, 
        location: str = None
    ):
        """查詢國道監視器"""
        await interaction.response.defer()
        
        try:
            # 高速公路 API
            api_url = "https://tisvcloud.freeway.gov.tw/api/v1/highway/camera/snapshot/info/all"
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        await interaction.followup.send(f"❌ API 請求失敗，狀態碼: {response.status}")
                        return
                    
                    data = await response.json()
                    
                    if not isinstance(data, list):
                        await interaction.followup.send("❌ API 回應格式錯誤")
                        return
                    
                    cameras = []
                    for camera_data in data:
                        devices = camera_data.get('Devices', [])
                        for device in devices:
                            camera_info = {
                                'id': device.get('DeviceID', ''),
                                'name': device.get('DeviceName', ''),
                                'highway': camera_data.get('RoadName', ''),
                                'direction': device.get('RoadDirection', ''),
                                'location': device.get('LocationDescription', ''),
                                'image_url': device.get('ImageUrl', ''),
                                'county': self._extract_county_from_location(device.get('LocationDescription', ''))
                            }
                            
                            # 篩選條件
                            if highway and str(highway) not in camera_info['highway']:
                                continue
                            
                            if location and location.lower() not in camera_info['location'].lower() and location.lower() not in camera_info['name'].lower():
                                continue
                            
                            cameras.append(camera_info)
                    
                    if not cameras:
                        filter_msg = []
                        if highway:
                            filter_msg.append(f"國道: {highway}")
                        if location:
                            filter_msg.append(f"地點: {location}")
                        
                        filter_text = "、".join(filter_msg) if filter_msg else "全部"
                        await interaction.followup.send(f"❌ 找不到符合條件的國道監視器\n篩選條件: {filter_text}")
                        return
                    
                    # 限制顯示數量
                    display_cameras = cameras[:20]
                    
                    # 建立 embed
                    embed = discord.Embed(
                        title="🛣️ 國道監視器",
                        color=0x00ff00,
                        timestamp=datetime.datetime.now()
                    )
                    
                    # 設定篩選資訊
                    filter_info = []
                    if highway:
                        filter_info.append(f"國道: {highway}")
                    if location:
                        filter_info.append(f"地點: {location}")
                    
                    if filter_info:
                        embed.add_field(
                            name="🔍 篩選條件",
                            value=" | ".join(filter_info),
                            inline=False
                        )
                    
                    embed.add_field(
                        name="📊 搜尋結果",
                        value=f"共找到 {len(cameras)} 個監視器，顯示前 {len(display_cameras)} 個",
                        inline=False
                    )
                    
                    # 顯示第一個監視器
                    first_camera = display_cameras[0]
                    image_url = self._add_timestamp_to_url(first_camera['image_url'])
                    
                    embed.add_field(
                        name=f"📹 {first_camera['name']}",
                        value=f"🛣️ 路段: {first_camera['highway']}\n📍 位置: {first_camera['location']}\n🧭 方向: {first_camera['direction']}\n🏙️ 縣市: {first_camera['county']}\n⏰ 更新時間: {datetime.datetime.now().strftime('%H:%M:%S')}",
                        inline=False
                    )
                    
                    if image_url and image_url != "N/A":
                        embed.set_image(url=image_url)
                    
                    if len(display_cameras) > 1:
                        embed.set_footer(text=f"第 1/{len(display_cameras)} 個監視器")
                    
                    await interaction.followup.send(embed=embed)
                        
        except Exception as e:
            logger.error(f"查詢國道監視器時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢國道監視器時發生錯誤: {str(e)}")

    @app_commands.command(name="general_road_cameras", description="查詢一般道路監視器")
    @app_commands.describe(
        county="選擇縣市",
        road="道路名稱"
    )
    @app_commands.choices(county=[
        app_commands.Choice(name="基隆市", value="基隆市"),
        app_commands.Choice(name="台北市", value="台北市"),
        app_commands.Choice(name="新北市", value="新北市"),
        app_commands.Choice(name="桃園市", value="桃園市"),
        app_commands.Choice(name="新竹市", value="新竹市"),
        app_commands.Choice(name="新竹縣", value="新竹縣"),
        app_commands.Choice(name="苗栗縣", value="苗栗縣"),
        app_commands.Choice(name="台中市", value="台中市"),
        app_commands.Choice(name="彰化縣", value="彰化縣"),
        app_commands.Choice(name="南投縣", value="南投縣"),
        app_commands.Choice(name="雲林縣", value="雲林縣"),
        app_commands.Choice(name="嘉義市", value="嘉義市"),
        app_commands.Choice(name="嘉義縣", value="嘉義縣"),
        app_commands.Choice(name="台南市", value="台南市"),
        app_commands.Choice(name="高雄市", value="高雄市"),
        app_commands.Choice(name="屏東縣", value="屏東縣"),
        app_commands.Choice(name="宜蘭縣", value="宜蘭縣"),
        app_commands.Choice(name="花蓮縣", value="花蓮縣"),
        app_commands.Choice(name="台東縣", value="台東縣"),
    ])
    async def general_road_cameras(
        self, 
        interaction: discord.Interaction, 
        county: str = None, 
        road: str = None
    ):
        """查詢一般道路監視器"""
        await interaction.response.defer()
        
        try:
            # 省道/縣道監視器 API
            api_urls = [
                "https://tisvcloud.freeway.gov.tw/api/v1/road/camera/snapshot/info/all",  # 省道
            ]
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            all_cameras = []
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # 嘗試多個 API
                for api_url in api_urls:
                    try:
                        async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                if isinstance(data, list):
                                    for item in data:
                                        if 'Devices' in item:
                                            # 省道格式
                                            devices = item.get('Devices', [])
                                            for device in devices:
                                                camera_info = {
                                                    'id': device.get('DeviceID', ''),
                                                    'name': device.get('DeviceName', ''),
                                                    'road': item.get('RoadName', ''),
                                                    'direction': device.get('RoadDirection', ''),
                                                    'location': device.get('LocationDescription', ''),
                                                    'image_url': device.get('ImageUrl', ''),
                                                    'county': self._extract_county_from_location(device.get('LocationDescription', ''))
                                                }
                                                all_cameras.append(camera_info)
                    except Exception as e:
                        logger.warning(f"API {api_url} 請求失敗: {str(e)}")
                        continue
                
                if not all_cameras:
                    await interaction.followup.send("❌ 無法取得一般道路監視器資料")
                    return
                
                # 篩選條件
                filtered_cameras = []
                for camera in all_cameras:
                    matches = True
                    
                    if county and matches:
                        if county not in camera['county'] and county.replace('市', '').replace('縣', '') not in camera['county']:
                            matches = False
                    
                    if road and matches:
                        if road.lower() not in camera['road'].lower() and road.lower() not in camera['location'].lower():
                            matches = False
                    
                    if matches:
                        filtered_cameras.append(camera)
                
                if not filtered_cameras:
                    filter_msg = []
                    if county:
                        filter_msg.append(f"縣市: {county}")
                    if road:
                        filter_msg.append(f"道路: {road}")
                    
                    filter_text = "、".join(filter_msg) if filter_msg else "全部"
                    await interaction.followup.send(f"❌ 找不到符合條件的一般道路監視器\n篩選條件: {filter_text}")
                    return
                
                # 限制顯示數量
                display_cameras = filtered_cameras[:20]
                
                # 建立 embed
                embed = discord.Embed(
                    title="🚗 一般道路監視器",
                    color=0xff9900,
                    timestamp=datetime.datetime.now()
                )
                
                # 設定篩選資訊
                filter_info = []
                if county:
                    filter_info.append(f"縣市: {county}")
                if road:
                    filter_info.append(f"道路: {road}")
                
                if filter_info:
                    embed.add_field(
                        name="🔍 篩選條件",
                        value=" | ".join(filter_info),
                        inline=False
                    )
                
                embed.add_field(
                    name="📊 搜尋結果",
                    value=f"共找到 {len(filtered_cameras)} 個監視器，顯示前 {len(display_cameras)} 個",
                    inline=False
                )
                
                # 顯示第一個監視器
                first_camera = display_cameras[0]
                image_url = self._add_timestamp_to_url(first_camera['image_url'])
                
                embed.add_field(
                    name=f"📹 {first_camera['name']}",
                    value=f"🛣️ 道路: {first_camera['road']}\n📍 位置: {first_camera['location']}\n🧭 方向: {first_camera['direction']}\n🏙️ 縣市: {first_camera['county']}\n⏰ 更新時間: {datetime.datetime.now().strftime('%H:%M:%S')}",
                    inline=False
                )
                
                if image_url and image_url != "N/A":
                    embed.set_image(url=image_url)
                
                if len(display_cameras) > 1:
                    embed.set_footer(text=f"第 1/{len(display_cameras)} 個監視器")
                
                await interaction.followup.send(embed=embed)
                        
        except Exception as e:
            logger.error(f"查詢一般道路監視器時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢一般道路監視器時發生錯誤: {str(e)}")

    @app_commands.command(name="water_disaster_cameras", description="查詢水利防災監控影像（舊版相容）")
    @app_commands.describe(location="地點關鍵字")
    async def water_disaster_cameras(self, interaction: discord.Interaction, location: str = None):
        """查詢水利防災監控影像（舊版相容指令）"""
        # 這個指令重導向到新的 water_cameras 指令
        await self.water_cameras(interaction, county=location)


async def setup(bot):
    """設置函數，用於載入 Cog"""
    await bot.add_cog(ReservoirCommands(bot))
