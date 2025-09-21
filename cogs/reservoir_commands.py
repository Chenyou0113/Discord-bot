#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水庫水情查詢指令 (清理版 - 移除監視器功能)
只包含水庫相關功能：水位查詢、水庫清單等
"""

import asyncio
import aiohttp
import discord
import datetime
import json
import ssl
import logging
import xml.etree.ElementTree as ET
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

class ReservoirCommands(commands.Cog):
    """水庫水情查詢指令（無監視器功能）"""
    
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
    
    async def _get_alert_water_levels(self):
        """取得河川警戒水位資料"""
        try:
            api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=47F8D7F2-4D6C-4F78-B90C-C4C7C1C6F7B7"
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        logger.warning(f"警戒水位 API 請求失敗，狀態碼: {response.status}")
                        return {}
                    
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]
                    
                    try:
                        data = json.loads(text)
                        
                        # 檢查資料結構
                        if isinstance(data, dict) and 'AlertingWaterLevel_OPENDATA' in data:
                            records = data['AlertingWaterLevel_OPENDATA']
                        elif isinstance(data, list):
                            records = data
                        else:
                            logger.warning("警戒水位 API 回應格式不符預期")
                            return {}
                        
                        # 建立測站對應表
                        alert_data = {}
                        for record in records:
                            if isinstance(record, dict):
                                station_id = record.get('ST_NO', '')
                                if station_id:
                                    alert_data[station_id] = {
                                        'first_alert': record.get('FirstAlert', ''),
                                        'second_alert': record.get('SecondAlert', ''),
                                        'third_alert': record.get('ThirdAlert', '')
                                    }
                        
                        return alert_data
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"警戒水位 JSON 解析失敗: {e}")
                        return {}
                        
        except Exception as e:
            logger.warning(f"獲取警戒水位資料時發生錯誤: {str(e)}")
            return {}
    
    def _check_water_level_alert(self, water_level, alert_data):
        """檢查水位警戒狀態"""
        if not alert_data or not water_level:
            return "無警戒資料", "⚪"
        
        try:
            water_level_float = float(water_level)
            
            # 取得警戒水位
            first_alert = alert_data.get('first_alert', '')
            second_alert = alert_data.get('second_alert', '')
            third_alert = alert_data.get('third_alert', '')
            
            # 轉換為浮點數（如果可能）
            try:
                first_alert_float = float(first_alert) if first_alert else None
                second_alert_float = float(second_alert) if second_alert else None
                third_alert_float = float(third_alert) if third_alert else None
            except:
                return "無警戒資料", "⚪"
            
            # 檢查警戒等級（假設數值越高警戒等級越高）
            if third_alert_float and water_level_float >= third_alert_float:
                return "三級警戒", "🔴"
            elif second_alert_float and water_level_float >= second_alert_float:
                return "二級警戒", "🟠"
            elif first_alert_float and water_level_float >= first_alert_float:
                return "一級警戒", "🟡"
            else:
                return "正常", "🟢"
                
        except ValueError:
            return "無警戒資料", "⚪"
    
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

    @app_commands.command(name="reservoir_list", description="顯示台灣主要水庫列表")
    async def reservoir_list(self, interaction: discord.Interaction):
        """顯示水庫清單"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🏔️ 台灣主要水庫清單",
                description="以下是台灣主要水庫的基本資訊",
                color=0x4A90E2,
                timestamp=datetime.datetime.now()
            )
            
            # 按地區分組
            northern_reservoirs = [
                ("石門水庫", "10501", "桃園/新竹"),
                ("新山水庫", "10502", "新北"),
                ("翡翠水庫", "10804", "台北/新北")
            ]
            
            central_reservoirs = [
                ("鯉魚潭水庫", "12101", "苗栗"),
                ("德基水庫", "12102", "台中"),
                ("石岡壩", "12103", "台中"),
                ("谷關水庫", "12104", "台中"),
                ("霧社水庫", "12401", "南投"),
                ("日月潭水庫", "12402", "南投")
            ]
            
            southern_reservoirs = [
                ("湖山水庫", "12901", "雲林"),
                ("曾文水庫", "13801", "台南"),
                ("烏山頭水庫", "13802", "台南"),
                ("白河水庫", "13803", "台南"),
                ("阿公店水庫", "14101", "高雄"),
                ("澄清湖水庫", "14102", "高雄"),
                ("牡丹水庫", "14602", "屏東")
            ]
            
            # 北部水庫
            north_text = "\n".join([f"🏔️ **{name}** (ID: {id_num})\n📍 {location}" 
                                   for name, id_num, location in northern_reservoirs])
            embed.add_field(name="🌏 北部地區", value=north_text, inline=False)
            
            # 中部水庫
            central_text = "\n".join([f"🏔️ **{name}** (ID: {id_num})\n📍 {location}" 
                                     for name, id_num, location in central_reservoirs])
            embed.add_field(name="🌄 中部地區", value=central_text, inline=False)
            
            # 南部水庫
            south_text = "\n".join([f"🏔️ **{name}** (ID: {id_num})\n📍 {location}" 
                                   for name, id_num, location in southern_reservoirs])
            embed.add_field(name="🏖️ 南部地區", value=south_text, inline=False)
            
            embed.add_field(
                name="💡 使用方式",
                value="使用 `/水位資訊 station:水庫ID` 可查詢特定水庫的詳細資訊",
                inline=False
            )
            
            embed.set_footer(text="資料來源：經濟部水利署")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"查詢水庫清單時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢水庫清單時發生錯誤: {str(e)}")

async def setup(bot):
    await bot.add_cog(ReservoirCommands(bot))
