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
            basin_name = image_data.get('BasinName', '')
            tributary = image_data.get('TRIBUTARY', '')
            image_url = image_data.get('ImageURL', '')
            status = image_data.get('Status', '')
            latitude = image_data.get('latitude_4326', '')
            longitude = image_data.get('Longitude_4326', '')
            station_id = image_data.get('StationID', 'N/A')
            
            # 組合完整地址
            full_location = f"{location}{district}" if location and district else (location or district or "N/A")
            
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
                'county': location or 'N/A',  # 新增 county 欄位
                'district': district or 'N/A',  # 新增 district 欄位
                'address': full_location,  # 新增 address 欄位（與 location 相同）
                'station_id': station_id,  # 新增 station_id 欄位
                'source': '水利防災',  # 新增 source 欄位
                'river': river_info,
                'image_url': processed_image_url,
                'status': "正常" if status == "1" else "異常" if status == "0" else "未知",
                'coordinates': f"{latitude}, {longitude}" if latitude and longitude else "N/A"
            }
            
        except Exception as e:
            logger.error(f"格式化水利防災影像資訊時發生錯誤: {str(e)}")
            return None
    
    def _process_and_validate_image_url(self, image_url):
        """處理和驗證圖片 URL - 增強版本"""
        if not image_url or not image_url.strip():
            return "N/A"
        
        processed_url = image_url.strip()
        
        # 移除可能的空白字符和特殊字符
        processed_url = processed_url.replace(' ', '').replace('\n', '').replace('\r', '')
        
        # 多重 URL 格式處理
        if not processed_url.startswith(('http://', 'https://')):
            if processed_url.startswith('//'):
                processed_url = 'https:' + processed_url
            elif processed_url.startswith('/'):
                # 嘗試不同的基礎域名
                base_urls = [
                    'https://opendata.wra.gov.tw',
                    'https://fhy.wra.gov.tw', 
                    'https://www.wra.gov.tw',
                    'https://alerts.ncdr.nat.gov.tw'
                ]
                for base_url in base_urls:
                    test_url = base_url + processed_url
                    if self._validate_image_url_format(test_url):
                        processed_url = test_url
                        break
                else:
                    # 如果都不匹配，使用第一個作為預設
                    processed_url = base_urls[0] + processed_url
            else:
                # 相對路徑，嘗試添加基礎 URL
                if not processed_url.startswith(('www.', 'fhy.', 'opendata.')):
                    processed_url = 'https://opendata.wra.gov.tw/' + processed_url
                else:
                    processed_url = 'https://' + processed_url
        
        # 確保 URL 有效性
        if self._validate_image_url_format(processed_url):
            return processed_url
        
        logger.warning(f"無效的圖片 URL 格式: {image_url} -> {processed_url}")
        return "N/A"
    
    def _validate_image_url_format(self, url):
        """驗證圖片 URL 格式"""
        if not url or url == "N/A":
            return False
        
        import re
        
        # 基本 URL 格式檢查
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False
        
        # 檢查是否可能是圖片 URL
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        has_image_extension = any(url.lower().endswith(ext) for ext in image_extensions)
        
        # 檢查是否包含可能的圖片路徑關鍵字
        image_keywords = ['image', 'img', 'photo', 'pic', 'camera', 'cam', 'surveillance']
        has_image_keyword = any(keyword in url.lower() for keyword in image_keywords)
        
        # 如果有圖片擴展名或關鍵字，認為是有效的
        return has_image_extension or has_image_keyword or len(url) > 20

    async def get_river_water_level_data(self):
        """取得河川水位資料"""
        try:
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        # 處理 UTF-8 BOM 問題
                        text = await response.text()
                        if text.startswith('\ufeff'):
                            text = text[1:]
                        
                        data = json.loads(text)
                        return data if isinstance(data, list) else []
                    else:
                        logger.error(f"河川水位 API 請求失敗: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"取得河川水位資料時發生錯誤: {str(e)}")
            return None

    def format_river_water_level_info(self, level_data):
        """格式化河川水位資訊"""
        try:
            station_name = level_data.get('StationName', 'N/A')
            county_name = level_data.get('CountyName', 'N/A')
            river_name = level_data.get('RiverName', 'N/A')
            water_level = level_data.get('WaterLevel', 'N/A')
            observation_time = level_data.get('ObservationTime', 'N/A')
            station_id = level_data.get('StationIdentifier', 'N/A')
            location = level_data.get('LocationDescription', 'N/A')
            altitude = level_data.get('StationAltitude', 'N/A')
            
            # 處理觀測時間格式
            formatted_time = observation_time
            if observation_time and observation_time != 'N/A':
                try:
                    # 嘗試格式化時間
                    dt = datetime.fromisoformat(observation_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_time = observation_time
            
            # 處理水位數值
            formatted_water_level = water_level
            if water_level and water_level != 'N/A':
                try:
                    level_float = float(water_level)
                    formatted_water_level = f"{level_float:.2f} 公尺"
                except:
                    formatted_water_level = f"{water_level} 公尺"
            
            return {
                'station_name': station_name,
                'county': county_name,
                'river': river_name,
                'water_level': formatted_water_level,
                'observation_time': formatted_time,
                'station_id': station_id,
                'location': location,
                'altitude': altitude if altitude != 'N/A' else None
            }
            
        except Exception as e:
            logger.error(f"格式化河川水位資訊時發生錯誤: {str(e)}")
            return None

    @app_commands.command(name="reservoir", description="查詢台灣水庫水情資訊")
    @app_commands.describe(
        reservoir_name="水庫名稱（可選，不指定則顯示主要水庫列表）"
    )
    async def reservoir_info(self, interaction: discord.Interaction, reservoir_name: str = None):
        """水庫水情查詢指令"""
        await interaction.response.defer()
        
        try:
            # 取得水庫資料
            reservoir_data = await self.get_reservoir_data()
            
            if not reservoir_data:
                embed = discord.Embed(
                    title="❌ 水庫資料取得失敗",
                    description="無法取得水庫水情資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 如果沒有指定水庫名稱，顯示主要水庫列表
            if not reservoir_name:
                embed = discord.Embed(
                    title="🏞️ 台灣主要水庫水情",
                    description="以下是主要水庫的最新水情資訊",
                    color=discord.Color.blue()
                )
                
                # 按照最新時間分組資料
                latest_data = {}
                for data in reservoir_data:
                    reservoir_id = data.get('ReservoirIdentifier', '')
                    if reservoir_id in self.reservoir_names:
                        if reservoir_id not in latest_data:
                            latest_data[reservoir_id] = data
                        else:
                            # 比較時間，保留最新的
                            current_time = data.get('ObservationTime', '')
                            stored_time = latest_data[reservoir_id].get('ObservationTime', '')
                            if current_time > stored_time:
                                latest_data[reservoir_id] = data
                
                # 顯示主要水庫資訊
                count = 0
                for reservoir_id, data in latest_data.items():
                    if count >= 10:  # 限制顯示數量
                        break
                    
                    info = self.format_reservoir_info(data)
                    if info:
                        embed.add_field(
                            name=f"🏞️ {info['name']}",
                            value=f"💧 水位: {info['water_level']} 公尺\n"
                                  f"📊 蓄水量: {info['capacity']} 萬立方公尺\n"
                                  f"🔄 流入量: {info['inflow']} 立方公尺/秒\n"
                                  f"📅 {info['time']}",
                            inline=True
                        )
                        count += 1
                
                embed.set_footer(text="💡 使用 /reservoir <水庫名稱> 查詢特定水庫詳細資訊")
                
            else:
                # 搜尋指定的水庫
                found_reservoirs = []
                reservoir_name_lower = reservoir_name.lower()
                
                # 按照最新時間分組資料
                latest_data = {}
                for data in reservoir_data:
                    reservoir_id = data.get('ReservoirIdentifier', '')
                    reservoir_display_name = self.reservoir_names.get(reservoir_id, f"水庫 {reservoir_id}")
                    
                    # 檢查是否符合搜尋條件
                    if (reservoir_name_lower in reservoir_display_name.lower() or 
                        reservoir_name_lower in reservoir_id.lower()):
                        
                        if reservoir_id not in latest_data:
                            latest_data[reservoir_id] = data
                        else:
                            # 比較時間，保留最新的
                            current_time = data.get('ObservationTime', '')
                            stored_time = latest_data[reservoir_id].get('ObservationTime', '')
                            if current_time > stored_time:
                                latest_data[reservoir_id] = data
                
                if latest_data:
                    # 顯示找到的水庫詳細資訊
                    for reservoir_id, data in list(latest_data.items())[:5]:  # 最多顯示5個
                        info = self.format_reservoir_info(data)
                        if info:
                            embed = discord.Embed(
                                title=f"🏞️ {info['name']} 水情資訊",
                                color=discord.Color.blue()
                            )
                            
                            embed.add_field(name="💧 水位", value=f"{info['water_level']} 公尺", inline=True)
                            embed.add_field(name="📊 有效蓄水量", value=f"{info['capacity']} 萬立方公尺", inline=True)
                            embed.add_field(name="🔄 流入量", value=f"{info['inflow']} 立方公尺/秒", inline=True)
                            embed.add_field(name="📤 流出量", value=f"{info['outflow']} 立方公尺/秒", inline=True)
                            embed.add_field(name="🏷️ 水庫代碼", value=info['id'], inline=True)
                            embed.add_field(name="📅 觀測時間", value=info['time'], inline=True)
                            
                            embed.set_footer(text="資料來源：經濟部水利署")
                            
                            await interaction.followup.send(embed=embed)
                            break
                else:
                    embed = discord.Embed(
                        title="❌ 找不到水庫",
                        description=f"找不到名稱包含「{reservoir_name}」的水庫。\n請使用 `/reservoir` 查看可用的水庫列表。",
                        color=discord.Color.orange()
                    )
                    await interaction.followup.send(embed=embed)
                    return
            
            if not reservoir_name:
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"水庫指令執行錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 指令執行錯誤",
                description="執行水庫查詢時發生錯誤，請稍後再試。",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="reservoir_list", description="顯示所有水庫容量資訊")
    @app_commands.describe(
        show_type="顯示類型",
        region="地區篩選（可選）"
    )
    @app_commands.choices(show_type=[
        app_commands.Choice(name="前20大水庫", value="top20"),
        app_commands.Choice(name="主要水庫", value="major"),
        app_commands.Choice(name="完整列表", value="all")
    ])
    @app_commands.choices(region=[
        app_commands.Choice(name="全部地區", value="all"),
        app_commands.Choice(name="北部", value="north"),
        app_commands.Choice(name="中部", value="central"),
        app_commands.Choice(name="南部", value="south"),
        app_commands.Choice(name="東部", value="east")
    ])
    async def reservoir_list(self, interaction: discord.Interaction, show_type: str = "major", region: str = "all"):
        """動態顯示水庫容量資訊"""
        await interaction.response.defer()
        
        try:
            # 取得水庫資料
            reservoir_data = await self.get_reservoir_data()
            
            if not reservoir_data:
                embed = discord.Embed(
                    title="❌ 水庫資料取得失敗",
                    description="無法取得水庫資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 解析並篩選水庫資料
            processed_reservoirs = []
            for data in reservoir_data:
                try:
                    reservoir_id = data.get('ReservoirIdentifier', '')
                    effective_capacity = data.get('EffectiveWaterStorageCapacity', '')
                    water_level = data.get('WaterLevel', '')
                    inflow = data.get('InflowDischarge', '')
                    outflow = data.get('TotalOutflow', '')
                    observation_time = data.get('ObservationTime', '')
                    
                    # 過濾掉無效資料
                    if not reservoir_id or not effective_capacity:
                        continue
                    
                    try:
                        capacity_value = float(effective_capacity)
                        if capacity_value <= 0:
                            continue
                    except:
                        continue
                    
                    # 取得水庫名稱
                    reservoir_name = self.reservoir_names.get(reservoir_id, f"水庫{reservoir_id}")
                    
                    # 地區判斷
                    region_tag = self._get_region_tag(reservoir_id)
                    
                    processed_reservoirs.append({
                        'id': reservoir_id,
                        'name': reservoir_name,
                        'capacity': capacity_value,
                        'water_level': water_level,
                        'inflow': inflow,
                        'outflow': outflow,
                        'time': observation_time,
                        'region': region_tag
                    })
                    
                except Exception as e:
                    continue
            
            # 地區篩選
            if region != "all":
                processed_reservoirs = [r for r in processed_reservoirs if r['region'] == region]
            
            # 根據顯示類型篩選
            if show_type == "top20":
                # 按容量排序取前20
                processed_reservoirs = sorted(processed_reservoirs, key=lambda x: x['capacity'], reverse=True)[:20]
                title = "🏆 台灣前20大水庫容量資訊"
            elif show_type == "major":
                # 只顯示主要水庫
                processed_reservoirs = [r for r in processed_reservoirs if r['id'] in self.reservoir_names]
                processed_reservoirs = sorted(processed_reservoirs, key=lambda x: x['capacity'], reverse=True)
                title = "🏞️ 主要水庫容量資訊"
            else:
                # 顯示所有，但限制前50個
                processed_reservoirs = sorted(processed_reservoirs, key=lambda x: x['capacity'], reverse=True)[:50]
                title = "📊 水庫容量資訊列表（前50）"
            
            if not processed_reservoirs:
                embed = discord.Embed(
                    title="❌ 沒有符合條件的水庫",
                    description="沒有找到符合篩選條件的水庫資料。",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 建立回應
            if region != "all":
                region_names = {"north": "北部", "central": "中部", "south": "南部", "east": "東部"}
                title += f" ({region_names.get(region, region)}地區)"
            
            embed = discord.Embed(
                title=title,
                description=f"共找到 {len(processed_reservoirs)} 個水庫",
                color=discord.Color.blue()
            )
            
            # 格式化時間
            try:
                if processed_reservoirs[0]['time']:
                    dt = datetime.fromisoformat(processed_reservoirs[0]['time'])
                    update_time = dt.strftime('%Y-%m-%d %H:%M')
                    embed.set_footer(text=f"📅 資料更新時間: {update_time}")
            except:
                pass
            
            # 分頁顯示
            reservoirs_per_page = 10
            total_pages = (len(processed_reservoirs) + reservoirs_per_page - 1) // reservoirs_per_page
            
            for page in range(min(total_pages, 2)):  # 最多顯示2頁
                start_idx = page * reservoirs_per_page
                end_idx = min(start_idx + reservoirs_per_page, len(processed_reservoirs))
                
                page_reservoirs = processed_reservoirs[start_idx:end_idx]
                
                field_value = ""
                for i, reservoir in enumerate(page_reservoirs, start_idx + 1):
                    capacity_str = f"{reservoir['capacity']:.1f}萬m³" if reservoir['capacity'] >= 1 else f"{reservoir['capacity']*10000:.0f}m³"
                    water_level_str = f"{reservoir['water_level']}m" if reservoir['water_level'] and reservoir['water_level'] != '' else "N/A"
                    inflow_str = f"{reservoir['inflow']}cms" if reservoir['inflow'] and reservoir['inflow'] != '' else "N/A"
                    
                    field_value += f"**{i}.** {reservoir['name']} `{reservoir['id']}`\n"
                    field_value += f"   💧 容量: {capacity_str} | 水位: {water_level_str}\n"
                    field_value += f"   ⬇️ 入流: {inflow_str} | 地區: {self._get_region_name(reservoir['region'])}\n\n"
                
                field_name = f"第 {page + 1} 頁" if total_pages > 1 else "水庫列表"
                embed.add_field(name=field_name, value=field_value, inline=False)
            
            if total_pages > 2:
                embed.add_field(
                    name="📋 更多資訊",
                    value=f"還有 {total_pages - 2} 頁資料未顯示，請使用更具體的篩選條件。",
                    inline=False
                )
            
            embed.add_field(
                name="💡 使用說明",
                value="• 使用 `/reservoir <水庫名稱>` 查詢特定水庫詳細資訊\n• 使用 `/reservoir_operation` 查詢營運狀況",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"水庫列表指令執行錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 指令執行錯誤",
                description="執行水庫列表查詢時發生錯誤，請稍後再試。",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="reservoir_operation", description="查詢台灣水庫營運狀況")
    @app_commands.describe(
        reservoir_name="水庫名稱（可選，不指定則顯示主要水庫營運狀況）"
    )
    async def reservoir_operation(self, interaction: discord.Interaction, reservoir_name: str = None):
        """水庫營運狀況查詢指令"""
        await interaction.response.defer()
        
        try:
            # 取得水庫營運資料
            operation_data = await self.get_reservoir_operation_data()
            
            if not operation_data:
                embed = discord.Embed(
                    title="❌ 水庫營運資料取得失敗",
                    description="無法取得水庫營運狀況資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 如果沒有指定水庫名稱，顯示主要水庫營運狀況
            if not reservoir_name:
                embed = discord.Embed(
                    title="🏗️ 台灣主要水庫營運狀況",
                    description="以下是主要水庫的最新營運狀況資訊",
                    color=discord.Color.blue()
                )
                
                # 顯示主要水庫營運資訊
                count = 0
                for data in operation_data:
                    if count >= 8:  # 限制顯示數量
                        break
                    
                    info = self.format_reservoir_operation_info(data)
                    if info and info['name'] != 'N/A':
                        embed.add_field(
                            name=f"🏗️ {info['name']}",
                            value=f"💧 蓄水量: {info['capacity']} 萬立方公尺\n"
                                  f"📊 水位: {info['water_level']} 公尺\n"
                                  f"🌧️ 降雨量: {info['rainfall']} 毫米\n"
                                  f"🔄 流入/出: {info['inflow']}/{info['outflow']}\n"
                                  f"📅 {info['time']}",
                            inline=True
                        )
                        count += 1
                
                embed.set_footer(text="💡 使用 /reservoir_operation <水庫名稱> 查詢特定水庫詳細營運資訊")
                
            else:
                # 搜尋指定的水庫
                found_reservoirs = []
                reservoir_name_lower = reservoir_name.lower()
                
                for data in operation_data:
                    reservoir_display_name = data.get('ReservoirName', '')
                    reservoir_id = data.get('ReservoirIdentifier', '')
                    
                    # 檢查是否符合搜尋條件
                    if (reservoir_name_lower in reservoir_display_name.lower() or 
                        reservoir_name_lower in reservoir_id.lower()):
                        found_reservoirs.append(data)
                
                if found_reservoirs:
                    # 顯示找到的水庫詳細營運資訊
                    data = found_reservoirs[0]  # 取第一個符合的
                    info = self.format_reservoir_operation_info(data)
                    
                    if info:
                        embed = discord.Embed(
                            title=f"🏗️ {info['name']} 營運狀況",
                            color=discord.Color.blue()
                        )
                        
                        embed.add_field(name="💧 蓄水量", value=f"{info['capacity']} 萬立方公尺", inline=True)
                        embed.add_field(name="📊 水位", value=f"{info['water_level']} 公尺", inline=True)
                        embed.add_field(name="📈 蓄水率", value=f"{info['percentage']}%", inline=True)
                        embed.add_field(name="🔄 流入量", value=f"{info['inflow']} 立方公尺/秒", inline=True)
                        embed.add_field(name="📤 流出量", value=f"{info['outflow']} 立方公尺/秒", inline=True)
                        embed.add_field(name="🌧️ 集水區降雨", value=f"{info['rainfall']} 毫米", inline=True)
                        embed.add_field(name="🌊 越域引水", value=f"{info['cross_flow']} 立方公尺/秒", inline=True)
                        embed.add_field(name="🏔️ 滿水位", value=f"{info['max_level']} 公尺", inline=True)
                        embed.add_field(name="🏷️ 水庫代碼", value=info['id'], inline=True)
                        embed.add_field(name="📅 資料時間", value=info['time'], inline=False)
                        
                        embed.set_footer(text="資料來源：經濟部水利署 - 水庫營運狀況")
                        
                        await interaction.followup.send(embed=embed)
                        return
                else:
                    embed = discord.Embed(
                        title="❌ 找不到水庫",
                        description=f"找不到名稱包含「{reservoir_name}」的水庫營運資料。\n請使用 `/reservoir_operation` 查看可用的水庫列表。",
                        color=discord.Color.orange()
                    )
                    await interaction.followup.send(embed=embed)
                    return
            
            if not reservoir_name:
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"水庫營運指令執行錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 指令執行錯誤",
                description="執行水庫營運查詢時發生錯誤，請稍後再試。",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    async def get_reservoir_basic_info(self):
        """取得水庫基本資料"""
        try:
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=D54BA676-ED9A-4077-9A10-A0971B3B020C"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        # 處理 UTF-8 BOM 問題
                        text = await response.text()
                        if text.startswith('\ufeff'):
                            text = text[1:]
                        
                        data = json.loads(text)
                        # 取得水庫基本資訊列表
                        reservoir_info = data.get('TaiwanWaterExchangingData', {}).get('ReservoirClass', {}).get('ReservoirsInformation', [])
                        return reservoir_info
                    else:
                        logger.error(f"水庫基本資料 API 請求失敗: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"取得水庫基本資料時發生錯誤: {str(e)}")
            return None

    async def get_water_disaster_images(self):
        """取得水利防災影像資料"""
        try:
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        # 處理 UTF-8 BOM 問題
                        text = await response.text()
                        if text.startswith('\ufeff'):
                            text = text[1:]
                        
                        data = json.loads(text)
                        return data if isinstance(data, list) else []
                    else:
                        logger.error(f"水利防災影像 API 請求失敗: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"取得水利防災影像資料時發生錯誤: {str(e)}")
            return None

    @app_commands.command(name="reservoir_info", description="查詢台灣水庫基本資料")
    @app_commands.describe(
        reservoir_name="水庫名稱（可選，不指定則顯示主要水庫基本資料列表）"
    )
    async def reservoir_basic_info(self, interaction: discord.Interaction, reservoir_name: str = None):
        """水庫基本資料查詢指令"""
        await interaction.response.defer()
        
        try:
            # 取得水庫基本資料
            basic_data = await self.get_reservoir_basic_info()
            
            if not basic_data:
                embed = discord.Embed(
                    title="❌ 水庫基本資料取得失敗",
                    description="無法取得水庫基本資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 如果沒有指定水庫名稱，顯示主要水庫基本資料
            if not reservoir_name:
                embed = discord.Embed(
                    title="🏗️ 台灣主要水庫基本資料",
                    description="以下是主要水庫的基本資料資訊",
                    color=discord.Color.blue()
                )
                
                # 顯示主要水庫基本資料
                count = 0
                for data in basic_data:
                    if count >= 8:  # 限制顯示數量
                        break
                    
                    info = self.format_reservoir_basic_info(data)
                    if info and info['name'] != 'N/A':
                        embed.add_field(
                            name=f"🏗️ {info['name']}",
                            value=f"📍 位置: {info['location']}\n"
                                  f"🌊 河川: {info['river'][:30]}...\n"
                                  f"🏛️ 壩型: {info['dam_type']}\n"
                                  f"📏 壩高: {info['height']} 公尺\n"
                                  f"💧 設計容量: {info['designed_capacity']} 萬立方公尺",
                            inline=True
                        )
                        count += 1
                
                embed.set_footer(text="💡 使用 /reservoir_info <水庫名稱> 查詢特定水庫詳細基本資料")
                
            else:
                # 搜尋指定的水庫
                found_reservoirs = []
                reservoir_name_lower = reservoir_name.lower()
                
                for data in basic_data:
                    reservoir_display_name = data.get('ReservoirName', '')
                    reservoir_id = data.get('ReservoirIdentifier', '')
                    
                    # 檢查是否符合搜尋條件
                    if (reservoir_name_lower in reservoir_display_name.lower() or 
                        reservoir_name_lower in reservoir_id.lower()):
                        found_reservoirs.append(data)
                
                if found_reservoirs:
                    # 顯示找到的水庫詳細基本資料
                    data = found_reservoirs[0]  # 取第一個符合的
                    info = self.format_reservoir_basic_info(data)
                    
                    if info:
                        embed = discord.Embed(
                            title=f"🏗️ {info['name']} 基本資料",
                            color=discord.Color.blue()
                        )
                        
                        embed.add_field(name="📍 所在地區", value=info['area'], inline=True)
                        embed.add_field(name="🏘️ 詳細位置", value=info['location'], inline=True)
                        embed.add_field(name="🌊 河川名稱", value=info['river'], inline=True)
                        embed.add_field(name="🏛️ 壩型", value=info['dam_type'], inline=True)
                        embed.add_field(name="📏 壩高", value=f"{info['height']} 公尺", inline=True)
                        embed.add_field(name="📐 壩長", value=f"{info['length']} 公尺", inline=True)
                        embed.add_field(name="🗺️ 集水面積", value=f"{info['drainage_area']} 平方公里", inline=True)
                        embed.add_field(name="💧 設計容量", value=f"{info['designed_capacity']} 萬立方公尺", inline=True)
                        embed.add_field(name="💧 現有容量", value=f"{info['current_capacity']} 萬立方公尺", inline=True)
                        embed.add_field(name="🎯 主要用途", value=info['application'], inline=True)
                        embed.add_field(name="🏢 管理機關", value=info['agency'], inline=True)
                        embed.add_field(name="🏷️ 水庫代碼", value=info['id'], inline=True)
                        
                        embed.set_footer(text="資料來源：經濟部水利署 - 水庫基本資料")
                        
                        await interaction.followup.send(embed=embed)
                        return
                else:
                    embed = discord.Embed(
                        title="❌ 找不到水庫",
                        description=f"找不到名稱包含「{reservoir_name}」的水庫基本資料。\n請使用 `/reservoir_info` 查看可用的水庫列表。",
                        color=discord.Color.orange()
                    )
                    await interaction.followup.send(embed=embed)
                    return
            
            if not reservoir_name:
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"水庫基本資料指令執行錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 指令執行錯誤",
                description="執行水庫基本資料查詢時發生錯誤，請稍後再試。",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="water_cameras", description="查詢水利防災監控影像")
    @app_commands.describe(
        location="地區名稱（可選，如：台南、彰化、基隆等）"
    )
    async def water_disaster_cameras(self, interaction: discord.Interaction, location: str = None):
        """水利防災影像查詢指令"""
        try:
            # 立即回應避免超時
            await interaction.response.defer()
            
            # 添加初始回應讓用戶知道正在處理
            loading_embed = discord.Embed(
                title="🔄 正在載入監視器資料...",
                description="請稍候，正在獲取水利防災監控影像資料",
                color=discord.Color.blue()
            )
            loading_message = await interaction.followup.send(embed=loading_embed)
            
            # 取得水利防災影像資料
            image_data = await self.get_water_disaster_images()
            
            if not image_data:
                embed = discord.Embed(
                    title="❌ 防災影像資料取得失敗",
                    description="無法取得水利防災影像資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await loading_message.edit(embed=embed)
                return
            
            # 如果沒有指定地區，顯示各地區監控點統計
            if not location:
                embed = discord.Embed(
                    title="📸 水利防災監控影像系統",
                    description="以下是各地區水利防災監控點分布",
                    color=discord.Color.blue()
                )
                
                # 統計各地區監控點數量
                location_stats = {}
                for data in image_data:
                    loc = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '未知地區')
                    location_stats[loc] = location_stats.get(loc, 0) + 1
                
                # 顯示各地區統計（按數量排序）
                sorted_locations = sorted(location_stats.items(), key=lambda x: x[1], reverse=True)
                
                count = 0
                for loc, num in sorted_locations[:12]:  # 顯示前12個地區
                    # 取該地區的一個範例
                    sample_camera = None
                    for data in image_data:
                        if data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '') == loc:
                            sample_camera = self.format_water_image_info(data)
                            break
                    
                    if sample_camera:
                        embed.add_field(
                            name=f"📍 {loc} ({num} 個監控點)",
                            value=f"📸 範例: {sample_camera['station_name']}\n"
                                  f"🌊 河川: {sample_camera['river']}\n"
                                  f"📡 狀態: {sample_camera['status']}",
                            inline=True
                        )
                        count += 1
                
                embed.set_footer(text="💡 使用 /water_cameras <地區名稱> 查詢特定地區監控影像")
                await loading_message.edit(embed=embed)
                
            else:
                # 搜尋指定地區的監控點
                found_cameras = []
                location_lower = location.lower()
                
                for data in image_data:
                    loc = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
                    district = data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
                    station_name = data.get('VideoSurveillanceStationName', '')
                    
                    # 檢查是否符合搜尋條件
                    if (location_lower in loc.lower() or 
                        location_lower in district.lower() or
                        location_lower in station_name.lower()):
                        found_cameras.append(data)
                
                if found_cameras:
                    # 過濾有效的監控點（有影像的）
                    valid_cameras = []
                    for data in found_cameras:
                        info = self.format_water_image_info(data)
                        if info and info['image_url'] and info['image_url'] != 'N/A':
                            valid_cameras.append(data)
                    
                    if valid_cameras:
                        # 顯示第一個監控器（簡化版本）
                        camera_data = valid_cameras[0]
                        info = self.format_water_image_info(camera_data)
                        
                        embed = discord.Embed(
                            title=f"📸 {location} 地區監控點",
                            description=f"**{info['station_name']}**",
                            color=discord.Color.blue()
                        )
                        
                        embed.add_field(
                            name="📍 位置資訊",
                            value=f"🏙️ 縣市：{info['county']}\n"
                                  f"🏘️ 區域：{info['district']}\n"
                                  f"📍 詳細：{info['address']}",
                            inline=True
                        )
                        
                        embed.add_field(
                            name="📊 技術資訊",
                            value=f"🆔 ID：{info['station_id']}\n"
                                  f"📡 來源：{info['source']}\n"
                                  f"📸 狀態：{'✅ 有影像' if info['image_url'] != 'N/A' else '❌ 無影像'}",
                            inline=True
                        )
                        
                        if info['image_url'] and info['image_url'] != 'N/A':
                            processed_url = await self._process_and_validate_image_url(info['image_url'])
                            if processed_url:
                                embed.set_image(url=processed_url)
                        
                        embed.set_footer(text=f"找到 {len(valid_cameras)} 個有效監控點 | 顯示第1個")
                        await loading_message.edit(embed=embed)
                    else:
                        embed = discord.Embed(
                            title=f"📸 {location} 地區監控點",
                            description=f"找到 {len(found_cameras)} 個監控點，但目前都沒有可用影像。",
                            color=discord.Color.orange()
                        )
                        await loading_message.edit(embed=embed)
                else:
                    # 沒有找到精確匹配，提供相似的建議
                    embed = discord.Embed(
                        title="❌ 找不到監控點",
                        description=f"找不到「{location}」地區的水利防災監控點。",
                        color=discord.Color.orange()
                    )
                    
                    # 嘗試找相似的地區名稱
                    similar_locations = set()
                    location_lower = location.lower()
                    
                    for data in image_data:
                        loc = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
                        district = data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
                        station_name = data.get('VideoSurveillanceStationName', '')
                        
                        # 部分匹配
                        if (any(char in loc.lower() for char in location_lower) or
                            any(char in district.lower() for char in location_lower) or
                            any(char in station_name.lower() for char in location_lower)):
                            similar_locations.add(loc)
                    
                    if similar_locations:
                        embed.add_field(
                            name="💡 您可能想找的地區",
                            value="\n".join([f"• {loc}" for loc in sorted(similar_locations)[:5]]),
                            inline=False
                        )
                    
                    embed.add_field(
                        name="📋 常見地區",
                        value="台南、台北、高雄、新北、台中、桃園、台東、花蓮、基隆、新竹",
                        inline=False
                    )
                    embed.add_field(
                        name="💡 使用提示",
                        value="• 使用 `/water_cameras` 查看所有地區\n• 可以搜尋縣市名稱，如「台南」\n• 也可以搜尋特定監控點名稱",
                        inline=False
                    )
                    
                    await loading_message.edit(embed=embed)
                    
        except Exception as e:
            logger.error(f"水利防災影像指令執行錯誤: {str(e)}")
            
            # 檢查是否已經有 loading_message 可以編輯
            try:
                if 'loading_message' in locals():
                    embed = discord.Embed(
                        title="❌ 指令執行錯誤",
                        description="執行水利防災影像查詢時發生錯誤，請稍後再試。",
                        color=discord.Color.red()
                    )
                    await loading_message.edit(embed=embed)
                else:
                    # 如果沒有 loading_message，使用 followup
                    embed = discord.Embed(
                        title="❌ 指令執行錯誤",
                        description="執行水利防災影像查詢時發生錯誤，請稍後再試。",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
            except:
                # 如果所有方法都失敗，記錄日誌
                logger.error("無法發送錯誤訊息到 Discord")

    @app_commands.command(name="national_highway_cameras", description="查詢國道監視器影像")
    @app_commands.describe(
        highway_number="國道號碼（如：1、3、5）",
        location="位置關鍵字（如：基隆、高雄、台中等）",
        direction="行駛方向（N北、S南、E東、W西）",
        city="縣市篩選"
    )
    async def national_highway_cameras(self, interaction: discord.Interaction, highway_number: str = None, location: str = None, direction: str = None, city: str = None):
        """查詢國道監視器（僅國道）"""
        await interaction.response.defer()
        loading_embed = discord.Embed(
            title="🔄 正在載入國道監視器資料...",
            description="請稍候，正在獲取國道監視器資料",
            color=discord.Color.blue()
        )
        loading_message = await interaction.followup.send(embed=loading_embed)
        cameras = await self._get_highway_cameras()
        if not cameras:
            embed = discord.Embed(
                title="❌ 查詢失敗",
                description="無法獲取國道監視器資料，請稍後再試",
                color=discord.Color.red()
            )
            await loading_message.edit(embed=embed)
            return
        # 只保留國道
        filtered_cameras = [c for c in cameras if self._classify_road_type(c) == 'national']
        if highway_number:
            filtered_cameras = [c for c in filtered_cameras if highway_number in c.get('RoadName', '') or highway_number in c.get('SurveillanceDescription', '')]
        if location:
            filtered_cameras = [c for c in filtered_cameras if location in c.get('SurveillanceDescription', '') or location in c.get('RoadName', '')]
        if direction:
            filtered_cameras = [c for c in filtered_cameras if direction in c.get('RoadDirection', '')]
        if city:
            filtered_cameras = [c for c in filtered_cameras if city in c.get('City', '') or city in c.get('SurveillanceDescription', '')]
        if not filtered_cameras:
            embed = discord.Embed(
                title="🔍 查詢結果",
                description="找不到符合條件的國道監視器。",
                color=discord.Color.orange()
            )
            await loading_message.edit(embed=embed)
            return
        camera = filtered_cameras[0]
        embed = discord.Embed(
            title="🛣️ 國道監視器",
            description=f"**{camera.get('SurveillanceDescription', '未知位置')}**",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📍 基本資訊",
            value=f"🛣️ 道路：{camera.get('RoadName', '未知')}\n"
                  f"🏷️ 類型：🛣️ 國道\n"
                  f"📍 里程：{camera.get('LocationMile', '未知')}\n"
                  f"🧭 方向：{camera.get('RoadDirection', '未知')}\n"
                  f"� ID：{camera.get('CCTVID', '未知')}",
            inline=True
        )
        lat = camera.get('PositionLat', '未知')
        lon = camera.get('PositionLon', '未知')
        estimated_city = "未知"
        if lat != '未知' and lon != '未知':
            estimated_city = self._get_city_by_coordinates(lat, lon) or "未知"
        embed.add_field(
            name="🌍 座標位置",
            value=f"�️ 縣市：{estimated_city}\n"
                  f"🌐 經度：{lon}\n"
                  f"🌐 緯度：{lat}",
            inline=True
        )
        image_url = camera.get('VideoImageURL')
        if image_url:
            processed_url = await self._process_highway_image_url(image_url)
            if processed_url:
                embed.set_image(url=processed_url)
                embed.add_field(
                    name="📸 影像狀態",
                    value="✅ 即時影像",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📸 影像狀態",
                    value="❌ 影像暫無法載入",
                    inline=False
                )
        embed.set_footer(text=f"找到 {len(filtered_cameras)} 個國道監視器 | 資料來源：公路總局")
        if len(filtered_cameras) > 1:
            view = HighwayCameraView(filtered_cameras, 0)
            await loading_message.edit(embed=embed, view=view)
        else:
            await loading_message.edit(embed=embed)

    @app_commands.command(name="general_road_cameras", description="查詢省道/快速公路/一般道路監視器影像")
    @app_commands.describe(
        road_type="道路類型（省道、快速公路、一般道路）",
        location="位置關鍵字（如：新竹、台中等）",
        direction="行駛方向（N北、S南、E東、W西）",
        city="縣市篩選"
    )
    @app_commands.choices(road_type=[
        app_commands.Choice(name="省道", value="provincial"),
        app_commands.Choice(name="快速公路", value="freeway"),
        app_commands.Choice(name="一般道路", value="general")
    ])
    async def general_road_cameras(self, interaction: discord.Interaction, road_type: str = None, location: str = None, direction: str = None, city: str = None):
        """查詢省道/快速公路/一般道路監視器（不含國道）"""
        await interaction.response.defer()
        loading_embed = discord.Embed(
            title="🔄 正在載入監視器資料...",
            description="請稍候，正在獲取監視器資料",
            color=discord.Color.blue()
        )
        loading_message = await interaction.followup.send(embed=loading_embed)
        cameras = await self._get_highway_cameras()
        if not cameras:
            embed = discord.Embed(
                title="❌ 查詢失敗",
                description="無法獲取監視器資料，請稍後再試",
                color=discord.Color.red()
            )
            await loading_message.edit(embed=embed)
            return
        # 排除國道
        filtered_cameras = [c for c in cameras if self._classify_road_type(c) != 'national']
        if road_type:
            filtered_cameras = [c for c in filtered_cameras if self._classify_road_type(c) == road_type]
        if location:
            filtered_cameras = [c for c in filtered_cameras if location in c.get('SurveillanceDescription', '') or location in c.get('RoadName', '')]
        if direction:
            filtered_cameras = [c for c in filtered_cameras if direction in c.get('RoadDirection', '')]
        if city:
            filtered_cameras = [c for c in filtered_cameras if city in c.get('City', '') or city in c.get('SurveillanceDescription', '')]
        if not filtered_cameras:
            embed = discord.Embed(
                title="🔍 查詢結果",
                description="找不到符合條件的省道/快速公路/一般道路監視器。",
                color=discord.Color.orange()
            )
            await loading_message.edit(embed=embed)
            return
        camera = filtered_cameras[0]
        road_type_display = {
            "provincial": "🛤️ 省道",
            "freeway": "🏎️ 快速公路",
            "general": "🚗 一般道路"
        }
        road_type_text = road_type_display.get(self._classify_road_type(camera), "🚗 一般道路")
        embed = discord.Embed(
            title=f"{road_type_text} 監視器",
            description=f"**{camera.get('SurveillanceDescription', '未知位置')}**",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📍 基本資訊",
            value=f"🛣️ 道路：{camera.get('RoadName', '未知')}\n"
                  f"🏷️ 類型：{road_type_text}\n"
                  f"📍 里程：{camera.get('LocationMile', '未知')}\n"
                  f"🧭 方向：{camera.get('RoadDirection', '未知')}\n"
                  f"� ID：{camera.get('CCTVID', '未知')}",
            inline=True
        )
        lat = camera.get('PositionLat', '未知')
        lon = camera.get('PositionLon', '未知')
        estimated_city = "未知"
        if lat != '未知' and lon != '未知':
            estimated_city = self._get_city_by_coordinates(lat, lon) or "未知"
        embed.add_field(
            name="🌍 座標位置",
            value=f"�️ 縣市：{estimated_city}\n"
                  f"🌐 經度：{lon}\n"
                  f"🌐 緯度：{lat}",
            inline=True
        )
        image_url = camera.get('VideoImageURL')
        if image_url:
            processed_url = await self._process_highway_image_url(image_url)
            if processed_url:
                embed.set_image(url=processed_url)
                embed.add_field(
                    name="📸 影像狀態",
                    value="✅ 即時影像",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📸 影像狀態",
                    value="❌ 影像暫無法載入",
                    inline=False
                )
        embed.set_footer(text=f"找到 {len(filtered_cameras)} 個監視器 | 資料來源：公路總局")
        if len(filtered_cameras) > 1:
            view = HighwayCameraView(filtered_cameras, 0)
            await loading_message.edit(embed=embed, view=view)
        else:
            await loading_message.edit(embed=embed)

    async def _get_highway_cameras(self):
        """獲取公路監視器資料"""
        url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=ssl_context, timeout=30) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        return await self._parse_highway_cameras_xml(xml_data)
                    else:
                        logger.error(f"公路監視器 API 請求失敗: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"獲取公路監視器資料失敗: {str(e)}")
            return None

    async def _parse_highway_cameras_xml(self, xml_data):
        """解析公路監視器 XML 資料"""
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(xml_data)
            namespace = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
            
            cameras = []
            cctvs = root.findall('.//ns:CCTV', namespace)
            
            for cctv in cctvs:
                camera_data = {}
                
                # 解析所有子元素
                for child in cctv:
                    tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                    camera_data[tag_name] = child.text
                
                cameras.append(camera_data)
            
            return cameras
            
        except ET.ParseError as e:
            logger.error(f"公路監視器 XML 解析失敗: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"解析公路監視器資料失敗: {str(e)}")
            return None

    async def _process_highway_image_url(self, image_url):
        """處理公路監視器圖片 URL"""
        if not image_url:
            return None
        
        # 檢查基本格式
        if not image_url.startswith(('http://', 'https://')):
            return None
        
        # 公路監視器的圖片可能需要特殊處理，先返回原始 URL 讓 Discord 嘗試載入
        # 如果不行，可以返回一個預設的佔位圖片或 None
        
        # 確保 URL 格式正確
        try:
            # 嘗試不同的後綴
            possible_urls = [
                image_url,
                image_url.rstrip('/') + '/snapshot',
                image_url.rstrip('/') + '/image',
                image_url.rstrip('/') + '.jpg'
            ]
            
            # 由於公路監視器 API 可能需要特殊認證，我們先返回原始 URL
            # Discord 會嘗試載入，如果失敗會顯示預設的破圖圖示
            return possible_urls[0]
            
        except Exception as e:
            logger.error(f"處理公路監視器圖片 URL 失敗: {str(e)}")
            return image_url  # 返回原始 URL

    def _get_city_by_coordinates(self, lat, lon):
        """根據經緯度獲取縣市"""
        try:
            lat = float(lat)
            lon = float(lon)
            
            # 台灣主要縣市經緯度範圍
            city_bounds = {
                "台北市": {"lat": (25.0, 25.3), "lon": (121.4, 121.7)},
                "新北市": {"lat": (24.6, 25.3), "lon": (121.2, 122.0)},
                "桃園市": {"lat": (24.8, 25.1), "lon": (121.0, 121.5)},
                "台中市": {"lat": (24.0, 24.5), "lon": (120.4, 121.0)},
                "台南市": {"lat": (22.9, 23.4), "lon": (120.0, 120.5)},
                "高雄市": {"lat": (22.4, 23.1), "lon": (120.1, 120.7)},
                "基隆市": {"lat": (25.1, 25.2), "lon": (121.6, 121.8)},
                "新竹市": {"lat": (24.7, 24.9), "lon": (120.9, 121.1)},
                "新竹縣": {"lat": (24.4, 25.0), "lon": (120.7, 121.2)},
                "苗栗縣": {"lat": (24.2, 24.8), "lon": (120.5, 121.1)},
                "彰化縣": {"lat": (23.8, 24.3), "lon": (120.3, 120.8)},
                "雲林縣": {"lat": (23.4, 23.9), "lon": (120.1, 120.6)},
                "嘉義縣": {"lat": (23.2, 23.7), "lon": (120.1, 120.7)},
                "屏東縣": {"lat": (22.0, 23.0), "lon": (120.2, 120.9)},
                "宜蘭縣": {"lat": (24.2, 24.8), "lon": (121.3, 122.0)},
                "花蓮縣": {"lat": (23.0, 24.5), "lon": (121.0, 121.8)},
                "台東縣": {"lat": (22.3, 23.5), "lon": (120.8, 121.6)}
            }
            
            # 檢查每個縣市的範圍
           
            for city, bounds in city_bounds.items():
                lat_min, lat_max = bounds["lat"]
                lon_min, lon_max = bounds["lon"]
                
                if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                    return city
            
            return None
            
        except (ValueError, TypeError):
            return None

    def _classify_road_type(self, camera):
        """根據監視器資料判斷道路類型"""
        road_name = camera.get('RoadName', '').lower()
        surveillance_desc = camera.get('SurveillanceDescription', '').lower()
        road_class = camera.get('RoadClass', '')
        road_id = camera.get('RoadID', '')
        
        # 快速公路判斷 (優先判斷，避免被誤分為國道)
        if any([
            '快速' in surveillance_desc,
            '快速公路' in surveillance_desc,
            road_name.startswith('台') and any(num in road_name for num in ['62', '64', '68', '72', '74', '76', '78', '82', '84', '86', '88']),
            '快速道路' in surveillance_desc,
            any(term in road_id for term in ['62', '64', '68', '72', '74', '76', '78', '82', '84', '86', '88']),
            # 明確的台X線快速公路
            (road_name.startswith('台') and any(c.isdigit() for c in road_name) and 
             any(keyword in surveillance_desc for keyword in ['快速', '交流道', '系統交流道']))
        ]):
            return 'freeway'
        
        # 國道判斷 (在快速公路之後判斷)
        elif any([
            # 明確的國道關鍵字
            '國道' in surveillance_desc,
            '高速公路' in surveillance_desc,
            'freeway' in surveillance_desc and '快速' not in surveillance_desc,
            'highway' in surveillance_desc and '快速' not in surveillance_desc,
            # 國道編號格式
            any(term in surveillance_desc for term in ['國1', '國3', '國5', '國6', '國8', '國10']),
            any(term in road_name for term in ['n1', 'n3', 'n5', 'n6', 'n8', 'n10']),
            # 國道ID格式 (但要排除快速公路)
            (road_class == '1' and 
             not any(keyword in surveillance_desc for keyword in ['快速', '台62', '台64', '台68', '台72', '台74', '台76', '台78', '台82', '台84', '台86', '台88']) and
             not road_name.startswith('台'))
        ]):
            return 'national'
        
        # 省道判斷
        elif any([
            road_name.startswith('台') and any(c.isdigit() for c in road_name) and '快速' not in surveillance_desc,  # 台1線、台9線等 (排除快速公路)
            '省道' in surveillance_desc,
            '台' in road_name and '線' in road_name and '快速' not in surveillance_desc,
            road_class == '2',  # 道路分類2可能代表省道
            any(term in road_id for term in ['20', '21', '22', '23', '24', '25', '26', '27', '28', '29'])
        ]):
            return 'provincial'
        
        # 一般道路
        else:
            return 'general'

    # ...existing code...

class HighwayCameraView(discord.ui.View):
    """公路監視器切換介面"""
    
    def __init__(self, cameras, current_index=0):
        super().__init__(timeout=300)
        self.cameras = cameras
        self.current_index = current_index
        self.total_cameras = len(cameras)
        
        # 更新按鈕狀態
        self._update_buttons()
    
    def _update_buttons(self):
        """更新按鈕狀態"""
        # 清除現有按鈕
        self.clear_items()
        
        # 上一個按鈕
        if self.current_index > 0:
            self.add_item(self.PreviousButton(self))
        
        # 刷新按鈕
        self.add_item(self.RefreshButton(self))
        
        # 下一個按鈕
        if self.current_index < self.total_cameras - 1:
            self.add_item(self.NextButton(self))
        
        # 資訊按鈕
        self.add_item(self.InfoButton(self))
    
    class PreviousButton(discord.ui.Button):
        def __init__(self, parent_view):
            super().__init__(style=discord.ButtonStyle.secondary, label="⬅️ 上一個", row=0)
            self.parent_view = parent_view
        
        async def callback(self, interaction: discord.Interaction):
            view = self.parent_view
            view.current_index -= 1
            view._update_buttons()
            
            camera = view.cameras[view.current_index]
            embed = await view._create_highway_camera_embed(camera, interaction)
            
            await interaction.response.edit_message(embed=embed, view=view)
    
    class NextButton(discord.ui.Button):
        def __init__(self, parent_view):
            super().__init__(style=discord.ButtonStyle.secondary, label="➡️ 下一個", row=0)
            self.parent_view = parent_view
        
        async def callback(self, interaction: discord.Interaction):
            view = self.parent_view
            view.current_index += 1
            view._update_buttons()
            
            camera = view.cameras[view.current_index]
            embed = await view._create_highway_camera_embed(camera, interaction)
            
            await interaction.response.edit_message(embed=embed, view=view)
    
    class RefreshButton(discord.ui.Button):
        def __init__(self, parent_view):
            super().__init__(style=discord.ButtonStyle.primary, label="🔄 刷新", row=0)
            self.parent_view = parent_view
        
        async def callback(self, interaction: discord.Interaction):
            view = self.parent_view
            camera = view.cameras[view.current_index]
            embed = await view._create_highway_camera_embed(camera, interaction)
            
            await interaction.response.edit_message(embed=embed, view=view)
    
    class InfoButton(discord.ui.Button):
        def __init__(self, parent_view):
            super().__init__(style=discord.ButtonStyle.success, label="ℹ️ 詳細", row=0)
            self.parent_view = parent_view
        
        async def callback(self, interaction: discord.Interaction):
            view = self.parent_view
            camera = view.cameras[view.current_index]
            
            modal = HighwayCameraInfoModal(camera, view.current_index + 1, view.total_cameras)
            await interaction.response.send_modal(modal)
    
    async def _create_highway_camera_embed(self, camera, interaction=None):
        """創建公路監視器 Embed"""
        embed = discord.Embed(
            title="🛣️ 公路監視器",
            description=f"**{camera.get('SurveillanceDescription', '未知位置')}**",
            color=discord.Color.blue()
        )
        
        # 基本資訊
        # 獲取 ReservoirCommands 實例來使用道路分類方法
        road_type_display = {
            "national": "🛣️ 國道",
            "provincial": "🛤️ 省道", 
            "freeway": "🏎️ 快速公路",
            "general": "🚗 一般道路"
        }
        
        cog = None
        # 嘗試從 interaction 獲取 cog
        if interaction and interaction.client:
            cog = discord.utils.get(interaction.client.cogs.values(), qualified_name='ReservoirCommands')
        
        camera_road_type = 'general'  # 預設值
        if cog and hasattr(cog, '_classify_road_type'):
            camera_road_type = cog._classify_road_type(camera)
        road_type_text = road_type_display.get(camera_road_type, "🛣️ 未知")
        
        embed.add_field(
            name="📍 基本資訊",
            value=f"🛣️ 道路：{camera.get('RoadName', '未知')}\n"
                  f"🏷️ 類型：{road_type_text}\n"
                  f"📍 里程：{camera.get('LocationMile', '未知')}\n"
                  f"🧭 方向：{camera.get('RoadDirection', '未知')}\n"
                  f"� ID：{camera.get('CCTVID', '未知')}",
            inline=True
        )
        
        # 位置資訊
        lat = camera.get('PositionLat', '未知')
        lon = camera.get('PositionLon', '未知')
        estimated_city = "未知"
        if lat != '未知' and lon != '未知' and cog:
            estimated_city = cog._get_city_by_coordinates(lat, lon) or "未知"
        
        embed.add_field(
            name="🌍 座標位置",
            value=f"�️ 縣市：{estimated_city}\n"
                  f"🌐 經度：{lon}\n"
                  f"🌐 緯度：{lat}",
            inline=True
        )
        
        # 圖片處理
        image_url = camera.get('VideoImageURL')
        if image_url:
            # 使用已經獲取的 cog 實例
            try:
                if cog and hasattr(cog, '_process_highway_image_url'):
                    processed_url = await cog._process_highway_image_url(image_url)
                    if processed_url:
                        embed.set_image(url=processed_url)
                        embed.add_field(
                            name="📸 影像狀態",
                            value="✅ 即時影像",
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="📸 影像狀態",
                            value="❌ 影像暫無法載入",
                            inline=False
                        )
                else:
                    # 如果無法獲取 cog，直接使用原始 URL
                    embed.set_image(url=image_url)
                    embed.add_field(
                        name="📸 影像狀態",
                        value="📸 影像",
                        inline=False
                    )
            except Exception as e:
                # 發生錯誤時使用原始 URL
                embed.set_image(url=image_url)
        
        embed.set_footer(text=f"監視器 {self.current_index + 1}/{self.total_cameras} | 資料來源：公路總局")
        
        return embed

class HighwayCameraInfoModal(discord.ui.Modal, title="🛣️ 公路監視器詳細資訊"):
    """公路監視器詳細資訊彈窗"""
    
    def __init__(self, camera, current_num, total_num):
        super().__init__()
        self.camera = camera
        
        # 創建詳細資訊文本
        info_text = f"監視器編號: {camera.get('CCTVID', '未知')}\n"
        info_text += f"道路名稱: {camera.get('RoadName', '未知')}\n"
        info_text += f"道路等級: {camera.get('RoadClass', '未知')}\n"
        info_text += f"行駛方向: {camera.get('RoadDirection', '未知')}\n"
        info_text += f"位置里程: {camera.get('LocationMile', '未知')}\n"
        info_text += f"經度: {camera.get('PositionLon', '未知')}\n"
        info_text += f"緯度: {camera.get('PositionLat', '未知')}\n"
        info_text += f"影像串流: {camera.get('VideoStreamURL', '未知')}\n"
        info_text += f"影像快照: {camera.get('VideoImageURL', '未知')}\n"
        info_text += f"監視器描述: {camera.get('SurveillanceDescription', '未知')}"
        
        self.info_field = discord.ui.TextInput(
            label=f"詳細資訊 ({current_num}/{total_num})",
            style=discord.TextStyle.paragraph,
            default=info_text,
            max_length=4000
        )
        self.add_item(self.info_field)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("📋 資訊已顯示在上方文字框中", ephemeral=True)

async def setup(bot):
    """設置 Cog"""
    await bot.add_cog(ReservoirCommands(bot))
