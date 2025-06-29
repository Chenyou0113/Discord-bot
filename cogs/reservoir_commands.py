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
    
    @app_commands.command(name="reservoir_list", description="顯示所有支援查詢的水庫列表")
    async def reservoir_list(self, interaction: discord.Interaction):
        """顯示水庫列表"""
        embed = discord.Embed(
            title="🏞️ 支援查詢的水庫列表",
            description="以下是目前支援查詢的主要水庫：",
            color=discord.Color.green()
        )
        
        # 將水庫按地區分組
        north_reservoirs = []
        central_reservoirs = []
        south_reservoirs = []
        east_reservoirs = []
        
        for reservoir_id, name in self.reservoir_names.items():
            if reservoir_id.startswith('105') or reservoir_id.startswith('201') or reservoir_id.startswith('202'):
                north_reservoirs.append(name)
            elif reservoir_id.startswith('106') or reservoir_id.startswith('107') or reservoir_id.startswith('108') or reservoir_id.startswith('109') or reservoir_id.startswith('110') or reservoir_id.startswith('111') or reservoir_id.startswith('301'):
                central_reservoirs.append(name)
            elif reservoir_id.startswith('112') or reservoir_id.startswith('114') or reservoir_id.startswith('115') or reservoir_id.startswith('116') or reservoir_id.startswith('117') or reservoir_id.startswith('118') or reservoir_id.startswith('119') or reservoir_id.startswith('120') or reservoir_id.startswith('121'):
                south_reservoirs.append(name)
            else:
                east_reservoirs.append(name)
        
        if north_reservoirs:
            embed.add_field(
                name="🏔️ 北部地區",
                value="\n".join([f"• {name}" for name in north_reservoirs]),
                inline=False
            )
        
        if central_reservoirs:
            embed.add_field(
                name="🏞️ 中部地區", 
                value="\n".join([f"• {name}" for name in central_reservoirs]),
                inline=False
            )
        
        if south_reservoirs:
            embed.add_field(
                name="🏖️ 南部地區",
                value="\n".join([f"• {name}" for name in south_reservoirs]),
                inline=False
            )
        
        if east_reservoirs:
            embed.add_field(
                name="🌊 東部地區",
                value="\n".join([f"• {name}" for name in east_reservoirs]),
                inline=False
            )
        
        embed.set_footer(text="💡 使用 /reservoir <水庫名稱> 查詢特定水庫資訊")
        
        await interaction.response.send_message(embed=embed)

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

async def setup(bot):
    """載入 Cog"""
    await bot.add_cog(ReservoirCommands(bot))
    logger.info("水庫水情查詢指令已載入")
