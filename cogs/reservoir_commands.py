#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水庫水情查詢指令
提供台灣水庫水情資訊查詢功能
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import json
import ssl
import asyncio
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ReservoirCommands(commands.Cog):
    """水庫水情查詢指令"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # 水庫 ID 對應表（部分主要水庫）
        self.reservoir_names = {
            "10501": "石門水庫",
            "10502": "新山水庫", 
            "10601": "寶山水庫",
            "10602": "寶山第二水庫",
            "10701": "永和山水庫",
            "10801": "明德水庫",
            "10901": "鯉魚潭水庫",
            "11001": "德基水庫",
            "11101": "石岡壩",
            "11201": "湖山水庫",
            "11401": "仁義潭水庫",
            "11501": "蘭潭水庫", 
            "11601": "白河水庫",
            "11701": "烏山頭水庫",
            "11801": "曾文水庫",
            "11901": "南化水庫",
            "12001": "阿公店水庫",
            "12101": "牡丹水庫",
            "20101": "翡翠水庫",
            "20201": "石門水庫後池",
            "30101": "日月潭水庫",
        }
    
    def _get_region_tag(self, reservoir_id):
        """根據水庫ID判斷地區"""
        try:
            if reservoir_id.startswith('105') or reservoir_id.startswith('201') or reservoir_id.startswith('202'):
                return "north"
            elif reservoir_id.startswith('106') or reservoir_id.startswith('107') or reservoir_id.startswith('108') or reservoir_id.startswith('109') or reservoir_id.startswith('110') or reservoir_id.startswith('111') or reservoir_id.startswith('301'):
                return "central"
            elif reservoir_id.startswith('112') or reservoir_id.startswith('114') or reservoir_id.startswith('115') or reservoir_id.startswith('116') or reservoir_id.startswith('117') or reservoir_id.startswith('118') or reservoir_id.startswith('119') or reservoir_id.startswith('120') or reservoir_id.startswith('121'):
                return "south"
            else:
                return "east"
        except:
            return "other"
    
    def _get_region_name(self, region_tag):
        """將地區標籤轉換為中文名稱"""
        region_names = {
            "north": "北部",
            "central": "中部", 
            "south": "南部",
            "east": "東部",
            "other": "其他"
        }
        return region_names.get(region_tag, "未知")

    async def get_reservoir_data(self):
        """取得水庫水情資料"""
        try:
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=1602CA19-B224-4CC3-AA31-11B1B124530F"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        # 處理 UTF-8 BOM 問題
                        text = await response.text()
                        if text.startswith('\ufeff'):
                            text = text[1:]
                        
                        data = json.loads(text)
                        return data.get('ReservoirConditionData_OPENDATA', [])
                    else:
                        logger.error(f"水庫 API 請求失敗: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"取得水庫資料時發生錯誤: {str(e)}")
            return None
    
    async def get_reservoir_operation_data(self):
        """取得水庫營運狀況資料"""
        try:
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=50C8256D-30C5-4B8D-9B84-2E14D5C6DF71"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        # 處理 UTF-8 BOM 問題
                        text = await response.text()
                        if text.startswith('\ufeff'):
                            text = text[1:]
                        
                        data = json.loads(text)
                        return data.get('DailyOperationalStatisticsOfReservoirs_OPENDATA', [])
                    else:
                        logger.error(f"水庫營運 API 請求失敗: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"取得水庫營運資料時發生錯誤: {str(e)}")
            return None

    
    def format_reservoir_info(self, reservoir_data):
        """格式化水庫資訊"""
        try:
            reservoir_id = reservoir_data.get('ReservoirIdentifier', '')
            reservoir_name = self.reservoir_names.get(reservoir_id, f"水庫 {reservoir_id}")
            
            # 取得數值資料
            water_level = reservoir_data.get('WaterLevel', '')
            effective_capacity = reservoir_data.get('EffectiveWaterStorageCapacity', '')
            inflow = reservoir_data.get('InflowDischarge', '')
            outflow = reservoir_data.get('TotalOutflow', '')
            observation_time = reservoir_data.get('ObservationTime', '')
            
            # 格式化觀測時間
            if observation_time:
                try:
                    dt = datetime.fromisoformat(observation_time)
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_time = observation_time
            else:
                formatted_time = "資料不足"
            
            return {
                'name': reservoir_name,
                'id': reservoir_id,
                'water_level': water_level if water_level else "N/A",
                'capacity': effective_capacity if effective_capacity else "N/A", 
                'inflow': inflow if inflow else "N/A",
                'outflow': outflow if outflow else "N/A",
                'time': formatted_time
            }
            
        except Exception as e:
            logger.error(f"格式化水庫資訊時發生錯誤: {str(e)}")
            return None
    
    def format_reservoir_operation_info(self, operation_data):
        """格式化水庫營運資訊"""
        try:
            reservoir_name = operation_data.get('ReservoirName', 'N/A')
            reservoir_id = operation_data.get('ReservoirIdentifier', '')
            
            # 取得營運數值資料
            capacity = operation_data.get('Capacity', '')  # 蓄水量 (萬立方公尺)
            dwl = operation_data.get('DWL', '')  # 水位 (公尺)
            inflow = operation_data.get('Inflow', '')  # 流入量
            outflow_total = operation_data.get('OutflowTotal', '')  # 總流出量
            basin_rainfall = operation_data.get('BasinRainfall', '')  # 集水區降雨量
            cross_flow = operation_data.get('CrossFlow', '')  # 越域引水
            nwl_max = operation_data.get('NWLMax', '')  # 滿水位
            date_time = operation_data.get('DateTime', '')
            
            # 格式化時間
            if date_time:
                try:
                    dt = datetime.fromisoformat(date_time)
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_time = date_time
            else:
                formatted_time = "資料不足"
            
            # 計算蓄水率（如果有滿水位資料）
            percentage = "N/A"
            if capacity and dwl and nwl_max:
                try:
                    capacity_val = float(capacity) if capacity else 0
                    dwl_val = float(dwl) if dwl else 0
                    nwl_max_val = float(nwl_max) if nwl_max else 0
                    if nwl_max_val > 0:
                        percentage = f"{(dwl_val / nwl_max_val * 100):.1f}"
                except:
                    pass
            
            return {
                'name': reservoir_name,
                'id': reservoir_id,
                'capacity': capacity if capacity else "N/A",  # 蓄水量
                'water_level': dwl if dwl else "N/A",  # 水位
                'percentage': percentage,  # 蓄水率
                'inflow': inflow if inflow else "N/A",  # 流入量
                'outflow': outflow_total if outflow_total else "N/A",  # 流出量
                'rainfall': basin_rainfall if basin_rainfall else "N/A",  # 降雨量
                'cross_flow': cross_flow if cross_flow else "N/A",  # 越域引水
                'max_level': nwl_max if nwl_max else "N/A",  # 滿水位
                'time': formatted_time
            }
            
        except Exception as e:
            logger.error(f"格式化水庫營運資訊時發生錯誤: {str(e)}")
            return None

    def format_reservoir_basic_info(self, basic_data):
        """格式化水庫基本資訊"""
        try:
            reservoir_name = basic_data.get('ReservoirName', 'N/A')
            reservoir_id = basic_data.get('ReservoirIdentifier', '')
            
            # 取得基本資料
            area = basic_data.get('Area', '')  # 地區
            river_name = basic_data.get('RiverName', '')  # 河川名稱
            town_name = basic_data.get('TownName', '')  # 所在地
            dam_type = basic_data.get('Type', '')  # 壩型
            height = basic_data.get('Height', '')  # 壩高
            length = basic_data.get('Length', '')  # 壩長
            drainage_area = basic_data.get('DrainageArea', '')  # 集水面積
            designed_capacity = basic_data.get('DesignedCapacity', '')  # 設計容量
            current_capacity = basic_data.get('CurruntCapacity', '')  # 現有容量
            application = basic_data.get('Application', '')  # 用途
            agency_name = basic_data.get('AgencyName', '')  # 管理機關
            
            return {
                'name': reservoir_name,
                'id': reservoir_id,
                'area': area if area else "N/A",
                'river': river_name if river_name else "N/A",
                'location': town_name if town_name else "N/A",
                'dam_type': dam_type if dam_type else "N/A",
                'height': height if height else "N/A",
                'length': length if length else "N/A",
                'drainage_area': drainage_area if drainage_area else "N/A",
                'designed_capacity': designed_capacity if designed_capacity else "N/A",
                'current_capacity': current_capacity if current_capacity else "N/A",
                'application': application if application else "N/A",
                'agency': agency_name if agency_name else "N/A"
            }
            
        except Exception as e:
            logger.error(f"格式化水庫基本資訊時發生錯誤: {str(e)}")
            return None

    def format_water_image_info(self, image_data):
        """格式化水利防災影像資訊 - 增強圖片 URL 處理"""
        try:
            station_name = image_data.get('VideoSurveillanceStationName', 'N/A')
            camera_name = image_data.get('CameraName', 'N/A') 
            location = image_data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
            district = image_data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
            address = image_data.get('VideoSurveillanceStationAddress', '')
            basin_name = image_data.get('BasinName', '')
            tributary = image_data.get('TRIBUTARY', '')
            image_url = image_data.get('ImageURL', '')
            status = image_data.get('Status', '')
            latitude = image_data.get('latitude_4326', '')
            longitude = image_data.get('Longitude_4326', '')
            station_id = image_data.get('VideoSurveillanceStationId', image_data.get('StationID', 'N/A'))
            
            # 縣市名稱標準化
            normalized_county = self._normalize_county_name(location)
            
            # 地址處理 - 如果沒有地址，嘗試組合縣市和區域
            if not address:
                if location and district:
                    full_location = f"{location}{district}"
                else:
                    full_location = location or district or "N/A"
            else:
                full_location = address
            
            # 組合河川資訊
            river_info = f"{basin_name}" if basin_name else "N/A"
            if tributary and tributary != basin_name:
                river_info += f" ({tributary})"
            
            # 增強的影像 URL 處理
            processed_image_url = self._process_and_validate_image_url(image_url)
            
            return {
                'station_name': station_name,
                'camera_name': camera_name if camera_name != 'N/A' else '主攝影機',
                'location': full_location,
                'county': normalized_county,  # 使用標準化的縣市名稱
                'district': district or 'N/A',
                'address': full_location,
                'station_id': station_id,
                'source': '水利防災',
                'river': river_info,
                'image_url': processed_image_url,
                'status': "正常" if status == "1" else "異常" if status == "0" else "未知",
                'coordinates': f"{latitude}, {longitude}" if latitude and longitude else "N/A"
            }
            
        except Exception as e:
            logger.error(f"格式化水利防災影像資訊時發生錯誤: {str(e)}")
            return None
    
    def _process_and_validate_image_url(self, image_url):
        """處理和驗證圖片 URL - 增強版本（帶快取破壞）"""
        if not image_url or not image_url.strip() or str(image_url).lower() == 'none':
            return "N/A"
        
        processed_url = str(image_url).strip()
        
        # 移除可能的空白字符和特殊字符
        processed_url = processed_url.replace(' ', '').replace('\n', '').replace('\r', '')
        
        # 如果已經是完整的 HTTP/HTTPS URL，加上時間戳避免快取
        if processed_url.startswith(('http://', 'https://')):
            final_url = self._add_timestamp_to_url(processed_url)
            return final_url
        
        # 如果以 // 開頭，添加 https: 並加上時間戳
        elif processed_url.startswith('//'):
            full_url = 'https:' + processed_url
            return self._add_timestamp_to_url(full_url)
        
        # 如果以 / 開頭，添加基礎域名並加上時間戳
        elif processed_url.startswith('/'):
            # 優先使用 alerts.ncdr.nat.gov.tw，因為很多水利防災影像在那裡
            base_urls = [
                'https://alerts.ncdr.nat.gov.tw',
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


# View 和 Modal 類別
class WaterCameraView(discord.ui.View):
    """水利監視器切換視圖"""
    def __init__(self, cameras, current_index):
        super().__init__(timeout=300)
        self.cameras = cameras
        self.current_index = current_index
        self.update_buttons()
    
    def update_buttons(self):
        """更新按鈕狀態"""
        self.previous_camera.disabled = self.current_index == 0
        self.next_camera.disabled = self.current_index == len(self.cameras) - 1
    
    @discord.ui.button(label="◀️ 上一個", style=discord.ButtonStyle.primary)
    async def previous_camera(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            
            # 建立新的 embed
            embed = await self._create_water_camera_embed(self.cameras[self.current_index])
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="▶️ 下一個", style=discord.ButtonStyle.primary)
    async def next_camera(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index < len(self.cameras) - 1:
            self.current_index += 1
            self.update_buttons()
            
            # 建立新的 embed
            embed = await self._create_water_camera_embed(self.cameras[self.current_index])
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="ℹ️ 詳細資訊", style=discord.ButtonStyle.secondary)
    async def show_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = WaterCameraInfoModal(self.cameras[self.current_index])
        await interaction.response.send_modal(modal)
    
    async def _create_water_camera_embed(self, camera_data):
        """建立水利監視器 embed"""
        try:
            station_name = camera_data.get('VideoSurveillanceStationName', '未知監控站')
            county = self._normalize_county_name(camera_data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', ''))
            district = camera_data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
            
            # 建立標題
            title = f"📹 {station_name}"
            
            # 建立 embed
            embed = discord.Embed(
                title=title,
                color=0x00bfff
            )
            
            # 添加位置資訊
            location_info = f"{county}"
            if district:
                location_info += f" {district}"
            embed.add_field(name="📍 位置", value=location_info, inline=True)
            
            # 處理圖片URL（加上時間戳避免快取）
            image_url = camera_data.get('VideoURL', '')
            if image_url:
                processed_url = self._process_and_validate_image_url(image_url)
                embed.set_image(url=processed_url)
            
            # 添加時間戳
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"💧 水利防災監控系統 ({self.current_index + 1}/{len(self.cameras)})")
            
            return embed
            
        except Exception as e:
            logger.error(f"建立水利監視器 embed 時發生錯誤: {str(e)}")
            return discord.Embed(
                title="❌ 資料處理錯誤",
                description="無法處理監視器資料",
                color=0xff0000
            )
    
    def _process_and_validate_image_url(self, url):
        """處理和驗證圖片URL，加上時間戳避免快取"""
        if not url:
            return url
        
        # 加上時間戳參數避免快取
        timestamp = int(time.time())
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}t={timestamp}"
    
    def _normalize_county_name(self, location_str):
        """標準化縣市名稱"""
        if not location_str:
            return location_str
        
        # 縣市名稱對應表
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
            '臺東': '台東縣', '澎湖': '澎湖縣',
            '金門': '金門縣', '連江': '連江縣'
        }
        
        # 嘗試匹配縣市名稱
        for key, value in county_mapping.items():
            if key in location_str:
                return value
        
        return location_str

class WaterCameraInfoModal(discord.ui.Modal):
    """水利監視器詳細資訊模態框"""
    def __init__(self, camera_data):
        super().__init__(title="監視器詳細資訊")
        self.camera_data = camera_data
    
    async def on_submit(self, interaction: discord.Interaction):
        """提交時顯示詳細資訊"""
        try:
            station_name = self.camera_data.get('VideoSurveillanceStationName', '未知監控站')
            county = self.camera_data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
            district = self.camera_data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
            
            embed = discord.Embed(
                title=f"📋 {station_name} - 詳細資訊",
                color=0x00bfff
            )
            
            embed.add_field(name="🏢 監控站名稱", value=station_name, inline=False)
            embed.add_field(name="🌏 所在縣市", value=county, inline=True)
            embed.add_field(name="📍 行政區域", value=district or "未提供", inline=True)
            
            # 添加其他可用資訊
            for key, value in self.camera_data.items():
                if key not in ['VideoSurveillanceStationName', 'CountiesAndCitiesWhereTheMonitoringPointsAreLocated', 
                              'AdministrativeDistrictWhereTheMonitoringPointIsLocated', 'VideoURL']:
                    if value:
                        embed.add_field(name=key, value=str(value), inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"顯示水利監視器詳細資訊時發生錯誤: {str(e)}")
            await interaction.response.send_message("❌ 無法顯示詳細資訊", ephemeral=True)

class HighwayCameraView(discord.ui.View):
    """公路監視器切換視圖"""
    
    def __init__(self, cameras, normalize_func):
        super().__init__(timeout=300)
        self.cameras = cameras
        self.current_index = 0
        self.total_cameras = len(cameras)
        self.normalize_func = normalize_func
    
    @discord.ui.button(label="⬅️ 上一個", style=discord.ButtonStyle.primary)
    async def previous_camera(self, interaction: discord.Interaction, button: discord.ui.Button):
        """切換到上一個監視器"""
        try:
            self.current_index = (self.current_index - 1) % self.total_cameras
            embed = await self._create_highway_camera_embed(self.cameras[self.current_index])
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            logger.error(f"切換上一個公路監視器時發生錯誤: {str(e)}")
            await interaction.response.send_message("切換時發生錯誤", ephemeral=True)
    
    @discord.ui.button(label="➡️ 下一個", style=discord.ButtonStyle.primary)
    async def next_camera(self, interaction: discord.Interaction, button: discord.ui.Button):
        """切換到下一個監視器"""
        try:
            self.current_index = (self.current_index + 1) % self.total_cameras
            embed = await self._create_highway_camera_embed(self.cameras[self.current_index])
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            logger.error(f"切換下一個公路監視器時發生錯誤: {str(e)}")
            await interaction.response.send_message("切換時發生錯誤", ephemeral=True)
    
    @discord.ui.button(label="ℹ️ 詳細資訊", style=discord.ButtonStyle.secondary)
    async def show_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """顯示詳細資訊"""
        try:
            camera = self.cameras[self.current_index]
            modal = HighwayCameraInfoModal(camera, self.current_index + 1, self.total_cameras, self.normalize_func)
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"顯示公路監視器詳細資訊時發生錯誤: {str(e)}")
            await interaction.response.send_message("顯示詳細資訊時發生錯誤", ephemeral=True)
    
    async def _create_highway_camera_embed(self, camera_data):
        """建立公路監視器嵌入訊息"""
        try:
            road_name = camera_data.get('RoadName', '未知道路')
            location_city = self.normalize_func(camera_data.get('LocationCityName', ''))
            location_district = camera_data.get('LocationDistrictName', '')
            direction = camera_data.get('RoadDirection', '')
            
            # 方向對應
            direction_map = {
                'N': '北向', 'S': '南向', 'E': '東向', 'W': '西向',
                '0': '北向', '1': '南向', '2': '東向', '3': '西向'
            }
            direction_text = direction_map.get(direction, direction)
            
            # 分類道路類型
            road_type = self._classify_road_type(camera_data)
            
            embed = discord.Embed(
                title=f"🛣️ {road_type}監視器 ({self.current_index + 1}/{self.total_cameras})",
                color=0x00ff00
            )
            
            embed.add_field(name="📍 道路", value=road_name, inline=True)
            embed.add_field(name="🗺️ 位置", value=f"{location_city}{location_district}", inline=True)
            embed.add_field(name="🧭 方向", value=direction_text, inline=True)
            
            # 處理圖片URL
            image_url = camera_data.get('ImageUrl', '')
            if image_url and image_url != "N/A":
                # 添加時間戳避免快取
                image_url = self._add_timestamp_to_url(image_url)
                embed.set_image(url=image_url)
            else:
                embed.add_field(name="⚠️ 注意", value="目前無法取得影像", inline=False)
            
            embed.set_footer(text="資料來源：交通部公路總局")
            
            return embed
            
        except Exception as e:
            logger.error(f"建立公路監視器嵌入訊息時發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 錯誤",
                description="建立訊息時發生錯誤",
                color=0xff0000
            )
            return embed
    
    def _classify_road_type(self, camera_data):
        """分類道路類型"""
        road_name = camera_data.get('RoadName', '').lower()
        road_class = camera_data.get('RoadClass', '').lower()
        
        # 國道判斷
        if ('國道' in road_name or 'freeway' in road_name or 
            '國1' in road_name or '國3' in road_name or
            'national' in road_class):
            return "國道"
        
        # 快速公路判斷
        if ('快速' in road_name or 'expressway' in road_name or
            '台61' in road_name or '台62' in road_name or '台64' in road_name):
            return "快速公路"
        
        # 省道判斷
        if ('台' in road_name and '線' in road_name):
            return "省道"
        
        return "一般道路"
    

class HighwayCameraInfoModal(discord.ui.Modal):
    """公路監視器詳細資訊彈窗"""
    
    def __init__(self, camera_data, current_num, total_num, normalize_func):
        super().__init__(title=f"🛣️ 公路監視器詳細資訊 ({current_num}/{total_num})")
        self.camera_data = camera_data
        self.normalize_func = normalize_func
        
        # 格式化詳細資訊
        info_text = self._format_highway_camera_info(camera_data)
        
        # 添加文字輸入框顯示資訊
        self.info_input = discord.ui.TextInput(
            label="監視器詳細資訊",
            style=discord.TextStyle.paragraph,
            default=info_text,
            max_length=4000,
            required=False
        )
        self.add_item(self.info_input)
    
    def _format_highway_camera_info(self, camera_data):
        """格式化公路監視器詳細資訊"""
        try:
            road_name = camera_data.get('RoadName', 'N/A')
            road_class = camera_data.get('RoadClass', 'N/A')
            road_id = camera_data.get('RoadID', 'N/A')
            location_city = self.normalize_func(camera_data.get('LocationCityName', 'N/A'))
            location_district = camera_data.get('LocationDistrictName', 'N/A')
            direction = camera_data.get('RoadDirection', 'N/A')
            camera_id = camera_data.get('CameraID', 'N/A')
            
            # 方向對應
            direction_map = {
                'N': '北向', 'S': '南向', 'E': '東向', 'W': '西向',
                '0': '北向', '1': '南向', '2': '東向', '3': '西向'
            }
            direction_text = direction_map.get(direction, direction)
            
            info_lines = [
                f"📍 道路名稱：{road_name}",
                f"🏷️ 道路分類：{road_class}",
                f"🆔 道路代碼：{road_id}",
                f"🗺️ 所在縣市：{location_city}",
                f"🏘️ 所在區域：{location_district}",
                f"🧭 行車方向：{direction_text}",
                f"📹 監視器ID：{camera_id}",
                f"⏰ 查詢時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            
            return '\n'.join(info_lines)
            
        except Exception as e:
            logger.error(f"格式化公路監視器資訊時發生錯誤: {str(e)}")
            return "格式化資訊時發生錯誤"
    
    async def on_submit(self, interaction: discord.Interaction):
        """提交時的處理"""
        await interaction.response.send_message("資訊已關閉", ephemeral=True, delete_after=1)

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
        app_commands.Choice(name="新竹市", value="新竹市"),
        app_commands.Choice(name="新竹縣", value="新竹縣"),
        app_commands.Choice(name="苗栗", value="苗栗"),
        app_commands.Choice(name="台中", value="台中"),
        app_commands.Choice(name="彰化", value="彰化"),
        app_commands.Choice(name="南投", value="南投"),
        app_commands.Choice(name="雲林", value="雲林"),
        app_commands.Choice(name="嘉義市", value="嘉義市"),
        app_commands.Choice(name="嘉義縣", value="嘉義縣"),
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
    async def water_level(self, interaction: discord.Interaction, city: str = None, river: str = None, station: str = None):
        """查詢全台河川水位資料"""
        try:
            await interaction.response.defer()
            
            # 獲取水位資料
            water_data = await self.get_water_level_data()
            if not water_data:
                embed = discord.Embed(
                    title="❌ 資料取得失敗",
                    description="無法取得水位資料，請稍後再試。",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 篩選資料
            filtered_data = []
            
            for data in water_data:
                # 縣市篩選
                if city:
                    normalized_city = self._normalize_county_name(city)
                    station_town = self._normalize_county_name(data.get('StationTown', ''))
                    if normalized_city.lower() not in station_town.lower():
                        continue
                
                # 河川篩選
                if river:
                    basin_name = data.get('BasinName', '')
                    if river.lower() not in basin_name.lower():
                        continue
                
                # 測站篩選
                if station:
                    station_name = data.get('StationName', '')
                    if station.lower() not in station_name.lower():
                        continue
                
                filtered_data.append(data)
            
            if not filtered_data:
                condition_text = []
                if city:
                    condition_text.append(f"{city}")
                if river:
                    condition_text.append(f"{river}")
                if station:
                    condition_text.append(f"{station}")
                conditions = "、".join(condition_text) if condition_text else "指定條件"
                
                embed = discord.Embed(
                    title="🔍 查無資料",
                    description=f"找不到符合「{conditions}」的水位測站。",
                    color=0xffa500
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 限制顯示數量
            display_data = filtered_data[:10]
            
            # 建立回應
            embed = discord.Embed(
                title="🌊 河川水位資料",
                color=0x0099ff
            )
            
            if len(display_data) == 1:
                # 單一測站詳細資訊
                station_data = display_data[0]
                self._add_water_level_fields(embed, station_data)
            else:
                # 多個測站概覽
                for i, station_data in enumerate(display_data):
                    station_name = station_data.get('StationName', 'N/A')
                    basin_name = station_data.get('BasinName', 'N/A')
                    station_town = self._normalize_county_name(station_data.get('StationTown', 'N/A'))
                    water_level = station_data.get('WaterLevel', 'N/A')
                    
                    field_name = f"📍 {station_name} ({station_town})"
                    field_value = f"河川：{basin_name}\n水位：{water_level} 公尺"
                    
                    embed.add_field(name=field_name, value=field_value, inline=True)
            
            if len(filtered_data) > 10:
                embed.set_footer(text=f"顯示前10筆，共找到 {len(filtered_data)} 筆資料")
            else:
                embed.set_footer(text=f"共 {len(filtered_data)} 筆資料")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"水位查詢錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 系統錯誤",
                description="查詢水位資料時發生錯誤，請稍後再試。",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)

    async def get_water_level_data(self):
        """取得水位資料"""
        try:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
            
            # 設定SSL上下文以解決證書問題
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 設定連接器和超時
            connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                logger.info(f"正在獲取水位資料...")
                
                # 設定請求標頭
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache'
                }
                
                async with session.get(url, headers=headers, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"成功獲取 {len(data)} 筆水位資料")
                        return data
                    else:
                        logger.error(f"水位資料 API 回應錯誤: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"獲取水位資料時發生錯誤: {str(e)}")
            return []

    def _add_water_level_fields(self, embed, station_data):
        """添加水位資料欄位到 embed"""
        try:
            station_name = station_data.get('StationName', 'N/A')
            basin_name = station_data.get('BasinName', 'N/A')
            station_town = self._normalize_county_name(station_data.get('StationTown', 'N/A'))
            water_level = station_data.get('WaterLevel', 'N/A')
            alert_level = station_data.get('AlertLevel', 'N/A')
            warning_level = station_data.get('WarningLevel', 'N/A')
            dangerous_level = station_data.get('DangerousLevel', 'N/A')
            
            embed.add_field(name="📍 測站名稱", value=station_name, inline=True)
            embed.add_field(name="🏞️ 河川流域", value=basin_name, inline=True)
            embed.add_field(name="🗺️ 所在縣市", value=station_town, inline=True)
            
            embed.add_field(name="🌊 目前水位", value=f"{water_level} 公尺", inline=True)
            embed.add_field(name="⚠️ 警戒水位", value=f"{alert_level} 公尺", inline=True)
            embed.add_field(name="🚨 危險水位", value=f"{dangerous_level} 公尺", inline=True)
            
            # 水位狀態評估
            try:
                current_level = float(water_level) if water_level != 'N/A' else 0
                danger_level = float(dangerous_level) if dangerous_level != 'N/A' else float('inf')
                alert_level_num = float(alert_level) if alert_level != 'N/A' else float('inf')
                
                if current_level >= danger_level:
                    status = "🚨 危險"
                    color = 0xff0000
                elif current_level >= alert_level_num:
                    status = "⚠️ 警戒"
                    color = 0xffa500
                else:
                    status = "✅ 正常"
                    color = 0x00ff00
                
                embed.add_field(name="📊 水位狀態", value=status, inline=True)
                embed.color = color
                
            except (ValueError, TypeError):
                embed.add_field(name="📊 水位狀態", value="資料不完整", inline=True)
            
        except Exception as e:
            logger.error(f"添加水位資料欄位時發生錯誤: {str(e)}")

    @app_commands.command(name="water_cameras", description="查詢水利防災監控影像")
    @app_commands.describe(
        city="選擇縣市",
        location="監控站名稱（可選）"
    )
    @app_commands.choices(city=[
        app_commands.Choice(name="基隆市", value="基隆"),
        app_commands.Choice(name="台北市", value="台北"),
        app_commands.Choice(name="新北市", value="新北"),
        app_commands.Choice(name="桃園市", value="桃園"),
        app_commands.Choice(name="新竹市", value="新竹市"),
        app_commands.Choice(name="新竹縣", value="新竹縣"),
        app_commands.Choice(name="苗栗縣", value="苗栗"),
        app_commands.Choice(name="台中市", value="台中"),
        app_commands.Choice(name="彰化縣", value="彰化"),
        app_commands.Choice(name="南投縣", value="南投"),
        app_commands.Choice(name="雲林縣", value="雲林"),
        app_commands.Choice(name="嘉義市", value="嘉義市"),
        app_commands.Choice(name="嘉義縣", value="嘉義縣"),
        app_commands.Choice(name="台南市", value="台南"),
        app_commands.Choice(name="高雄市", value="高雄"),
        app_commands.Choice(name="屏東縣", value="屏東"),
        app_commands.Choice(name="宜蘭縣", value="宜蘭"),
        app_commands.Choice(name="花蓮縣", value="花蓮"),
        app_commands.Choice(name="台東縣", value="台東"),
        app_commands.Choice(name="澎湖縣", value="澎湖"),
        app_commands.Choice(name="金門縣", value="金門"),
        app_commands.Choice(name="連江縣", value="連江")
    ])
    async def water_cameras(self, interaction: discord.Interaction, city: str = None, location: str = None):
        """查詢水利防災監控影像"""
        try:
            await interaction.response.defer()
            
            # 取得水利防災影像資料
            image_data = await self.get_water_disaster_images()
            
            if not image_data:
                embed = discord.Embed(
                    title="❌ 無法取得水利防災影像資料",
                    description="請稍後再試，或聯繫管理員。",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 篩選資料
            filtered_data = []
            
            if city:
                city_lower = city.lower()
                for data in image_data:
                    loc = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
                    district = data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
                    station_name = data.get('VideoSurveillanceStationName', '')
                    
                    if (city_lower in loc.lower() or 
                        city_lower in district.lower() or
                        city_lower in station_name.lower()):
                        filtered_data.append(data)
            
            if location:
                location_lower = location.lower()
                temp_data = filtered_data if filtered_data else image_data
                filtered_data = []
                for data in temp_data:
                    station_name = data.get('VideoSurveillanceStationName', '')
                    if location_lower in station_name.lower():
                        filtered_data.append(data)
            
            if not city and not location:
                filtered_data = image_data
            
            if not filtered_data:
                embed = discord.Embed(
                    title="🔍 查無相關監控點",
                    description=f"找不到符合條件的監控點：{city or ''} {location or ''}",
                    color=0xffa500
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 建立第一個監控點的 embed
            first_camera = filtered_data[0]
            embed = await self._create_water_camera_embed(first_camera)
            
            # 如果有多個監控點，使用 View 來切換
            if len(filtered_data) > 1:
                view = WaterCameraView(filtered_data, 0)
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"查詢水利監控影像時發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 查詢失敗",
                description="查詢水利防災影像時發生錯誤，請稍後再試。",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="national_highway_cameras", description="查詢國道監視器")
    @app_commands.describe(
        highway_number="國道號碼",
        city="選擇縣市",
        direction="行車方向",
        location="地點名稱（可選）"
    )
    @app_commands.choices(
        highway_number=[
            app_commands.Choice(name="國道1號", value="1"),
            app_commands.Choice(name="國道3號", value="3"),
            app_commands.Choice(name="國道5號", value="5"),
            app_commands.Choice(name="國道6號", value="6"),
            app_commands.Choice(name="國道8號", value="8"),
            app_commands.Choice(name="國道10號", value="10")
        ],
        city=[
            app_commands.Choice(name="基隆市", value="基隆"),
            app_commands.Choice(name="台北市", value="台北"),
            app_commands.Choice(name="新北市", value="新北"),
            app_commands.Choice(name="桃園市", value="桃園"),
            app_commands.Choice(name="新竹市", value="新竹市"),
            app_commands.Choice(name="新竹縣", value="新竹縣"),
            app_commands.Choice(name="苗栗縣", value="苗栗"),
            app_commands.Choice(name="台中市", value="台中"),
            app_commands.Choice(name="彰化縣", value="彰化"),
            app_commands.Choice(name="南投縣", value="南投"),
            app_commands.Choice(name="雲林縣", value="雲林"),
            app_commands.Choice(name="嘉義市", value="嘉義市"),
            app_commands.Choice(name="嘉義縣", value="嘉義縣"),
            app_commands.Choice(name="台南市", value="台南"),
            app_commands.Choice(name="高雄市", value="高雄"),
            app_commands.Choice(name="屏東縣", value="屏東"),
            app_commands.Choice(name="宜蘭縣", value="宜蘭"),
            app_commands.Choice(name="花蓮縣", value="花蓮"),
            app_commands.Choice(name="台東縣", value="台東")
        ],
        direction=[
            app_commands.Choice(name="北向", value="北向"),
            app_commands.Choice(name="南向", value="南向"),
            app_commands.Choice(name="東向", value="東向"),
            app_commands.Choice(name="西向", value="西向")
        ]
    )
    async def national_highway_cameras(self, interaction: discord.Interaction, 
                                     highway_number: str = None, 
                                     city: str = None, 
                                     direction: str = None, 
                                     location: str = None):
        """查詢國道監視器"""
        try:
            await interaction.response.defer()
            
            # 取得公路監視器資料
            camera_data = await self._get_highway_cameras()
            
            if not camera_data:
                embed = discord.Embed(
                    title="❌ 無法取得國道監視器資料",
                    description="請稍後再試，或聯繫管理員。",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 篩選國道監視器
            national_cameras = []
            for camera in camera_data:
                road_type = self._classify_road_type(camera.get('RoadName', ''))
                if road_type == '國道':
                    national_cameras.append(camera)
            
            # 進一步篩選
            filtered_cameras = national_cameras
            
            if highway_number:
                filtered_cameras = [
                    cam for cam in filtered_cameras 
                    if highway_number in cam.get('RoadName', '')
                ]
            
            if city:
                city_lower = city.lower()
                filtered_cameras = [
                    cam for cam in filtered_cameras
                    if (city_lower in cam.get('LocationDescription', '').lower() or
                        city_lower in self._normalize_county_name(cam.get('LocationDescription', '')).lower())
                ]
            
            if direction:
                filtered_cameras = [
                    cam for cam in filtered_cameras
                    if direction in cam.get('RoadDirection', '')
                ]
            
            if location:
                location_lower = location.lower()
                filtered_cameras = [
                    cam for cam in filtered_cameras
                    if location_lower in cam.get('LocationDescription', '').lower()
                ]
            
            if not filtered_cameras:
                embed = discord.Embed(
                    title="🔍 查無相關國道監視器",
                    description="找不到符合條件的國道監視器",
                    color=0xffa500
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 建立第一個監視器的 embed
            first_camera = filtered_cameras[0]
            embed = await self._create_highway_camera_embed(first_camera)
            
            # 如果有多個監視器，使用 View 來切換
            if len(filtered_cameras) > 1:
                view = HighwayCameraView(filtered_cameras, 0)
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"查詢國道監視器時發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 查詢失敗",
                description="查詢國道監視器時發生錯誤，請稍後再試。",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="general_road_cameras", description="查詢一般道路監視器")
    @app_commands.describe(
        road_type="道路類型",
        city="選擇縣市",
        location="地點名稱（可選）"
    )
    @app_commands.choices(
        road_type=[
            app_commands.Choice(name="省道", value="省道"),
            app_commands.Choice(name="縣道", value="縣道"),
            app_commands.Choice(name="快速公路", value="快速公路"),
            app_commands.Choice(name="市區道路", value="市區道路")
        ],
        city=[
            app_commands.Choice(name="基隆市", value="基隆"),
            app_commands.Choice(name="台北市", value="台北"),
            app_commands.Choice(name="新北市", value="新北"),
            app_commands.Choice(name="桃園市", value="桃園"),
            app_commands.Choice(name="新竹市", value="新竹市"),
            app_commands.Choice(name="新竹縣", value="新竹縣"),
            app_commands.Choice(name="苗栗縣", value="苗栗"),
            app_commands.Choice(name="台中市", value="台中"),
            app_commands.Choice(name="彰化縣", value="彰化"),
            app_commands.Choice(name="南投縣", value="南投"),
            app_commands.Choice(name="雲林縣", value="雲林"),
            app_commands.Choice(name="嘉義市", value="嘉義市"),
            app_commands.Choice(name="嘉義縣", value="嘉義縣"),
            app_commands.Choice(name="台南市", value="台南"),
            app_commands.Choice(name="高雄市", value="高雄"),
            app_commands.Choice(name="屏東縣", value="屏東"),
            app_commands.Choice(name="宜蘭縣", value="宜蘭"),
            app_commands.Choice(name="花蓮縣", value="花蓮"),
            app_commands.Choice(name="台東縣", value="台東")
        ]
    )
    async def general_road_cameras(self, interaction: discord.Interaction, 
                                 road_type: str = None, 
                                 city: str = None, 
                                 location: str = None):
        """查詢一般道路監視器"""
        try:
            await interaction.response.defer()
            
            # 取得公路監視器資料
            camera_data = await self._get_highway_cameras()
            
            if not camera_data:
                embed = discord.Embed(
                    title="❌ 無法取得道路監視器資料",
                    description="請稍後再試，或聯繫管理員。",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 篩選非國道監視器
            general_cameras = []
            for camera in camera_data:
                road_class = self._classify_road_type(camera.get('RoadName', ''))
                if road_class != '國道':
                    general_cameras.append(camera)
            
            # 進一步篩選
            filtered_cameras = general_cameras
            
            if road_type:
                filtered_cameras = [
                    cam for cam in filtered_cameras
                    if self._classify_road_type(cam.get('RoadName', '')) == road_type
                ]
            
            if city:
                city_lower = city.lower()
                filtered_cameras = [
                    cam for cam in filtered_cameras
                    if (city_lower in cam.get('LocationDescription', '').lower() or
                        city_lower in self._normalize_county_name(cam.get('LocationDescription', '')).lower())
                ]
            
            if location:
                location_lower = location.lower()
                filtered_cameras = [
                    cam for cam in filtered_cameras
                    if location_lower in cam.get('LocationDescription', '').lower()
                ]
            
            if not filtered_cameras:
                embed = discord.Embed(
                    title="🔍 查無相關道路監視器",
                    description="找不到符合條件的道路監視器",
                    color=0xffa500
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 建立第一個監視器的 embed
            first_camera = filtered_cameras[0]
            embed = await self._create_highway_camera_embed(first_camera)
            
            # 如果有多個監視器，使用 View 來切換
            if len(filtered_cameras) > 1:
                view = HighwayCameraView(filtered_cameras, 0)
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"查詢道路監視器時發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 查詢失敗",
                description="查詢道路監視器時發生錯誤，請稍後再試。",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="water_disaster_cameras", description="查詢水利防災監控影像（舊版相容）")
    @app_commands.describe(
        city="選擇縣市",
        location="監控站名稱（可選）"
    )
    @app_commands.choices(city=[
        app_commands.Choice(name="基隆市", value="基隆"),
        app_commands.Choice(name="台北市", value="台北"),
        app_commands.Choice(name="新北市", value="新北"),
        app_commands.Choice(name="桃園市", value="桃園"),
        app_commands.Choice(name="新竹市", value="新竹市"),
        app_commands.Choice(name="新竹縣", value="新竹縣"),
        app_commands.Choice(name="苗栗縣", value="苗栗"),
        app_commands.Choice(name="台中市", value="台中"),
        app_commands.Choice(name="彰化縣", value="彰化"),
        app_commands.Choice(name="南投縣", value="南投"),
        app_commands.Choice(name="雲林縣", value="雲林"),
        app_commands.Choice(name="嘉義市", value="嘉義市"),
        app_commands.Choice(name="嘉義縣", value="嘉義縣"),
        app_commands.Choice(name="台南市", value="台南"),
        app_commands.Choice(name="高雄市", value="高雄"),
        app_commands.Choice(name="屏東縣", value="屏東"),
        app_commands.Choice(name="宜蘭縣", value="宜蘭"),
        app_commands.Choice(name="花蓮縣", value="花蓮"),
        app_commands.Choice(name="台東縣", value="台東"),
        app_commands.Choice(name="澎湖縣", value="澎湖"),
        app_commands.Choice(name="金門縣", value="金門"),
        app_commands.Choice(name="連江縣", value="連江")
    ])
    async def water_disaster_cameras(self, interaction: discord.Interaction, city: str = None, location: str = None):
        """查詢水利防災監控影像（舊版相容）"""
        # 直接調用 water_cameras 方法
        await self.water_cameras(interaction, city, location)

    # ...existing helper methods...
    
    async def get_water_disaster_images(self):
        """取得水利防災影像資料"""
        try:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=cea6b0b1-3d17-4493-9c49-0b5b7ff0fa8c"
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"API 回應錯誤: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"取得水利防災影像資料時發生錯誤: {str(e)}")
            return []

    async def _get_highway_cameras(self):
        """取得公路監視器資料"""
        try:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=xml&id=c3951d30-20f8-4e19-8e1d-84c7bf4b4b50"
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        return self._parse_highway_cameras_xml(xml_content)
                    else:
                        logger.error(f"公路監視器API回應錯誤: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"取得公路監視器資料時發生錯誤: {str(e)}")
            return []

    def _parse_highway_cameras_xml(self, xml_content):
        """解析公路監視器XML資料"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)
            
            cameras = []
            for item in root.findall('.//resource'):
                camera = {}
                for field in item:
                    camera[field.tag] = field.text
                cameras.append(camera)
            
            return cameras
        except Exception as e:
            logger.error(f"解析公路監視器XML時發生錯誤: {str(e)}")
            return []

    def _classify_road_type(self, road_name):
        """分類道路類型"""
        if not road_name:
            return "未知"
        
        road_name = road_name.upper()
        
        if "國道" in road_name or "FREEWAY" in road_name:
            return "國道"
        elif "快速" in road_name or "EXPRESSWAY" in road_name:
            return "快速公路"
        elif "省道" in road_name or road_name.startswith("台"):
            return "省道"
        elif "縣道" in road_name:
            return "縣道"
        else:
            return "市區道路"

    async def _create_water_camera_embed(self, camera_data):
        """建立水利監視器 embed"""
        try:
            station_name = camera_data.get('VideoSurveillanceStationName', '未知監控站')
            county = self._normalize_county_name(camera_data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', ''))
            district = camera_data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
            
            # 建立標題
            title = f"📹 {station_name}"
            
            # 建立 embed
            embed = discord.Embed(
                title=title,
                color=0x00bfff
            )
            
            # 添加位置資訊
            location_info = f"{county}"
            if district:
                location_info += f" {district}"
            embed.add_field(name="📍 位置", value=location_info, inline=True)
            
            # 處理圖片URL（加上時間戳避免快取）
            image_url = camera_data.get('VideoURL', '')
            if image_url:
                processed_url = self._process_and_validate_image_url(image_url)
                embed.set_image(url=processed_url)
            
            # 添加時間戳
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text="💧 水利防災監控系統")
            
            return embed
            
        except Exception as e:
            logger.error(f"建立水利監視器 embed 時發生錯誤: {str(e)}")
            return discord.Embed(
                title="❌ 資料處理錯誤",
                description="無法處理監視器資料",
                color=0xff0000
            )

    def _process_and_validate_image_url(self, url):
        """處理和驗證圖片URL，加上時間戳避免快取"""
        if not url:
            return url
        
        # 加上時間戳參數避免快取
        import time
        timestamp = int(time.time())
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}t={timestamp}"

    def _normalize_county_name(self, location_str):
        """標準化縣市名稱"""
        if not location_str:
            return location_str
        
        # 縣市名稱對應表
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

async def setup(bot):
    """設置函數，用於載入 Cog"""
    await bot.add_cog(ReservoirCommands(bot))
