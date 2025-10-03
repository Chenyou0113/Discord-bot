import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict, List

class HelpCategorySelect(discord.ui.Select):
    """幫助指令的分類選擇器"""
    
    def __init__(self, help_cog):
        self.help_cog = help_cog
        
        # 定義指令分類
        options = [
            discord.SelectOption(
                label="📊 基本功能",
                description="基本的機器人功能與測試指令",
                emoji="🤖",
                value="basic"
            ),
            discord.SelectOption(
                label="🌋 災害資訊",
                description="地震、海嘯等災害資訊查詢",
                emoji="⚠️",
                value="disaster"
            ),
            discord.SelectOption(
                label="🚊 交通資訊",
                description="台鐵、高鐵、捷運即時資訊",
                emoji="🚇",
                value="transport"
            ),
            discord.SelectOption(
                label="🌤️ 天氣資訊",
                description="天氣預報、氣象站資料查詢",
                emoji="⛅",
                value="weather"
            ),
            discord.SelectOption(
                label="💨 空氣品質",
                description="全台空氣品質監測資訊",
                emoji="🌬️",
                value="air_quality"
            ),
            discord.SelectOption(
                label="📡 雷達資訊",
                description="降雨雷達圖與氣象雷達",
                emoji="🛰️",
                value="radar"
            ),
            discord.SelectOption(
                label="🌡️ 溫度資訊",
                description="全台溫度分布監測",
                emoji="🔥",
                value="temperature"
            ),
            discord.SelectOption(
                label="💧 水文資訊",
                description="水庫、河川水位等水文資料",
                emoji="🌊",
                value="water"
            ),
            discord.SelectOption(
                label="🎮 互動功能",
                description="等級系統、語音房設置",
                emoji="🎯",
                value="interactive"
            ),
            discord.SelectOption(
                label="🔧 管理功能",
                description="伺服器管理與開發者工具",
                emoji="⚙️",
                value="admin"
            )
        ]
        
        super().__init__(
            placeholder="請選擇要查看的指令分類...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        """處理分類選擇"""
        selected_category = self.values[0]
        embed = self.help_cog.create_category_embed(selected_category)
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    """幫助指令的視圖"""
    
    def __init__(self, help_cog):
        super().__init__(timeout=300)
        self.help_cog = help_cog
        self.add_item(HelpCategorySelect(help_cog))
    
    @discord.ui.button(label="回到主頁", style=discord.ButtonStyle.secondary, emoji="🏠")
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """回到幫助主頁"""
        embed = self.help_cog.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """超時處理"""
        for item in self.children:
            item.disabled = True

class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.GREETING = "你好！我是AI助手 🤖"
        
        # 定義指令分類
        self.command_categories = {
            "basic": {
                "name": "📊 基本功能",
                "description": "機器人的基本功能與測試指令",
                "commands": [
                    {"name": "hello", "description": "跟機器人打招呼"},
                    {"name": "ping", "description": "檢查機器人延遲時間"},
                    {"name": "latency", "description": "檢查機器人的延遲時間（中文版）"},
                    {"name": "help", "description": "顯示所有可用指令的幫助資訊"}
                ]
            },
            "disaster": {
                "name": "🌋 災害資訊",
                "description": "地震、海嘯等自然災害資訊查詢",
                "commands": [
                    {"name": "earthquake", "description": "查詢最新地震資訊"},
                    {"name": "tsunami", "description": "查詢最新海嘯資訊"},
                    {"name": "set_earthquake_channel", "description": "設定地震通知頻道（需管理員權限）"}
                ]
            },
            "transport": {
                "name": "🚊 交通資訊",
                "description": "台鐵、高鐵、捷運等大眾運輸即時資訊",
                "commands": [
                    {"name": "railway_incident", "description": "查詢台鐵或高鐵事故資訊"},
                    {"name": "tra_news", "description": "查詢台鐵最新消息"},
                    {"name": "thsr_news", "description": "查詢高鐵最新消息"},
                    {"name": "metro_status", "description": "查詢各捷運系統運行狀態"},
                    {"name": "metro_liveboard", "description": "查詢捷運車站即時到離站電子看板"},
                    {"name": "metro_direction", "description": "查詢捷運車站上行/下行方向即時看板"},
                    {"name": "tra_liveboard", "description": "查詢台鐵車站即時電子看板"},
                    {"name": "tra_delay", "description": "查詢台鐵列車誤點資訊"},
                    {"name": "metro_news", "description": "查詢捷運系統最新消息與公告"},
                    {"name": "metro_facility", "description": "查詢捷運車站設施資料"},
                    {"name": "metro_network", "description": "查詢捷運路網資料"}
                ]
            },
            "weather": {
                "name": "🌤️ 天氣資訊",
                "description": "天氣預報、氣象站資料等氣象資訊",
                "commands": [
                    {"name": "weather_stations", "description": "查詢中央氣象署無人氣象測站基本資料"},
                    {"name": "county_weather_stations", "description": "按縣市查詢無人氣象測站"},
                    {"name": "station_details", "description": "查詢特定測站的詳細資訊"},
                    {"name": "weather", "description": "查詢台灣天氣觀測資訊"}
                ]
            },
            "air_quality": {
                "name": "💨 空氣品質",
                "description": "全台空氣品質監測站資訊查詢",
                "commands": [
                    {"name": "air_quality", "description": "查詢空氣品質資訊"},
                    {"name": "air_quality_county", "description": "按縣市查詢空氣品質"},
                    {"name": "air_station", "description": "查詢特定測站的詳細空氣品質資訊"}
                ]
            },
            "radar": {
                "name": "📡 雷達資訊",
                "description": "降雨雷達圖與氣象雷達監測",
                "commands": [
                    {"name": "radar", "description": "查詢台灣雷達圖整合（無地形）"},
                    {"name": "radar_info", "description": "雷達圖功能說明"},
                    {"name": "large_radar", "description": "查詢台灣大範圍雷達圖整合"},
                    {"name": "rainfall_radar", "description": "查詢降雨雷達圖（樹林/南屯/林園）"}
                ]
            },
            "temperature": {
                "name": "🌡️ 溫度資訊",
                "description": "全台溫度分布監測資訊",
                "commands": [
                    {"name": "temperature", "description": "查詢台灣溫度分布狀態"}
                ]
            },
            "water": {
                "name": "💧 水文資訊",
                "description": "水庫、河川水位等水文資料查詢",
                "commands": [
                    {"name": "water_level", "description": "查詢全台河川水位即時資料"},
                    {"name": "reservoir_list", "description": "顯示台灣主要水庫列表"}
                ]
            },
            "interactive": {
                "name": "🎮 互動功能",
                "description": "等級系統、語音房設置等互動功能",
                "commands": [
                    {"name": "level", "description": "查看你的等級資訊"},
                    {"name": "rank", "description": "查看自己或其他人的等級"},
                    {"name": "leaderboard", "description": "顯示伺服器等級排行榜"},
                    {"name": "setup_voice", "description": "設置自動語音房系統"}
                ]
            },
            "admin": {
                "name": "🔧 管理功能",
                "description": "伺服器管理與開發者工具（需要管理員權限）",
                "commands": [
                    {"name": "dev_tools", "description": "開發者工具（僅限管理員）"},
                    {"name": "set_level_channel", "description": "設定等級通知頻道"},
                    {"name": "clear_level_channel", "description": "清除等級通知頻道"},
                    {"name": "toggle_level_system", "description": "開啟/關閉等級系統"},
                    {"name": "level_system_status", "description": "查看等級系統狀態"},
                    {"name": "set_monitor_channel", "description": "設定監控頻道"},
                    {"name": "monitor", "description": "查看系統監控資訊"}
                ]
            }
        }
    
    def create_main_embed(self):
        """創建主要的幫助頁面"""
        embed = discord.Embed(
            title="🤖 機器人指令幫助",
            description="歡迎使用多功能 Discord 機器人！\n請從下方選單選擇要查看的指令分類。",
            color=0x3498DB
        )
        
        # 統計指令數量
        total_commands = sum(len(category["commands"]) for category in self.command_categories.values())
        
        embed.add_field(
            name="📊 指令統計",
            value=f"• 總指令數：**{total_commands}** 個\n• 分類數：**{len(self.command_categories)}** 種",
            inline=False
        )
        
        embed.add_field(
            name="🎯 如何使用",
            value="1. 使用下方的**下拉選單**選擇指令分類\n2. 點擊 🏠 **回到主頁**按鈕返回此頁面\n3. 所有指令都使用 `/` 開頭",
            inline=False
        )
        
        embed.add_field(
            name="⚡ 快速分類",
            value=(
                "📊 **基本功能** - 測試與基本操作\n"
                "🌋 **災害資訊** - 地震、海嘯警報\n"
                "🚊 **交通資訊** - 台鐵、高鐵、捷運\n"
                "🌤️ **天氣資訊** - 氣象預報與觀測\n"
                "💨 **空氣品質** - 環境監測資訊\n"
                "🎮 **互動功能** - 等級系統與遊戲"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🔧 管理功能",
            value=(
                "📡 **雷達資訊** - 氣象雷達圖\n"
                "🌡️ **溫度資訊** - 溫度分布監測\n"
                "💧 **水文資訊** - 水庫、河川資料\n"
                "⚙️ **管理功能** - 伺服器管理工具"
            ),
            inline=True
        )
        
        embed.set_footer(
            text="💡 提示：選單將在 5 分鐘後自動失效 | 由 CY 開發",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        return embed
    
    def create_category_embed(self, category_key: str):
        """創建特定分類的幫助頁面"""
        if category_key not in self.command_categories:
            return self.create_main_embed()
        
        category = self.command_categories[category_key]
        
        embed = discord.Embed(
            title=f"{category['name']}",
            description=category['description'],
            color=0x2ECC71
        )
        
        # 分批顯示指令，每個 field 最多 10 個指令
        commands = category['commands']
        batch_size = 10
        
        for i in range(0, len(commands), batch_size):
            batch = commands[i:i + batch_size]
            field_name = f"📋 可用指令 ({i//batch_size + 1})" if len(commands) > batch_size else "📋 可用指令"
            
            command_list = []
            for cmd in batch:
                command_list.append(f"`/{cmd['name']}` - {cmd['description']}")
            
            embed.add_field(
                name=field_name,
                value="\n".join(command_list),
                inline=False
            )
        
        embed.add_field(
            name="💡 使用說明",
            value="• 所有指令都以 `/` 開頭\n• 部分指令需要管理員權限\n• 有些指令提供互動式選單",
            inline=False
        )
        
        embed.set_footer(
            text=f"分類：{category['name']} | 共 {len(commands)} 個指令 | 點擊 🏠 返回主頁"
        )
        
        return embed

    @app_commands.command(name="help", description="顯示所有可用指令的幫助資訊")
    async def help_command(self, interaction: discord.Interaction):
        """顯示互動式的幫助指令選單"""
        try:
            view = HelpView(self)
            embed = self.create_main_embed()
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ 錯誤",
                description="無法載入幫助選單，請稍後再試。",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @app_commands.command(name="hello", description="跟機器人打招呼")
    async def hello(self, interaction: discord.Interaction):
        """簡單的打招呼指令，固定使用中文回應"""
        # 由於這是中文指令「你好」，直接使用中文回應
        response = "你好！我是AI助手 🤖\n很高興為你服務！"
        await interaction.response.send_message(response)

    @app_commands.command(name="latency", description="檢查機器人的延遲時間")
    async def ping_chinese(self, interaction: discord.Interaction):
        """檢查機器人延遲"""
        await interaction.response.send_message(f'🏓 延遲時間: {round(self.bot.latency * 1000)}ms')
        
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f'🏓 Pong! Latency: {latency}ms')

async def setup(bot: commands.Bot):
    await bot.add_cog(BasicCommands(bot))