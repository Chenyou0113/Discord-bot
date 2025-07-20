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
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

class CameraView(discord.ui.View):
    """監視器分頁顯示的 View 類別"""
    
    def __init__(self, cameras, current_index=0, county=None, road_type=None, command_type="highway"):
        super().__init__(timeout=300)  # 5分鐘後過期
        self.cameras = cameras
        self.current_index = current_index
        self.county = county
        self.road_type = road_type
        self.command_type = command_type
        self.max_index = len(cameras) - 1
        
        # 根據當前位置更新按鈕狀態
        self.update_buttons()
    
    def update_buttons(self):
        """根據當前位置更新按鈕狀態"""
        # 清除現有按鈕
        self.clear_items()
        
        # 上一個按鈕
        if self.current_index > 0:
            prev_button = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="◀️ 上一個",
                custom_id="previous_camera"
            )
            prev_button.callback = self.previous_callback
            self.add_item(prev_button)
        
        # 位置指示器
        pos_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label=f"{self.current_index + 1} / {len(self.cameras)}",
            disabled=True,
            custom_id="position_indicator"
        )
        self.add_item(pos_button)
        
        # 下一個按鈕
        if self.current_index < self.max_index:
            next_button = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="下一個 ▶️",
                custom_id="next_camera"
            )
            next_button.callback = self.next_callback
            self.add_item(next_button)
    
    async def previous_callback(self, interaction: discord.Interaction):
        """上一個按鈕回調"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            
            embed = self.create_embed()
            if embed:
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ 無法載入監視器資料", ephemeral=True)
    
    async def next_callback(self, interaction: discord.Interaction):
        """下一個按鈕回調"""
        if self.current_index < self.max_index:
            self.current_index += 1
            self.update_buttons()
            
            embed = self.create_embed()
            if embed:
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ 無法載入監視器資料", ephemeral=True)
    
    def get_current_camera(self):
        """取得當前監視器資料"""
        if 0 <= self.current_index < len(self.cameras):
            return self.cameras[self.current_index]
        return None
    
    def create_embed(self):
        """創建當前監視器的 embed"""
        camera = self.get_current_camera()
        if not camera:
            return None
        
        # 創建篩選條件描述
        filter_desc = []
        if self.county:
            filter_desc.append(f"縣市: {self.county}")
        if self.road_type:
            if self.command_type == "national":
                filter_desc.append(f"國道: {self.road_type}")
            else:
                filter_desc.append(f"道路: {self.road_type}")
        
        filter_text = " | ".join(filter_desc) if filter_desc else "全部監視器"
        
        # 根據指令類型設定標題和顏色
        if self.command_type == "national":
            title = "🛣️ 國道監視器"
            color = 0x00ff00
        elif self.command_type == "general":
            title = "🚗 一般道路監視器"
            color = 0xff9900
        else:
            title = "🛣️ 公路監視器"
            color = 0x2E8B57
        
        embed = discord.Embed(
            title=title,
            description=f"📍 {camera.get('name', '未知監視器')}",
            color=color,
            timestamp=datetime.datetime.now()
        )
        
        # 篩選條件
        embed.add_field(
            name="🔍 篩選條件",
            value=filter_text,
            inline=False
        )
        
        # 道路資訊
        road_info = []
        if camera.get('road'):
            direction = f" ({camera.get('direction', '')})" if camera.get('direction') else ""
            road_info.append(f"🛣️ 道路: {camera.get('road')}{direction}")
        elif camera.get('highway'):
            direction = f" ({camera.get('direction', '')})" if camera.get('direction') else ""
            road_info.append(f"🛣️ 國道: {camera.get('highway')}{direction}")
        
        if camera.get('mile'):
            road_info.append(f"📏 里程: {camera.get('mile')}")
        
        if road_info:
            embed.add_field(
                name="道路資訊",
                value="\n".join(road_info),
                inline=True
            )
        
        # 位置資訊
        location_info = []
        if camera.get('county'):
            location_info.append(f"📍 縣市: {camera.get('county')}")
        if camera.get('location'):
            location_info.append(f"📍 位置: {camera.get('location')}")
        if camera.get('lat') and camera.get('lon'):
            location_info.append(f"🌐 座標: {camera.get('lat')}, {camera.get('lon')}")
        
        if location_info:
            embed.add_field(
                name="位置資訊",
                value="\n".join(location_info),
                inline=True
            )
        
        # 即時影像連結
        if camera.get('video_url'):
            embed.add_field(
                name="🎥 即時影像",
                value=f"[點擊觀看即時影像]({camera.get('video_url')})",
                inline=False
            )
        
        # 設置監視器快照圖片
        if camera.get('image_url'):
            # 添加時間戳避免快取
            timestamp = int(time.time())
            image_url_with_timestamp = f"{camera.get('image_url')}?t={timestamp}"
            embed.set_image(url=image_url_with_timestamp)
        
        # 統計資訊
        embed.add_field(
            name="📊 瀏覽資訊",
            value=f"第 {self.current_index + 1} / {len(self.cameras)} 個監視器\n資料來源: TDX 運輸資料流通服務平臺",
            inline=False
        )
        
        embed.set_footer(text="💡 使用按鈕切換監視器 | 點擊連結查看即時影像")
        
        return embed

# 設定日誌
logger = logging.getLogger(__name__)

class CameraView(discord.ui.View):
    """監視器分頁顯示的 View 類別"""
    
    def __init__(self, cameras, current_index=0, county=None, road_type=None, command_type="general"):
        super().__init__(timeout=300)  # 5分鐘後過期
        self.cameras = cameras
        self.current_index = current_index
        self.county = county
        self.road_type = road_type
        self.command_type = command_type  # "general", "national", "water"
        self.max_index = len(cameras) - 1
        
        # 根據當前位置更新按鈕狀態
        self.update_buttons()
    
    def update_buttons(self):
        """根據當前位置更新按鈕狀態"""
        # 清除現有按鈕
        self.clear_items()
        
        # 上一個按鈕
        if self.current_index > 0:
            prev_button = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="◀️ 上一個",
                custom_id="previous_camera"
            )
            prev_button.callback = self.previous_callback
            self.add_item(prev_button)
        
        # 位置指示器
        pos_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label=f"{self.current_index + 1} / {len(self.cameras)}",
            disabled=True,
            custom_id="position_indicator"
        )
        self.add_item(pos_button)
        
        # 下一個按鈕
        if self.current_index < self.max_index:
            next_button = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="下一個 ▶️",
                custom_id="next_camera"
            )
            next_button.callback = self.next_callback
            self.add_item(next_button)
    
    async def previous_callback(self, interaction: discord.Interaction):
        """上一個按鈕回調"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            
            embed = self.create_embed()
            if embed:
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ 無法載入監視器資料", ephemeral=True)
    
    async def next_callback(self, interaction: discord.Interaction):
        """下一個按鈕回調"""
        if self.current_index < self.max_index:
            self.current_index += 1
            self.update_buttons()
            
            embed = self.create_embed()
            if embed:
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ 無法載入監視器資料", ephemeral=True)
    
    def get_current_camera(self):
        """取得當前監視器資料"""
        if 0 <= self.current_index < len(self.cameras):
            return self.cameras[self.current_index]
        return None
    
    def create_embed(self):
        """創建當前監視器的 embed"""
        camera = self.get_current_camera()
        if not camera:
            return None
        
        # 根據指令類型設置不同的標題和顏色
        if self.command_type == "national":
            title = "🛣️ 國道監視器"
            color = 0x00ff00
        elif self.command_type == "water":
            title = "🌊 水利防災監控影像"
            color = 0x0099ff
        else:
            title = "🚗 一般道路監視器"
            color = 0xff9900
        
        # 創建篩選條件描述
        filter_desc = []
        if self.county:
            filter_desc.append(f"縣市: {self.county}")
        if self.road_type:
            filter_desc.append(f"道路: {self.road_type}")
        
        filter_text = " | ".join(filter_desc) if filter_desc else "全部監視器"
        
        embed = discord.Embed(
            title=title,
            description=f"📍 {camera.get('name', '未知監視器')}",
            color=color,
            timestamp=datetime.datetime.now()
        )
        
        # 篩選條件
        embed.add_field(
            name="🔍 篩選條件",
            value=filter_text,
            inline=False
        )
        
        # 道路資訊
        road_info = []
        if camera.get('road'):
            direction = f" ({camera.get('direction', '')})" if camera.get('direction') else ""
            road_info.append(f"🛣️ 道路: {camera.get('road')}{direction}")
        elif camera.get('highway'):
            direction = f" ({camera.get('direction', '')})" if camera.get('direction') else ""
            road_info.append(f"🛣️ 國道: {camera.get('highway')}{direction}")
        
        if camera.get('mile'):
            road_info.append(f"📏 里程: {camera.get('mile')}")
        
        if road_info:
            embed.add_field(
                name="道路資訊",
                value="\n".join(road_info),
                inline=True
            )
        
        # 位置資訊
        location_info = []
        if camera.get('county'):
            location_info.append(f"📍 縣市: {camera.get('county')}")
        if camera.get('district'):
            location_info.append(f"🏘️ 區域: {camera.get('district')}")
        if camera.get('location'):
            location_info.append(f"📍 位置: {camera.get('location')}")
        if camera.get('lat') and camera.get('lon'):
            location_info.append(f"🌐 座標: {camera.get('lat')}, {camera.get('lon')}")
        
        if location_info:
            embed.add_field(
                name="位置資訊",
                value="\n".join(location_info),
                inline=True
            )
        
        # 即時影像連結
        if camera.get('video_url'):
            embed.add_field(
                name="🎥 即時影像",
                value=f"[點擊觀看即時影像]({camera.get('video_url')})",
                inline=False
            )
        
        # 設置監視器快照圖片
        image_url = camera.get('image_url')
        if image_url and image_url != "N/A":
            # 添加時間戳避免快取
            timestamp = int(time.time())
            if '?' in image_url:
                image_url_with_timestamp = f"{image_url}&t={timestamp}"
            else:
                image_url_with_timestamp = f"{image_url}?t={timestamp}"
            embed.set_image(url=image_url_with_timestamp)
        
        # 統計資訊
        embed.add_field(
            name="📊 瀏覽資訊",
            value=f"第 {self.current_index + 1} / {len(self.cameras)} 個監視器\n⏰ 更新時間: {datetime.datetime.now().strftime('%H:%M:%S')}\n資料來源: {camera.get('source', 'TDX')}",
            inline=False
        )
        
        return embed

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
        """從位置描述中提取縣市（增強版）"""
        if not location_description:
            return '未知'
        
        location_str = location_description.lower()
        
        # 縣市關鍵字映射（包含更多關鍵字）
        county_keywords = {
            '基隆': ['基隆', '暖暖', '七堵', '安樂'],
            '台北': ['台北', '臺北', '北市', '信義', '松山', '大安', '中山', '中正', '萬華', '文山', '南港', '內湖', '士林', '北投'],
            '新北': ['新北', '板橋', '三重', '中和', '永和', '新店', '新莊', '土城', '蘆洲', '樹林', '汐止', '鶯歌', '三峽', 
                    '淡水', '瑞芳', '五股', '泰山', '林口', '深坑', '石碇', '坪林', '三芝', '石門', '八里', '平溪', '雙溪', 
                    '貢寮', '金山', '萬里', '烏來', '大華', '新北環快'],
            '桃園': ['桃園', '中壢', '平鎮', '八德', '楊梅', '蘆竹', '龜山', '龍潭', '大溪', '大園', '觀音', '新屋', '復興'],
            '新竹': ['新竹', '竹北', '湖口', '新豐', '關西', '芎林', '寶山', '竹東', '五峰', '橫山', '尖石', '北埔', '峨眉'],
            '苗栗': ['苗栗', '頭份', '竹南', '後龍', '通霄', '苑裡', '造橋', '頭屋', '公館', '大湖', '泰安', '銅鑼', '三義', '西湖', '卓蘭', '三灣', '南庄', '獅潭'],
            '台中': ['台中', '臺中', '中市', '北屯', '西屯', '南屯', '太平', '大里', '霧峰', '烏日', '豐原', '后里', '石岡', '東勢', '和平', '新社', '潭子', '大雅', '神岡', '大肚', '沙鹿', '龍井', '梧棲', '清水', '大甲', '外埔', '大安'],
            '彰化': ['彰化', '鹿港', '和美', '線西', '伸港', '福興', '秀水', '花壇', '芬園', '員林', '溪湖', '田中', '大村', '埔鹽', '埔心', '永靖', '社頭', '二水', '北斗', '二林', '田尾', '埤頭', '芳苑', '大城', '竹塘', '溪州'],
            '南投': ['南投', '埔里', '草屯', '竹山', '集集', '名間', '鹿谷', '中寮', '魚池', '國姓', '水里', '信義', '仁愛'],
            '雲林': ['雲林', '斗六', '斗南', '虎尾', '西螺', '土庫', '北港', '古坑', '大埤', '莿桐', '林內', '二崙', '崙背', '麥寮', '東勢', '褒忠', '台西', '元長', '四湖', '口湖', '水林'],
            '嘉義': ['嘉義', '民雄', '大林', '溪口', '新港', '朴子', '東石', '六腳', '太保', '鹿草', '水上', '中埔', '竹崎', '梅山', '番路', '大埔', '阿里山'],
            '台南': ['台南', '南市', '臺南', '永康', '歸仁', '新化', '左鎮', '玉井', '楠西', '南化', '仁德', '關廟', '龍崎', '官田', '麻豆', '佳里', '西港', '七股', '將軍', '學甲', '北門', '新營', '後壁', '白河', '東山', '六甲', '下營', '柳營', '鹽水', '善化', '大內', '山上', '新市', '安定', '安南', '中西', '東區', '南區', '北區', '安平'],
            '高雄': ['高雄', '鳳山', '岡山', '旗山', '美濃', '橋頭', '梓官', '彌陀', '永安', '燕巢', '田寮', '阿蓮', '路竹', '湖內', '茄萣', '仁武', '大社', '鳥松', '大樹', '旗津', '前金', '苓雅', '鹽埕', '鼓山', '三民', '新興', '前鎮', '小港', '左營', '楠梓', '六龜', '內門', '杉林', '甲仙', '桃源', '那瑪夏', '茂林'],
            '屏東': ['屏東', '潮州', '東港', '恆春', '萬丹', '長治', '麟洛', '九如', '里港', '鹽埔', '高樹', '萬巒', '內埔', '竹田', '新埤', '枋寮', '新園', '崁頂', '林邊', '南州', '佳冬', '琉球', '車城', '滿州', '枋山', '三地門', '霧台', '瑪家', '泰武', '來義', '春日', '獅子', '牡丹'],
            '宜蘭': ['宜蘭', '羅東', '蘇澳', '頭城', '礁溪', '壯圍', '員山', '冬山', '五結', '三星', '大同', '南澳'],
            '花蓮': ['花蓮', '鳳林', '玉里', '新城', '吉安', '壽豐', '光復', '豐濱', '瑞穗', '富里', '秀林', '萬榮', '卓溪'],
            '台東': ['台東', '臺東', '成功', '關山', '卑南', '大武', '太麻里', '東河', '長濱', '鹿野', '池上', '綠島', '延平', '海端', '達仁', '金峰', '蘭嶼']
        }
        
        for county, keywords in county_keywords.items():
            for keyword in keywords:
                if keyword in location_str:
                    return f"{county}{'市' if county in ['基隆', '台北', '新北', '桃園', '新竹', '台中', '嘉義', '台南', '高雄'] else '縣'}"
        
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
    
    @app_commands.command(name="水位資訊", description="查詢全台河川水位即時資料（依測站編號）")
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

    @app_commands.command(name="水利監視器(暫時停用)", description="查詢水利防災監控影像(暫時停用)")
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
                        
    @app_commands.command(name="國道監視器(暫時停用)", description="查詢國道監視器(暫時停用)")
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
            # 從環境變數讀取 TDX API 憑證
            client_id = os.getenv('TDX_CLIENT_ID')
            client_secret = os.getenv('TDX_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                await interaction.followup.send("❌ 錯誤: 找不到 TDX API 憑證，請聯繫管理員設定。", ephemeral=True)
                return
            
            # 1. 取得 TDX access token
            token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
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
                    
                    # 創建分頁視圖
                    view = CameraView(
                        cameras=cameras,
                        current_index=0,
                        county=None,
                        road_type=highway,
                        command_type="national"
                    )
                    
                    # 創建第一個監視器的 embed
                    embed = view.create_embed()
                    
                    if embed:
                        await interaction.followup.send(embed=embed, view=view)
                    else:
                        await interaction.followup.send("❌ 無法載入監視器資料，請稍後再試。")
                        
        except Exception as e:
            logger.error(f"查詢國道監視器時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢國道監視器時發生錯誤: {str(e)}")

    @app_commands.command(name="一般道路監視器(暫時停用)", description="查詢一般道路監視器(暫時停用)")
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
                
                # 篩選條件（改進版）
                filtered_cameras = []
                for camera in all_cameras:
                    matches = True
                    
                    # 縣市篩選（增強版）
                    if county and matches:
                        camera_county = camera['county']
                        camera_location = camera['location'].lower()
                        camera_name = camera['name'].lower()
                        camera_road = camera['road'].lower()
                        
                        # 多重匹配策略
                        county_match = False
                        
                        # 1. 直接匹配完整縣市名
                        if county in camera_county:
                            county_match = True
                        
                        # 2. 匹配縣市簡稱
                        county_short = county.replace('市', '').replace('縣', '')
                        if county_short in camera_county or county_short in camera_location or county_short in camera_name:
                            county_match = True
                        
                        # 3. 根據縣市關鍵字匹配（更嚴格的邏輯）
                        county_keywords_map = {
                            '基隆市': ['基隆', '暖暖', '七堵'],
                            '台北市': ['台北', '臺北', '北市', '信義', '松山'],
                            '新北市': ['新北', '板橋', '三重', '中和', '瑞芳', '大華', '五股', '林口'],
                            '桃園市': ['桃園', '中壢', '觀音', '青埔'],
                            '新竹市': ['新竹', '竹北'],
                            '新竹縣': ['新竹', '竹北', '湖口'],
                            '苗栗縣': ['苗栗', '頭份'],
                            '台中市': ['台中', '臺中', '中市'],
                            '彰化縣': ['彰化', '鹿港'],
                            '南投縣': ['南投', '埔里'],
                            '雲林縣': ['雲林', '斗六'],
                            '嘉義市': ['嘉義'],
                            '嘉義縣': ['嘉義'],
                            '台南市': ['台南', '臺南', '南市'],
                            '高雄市': ['高雄', '鳳山'],
                            '屏東縣': ['屏東', '潮州'],
                            '宜蘭縣': ['宜蘭', '羅東', '蘇澳'],
                            '花蓮縣': ['花蓮', '鳳林'],
                            '台東縣': ['台東', '臺東']
                        }
                        
                        # 如果已經從位置描述中正確提取到縣市，優先使用提取結果
                        if camera_county != '未知' and county == camera_county:
                            county_match = True
                        elif county in county_keywords_map and camera_county == '未知':
                            # 只有在無法從位置描述提取縣市時，才使用關鍵字匹配
                            for keyword in county_keywords_map[county]:
                                if keyword in camera_location or keyword in camera_name or keyword in camera_road:
                                    county_match = True
                                    break
                        
                        matches = county_match
                    
                    # 道路篩選
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
                
                # 創建分頁視圖
                view = CameraView(
                    cameras=filtered_cameras,
                    current_index=0,
                    county=county,
                    road_type=road,
                    command_type="general"
                )
                
                # 創建第一個監視器的 embed
                embed = view.create_embed()
                
                if embed:
                    await interaction.followup.send(embed=embed, view=view)
                else:
                    await interaction.followup.send("❌ 無法載入監視器資料，請稍後再試。")
                        
        except Exception as e:
            logger.error(f"查詢一般道路監視器時發生錯誤: {str(e)}")
            await interaction.followup.send(f"❌ 查詢一般道路監視器時發生錯誤: {str(e)}")
async def setup(bot):
    """設置函數，用於載入 Cog"""
    await bot.add_cog(ReservoirCommands(bot))