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
import time
import random
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
        location="地點關鍵字",
        data_source="選擇資料來源"
    )
    @app_commands.choices(data_source=[
        app_commands.Choice(name="合併兩來源 (預設)", value="merged"),
        app_commands.Choice(name="TDX API", value="tdx"),
        app_commands.Choice(name="高速公路局 XML", value="freeway"),
    ])
    async def national_highway_cameras(
        self, 
        interaction: discord.Interaction, 
        highway: str = None, 
        location: str = None,
        data_source: str = "merged"
    ):
        """查詢國道監視器 (TDX Freeway API)"""
        await interaction.response.defer()
        
        try:
            # 1. 取得 TDX access token
            token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
            client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
            client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
            api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Freeway?%24top=30&%24format=JSON"

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)

            async with aiohttp.ClientSession(connector=connector) as session:
                # 取得 access token
                token_data = {
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret
                }
                token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                
                async with session.post(token_url, data=token_data, headers=token_headers) as token_resp:
                    if token_resp.status != 200:
                        await interaction.followup.send(f"❌ 無法取得 TDX Token，狀態碼: {token_resp.status}")
                        return
                    
                    token_json = await token_resp.json()
                    access_token = token_json.get('access_token')
                    if not access_token:
                        await interaction.followup.send("❌ 無法取得 TDX access_token")
                        return
                
                # 2. 查詢監視器 API
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
                
                async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        await interaction.followup.send(f"❌ API 請求失敗，狀態碼: {response.status}")
                        return
                    
                    try:
                        data = await response.json()
                    except Exception as e:
                        await interaction.followup.send(f"❌ JSON 解析失敗: {e}")
                        return
                    
                    # 處理 TDX API 回應結構
                    if isinstance(data, dict) and 'CCTVs' in data:
                        cctv_list = data['CCTVs']
                    elif isinstance(data, list):
                        cctv_list = data
                    else:
                        await interaction.followup.send("❌ API 回應格式錯誤")
                        return
                    
                    if not cctv_list:
                        await interaction.followup.send("❌ 無法解析國道監視器資料")
                        return
                    
                    cameras = []
                    for cctv in cctv_list:
                        try:
                            # 根據分析結果，TDX Freeway API 的實際欄位名稱
                            road_section = cctv.get('RoadSection', {})
                            if isinstance(road_section, dict):
                                location_desc = f"{road_section.get('Start', '')} 到 {road_section.get('End', '')}"
                            else:
                                location_desc = str(road_section) if road_section else ""
                            
                            camera_info = {
                                'id': cctv.get('CCTVID', ''),
                                'name': location_desc or f"{cctv.get('RoadName', '')} {cctv.get('LocationMile', '')}",
                                'highway': cctv.get('RoadName', '未知道路'),
                                'direction': cctv.get('RoadDirection', ''),
                                'location': location_desc,
                                'video_url': cctv.get('VideoStreamURL', ''),
                                'image_url': cctv.get('VideoImageURL', ''),  # 可能沒有此欄位
                                'lat': str(cctv.get('PositionLat', '')),
                                'lon': str(cctv.get('PositionLon', '')),
                                'mile': cctv.get('LocationMile', ''),
                                'county': '',  # Freeway API 可能沒有縣市資訊
                                'update_time': '',  # 個別 CCTV 可能沒有更新時間
                                'road_section': road_section
                            }
                            
                            # 篩選條件
                            if highway and str(highway) not in camera_info['highway']:
                                continue
                            
                            # 搜尋邏輯改善
                            if location:
                                search_fields = [
                                    camera_info['location'].lower(),
                                    camera_info['name'].lower(),
                                    camera_info['highway'].lower(),
                                    camera_info['mile'].lower()
                                ]
                                if not any(location.lower() in field for field in search_fields):
                                    continue
                            
                            # 只要有基本資訊就加入
                            if camera_info['highway'] != '未知道路':
                                cameras.append(camera_info)
                                
                        except Exception as e:
                            logger.error(f"處理國道監視器資料時發生錯誤: {e}")
                            continue
                    
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
                        title="🛣️ 國道監視器 (TDX Freeway API)",
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
                    
                    # 顯示前幾個監視器
                    for i, camera in enumerate(display_cameras[:5], 1):
                        name = camera['name']
                        highway_info = camera['highway']
                        direction = camera['direction']
                        location_desc = camera['location']
                        video_url = camera['video_url']
                        image_url = camera['image_url']
                        mile = camera.get('mile', '')
                        county = camera.get('county', '')
                        
                        # 組合位置資訊
                        location_info = highway_info
                        if direction:
                            location_info += f" {direction}向"
                        if county:
                            location_info += f"\n🏛️ {county}"
                        if mile:
                            location_info += f"\n📏 {mile}"
                        
                        # 處理影像 URL（優先使用快照圖片）
                        if image_url:
                            timestamp = int(datetime.datetime.now().timestamp())
                            cache_busted_url = f"{image_url}?t={timestamp}"
                            url_text = f"🔗 [查看影像]({cache_busted_url})"
                        elif video_url:
                            timestamp = int(datetime.datetime.now().timestamp())
                            cache_busted_url = f"{video_url}?t={timestamp}"
                            url_text = f"� [查看影像]({cache_busted_url})"
                        else:
                            url_text = "🔗 影像連結暫不可用"
                        
                        # 座標資訊
                        lat = camera.get('lat', '')
                        lon = camera.get('lon', '')
                        if lat and lon:
                            url_text += f"\n📍 座標: {lat}, {lon}"
                        
                        embed.add_field(
                            name=f"{i}. {name[:35]}{'...' if len(name) > 35 else ''}",
                            value=f"🛣️ {location_info}\n📍 {location_desc}\n{url_text}",
                            inline=True
                        )
                    
                    embed.add_field(
                        name="📊 統計",
                        value=f"共找到 {len(cameras)} 個監視器，顯示前 {len(display_cameras[:5])} 個",
                        inline=False
                    )
                    
                    embed.set_footer(text="💡 點擊連結查看即時影像 | 資料來源：運輸資料流通服務平臺 (TDX)")
                    
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

    @app_commands.command(name="highway_cameras", description="查詢公路監視器 (整合TDX與公路局資料)")
    @app_commands.describe(
        county="選擇縣市",
        road_type="選擇道路類型（台幾線）",
        data_source="選擇資料來源"
    )
    @app_commands.choices(county=[
        app_commands.Choice(name="基隆市", value="基隆"),
        app_commands.Choice(name="台北市", value="台北"),
        app_commands.Choice(name="新北市", value="新北"),
        app_commands.Choice(name="桃園市", value="桃園"),
        app_commands.Choice(name="新竹市", value="新竹"),
        app_commands.Choice(name="新竹縣", value="新竹"),
        app_commands.Choice(name="苗栗縣", value="苗栗"),
        app_commands.Choice(name="台中市", value="台中"),
        app_commands.Choice(name="彰化縣", value="彰化"),
        app_commands.Choice(name="南投縣", value="南投"),
        app_commands.Choice(name="雲林縣", value="雲林"),
        app_commands.Choice(name="嘉義市", value="嘉義"),
        app_commands.Choice(name="嘉義縣", value="嘉義"),
        app_commands.Choice(name="台南市", value="台南"),
        app_commands.Choice(name="高雄市", value="高雄"),
        app_commands.Choice(name="屏東縣", value="屏東"),
        app_commands.Choice(name="宜蘭縣", value="宜蘭"),
        app_commands.Choice(name="花蓮縣", value="花蓮"),
        app_commands.Choice(name="台東縣", value="台東"),
    ])
    @app_commands.choices(road_type=[
        app_commands.Choice(name="台1線", value="台1線"),
        app_commands.Choice(name="台2線", value="台2線"),
        app_commands.Choice(name="台3線", value="台3線"),
        app_commands.Choice(name="台4線", value="台4線"),
        app_commands.Choice(name="台5線", value="台5線"),
        app_commands.Choice(name="台7線", value="台7線"),
        app_commands.Choice(name="台8線", value="台8線"),
        app_commands.Choice(name="台9線", value="台9線"),
        app_commands.Choice(name="台11線", value="台11線"),
        app_commands.Choice(name="台14線", value="台14線"),
        app_commands.Choice(name="台15線", value="台15線"),
        app_commands.Choice(name="台17線", value="台17線"),
        app_commands.Choice(name="台18線", value="台18線"),
        app_commands.Choice(name="台19線", value="台19線"),
        app_commands.Choice(name="台20線", value="台20線"),
        app_commands.Choice(name="台21線", value="台21線"),
        app_commands.Choice(name="台24線", value="台24線"),
        app_commands.Choice(name="台26線", value="台26線"),
        app_commands.Choice(name="台61線", value="台61線"),
        app_commands.Choice(name="台62線", value="台62線"),
        app_commands.Choice(name="台64線", value="台64線"),
        app_commands.Choice(name="台65線", value="台65線"),
        app_commands.Choice(name="台66線", value="台66線"),
        app_commands.Choice(name="台68線", value="台68線"),
        app_commands.Choice(name="台88線", value="台88線"),
    ])
    @app_commands.choices(data_source=[
        app_commands.Choice(name="自動合併 (TDX + 公路局)", value="merged"),
        app_commands.Choice(name="僅TDX資料", value="tdx"),
        app_commands.Choice(name="僅公路局資料", value="highway_bureau"),
    ])
    async def highway_cameras(self, interaction: discord.Interaction, county: str = None, road_type: str = None, data_source: str = "merged"):
        """查詢公路監視器 (整合TDX與公路局資料)"""
        await interaction.response.defer()
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)

            async with aiohttp.ClientSession(connector=connector) as session:
                cameras = []
                data_sources_used = []
                
                # 根據資料來源選擇獲取資料
                if data_source in ["merged", "tdx"]:
                    tdx_cameras = await self._get_tdx_cameras(session, county, road_type)
                    if tdx_cameras:
                        cameras.extend(tdx_cameras)
                        data_sources_used.append("TDX")
                
                if data_source in ["merged", "highway_bureau"]:
                    bureau_cameras = await self._get_highway_bureau_cameras(session, county, road_type)
                    if bureau_cameras:
                        cameras.extend(bureau_cameras)
                        data_sources_used.append("公路局")
                
                if not cameras:
                    filter_conditions = []
                    if county:
                        filter_conditions.append(f"縣市: {county}")
                    if road_type:
                        filter_conditions.append(f"道路: {road_type}")
                    
                    filter_text = "、".join(filter_conditions) if filter_conditions else "全部"
                    source_text = " + ".join(data_sources_used) if data_sources_used else data_source
                    await interaction.followup.send(f"❌ 找不到符合條件的公路監視器\n篩選條件: {filter_text}\n資料來源: {source_text}")
                    return
                
                # 隨機選擇一支監視器顯示
                selected_camera = random.choice(cameras)
                
                # 創建 embed
                embed = await self._create_highway_camera_embed(selected_camera, county, road_type, len(cameras), data_sources_used)
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"查詢公路監視器時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢公路監視器時發生錯誤: {str(e)}")

    async def _get_tdx_cameras(self, session, county=None, road_type=None):
        """取得 TDX API 監視器資料"""
        try:
            # 1. 取得 TDX access token
            token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
            client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
            client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
            
            # 根據道路類型選擇 API 端點
            if road_type and road_type.startswith('台'):
                api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=300&%24format=JSON"
            else:
                api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Highway?%24top=300&%24format=JSON"

            # 取得 access token
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            }
            token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            async with session.post(token_url, data=token_data, headers=token_headers) as token_resp:
                if token_resp.status != 200:
                    logger.error(f"無法取得 TDX Token，狀態碼: {token_resp.status}")
                    return []
                token_json = await token_resp.json()
                access_token = token_json.get('access_token')
                if not access_token:
                    logger.error("無法取得 TDX access_token")
                    return []
            
            # 2. 查詢監視器 API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    logger.error(f"TDX API 請求失敗，狀態碼: {response.status}")
                    return []
                
                data = await response.json()
                
                # 處理 TDX API 回應結構
                if isinstance(data, dict) and 'CCTVs' in data:
                    cctv_list = data['CCTVs']
                elif isinstance(data, list):
                    cctv_list = data
                else:
                    logger.error("TDX API 回應格式錯誤")
                    return []
                
                if not cctv_list:
                    return []
                
                cameras = []
                for cctv in cctv_list:
                    try:
                        camera_info = {
                            'id': cctv.get('CCTVID', ''),
                            'name': cctv.get('SurveillanceDescription', '未知監視器'),
                            'road': cctv.get('RoadName', '未知道路'),
                            'direction': cctv.get('RoadDirection', ''),
                            'video_url': cctv.get('VideoStreamURL', ''),
                            'image_url': cctv.get('VideoImageURL', ''),
                            'lat': str(cctv.get('PositionLat', '')),
                            'lon': str(cctv.get('PositionLon', '')),
                            'location_desc': cctv.get('SurveillanceDescription', ''),
                            'mile': cctv.get('LocationMile', ''),
                            'road_class': cctv.get('RoadClass', ''),
                            'county': cctv.get('County', ''),
                            'update_time': cctv.get('UpdateTime', ''),
                            'source': 'TDX'
                        }
                        
                        if camera_info['name'] and camera_info['name'] != '未知監視器':
                            cameras.append(camera_info)
                            
                    except Exception as e:
                        logger.error(f"處理 TDX 監視器資料時發生錯誤: {e}")
                        continue
                
                # 篩選監視器
                return self._filter_cameras(cameras, county, road_type)
                
        except Exception as e:
            logger.error(f"取得 TDX 監視器資料時發生錯誤: {e}")
            return []

    async def _get_highway_bureau_cameras(self, session, county=None, road_type=None):
        """取得公路局 XML API 監視器資料"""
        try:
            api_url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
            
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status != 200:
                    logger.error(f"公路局 API 請求失敗，狀態碼: {response.status}")
                    return []
                
                xml_content = await response.text(encoding='utf-8')
                
                # 解析 XML
                root = ET.fromstring(xml_content)
                
                # 處理命名空間
                ns = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
                
                # 找到監視器資料
                cctvs_element = root.find('ns:CCTVs', ns)
                if cctvs_element is None:
                    logger.error("在公路局 XML 中找不到 CCTVs 元素")
                    return []
                
                cameras = []
                for cctv in cctvs_element.findall('ns:CCTV', ns):
                    try:
                        # 提取監視器資料
                        cctv_id = cctv.find('ns:CCTVID', ns)
                        sub_authority = cctv.find('ns:SubAuthorityCode', ns)
                        video_stream = cctv.find('ns:VideoStreamURL', ns)
                        video_image = cctv.find('ns:VideoImageURL', ns)
                        position_lat = cctv.find('ns:PositionLat', ns)
                        position_lon = cctv.find('ns:PositionLon', ns)
                        surveillance_desc = cctv.find('ns:SurveillanceDescription', ns)
                        road_name = cctv.find('ns:RoadName', ns)
                        road_direction = cctv.find('ns:RoadDirection', ns)
                        location_mile = cctv.find('ns:LocationMile', ns)
                        road_class = cctv.find('ns:RoadClass', ns)
                        
                        camera_info = {
                            'id': cctv_id.text.strip() if cctv_id is not None and cctv_id.text else '',
                            'name': surveillance_desc.text.strip() if surveillance_desc is not None and surveillance_desc.text else '未知監視器',
                            'road': road_name.text.strip() if road_name is not None and road_name.text else '未知道路',
                            'direction': road_direction.text.strip() if road_direction is not None and road_direction.text else '',
                            'video_url': video_stream.text.strip() if video_stream is not None and video_stream.text else '',
                            'image_url': video_image.text.strip() if video_image is not None and video_image.text else '',
                            'lat': position_lat.text.strip() if position_lat is not None and position_lat.text else '',
                            'lon': position_lon.text.strip() if position_lon is not None and position_lon.text else '',
                            'location_desc': surveillance_desc.text.strip() if surveillance_desc is not None and surveillance_desc.text else '',
                            'mile': location_mile.text.strip() if location_mile is not None and location_mile.text else '',
                            'road_class': road_class.text.strip() if road_class is not None and road_class.text else '',
                            'county': self._get_county_from_sub_authority(sub_authority.text.strip() if sub_authority is not None and sub_authority.text else ''),
                            'update_time': '',
                            'source': '公路局',
                            'sub_authority': sub_authority.text.strip() if sub_authority is not None and sub_authority.text else ''
                        }
                        
                        if camera_info['name'] and camera_info['name'] != '未知監視器':
                            cameras.append(camera_info)
                            
                    except Exception as e:
                        logger.error(f"處理公路局監視器資料時發生錯誤: {e}")
                        continue
                
                # 篩選監視器
                return self._filter_cameras(cameras, county, road_type)
                
        except Exception as e:
            logger.error(f"取得公路局監視器資料時發生錯誤: {e}")
            return []

    def _get_county_from_sub_authority(self, sub_authority_code):
        """根據 SubAuthorityCode 推斷縣市"""
        # 公路總局區域分局對應縣市
        region_mapping = {
            "THB-1R": ["基隆", "台北", "新北"],
            "THB-2R": ["桃園", "新竹"],
            "THB-3R": ["苗栗", "台中", "彰化", "南投"],
            "THB-4R": ["雲林", "嘉義", "台南"],
            "THB-5R": ["高雄", "屏東"],
            "THB-EO": ["宜蘭", "花蓮", "台東"]
        }
        
        if sub_authority_code in region_mapping:
            # 返回該區域的第一個主要縣市
            return region_mapping[sub_authority_code][0] + "市" if region_mapping[sub_authority_code][0] in ["基隆", "台北", "新北", "桃園", "台中", "台南", "高雄"] else region_mapping[sub_authority_code][0] + "縣"
        
        return '未知'

    def _filter_cameras(self, cameras, county=None, road_type=None):
        """篩選監視器資料"""
        filtered_cameras = []
        
        for cam in cameras:
            include_camera = True
            
            # 縣市篩選
            if county and include_camera:
                # 擴展縣市關鍵字對應
                county_keywords = {
                    '基隆': ['基隆', '暖暖', '七堵', '安樂', '中正', '仁愛', '信義'],
                    '台北': ['台北', '北市', '臺北', '大安', '中山', '信義', '松山', '中正', '萬華', '大同', '南港', '內湖', '士林', '北投', '文山', '木柵', '景美', '天母', '社子', '關渡'],
                    '新北': ['新北', '板橋', '三重', '中和', '永和', '新店', '新莊', '土城', '蘆洲', '樹林', '汐止', '鶯歌', '三峽', '淡水', '瑞芳', '五股', '泰山', '林口', '深坑', '石碇', '坪林', '三芝', '石門', '八里', '平溪', '雙溪', '貢寮', '金山', '萬里', '烏來', '中山', '重陽', '大華', '重新'],
                    '桃園': ['桃園', '中壢', '平鎮', '八德', '楊梅', '蘆竹', '大溪', '龜山', '大園', '觀音', '新屋', '復興', '龍潭', '青埔'],
                    '新竹': ['新竹', '竹北', '竹東', '新埔', '關西', '湖口', '新豐', '峨眉', '寶山', '北埔', '芎林', '橫山', '五峰', '尖石', '香山'],
                    '苗栗': ['苗栗', '頭份', '竹南', '後龍', '通霄', '苑裡', '三義', '西湖', '銅鑼', '南庄', '頭屋', '公館', '大湖', '泰安', '獅潭', '三灣', '造橋', '卓蘭'],
                    '台中': ['台中', '中市', '臺中', '豐原', '大里', '太平', '東勢', '梧棲', '烏日', '神岡', '大肚', '沙鹿', '龍井', '霧峰', '清水', '大甲', '外埔', '大安', '石岡', '新社', '和平', '潭子', '后里'],
                    '彰化': ['彰化', '員林', '和美', '鹿港', '溪湖', '二林', '田中', '北斗', '花壇', '芬園', '大村', '埔鹽', '埔心', '永靖', '社頭', '二水', '田尾', '埤頭', '芳苑', '大城', '竹塘', '溪州'],
                    '南投': ['南投', '埔里', '草屯', '竹山', '集集', '名間', '鹿谷', '中寮', '魚池', '國姓', '水里', '信義', '仁愛'],
                    '雲林': ['雲林', '斗六', '虎尾', '西螺', '土庫', '北港', '古坑', '大埤', '莿桐', '林內', '二崙', '崙背', '麥寮', '東勢', '褒忠', '台西', '元長', '四湖', '口湖', '水林'],
                    '嘉義': ['嘉義', '太保', '朴子', '布袋', '大林', '民雄', '溪口', '新港', '六腳', '東石', '義竹', '鹿草', '水上', '中埔', '竹崎', '梅山', '番路', '大埔', '阿里山'],
                    '台南': ['台南', '南市', '臺南', '永康', '歸仁', '新化', '左鎮', '玉井', '楠西', '南化', '仁德', '關廟', '龍崎', '官田', '麻豆', '佳里', '西港', '七股', '將軍', '學甲', '北門', '新營', '後壁', '白河', '東山', '六甲', '下營', '柳營', '鹽水', '善化', '大內', '山上', '新市', '安定', '安南', '中西', '東區', '南區', '北區', '安平'],
                    '高雄': ['高雄', '鳳山', '岡山', '旗山', '美濃', '橋頭', '梓官', '彌陀', '永安', '燕巢', '田寮', '阿蓮', '路竹', '湖內', '茄萣', '仁武', '大社', '鳥松', '大樹', '旗津', '前金', '苓雅', '鹽埕', '鼓山', '三民', '新興', '前鎮', '小港', '左營', '楠梓', '六龜', '內門', '杉林', '甲仙', '桃源', '那瑪夏', '茂林'],
                    '屏東': ['屏東', '潮州', '東港', '恆春', '萬丹', '長治', '麟洛', '九如', '里港', '鹽埔', '高樹', '萬巒', '內埔', '竹田', '新埤', '枋寮', '新園', '崁頂', '林邊', '南州', '佳冬', '琉球', '車城', '滿州', '枋山', '三地門', '霧台', '瑪家', '泰武', '來義', '春日', '獅子', '牡丹'],
                    '宜蘭': ['宜蘭', '羅東', '蘇澳', '頭城', '礁溪', '壯圍', '員山', '冬山', '五結', '三星', '大同', '南澳'],
                    '花蓮': ['花蓮', '鳳林', '玉里', '新城', '吉安', '壽豐', '光復', '豐濱', '瑞穗', '富里', '秀林', '萬榮', '卓溪'],
                    '台東': ['台東', '成功', '關山', '卑南', '大武', '太麻里', '東河', '長濱', '鹿野', '池上', '綠島', '延平', '海端', '達仁', '金峰', '蘭嶼']
                }
                
                # 取得查詢縣市的關鍵字
                search_keywords = county_keywords.get(county, [county])
                
                # 在監視器資料中搜尋
                search_text = f"{cam['name']} {cam['location_desc']} {cam['road']} {cam.get('county', '')}".lower()
                
                # 檢查是否包含任何關鍵字
                found_match = False
                for keyword in search_keywords:
                    if keyword.lower() in search_text:
                        found_match = True
                        break
                
                if not found_match:
                    include_camera = False
            
            # 道路類型篩選
            if road_type and include_camera:
                road_name = cam['road'].lower()
                if road_type.lower() not in road_name:
                    include_camera = False
            
            if include_camera:
                filtered_cameras.append(cam)
        
        return filtered_cameras

    async def _create_highway_camera_embed(self, camera, county, road_type, total_count, data_sources):
        """創建公路監視器 embed"""
        name = camera['name']
        road = camera['road']
        direction = camera['direction']
        video_url = camera['video_url']
        image_url = camera['image_url']
        mile = camera.get('mile', '')
        county_info = camera.get('county', '')
        update_time = camera.get('update_time', '')
        lat = camera.get('lat', '')
        lon = camera.get('lon', '')
        source = camera.get('source', '')
        
        # 創建 embed
        embed = discord.Embed(
            title="🛣️ 公路監視器",
            description=f"**{name}**",
            color=0x00aa00,
            timestamp=datetime.datetime.now()
        )
        
        # 顯示篩選條件
        filter_conditions = []
        if county:
            filter_conditions.append(f"縣市: {county}")
        if road_type:
            filter_conditions.append(f"道路: {road_type}")
        
        if filter_conditions:
            embed.add_field(
                name="🔍 篩選條件",
                value=" | ".join(filter_conditions),
                inline=False
            )
        
        # 道路資訊
        road_info = f"🛣️ **道路**: {road}"
        if direction:
            road_info += f" ({direction}向)"
        if mile:
            road_info += f"\n📏 **里程**: {mile}"
        
        embed.add_field(
            name="道路資訊",
            value=road_info,
            inline=True
        )
        
        # 位置資訊
        location_info = ""
        if lat and lon:
            location_info += f"📍 **座標**: {lat}, {lon}"
        if county_info:
            location_info += f"\n🏛️ **縣市**: {county_info}"
        
        if location_info:
            embed.add_field(
                name="位置資訊",
                value=location_info,
                inline=True
            )
        
        # 影像連結
        if video_url:
            embed.add_field(
                name="🎥 即時影像",
                value=f"[點擊觀看即時影像]({video_url})",
                inline=False
            )
        
        # 設定監視器快照圖片
        if image_url:
            # 加上時間戳避免快取
            timestamp = int(datetime.datetime.now().timestamp())
            cache_busted_url = f"{image_url}?t={timestamp}"
            embed.set_image(url=cache_busted_url)
        
        # 統計資訊
        source_text = " + ".join(data_sources) if data_sources else "混合資料"
        embed.add_field(
            name="📊 統計資訊",
            value=f"共找到 {total_count} 個符合條件的監視器\n目前顯示：隨機選擇的 1 個監視器\n資料來源：{source_text}",
            inline=False
        )
        
        # 更新時間資訊
        footer_text = f"資料來源：{source}"
        if update_time:
            footer_text += f" | 更新時間: {update_time}"
        embed.set_footer(text=footer_text)
        
        return embed

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