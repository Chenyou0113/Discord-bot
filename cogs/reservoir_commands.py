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
        """格式化水利防災影像資訊"""
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
            
            # 組合完整地址
            full_location = f"{location}{district}" if location and district else (location or district or "N/A")
            
            # 組合河川資訊
            river_info = f"{basin_name}" if basin_name else "N/A"
            if tributary and tributary != basin_name:
                river_info += f" ({tributary})"
            
            return {
                'station_name': station_name,
                'camera_name': camera_name,
                'location': full_location,
                'river': river_info,
                'image_url': image_url if image_url else "N/A",
                'status': "正常" if status == "1" else "異常" if status == "0" else "未知",
                'coordinates': f"{latitude}, {longitude}" if latitude and longitude else "N/A"
            }
            
        except Exception as e:
            logger.error(f"格式化水利防災影像資訊時發生錯誤: {str(e)}")
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
        await interaction.response.defer()
        
        try:
            # 取得水利防災影像資料
            image_data = await self.get_water_disaster_images()
            
            if not image_data:
                embed = discord.Embed(
                    title="❌ 防災影像資料取得失敗",
                    description="無法取得水利防災影像資料，請稍後再試。",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
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
                await interaction.followup.send(embed=embed)
                
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
                        # 使用新的 View 系統顯示監控器
                        view = WaterCameraView(self, valid_cameras, location)
                        embed = view.create_embed(0)  # 顯示第一個監控器
                        await interaction.followup.send(embed=embed, view=view)
                    else:
                        embed = discord.Embed(
                            title=f"📸 {location} 地區監控點",
                            description=f"找到 {len(found_cameras)} 個監控點，但目前都沒有可用影像。",
                            color=discord.Color.orange()
                        )
                        await interaction.followup.send(embed=embed)
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
                    
                    await interaction.followup.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"水利防災影像指令執行錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 指令執行錯誤",
                description="執行水利防災影像查詢時發生錯誤，請稍後再試。",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

class WaterCameraView(discord.ui.View):
    """水利監視器切換視圖"""
    
    def __init__(self, cog, cameras: list, location: str):
        super().__init__(timeout=300)  # 5分鐘超時
        self.cog = cog
        self.cameras = cameras
        self.location = location
        self.current_index = 0
        self.total_cameras = len(cameras)
        
        # 更新按鈕狀態
        self.update_buttons()
    
    def update_buttons(self):
        """更新按鈕狀態"""
        # 清除現有按鈕
        self.clear_items()
        
        # 上一個按鈕
        prev_button = discord.ui.Button(
            label="◀️ 上一個",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_index == 0)
        )
        prev_button.callback = self.previous_camera
        self.add_item(prev_button)
        
        # 刷新按鈕
        refresh_button = discord.ui.Button(
            label="🔄 刷新",
            style=discord.ButtonStyle.primary,
            emoji="🔄"
        )
        refresh_button.callback = self.refresh_camera
        self.add_item(refresh_button)
        
        # 下一個按鈕
        next_button = discord.ui.Button(
            label="▶️ 下一個",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_index == self.total_cameras - 1)
        )
        next_button.callback = self.next_camera
        self.add_item(next_button)
        
        # 位置資訊按鈕
        info_button = discord.ui.Button(
            label="📍 詳細資訊",
            style=discord.ButtonStyle.success,
            emoji="📍"
        )
        info_button.callback = self.show_detailed_info
        self.add_item(info_button)
    
    def create_embed(self, index: int):
        """創建監視器 embed"""
        if not (0 <= index < self.total_cameras):
            return None
        
        data = self.cameras[index]
        info = self.cog.format_water_image_info(data)
        
        if not info:
            return None
        
        embed = discord.Embed(
            title=f"📸 {info['station_name']}",
            description=f"📍 **位置**: {info['location']}\n"
                      f"🌊 **河川**: {info['river']}\n"
                      f"📡 **狀態**: {info['status']}",
            color=discord.Color.blue()
        )
        
        # 顯示影像
        if info['image_url'] and info['image_url'] != 'N/A':
            embed.set_image(url=info['image_url'])
        else:
            embed.add_field(
                name="⚠️ 影像狀態",
                value="此監控點目前無可用影像",
                inline=False
            )
        
        # 顯示進度資訊
        embed.set_footer(text=f"第 {index + 1} / {self.total_cameras} 個監控點 • {self.location}地區 • 資料來源：經濟部水利署")
        
        return embed
    
    async def previous_camera(self, interaction: discord.Interaction):
        """切換到上一個監視器"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            embed = self.create_embed(self.current_index)
            if embed:
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ 獲取監視器資訊失敗", ephemeral=True)
        else:
            await interaction.response.send_message("📸 已經是第一個監視器了", ephemeral=True)
    
    async def next_camera(self, interaction: discord.Interaction):
        """切換到下一個監視器"""
        if self.current_index < self.total_cameras - 1:
            self.current_index += 1
            self.update_buttons()
            embed = self.create_embed(self.current_index)
            if embed:
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ 獲取監視器資訊失敗", ephemeral=True)
        else:
            await interaction.response.send_message("📸 已經是最後一個監視器了", ephemeral=True)
    
    async def refresh_camera(self, interaction: discord.Interaction):
        """刷新當前監視器"""
        await interaction.response.defer()
        
        try:
            # 重新獲取影像資料
            image_data = await self.cog.get_water_disaster_images()
            if image_data:
                # 重新查找當前監視器的最新資料
                current_camera_data = self.cameras[self.current_index]
                current_station_name = current_camera_data.get('VideoSurveillanceStationName', '')
                
                # 在新資料中找到對應的監視器
                for data in image_data:
                    if data.get('VideoSurveillanceStationName', '') == current_station_name:
                        self.cameras[self.current_index] = data
                        break
                
                embed = self.create_embed(self.current_index)
                if embed:
                    await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
                else:
                    await interaction.followup.send("❌ 刷新失敗", ephemeral=True)
            else:
                await interaction.followup.send("❌ 無法獲取最新資料", ephemeral=True)
                
        except Exception as e:
            await interaction.followup.send("❌ 刷新時發生錯誤", ephemeral=True)
    
    async def show_detailed_info(self, interaction: discord.Interaction):
        """顯示詳細資訊"""
        data = self.cameras[self.current_index]
        info = self.cog.format_water_image_info(data)
        
        if not info:
            await interaction.response.send_message("❌ 無法獲取詳細資訊", ephemeral=True)
            return
        
        detail_embed = discord.Embed(
            title=f"📋 {info['station_name']} 詳細資訊",
            color=discord.Color.green()
        )
        
        detail_embed.add_field(
            name="📍 基本資訊",
            value=f"**監控點名稱**: {info['station_name']}\n"
                  f"**所在縣市**: {info['location']}\n"
                  f"**河川名稱**: {info['river']}\n"
                  f"**運作狀態**: {info['status']}",
            inline=False
        )
        
        if info['coordinates'] != 'N/A':
            detail_embed.add_field(
                name="🗺️ 位置座標",
                value=info['coordinates'],
                inline=False
            )
        
        if info['image_url'] and info['image_url'] != 'N/A':
            detail_embed.add_field(
                name="📸 影像連結",
                value=f"[點擊查看原始影像]({info['image_url']})",
                inline=False
            )
            detail_embed.set_thumbnail(url=info['image_url'])
        
        detail_embed.set_footer(text="資料來源：經濟部水利署 - 水利防災影像監控系統")
        
        await interaction.response.send_message(embed=detail_embed, ephemeral=True)
    
    async def on_timeout(self):
        """超時處理"""
        # 禁用所有按鈕
        for item in self.children:
            item.disabled = True

async def setup(bot):
    """設置 Cog"""
    await bot.add_cog(ReservoirCommands(bot))
