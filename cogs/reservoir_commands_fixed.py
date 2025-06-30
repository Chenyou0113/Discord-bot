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
import time
import xml.etree.ElementTree as ET

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
            "10602": "寶二水庫",
            "10701": "永和山水庫",
            "10801": "明德水庫",
            "10901": "鯉魚潭水庫",
            "11001": "德基水庫",
            "11002": "石岡壩",
            "11101": "霧社水庫",
            "11201": "日月潭水庫",
            "11301": "集集攔河堰",
            "11401": "湖山水庫",
            "11501": "仁義潭水庫",
            "11502": "蘭潭水庫",
            "11601": "白河水庫",
            "11602": "烏山頭水庫",
            "11603": "曾文水庫",
            "11604": "南化水庫",
            "11701": "阿公店水庫",
            "11702": "牡丹水庫",
            "11801": "龍鑾潭",
            "11901": "成功水庫",
            "12001": "鳳山水庫"
        }

    async def get_reservoir_data(self):
        """取得水庫水情資料"""
        try:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2F159D49-5DA8-4E98-8960-C2055B89F415"
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"水庫API回應錯誤: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"取得水庫資料時發生錯誤: {str(e)}")
            return []

    async def get_reservoir_operation_data(self):
        """取得水庫操作資料"""
        try:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=1602CA19-B224-4CC3-A06E-2FC396C7B0C9"
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"水庫操作API回應錯誤: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"取得水庫操作資料時發生錯誤: {str(e)}")
            return []

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
        try:
            await interaction.response.defer()
            
            # 取得水位資料
            water_data = await self.get_water_level_data()
            
            if not water_data:
                embed = discord.Embed(
                    title="❌ 無法取得水位資料",
                    description="請稍後再試，或聯繫管理員。",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 篩選資料
            filtered_data = []
            
            for data in water_data:
                # 基本檢查
                if not data.get('StationName'):
                    continue
                
                match = True
                
                # 縣市篩選
                if city:
                    location = data.get('County', '') + data.get('Township', '')
                    normalized_location = self._normalize_county_name(location)
                    if city not in normalized_location:
                        match = False
                
                # 河川篩選
                if river and match:
                    river_name = data.get('RiverName', '')
                    if river.lower() not in river_name.lower():
                        match = False
                
                # 測站篩選
                if station and match:
                    station_name = data.get('StationName', '')
                    if station.lower() not in station_name.lower():
                        match = False
                
                if match:
                    filtered_data.append(data)
            
            if not filtered_data:
                embed = discord.Embed(
                    title="🔍 查無相關測站",
                    description=f"找不到符合條件的水位測站\n條件：{city or ''} {river or ''} {station or ''}",
                    color=0xffa500
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 限制顯示數量
            display_data = filtered_data[:10]
            
            if len(filtered_data) == 1:
                # 單一測站，顯示詳細資訊
                data = filtered_data[0]
                embed = self._create_water_level_embed(data)
                await interaction.followup.send(embed=embed)
            else:
                # 多個測站，顯示列表
                embed = discord.Embed(
                    title="💧 河川水位查詢結果",
                    color=0x00bfff
                )
                
                if len(filtered_data) > 10:
                    embed.description = f"找到 {len(filtered_data)} 個測站，顯示前 10 個："
                else:
                    embed.description = f"找到 {len(filtered_data)} 個測站："
                
                for i, data in enumerate(display_data, 1):
                    station_name = data.get('StationName', '未知測站')
                    river_name = data.get('RiverName', '未知河川')
                    county = self._normalize_county_name(data.get('County', ''))
                    township = data.get('Township', '')
                    water_level = data.get('WaterLevel', 'N/A')
                    
                    location = f"{county} {township}".strip()
                    
                    field_value = f"河川：{river_name}\n位置：{location}\n水位：{water_level} m"
                    embed.add_field(
                        name=f"{i}. {station_name}",
                        value=field_value,
                        inline=True
                    )
                
                embed.set_footer(text="💧 中央氣象署水位資料")
                embed.timestamp = discord.utils.utcnow()
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"查詢水位資料時發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 查詢失敗",
                description="查詢水位資料時發生錯誤，請稍後再試。",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)

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

    # 輔助方法
    async def get_water_level_data(self):
        """取得河川水位資料"""
        try:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"水位API回應錯誤: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"取得水位資料時發生錯誤: {str(e)}")
            return []

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

    def _create_water_level_embed(self, data):
        """建立水位資料 embed"""
        try:
            station_name = data.get('StationName', '未知測站')
            river_name = data.get('RiverName', '未知河川')
            county = self._normalize_county_name(data.get('County', ''))
            township = data.get('Township', '')
            water_level = data.get('WaterLevel', 'N/A')
            
            # 建立 embed
            embed = discord.Embed(
                title=f"💧 {station_name}",
                color=0x00bfff
            )
            
            # 基本資訊
            location = f"{county} {township}".strip()
            embed.add_field(name="🏞️ 河川", value=river_name, inline=True)
            embed.add_field(name="📍 位置", value=location, inline=True)
            embed.add_field(name="💧 水位", value=f"{water_level} m", inline=True)
            
            # 添加水位狀態判斷
            try:
                current_level = float(water_level) if water_level != 'N/A' else 0
                alert_level = data.get('AlertLevel', '')
                action_level = data.get('ActionLevel', '')
                
                alert_level_num = float(alert_level) if alert_level else 0
                action_level_num = float(action_level) if action_level else 0
                
                if current_level >= action_level_num and action_level_num > 0:
                    status = "🚨 危險"
                    color = 0xff0000
                elif current_level >= alert_level_num and alert_level_num > 0:
                    status = "⚠️ 警戒"
                    color = 0xffa500
                else:
                    status = "✅ 正常"
                    color = 0x00ff00
                
                embed.add_field(name="📊 水位狀態", value=status, inline=True)
                embed.color = color
                
            except (ValueError, TypeError):
                embed.add_field(name="📊 水位狀態", value="資料不完整", inline=True)
            
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text="💧 水利署河川水位資料")
            
            return embed
            
        except Exception as e:
            logger.error(f"建立水位 embed 時發生錯誤: {str(e)}")
            return discord.Embed(
                title="❌ 資料處理錯誤",
                description="無法處理水位資料",
                color=0xff0000
            )

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

    async def _create_highway_camera_embed(self, camera_data):
        """建立公路監視器 embed"""
        try:
            road_name = camera_data.get('RoadName', '未知道路')
            location = camera_data.get('LocationDescription', '未知位置')
            direction = camera_data.get('RoadDirection', '')
            
            # 標準化縣市名稱
            normalized_location = self._normalize_county_name(location)
            
            # 建立標題
            title = f"🛣️ {road_name}"
            if direction:
                title += f" ({direction})"
            
            # 建立 embed
            embed = discord.Embed(
                title=title,
                color=0xffa500
            )
            
            # 添加位置資訊
            embed.add_field(name="📍 位置", value=normalized_location, inline=True)
            
            # 添加道路類型
            road_type = self._classify_road_type(road_name)
            embed.add_field(name="🛣️ 道路類型", value=road_type, inline=True)
            
            # 處理圖片URL（加上時間戳避免快取）
            image_url = camera_data.get('VideoURL', '')
            if image_url:
                processed_url = self._process_and_validate_image_url(image_url)
                embed.set_image(url=processed_url)
            
            # 添加時間戳
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text="🛣️ 公路監視系統")
            
            return embed
            
        except Exception as e:
            logger.error(f"建立公路監視器 embed 時發生錯誤: {str(e)}")
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
            embed = await self._create_highway_camera_embed(self.cameras[self.current_index])
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="▶️ 下一個", style=discord.ButtonStyle.primary)
    async def next_camera(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index < len(self.cameras) - 1:
            self.current_index += 1
            self.update_buttons()
            
            # 建立新的 embed
            embed = await self._create_highway_camera_embed(self.cameras[self.current_index])
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="ℹ️ 詳細資訊", style=discord.ButtonStyle.secondary)
    async def show_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = HighwayCameraInfoModal(self.cameras[self.current_index])
        await interaction.response.send_modal(modal)
    
    async def _create_highway_camera_embed(self, camera_data):
        """建立公路監視器 embed"""
        try:
            road_name = camera_data.get('RoadName', '未知道路')
            location = camera_data.get('LocationDescription', '未知位置')
            direction = camera_data.get('RoadDirection', '')
            
            # 標準化縣市名稱
            normalized_location = self._normalize_county_name(location)
            
            # 建立標題
            title = f"🛣️ {road_name}"
            if direction:
                title += f" ({direction})"
            
            # 建立 embed
            embed = discord.Embed(
                title=title,
                color=0xffa500
            )
            
            # 添加位置資訊
            embed.add_field(name="📍 位置", value=normalized_location, inline=True)
            
            # 添加道路類型
            road_type = self._classify_road_type(road_name)
            embed.add_field(name="🛣️ 道路類型", value=road_type, inline=True)
            
            # 處理圖片URL（加上時間戳避免快取）
            image_url = camera_data.get('VideoURL', '')
            if image_url:
                processed_url = self._process_and_validate_image_url(image_url)
                embed.set_image(url=processed_url)
            
            # 添加時間戳
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"🛣️ 公路監視系統 ({self.current_index + 1}/{len(self.cameras)})")
            
            return embed
            
        except Exception as e:
            logger.error(f"建立公路監視器 embed 時發生錯誤: {str(e)}")
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

