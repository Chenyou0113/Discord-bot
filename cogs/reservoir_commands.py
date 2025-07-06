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
import xml.etree.ElementTree as ET
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
    
    @app_commands.command(name="water_level", description="查詢全台河川水位即時資料（依測站編號）")
    @app_commands.describe(
        city="縣市名稱（目前暫不支援，正在開發中）",
        river="河川名稱（目前暫不支援，正在開發中）",
        station="測站編號或識別碼（部分關鍵字搜尋）"
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
        """查詢河川水位資料（包含警戒水位檢查）"""
        await interaction.response.defer()
        
        try:
            # 同時獲取水位資料和警戒水位資料
            api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
            
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            # 獲取警戒水位資料
            alert_levels = await self._get_alert_water_levels()
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        await interaction.followup.send(f"❌ API 請求失敗，狀態碼: {response.status}")
                        return
                    
                    # 處理 UTF-8 BOM 問題
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]
                    
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError as e:
                        await interaction.followup.send(f"❌ JSON 解析失敗: {str(e)}")
                        return
                    
                    # 檢查資料結構 - 水利署 API 回應是字典格式
                    if not isinstance(data, dict):
                        await interaction.followup.send("❌ API 回應格式錯誤")
                        return
                    
                    # 從回應中提取實際的水位資料列表
                    records = data.get('RealtimeWaterLevel_OPENDATA', [])
                    
                    if not records:
                        await interaction.followup.send("❌ 無水位資料")
                        return
                    
                    # 篩選資料
                    filtered_records = []
                    
                    for record in records:
                        # 確保 record 是字典
                        if not isinstance(record, dict):
                            logger.warning(f"跳過非字典記錄: {type(record)} - {record}")
                            continue
                            
                        station_id = record.get('ST_NO', '')
                        observatory_id = record.get('ObservatoryIdentifier', '')
                        water_level = record.get('WaterLevel', '')
                        
                        # 篩選條件 (由於缺少縣市和河川資訊，只能根據測站編號篩選)
                        matches = True
                        
                        if city:
                            # 由於沒有縣市資訊，暫時跳過縣市篩選
                            # 可以在未來加入測站編號對應表
                            pass
                        
                        if river:
                            # 由於沒有河川資訊，暫時跳過河川篩選
                            pass
                        
                        if station and matches:
                            # 根據測站編號或識別碼篩選
                            if (station.lower() not in station_id.lower() and 
                                station.lower() not in observatory_id.lower()):
                                matches = False
                        
                        # 過濾空水位資料
                        if water_level == '' or water_level is None:
                            matches = False
                        
                        if matches:
                            filtered_records.append(record)
                    
                    if not filtered_records:
                        filter_msg = []
                        if city:
                            filter_msg.append(f"縣市: {city} (註: 目前API未提供縣市資訊)")
                        if river:
                            filter_msg.append(f"河川: {river} (註: 目前API未提供河川資訊)")
                        if station:
                            filter_msg.append(f"測站: {station}")
                        
                        filter_text = "、".join(filter_msg) if filter_msg else "全台"
                        await interaction.followup.send(f"❌ 找不到符合條件的水位資料\n篩選條件: {filter_text}")
                        return
                    
                    # 限制顯示數量
                    display_records = filtered_records[:15]
                    
                    # 統計警戒狀況
                    alert_counts = {"正常": 0, "一級警戒": 0, "二級警戒": 0, "三級警戒": 0, "無警戒資料": 0}
                    
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
                        # 使用實際可用的欄位
                        station_id = record.get('ST_NO', 'N/A')
                        observatory_id = record.get('ObservatoryIdentifier', 'N/A')
                        water_level = record.get('WaterLevel', 'N/A')
                        record_time = record.get('RecordTime', 'N/A')
                        
                        # 檢查警戒水位
                        station_alert_data = alert_levels.get(station_id, {})
                        alert_status, alert_icon = self._check_water_level_alert(water_level, station_alert_data)
                        alert_counts[alert_status] = alert_counts.get(alert_status, 0) + 1
                        
                        # 格式化水位資料
                        if water_level != 'N/A' and water_level is not None and str(water_level).strip():
                            try:
                                water_level_num = float(water_level)
                                water_level_str = f"{water_level_num:.2f} 公尺"
                            except:
                                water_level_str = str(water_level)
                        else:
                            water_level_str = "無資料"
                        
                        # 格式化時間
                        try:
                            if record_time != 'N/A' and record_time:
                                # 處理不同的時間格式
                                if 'T' in record_time:
                                    dt = datetime.datetime.fromisoformat(record_time.replace('Z', '+00:00'))
                                    # 轉換為台灣時間 (UTC+8)
                                    dt_tw = dt + datetime.timedelta(hours=8)
                                    time_str = dt_tw.strftime('%m/%d %H:%M')
                                else:
                                    # 假設已經是本地時間
                                    time_str = record_time
                            else:
                                time_str = "無資料"
                        except:
                            time_str = str(record_time)
                        
                        embed.add_field(
                            name=f"{i}. 測站: {station_id}",
                            value=f"🏷️ 識別碼: {observatory_id}\n💧 水位: {water_level_str}\n{alert_icon} 警戒: {alert_status}\n⏰ 時間: {time_str}",
                            inline=True
                        )
                    
                    # 加入警戒統計
                    alert_summary = []
                    for status, count in alert_counts.items():
                        if count > 0:
                            if status == "正常":
                                alert_summary.append(f"🟢 {status}: {count}")
                            elif status == "一級警戒":
                                alert_summary.append(f"🟡 {status}: {count}")
                            elif status == "二級警戒":
                                alert_summary.append(f"🟠 {status}: {count}")
                            elif status == "三級警戒":
                                alert_summary.append(f"🔴 {status}: {count}")
                            else:
                                alert_summary.append(f"⚪ {status}: {count}")
                    
                    if alert_summary:
                        embed.add_field(
                            name="🚨 警戒狀況統計",
                            value=" | ".join(alert_summary),
                            inline=False
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
                    
                    embed.set_footer(text="💡 使用 city/river/station 參數可以縮小搜尋範圍 | 🚨 警戒水位資料來源：水利署")
                    
                    await interaction.followup.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"查詢河川水位時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢水位資料時發生錯誤: {str(e)}")

    async def _get_water_cameras(self, interaction: discord.Interaction, county: str = None):
        """私有方法：獲取水利防災監控影像資料 (使用 XML API)"""
        try:
            # 使用正確的 XML API
            api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=xml&id=362C7288-F378-4BF2-966C-2CD961732C52"
            
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
                    
                    # 檢查回應是否為空
                    if not content or len(content.strip()) == 0:
                        await interaction.followup.send("❌ API 回應為空，水利防災監視器服務可能暫時不可用")
                        return
                    
                    # 處理可能的 BOM
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    
                    # 解析 XML
                    try:
                        root = ET.fromstring(content)
                        
                        # 查找所有的 Table 元素
                        items = root.findall('.//diffgr:diffgram//NewDataSet//Table', 
                                           {'diffgr': 'urn:schemas-microsoft-com:xml-diffgram-v1'})
                        if not items:
                            # 嘗試其他可能的路徑
                            items = root.findall('.//Table')
                        
                    except ET.ParseError as e:
                        logger.error(f"XML 解析失敗: {e}")
                        await interaction.followup.send("❌ 水利防災監視器資料格式錯誤，服務可能暫時不可用")
                        return
                    
                    if not items or len(items) == 0:
                        await interaction.followup.send("❌ 目前無可用的水利防災監視器資料")
                        return
                    
                    cameras = []
                    for item in items:
                        try:
                            # 從 XML 元素中提取資料
                            def get_xml_text(element, tag_name, default=''):
                                elem = element.find(tag_name)
                                return elem.text if elem is not None and elem.text else default
                            
                            # 使用正確的 XML API 欄位結構
                            camera_info = {
                                'id': get_xml_text(item, 'CameraID'),
                                'name': get_xml_text(item, 'VideoSurveillanceStationName') or get_xml_text(item, 'CameraName', '未知監視器'),
                                'county': get_xml_text(item, 'CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '未知'),
                                'district': get_xml_text(item, 'AdministrativeDistrictWhereTheMonitoringPointIsLocated'),
                                'image_url': get_xml_text(item, 'ImageURL'),  # 使用正確的 ImageURL 欄位
                                'lat': get_xml_text(item, 'latitude_4326'),
                                'lon': get_xml_text(item, 'Longitude_4326'),
                                'status': get_xml_text(item, 'Status'),
                                'basin': get_xml_text(item, 'BasinName'),
                                'tributary': get_xml_text(item, 'TRIBUTARY'),
                                'raw_item': item  # 保留原始 XML 元素用於調試
                            }
                            
                            # 確保有基本資訊（即使沒有影像 URL 也顯示）
                            if camera_info['name'] and camera_info['name'] != '未知監視器':
                                cameras.append(camera_info)
                                
                        except Exception as e:
                            logger.error(f"處理監視器資料時發生錯誤: {e}")
                            continue
                    
                    if not cameras:
                        await interaction.followup.send("❌ 無法解析水利防災監視器資料")
                        return
                    
                    # 篩選指定縣市
                    if county:
                        # 支援簡化縣市名稱搜尋
                        normalized_county = county.replace('台', '臺')
                        if not normalized_county.endswith(('市', '縣')):
                            # 嘗試添加市或縣
                            test_county_names = [f"{normalized_county}市", f"{normalized_county}縣"]
                        else:
                            test_county_names = [normalized_county]
                        
                        filtered_cameras = []
                        for cam in cameras:
                            cam_county = cam['county'].replace('台', '臺')
                            if any(test_name in cam_county or cam_county in test_name for test_name in test_county_names):
                                filtered_cameras.append(cam)
                        
                        if not filtered_cameras:
                            await interaction.followup.send(f"❌ 在 {county} 找不到水利防災監視器")
                            return
                    else:
                        filtered_cameras = cameras
                    
                    # 限制顯示數量
                    display_cameras = filtered_cameras[:20]
                    
                    # 建立 embed
                    embed = discord.Embed(
                        title="🌊 水利防災監控影像",
                        color=0x0099ff,
                        timestamp=datetime.datetime.now()
                    )
                    
                    if county:
                        embed.add_field(
                            name="🏛️ 查詢地區",
                            value=county,
                            inline=False
                        )
                    
                    for i, camera in enumerate(display_cameras, 1):
                        name = camera['name']
                        county_info = camera['county']
                        district_info = camera['district']
                        image_url = camera['image_url']
                        
                        # 組合位置資訊
                        location = county_info
                        if district_info:
                            location += f" {district_info}"
                        
                        # 處理影像 URL
                        if image_url:
                            # 加上時間戳避免快取
                            timestamp = int(datetime.datetime.now().timestamp())
                            cache_busted_url = f"{image_url}?t={timestamp}"
                            url_text = f"🔗 [查看影像]({cache_busted_url})"
                        else:
                            # 如果沒有影像 URL，提供替代資訊
                            camera_id = camera.get('id', '')
                            if camera_id:
                                url_text = f"📷 監視器ID: {camera_id}\n🔗 影像連結暫不可用"
                            else:
                                url_text = "🔗 影像連結暫不可用"
                        
                        # 添加座標資訊（如果有的話）
                        coord_text = ""
                        lat = camera.get('lat', '')
                        lon = camera.get('lon', '')
                        if lat and lon:
                            coord_text = f"\n📍 座標: {lat}, {lon}"
                        
                        embed.add_field(
                            name=f"{i}. {name}",
                            value=f"📍 {location}{coord_text}\n{url_text}",
                            inline=True
                        )
                    
                    embed.add_field(
                        name="📊 統計",
                        value=f"共找到 {len(filtered_cameras)} 個監視器，顯示前 {len(display_cameras)} 個",
                        inline=False
                    )
                    
                    embed.set_footer(text="💡 點擊連結查看即時影像 | 資料來源：水利署開放資料")
                    
                    await interaction.followup.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"查詢水利防災監控影像時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢監控影像時發生錯誤: {str(e)}")

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
        
        # 使用私有方法獲取監視器資料
        await self._get_water_cameras(interaction, county=county)
                        
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
        await interaction.response.defer()
        
        # 調用私有方法獲取監視器資料
        await self._get_water_cameras(interaction, county=location)

    async def _get_alert_levels(self):
        """獲取警戒水位資料，建立測站編號對應表"""
        try:
            alert_api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=D2A498A6-8706-42FB-B623-C08C9665BDFD"
            
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(alert_api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.warning(f"警戒水位 API 請求失敗，狀態碼: {response.status}")
                        return {}
                    
                    # 處理 UTF-8 BOM 問題
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]
                    
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError as e:
                        logger.warning(f"警戒水位 JSON 解析失敗: {str(e)}")
                        return {}
                    
                    # 尋找警戒水位資料
                    alert_records = []
                    if isinstance(data, dict):
                        # 嘗試各種可能的鍵名
                        possible_keys = ['FloodLevel_OPENDATA', 'AlertLevel_OPENDATA', 'WarningLevel_OPENDATA']
                        for key in possible_keys:
                            if key in data and isinstance(data[key], list):
                                alert_records = data[key]
                                break
                        
                        # 如果沒找到預期的鍵，使用第一個包含列表的鍵
                        if not alert_records:
                            for key, value in data.items():
                                if isinstance(value, list) and value:
                                    alert_records = value
                                    break
                    elif isinstance(data, list):
                        alert_records = data
                    
                    if not alert_records:
                        logger.warning("無法找到警戒水位資料")
                        return {}
                    
                    # 建立測站編號到警戒水位的對應表
                    alert_dict = {}
                    for record in alert_records:
                        if isinstance(record, dict):
                            # 尋找測站編號
                            station_keys = ['ST_NO', 'StationId', 'StationCode', 'StationNo', 'ID']
                            station_id = None
                            
                            for key in station_keys:
                                if key in record and record[key]:
                                    station_id = record[key]
                                    break
                            
                            if station_id:
                                # 尋找警戒水位
                                alert_keys = ['AlertLevel', 'WarningLevel', 'FloodLevel', 'AlertWaterLevel']
                                alert_level = None
                                
                                for key in alert_keys:
                                    if key in record and record[key] is not None:
                                        try:
                                            alert_level = float(record[key])
                                            break
                                        except (ValueError, TypeError):
                                            continue
                                
                                if alert_level is not None:
                                    alert_dict[station_id] = alert_level
                    
                    logger.info(f"成功獲取 {len(alert_dict)} 個測站的警戒水位資料")
                    return alert_dict
                    
        except Exception as e:
            logger.error(f"獲取警戒水位資料時發生錯誤: {str(e)}")
            return {}

    async def _get_alert_water_levels(self):
        """獲取警戒水位資料"""
        try:
            api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=D2A498A6-8706-42FB-B623-C08C9665BDFD"
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"警戒水位 API 請求失敗: {response.status}")
                        return {}
                    
                    content = await response.text()
                    
                    # 處理 BOM
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        logger.error(f"警戒水位資料 JSON 解析失敗: {e}")
                        return {}
                    
                    # 建立測站編號到警戒水位的映射
                    alert_levels = {}
                    for item in data:
                        if isinstance(item, dict):
                            station_no = item.get('StationNo', item.get('ST_NO', ''))
                            first_alert = item.get('FirstAlert', item.get('AlertLevel1', ''))
                            second_alert = item.get('SecondAlert', item.get('AlertLevel2', ''))
                            third_alert = item.get('ThirdAlert', item.get('AlertLevel3', ''))
                            
                            if station_no:
                                alert_levels[station_no] = {
                                    'first_alert': first_alert,
                                    'second_alert': second_alert,
                                    'third_alert': third_alert
                                }
                    
                    return alert_levels
                    
        except Exception as e:
            logger.error(f"獲取警戒水位資料時發生錯誤: {e}")
            return {}

    def _check_water_level_alert(self, current_level, alert_levels):
        """檢查水位是否達到警戒值"""
        if not alert_levels or not current_level:
            return "無警戒資料", "⚪"
        
        try:
            current = float(current_level)
            
            # 檢查三級警戒
            third_alert = alert_levels.get('third_alert', '')
            second_alert = alert_levels.get('second_alert', '')
            first_alert = alert_levels.get('first_alert', '')
            
            if third_alert and str(third_alert).replace('.', '').isdigit():
                if current >= float(third_alert):
                    return "三級警戒", "🔴"
            
            if second_alert and str(second_alert).replace('.', '').isdigit():
                if current >= float(second_alert):
                    return "二級警戒", "🟠"
            
            if first_alert and str(first_alert).replace('.', '').isdigit():
                if current >= float(first_alert):
                    return "一級警戒", "🟡"
            
            return "正常", "🟢"
            
        except (ValueError, TypeError):
            return "無法判斷", "⚪"

    @app_commands.command(name="highway_cameras", description="查詢公路總局監視器")
    @app_commands.describe(
        location="地點關鍵字（如：國道一號、台北、高速公路等）"
    )
    async def highway_cameras(self, interaction: discord.Interaction, location: str = None):
        """查詢公路總局監視器"""
        await interaction.response.defer()
        
        try:
            api_url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
            
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
                    
                    # 檢查回應是否為空
                    if not content or len(content.strip()) == 0:
                        await interaction.followup.send("❌ API 回應為空，公路監視器服務可能暫時不可用")
                        return
                    
                    # 解析 XML
                    import xml.etree.ElementTree as ET
                    try:
                        root = ET.fromstring(content)
                    except ET.ParseError as e:
                        logger.error(f"XML 解析失敗: {e}")
                        await interaction.followup.send("❌ 公路監視器資料格式錯誤，服務可能暫時不可用")
                        return
                    
                    cameras = []
                    for cctv in root.findall('.//CCTV'):
                        try:
                            camera_info = {
                                'id': cctv.find('CCTVID').text if cctv.find('CCTVID') is not None else '',
                                'name': cctv.find('CCTVName').text if cctv.find('CCTVName') is not None else '未知監視器',
                                'road': cctv.find('RoadName').text if cctv.find('RoadName') is not None else '未知道路',
                                'direction': cctv.find('RoadDirection').text if cctv.find('RoadDirection') is not None else '',
                                'video_url': cctv.find('VideoStreamURL').text if cctv.find('VideoStreamURL') is not None else '',
                                'lat': cctv.find('PositionLat').text if cctv.find('PositionLat') is not None else '',
                                'lon': cctv.find('PositionLon').text if cctv.find('PositionLon') is not None else '',
                                'location_desc': cctv.find('LocationDescription').text if cctv.find('LocationDescription') is not None else ''
                            }
                            
                            # 確保有基本資訊
                            if camera_info['name'] and camera_info['name'] != '未知監視器':
                                cameras.append(camera_info)
                                
                        except Exception as e:
                            logger.error(f"處理公路監視器資料時發生錯誤: {e}")
                            continue
                    
                    if not cameras:
                        await interaction.followup.send("❌ 無法解析公路監視器資料")
                        return
                    
                    # 篩選指定地點
                    if location:
                        filtered_cameras = []
                        location_lower = location.lower()
                        
                        for cam in cameras:
                            # 在名稱、道路、方向、位置描述中搜尋
                            search_fields = [
                                cam['name'].lower(),
                                cam['road'].lower(),
                                cam['direction'].lower(),
                                cam['location_desc'].lower()
                            ]
                            
                            if any(location_lower in field for field in search_fields):
                                filtered_cameras.append(cam)
                        
                        if not filtered_cameras:
                            await interaction.followup.send(f"❌ 在 {location} 找不到公路監視器")
                            return
                    else:
                        filtered_cameras = cameras
                    
                    # 限制顯示數量
                    display_cameras = filtered_cameras[:20]
                    
                    # 建立 embed
                    embed = discord.Embed(
                        title="🛣️ 公路總局監視器",
                        color=0x00aa00,
                        timestamp=datetime.datetime.now()
                    )
                    
                    if location:
                        embed.add_field(
                            name="🔍 搜尋關鍵字",
                            value=location,
                            inline=False
                        )
                    
                    for i, camera in enumerate(display_cameras, 1):
                        name = camera['name']
                        road = camera['road']
                        direction = camera['direction']
                        video_url = camera['video_url']
                        location_desc = camera['location_desc']
                        
                        # 組合位置資訊
                        location_info = road
                        if direction:
                            location_info += f" {direction}"
                        if location_desc:
                            location_info += f"\n📍 {location_desc}"
                        
                        # 處理影像 URL
                        if video_url:
                            # 加上時間戳避免快取
                            timestamp = int(datetime.datetime.now().timestamp())
                            cache_busted_url = f"{video_url}?t={timestamp}"
                            url_text = f"🔗 [查看影像]({cache_busted_url})"
                        else:
                            url_text = "🔗 影像連結暫不可用"
                        
                        embed.add_field(
                            name=f"{i}. {name}",
                            value=f"🛣️ {location_info}\n{url_text}",
                            inline=True
                        )
                    
                    embed.add_field(
                        name="📊 統計",
                        value=f"共找到 {len(filtered_cameras)} 個監視器，顯示前 {len(display_cameras)} 個",
                        inline=False
                    )
                    
                    embed.set_footer(text="💡 點擊連結查看即時影像 | 資料來源：公路總局")
                    
                    await interaction.followup.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"查詢公路監視器時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢公路監視器時發生錯誤: {str(e)}")

    @app_commands.command(name="debug_water_cameras", description="調試水利防災監控影像 API 資料結構（僅管理員）")
    @app_commands.describe(
        show_raw_data="是否顯示原始資料結構"
    )
    async def debug_water_cameras(self, interaction: discord.Interaction, show_raw_data: bool = False):
        """調試水利防災監控影像 API 資料結構"""
        await interaction.response.defer(ephemeral=True)  # 只有使用者可見
        
        try:
            api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
            
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
                    
                    # 處理 BOM
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        await interaction.followup.send(f"❌ JSON 解析失敗: {e}")
                        return
                    
                    if not isinstance(data, list) or len(data) == 0:
                        await interaction.followup.send("❌ API 回應格式錯誤或無資料")
                        return
                    
                    # 分析第一筆資料
                    first_item = data[0]
                    
                    embed = discord.Embed(
                        title="🔍 水利防災監控影像 API 調試資訊",
                        color=0xff9900,
                        timestamp=datetime.datetime.now()
                    )
                    
                    embed.add_field(
                        name="📊 基本資訊",
                        value=f"總資料筆數: {len(data)}",
                        inline=False
                    )
                    
                    # 顯示欄位結構
                    field_info = []
                    url_fields = []
                    
                    for key, value in first_item.items():
                        if value:
                            field_info.append(f"✅ {key}")
                            # 檢查是否可能是 URL
                            if isinstance(value, str) and any(keyword in value.lower() for keyword in ['http', '.jpg', '.png', 'image']):
                                url_fields.append(f"{key}: {value}")
                        else:
                            field_info.append(f"⚪ {key}")
                    
                    # 分批顯示欄位（Discord embed 有字數限制）
                    field_chunks = [field_info[i:i+10] for i in range(0, len(field_info), 10)]
                    
                    for i, chunk in enumerate(field_chunks):
                        embed.add_field(
                            name=f"📋 欄位結構 ({i+1}/{len(field_chunks)})",
                            value="\n".join(chunk),
                            inline=True
                        )
                    
                    if url_fields:
                        embed.add_field(
                            name="🔗 可能的 URL 欄位",
                            value="\n".join(url_fields[:5]),  # 只顯示前5個
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="🔗 URL 欄位",
                            value="❌ 未找到明顯的 URL 欄位",
                            inline=False
                        )
                    
                    # 檢查宜蘭資料
                    yilan_count = sum(1 for item in data if '宜蘭' in item.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', ''))
                    embed.add_field(
                        name="🏞️ 宜蘭縣資料",
                        value=f"宜蘭縣監視器數量: {yilan_count}",
                        inline=False
                    )
                    
                    if show_raw_data:
                        # 顯示第一筆原始資料（截短）
                        raw_data_text = json.dumps(first_item, ensure_ascii=False, indent=2)[:1000]
                        embed.add_field(
                            name="📄 第一筆原始資料（前1000字元）",
                            value=f"```json\n{raw_data_text}...\n```",
                            inline=False
                        )
                    
                    embed.set_footer(text="💡 這是調試資訊，用於分析 API 資料結構")
                    
                    await interaction.followup.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"調試水利防災監控影像時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 調試過程中發生錯誤: {str(e)}")

    async def _get_alert_levels(self):
        """獲取警戒水位資料，建立測站編號對應表"""
        try:
            alert_api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=D2A498A6-8706-42FB-B623-C08C9665BDFD"
            
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(alert_api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.warning(f"警戒水位 API 請求失敗，狀態碼: {response.status}")
                        return {}
                    
                    # 處理 UTF-8 BOM 問題
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]
                    
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError as e:
                        logger.warning(f"警戒水位 JSON 解析失敗: {str(e)}")
                        return {}
                    
                    # 尋找警戒水位資料
                    alert_records = []
                    if isinstance(data, dict):
                        # 嘗試各種可能的鍵名
                        possible_keys = ['FloodLevel_OPENDATA', 'AlertLevel_OPENDATA', 'WarningLevel_OPENDATA']
                        for key in possible_keys:
                            if key in data and isinstance(data[key], list):
                                alert_records = data[key]
                                break
                        
                        # 如果沒找到預期的鍵，使用第一個包含列表的鍵
                        if not alert_records:
                            for key, value in data.items():
                                if isinstance(value, list) and value:
                                    alert_records = value
                                    break
                    elif isinstance(data, list):
                        alert_records = data
                    
                    if not alert_records:
                        logger.warning("無法找到警戒水位資料")
                        return {}
                    
                    # 建立測站編號到警戒水位的對應表
                    alert_dict = {}
                    for record in alert_records:
                        if isinstance(record, dict):
                            # 尋找測站編號
                            station_keys = ['ST_NO', 'StationId', 'StationCode', 'StationNo', 'ID']
                            station_id = None
                            
                            for key in station_keys:
                                if key in record and record[key]:
                                    station_id = record[key]
                                    break
                            
                            if station_id:
                                # 尋找警戒水位
                                alert_keys = ['AlertLevel', 'WarningLevel', 'FloodLevel', 'AlertWaterLevel']
                                alert_level = None
                                
                                for key in alert_keys:
                                    if key in record and record[key] is not None:
                                        try:
                                            alert_level = float(record[key])
                                            break
                                        except (ValueError, TypeError):
                                            continue
                                
                                if alert_level is not None:
                                    alert_dict[station_id] = alert_level
                    
                    logger.info(f"成功獲取 {len(alert_dict)} 個測站的警戒水位資料")
                    return alert_dict
                    
        except Exception as e:
            logger.error(f"獲取警戒水位資料時發生錯誤: {str(e)}")
            return {}

    async def _get_alert_water_levels(self):
        """獲取警戒水位資料"""
        try:
            api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=D2A498A6-8706-42FB-B623-C08C9665BDFD"
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"警戒水位 API 請求失敗: {response.status}")
                        return {}
                    
                    content = await response.text()
                    
                    # 處理 BOM
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        logger.error(f"警戒水位資料 JSON 解析失敗: {e}")
                        return {}
                    
                    # 建立測站編號到警戒水位的映射
                    alert_levels = {}
                    for item in data:
                        if isinstance(item, dict):
                            station_no = item.get('StationNo', item.get('ST_NO', ''))
                            first_alert = item.get('FirstAlert', item.get('AlertLevel1', ''))
                            second_alert = item.get('SecondAlert', item.get('AlertLevel2', ''))
                            third_alert = item.get('ThirdAlert', item.get('AlertLevel3', ''))
                            
                            if station_no:
                                alert_levels[station_no] = {
                                    'first_alert': first_alert,
                                    'second_alert': second_alert,
                                    'third_alert': third_alert
                                }
                    
                    return alert_levels
                    
        except Exception as e:
            logger.error(f"獲取警戒水位資料時發生錯誤: {e}")
            return {}

    def _check_water_level_alert(self, current_level, alert_levels):
        """檢查水位是否達到警戒值"""
        if not alert_levels or not current_level:
            return "無警戒資料", "⚪"
        
        try:
            current = float(current_level)
            
            # 檢查三級警戒
            third_alert = alert_levels.get('third_alert', '')
            second_alert = alert_levels.get('second_alert', '')
            first_alert = alert_levels.get('first_alert', '')
            
            if third_alert and str(third_alert).replace('.', '').isdigit():
                if current >= float(third_alert):
                    return "三級警戒", "🔴"
            
            if second_alert and str(second_alert).replace('.', '').isdigit():
                if current >= float(second_alert):
                    return "二級警戒", "🟠"
            
            if first_alert and str(first_alert).replace('.', '').isdigit():
                if current >= float(first_alert):
                    return "一級警戒", "🟡"
            
            return "正常", "🟢"
            
        except (ValueError, TypeError):
            return "無法判斷", "⚪"

    def _construct_image_url(self, xml_item):
        """從 XML 元素中提取影像 URL"""
        # 對於新的 XML API，直接使用 ImageURL 標籤
        if hasattr(xml_item, 'find'):
            # 這是 XML 元素
            image_url_elem = xml_item.find('ImageURL')
            if image_url_elem is not None and image_url_elem.text:
                url = image_url_elem.text.strip()
                if url and ('http' in url.lower() or url.startswith('//')):
                    return url
            
            # 嘗試其他可能的 URL 欄位
            other_url_fields = ['VideoSurveillanceImageUrl', 'ImageUrl', 'Url', 'StreamUrl', 'VideoUrl']
            for field in other_url_fields:
                elem = xml_item.find(field)
                if elem is not None and elem.text:
                    url = elem.text.strip()
                    if url and ('http' in url.lower() or url.startswith('//')):
                        return url
            
            # 如果沒有找到 URL，嘗試通過 CameraID 構造
            camera_id_elem = xml_item.find('CameraID')
            if camera_id_elem is not None and camera_id_elem.text:
                camera_id = camera_id_elem.text.strip()
                if camera_id:
                    # 嘗試一些常見的監視器 URL 模式
                    possible_patterns = [
                        f"https://alerts.ncdr.nat.gov.tw/Image.aspx?mode=getNewImage&id={camera_id}",
                        f"https://fhy.wra.gov.tw/fhy/Monitor/Image.aspx?id={camera_id}",
                        f"https://opendata.wra.gov.tw/image/{camera_id}.jpg"
                    ]
                    return possible_patterns[0]
        
        # 如果是字典格式（舊的相容性）
        elif isinstance(xml_item, dict):
            url_fields = ['ImageURL', 'VideoSurveillanceImageUrl', 'ImageUrl', 'Url', 'StreamUrl', 'VideoUrl', 'CameraUrl', 'LinkUrl']
            
            for field in url_fields:
                url = xml_item.get(field, '')
                if url and ('http' in url.lower() or url.startswith('//')):
                    return url
            
            # 嘗試通過 ID 構造 URL
            camera_id = xml_item.get('CameraID', '')
            if camera_id:
                possible_patterns = [
                    f"https://alerts.ncdr.nat.gov.tw/Image.aspx?mode=getNewImage&id={camera_id}",
                    f"https://fhy.wra.gov.tw/fhy/Monitor/Image.aspx?id={camera_id}",
                    f"https://opendata.wra.gov.tw/image/{camera_id}.jpg"
                ]
                return possible_patterns[0]
        
        return ''

async def setup(bot):
    """設置函數，用於載入 Cog"""
    await bot.add_cog(ReservoirCommands(bot))