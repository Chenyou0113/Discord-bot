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

    def _normalize_county_name(self, county_name):
        """標準化縣市名稱"""
        try:
            # 基本的替換規則
            replacements = {
                "台北市": "臺北市",
                "高雄市": "高雄",
                "台中市": "臺中市",
                "台南市": "臺南",
                "基隆市": "基隆",
                "新竹市": "新竹",
                "嘉義市": "嘉義",
                "屏東縣": "屏東",
                "宜蘭縣": "宜蘭",
                "花蓮縣": "花蓮",
                "台東縣": "台東",
                "澎湖縣": "澎湖",
                "金門縣": "金門",
                "連江縣": "連江",
                "南投縣": "南投",
                "苗栗縣": "苗栗",
                "彰化縣": "彰化",
                "雲林縣": "雲林",
                "新北市": "新北",
                "桃園市": "桃園",
                "台北": "臺北",
                "高雄": "高雄",
                "台中": "臺中",
                "台南": "臺南",
                "基隆": "基隆",
                "新竹": "新竹",
                "嘉義": "嘉義",
                "屏東": "屏東",
                "宜蘭": "宜蘭",
                "花蓮": "花蓮",
                "台東": "台東",
                "澎湖": "澎湖",
                "金門": "金門",
                "連江": "連江",
                "南投": "南投",
                "苗栗": "苗栗",
                "彰化": "彰化",
                "雲林": "雲林",
                "新北": "新北",
                "桃園": "桃園"
            }
            
            normalized = county_name
            for key, value in replacements.items():
                normalized = normalized.replace(key, value)
            
            return normalized

        except Exception as e:
            logger.error(f"標準化縣市名稱時發生錯誤: {str(e)}")
            return county_name

    async def get_water_level_data(self):
        """從水利署 API 獲取水位資料"""
        try:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx"
            params = {
                'format': 'json',
                'id': '2D09DB8B-6A1B-485E-88B5-923A462F475C'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"成功獲取水位資料，共 {len(data)} 筆")
                        return data
                    else:
                        logger.error(f"水位 API 請求失敗: HTTP {response.status}")
                        return []
        except Exception as e:
            logger.error(f"獲取水位資料時發生錯誤: {str(e)}")
            return []

    def format_water_level_info(self, data):
        """格式化水位資料"""
        try:
            station_name = data.get('StationName', '未知測站')
            station_id = data.get('StationId', '未知ID')
            county = data.get('County', '未知縣市')
            district = data.get('District', '未知區域')
            river = data.get('RiverName', '未知河川')
            water_level = data.get('WaterLevel', 'N/A')
            update_time = data.get('UpdateTime', '未知時間')
            
            # 標準化縣市名稱
            normalized_county = self._normalize_county_name(county)
            
            return {
                'station_name': station_name,
                'station_id': station_id,
                'county': normalized_county,
                'district': district,
                'river': river,
                'water_level': water_level,
                'update_time': update_time
            }
        except Exception as e:
            logger.error(f"格式化水位資料時發生錯誤: {str(e)}")
            return None

    @app_commands.command(name="water_level", description="查詢全台河川水位資料")
    @app_commands.describe(
        city="選擇縣市",
        river="河川名稱（可選）",
        station="測站名稱（可選）"
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
    async def water_level(self, interaction: discord.Interaction, city: str = None, river: str = None, station: str = None):
        """查詢河川水位資料"""
        await interaction.response.defer()
        
        try:
            # 獲取水位資料
            water_level_data = await self.get_water_level_data()
            
            if not water_level_data:
                embed = discord.Embed(
                    title="❌ 無法獲取水位資料",
                    description="目前無法連接到水利署 API，請稍後再試",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 篩選資料
            filtered_data = []
            
            for data in water_level_data:
                info = self.format_water_level_info(data)
                if not info:
                    continue
                
                # 縣市篩選
                if city:
                    county_match = (city.lower() in info['county'].lower() or 
                                  city.lower() in info['district'].lower())
                    if not county_match:
                        continue
                
                # 河川篩選
                if river:
                    river_match = river.lower() in info['river'].lower()
                    if not river_match:
                        continue
                
                # 測站篩選
                if station:
                    station_match = (station.lower() in info['station_name'].lower() or
                                   station.lower() in info['station_id'].lower())
                    if not station_match:
                        continue
                
                filtered_data.append(info)
            
            # 建立回應
            if not filtered_data:
                embed = discord.Embed(
                    title="🔍 未找到符合條件的水位測站",
                    description="請嘗試不同的搜尋條件",
                    color=discord.Color.orange()
                )
                if city:
                    embed.add_field(name="查詢縣市", value=city, inline=True)
                if river:
                    embed.add_field(name="查詢河川", value=river, inline=True)
                if station:
                    embed.add_field(name="查詢測站", value=station, inline=True)
                
                await interaction.followup.send(embed=embed)
                return
            
            # 限制顯示數量
            if len(filtered_data) > 10:
                display_data = filtered_data[:10]
                has_more = True
            else:
                display_data = filtered_data
                has_more = False
            
            # 建立 Embed
            search_terms = []
            if city:
                search_terms.append(f"縣市: {city}")
            if river:
                search_terms.append(f"河川: {river}")
            if station:
                search_terms.append(f"測站: {station}")
            
            search_desc = " | ".join(search_terms) if search_terms else "全台水位"
            
            embed = discord.Embed(
                title="🌊 河川水位查詢結果",
                description=f"**查詢條件**: {search_desc}\n**找到**: {len(filtered_data)} 個測站",
                color=discord.Color.blue()
            )
            
            for i, info in enumerate(display_data, 1):
                water_level_str = f"{info['water_level']} 公尺" if info['water_level'] != 'N/A' else '無資料'
                
                embed.add_field(
                    name=f"{i}. {info['station_name']}",
                    value=f"🏙️ 縣市：{info['county']}\n"
                          f"🌊 河川：{info['river']}\n"
                          f"📏 水位：{water_level_str}\n"
                          f"⏰ 更新：{info['update_time']}",
                    inline=True
                )
            
            if has_more:
                embed.add_field(
                    name="📊 顯示說明",
                    value=f"僅顯示前 10 筆結果，總共有 {len(filtered_data)} 筆資料",
                    inline=False
                )
            
            embed.set_footer(text="資料來源：經濟部水利署")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"水位查詢指令執行錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 指令執行失敗",
                description=f"執行過程中發生錯誤: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    # ...existing code...

class WaterCameraInfoModal(discord.ui.Modal):
    """水利防災監視器詳細資訊彈窗"""
    
    def __init__(self, camera, current_num, total_num, normalize_func=None):
        super().__init__(title=f"水利防災監視器詳細資訊 ({current_num}/{total_num})")
        
        # 直接格式化詳細資訊，並標準化縣市名稱
        station_name = camera.get('VideoSurveillanceStationName', '未知監控站')
        station_id = camera.get('VideoSurveillanceStationId', '未知ID')
        raw_county = camera.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '未知縣市')
        district = camera.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '未知區域')
        address = camera.get('VideoSurveillanceStationAddress', '未知地址')
        river = camera.get('River', camera.get('RiverName', '未知河川'))
        image_url = camera.get('ImageURL', '無影像URL')
        
        # 標準化縣市名稱（如果提供了標準化函數）
        if normalize_func:
            county = normalize_func(raw_county)
        else:
            county = raw_county
        
        info_text = f"監控站名稱: {station_name}\n"
        info_text += f"監控站ID: {station_id}\n"
        info_text += f"縣市: {county}\n"
        info_text += f"區域: {district}\n"
        info_text += f"詳細地址: {address}\n"
        info_text += f"河川名稱: {river}\n"
        info_text += f"資料來源: 水利署\n"
        info_text += f"影像URL: {image_url}\n"
        info_text += f"狀態: {'✅ 有影像' if image_url else '❌ 無影像'}"
        
        self.info_field = discord.ui.TextInput(
            label=f"詳細資訊 ({current_num}/{total_num})",
            style=discord.TextStyle.paragraph,
            default=info_text,
            max_length=4000
        )
        self.add_item(self.info_field)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("📋 資訊已顯示在上方文字框中", ephemeral=True)