class HighwayCameraInfoModal(discord.ui.Modal):
    """公路監視器詳細資訊模態框"""
    def __init__(self, camera_data):
        super().__init__(title="監視器詳細資訊")
        self.camera_data = camera_data
    
    async def on_submit(self, interaction: discord.Interaction):
        """提交時顯示詳細資訊"""
        try:
            road_name = self.camera_data.get('RoadName', '未知道路')
            location = self.camera_data.get('LocationDescription', '未知位置')
            direction = self.camera_data.get('RoadDirection', '')
            
            embed = discord.Embed(
                title=f"📋 {road_name} - 詳細資訊",
                color=0xffa500
            )
            
            embed.add_field(name="🛣️ 道路名稱", value=road_name, inline=False)
            embed.add_field(name="📍 位置描述", value=location, inline=False)
            if direction:
                embed.add_field(name="🧭 行車方向", value=direction, inline=True)
            
            # 添加其他可用資訊
            for key, value in self.camera_data.items():
                if key not in ['RoadName', 'LocationDescription', 'RoadDirection', 'VideoURL']:
                    if value:
                        embed.add_field(name=key, value=str(value), inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"顯示公路監視器詳細資訊時發生錯誤: {str(e)}")
            await interaction.response.send_message("❌ 無法顯示詳細資訊", ephemeral=True)

async def setup(bot):
    """設置 Cog"""
    await bot.add_cog(ReservoirCommands(bot))
