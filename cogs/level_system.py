import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import asyncio
from datetime import datetime, timedelta

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'levels.json'
        self.config_file = 'level_config.json'
        self.user_data = {}
        self.cooldowns = {}
        self.level_channels = {}  # 儲存每個伺服器的等級通知頻道
        self.disabled_guilds = set()  # 追蹤已禁用等級系統的伺服器
        self.load_data()
        self.load_config()
        
    def load_data(self):
        """載入等級資料"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.user_data = json.load(f)
        except Exception as e:
            print(f'載入等級資料時發生錯誤: {e}')
            self.user_data = {}

    def load_config(self):
        """載入頻道設定和禁用狀態"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                    # 兼容舊版配置文件
                    if isinstance(config_data, dict):
                        if "level_channels" in config_data:
                            self.level_channels = config_data["level_channels"]
                        else:
                            self.level_channels = config_data
                            
                        # 加載禁用的伺服器列表
                        if "disabled_guilds" in config_data:
                            self.disabled_guilds = set(config_data["disabled_guilds"])
                    else:
                        # 如果是舊格式，直接作為頻道配置
                        self.level_channels = config_data
        except Exception as e:
            print(f'載入配置時發生錯誤: {e}')
            self.level_channels = {}
            self.disabled_guilds = set()

    def save_data(self):
        """儲存等級資料"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f'儲存等級資料時發生錯誤: {e}')

    def save_config(self):
        """儲存頻道設定和禁用狀態"""
        try:
            config_data = {
                "level_channels": self.level_channels,
                "disabled_guilds": list(self.disabled_guilds)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f'儲存配置時發生錯誤: {e}')

    def get_xp_for_level(self, level):
        """計算升級所需經驗值"""
        return 5 * (level ** 2) + 50 * level + 100

    def get_user_data(self, user_id, guild_id):
        """獲取用戶資料"""
        guild_id = str(guild_id)
        user_id = str(user_id)
        
        if guild_id not in self.user_data:
            self.user_data[guild_id] = {}
            
        if user_id not in self.user_data[guild_id]:
            self.user_data[guild_id][user_id] = {
                'level': 1,
                'xp': 0,
                'total_xp': 0,
                'messages': 0
            }
            
        return self.user_data[guild_id][user_id]

    async def add_xp(self, user_id, guild_id, xp_amount):
        """增加經驗值並檢查是否升級"""
        user_data = self.get_user_data(user_id, guild_id)
        user_data['xp'] += xp_amount
        user_data['total_xp'] += xp_amount
        user_data['messages'] += 1
        
        # 檢查是否可以升級
        while user_data['xp'] >= self.get_xp_for_level(user_data['level']):
            user_data['xp'] -= self.get_xp_for_level(user_data['level'])
            user_data['level'] += 1
            return True
            
        self.save_data()
        return False

    async def send_level_up_notification(self, member, level, guild):
        """發送升級通知"""
        guild_id = str(guild.id)
        
        # 檢查是否有設定等級通知頻道
        if guild_id in self.level_channels:
            channel = guild.get_channel(int(self.level_channels[guild_id]))
        else:
            # 尋找等級或發言頻道
            channel = discord.utils.find(
                lambda c: isinstance(c, discord.TextChannel) and 
                         c.permissions_for(guild.me).send_messages and
                         ("等級" in c.name or "level" in c.name.lower() or
                          "發言" in c.name or "chat" in c.name.lower()),
                guild.channels
            )

        if channel:
            embed = discord.Embed(
                title="🎉 等級提升！",
                description=f"恭喜 {member.mention} 升到了 {level} 等！",
                color=discord.Color.gold()
            )
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f'發送升級通知時發生錯誤: {e}')

    @commands.Cog.listener()
    async def on_message(self, message):
        """監聽訊息以增加經驗值"""
        if message.author.bot:
            return
            
        # 檢查伺服器是否禁用了等級系統
        if str(message.guild.id) in self.disabled_guilds:
            return
            
        # 檢查冷卻時間（60秒）
        user_id = str(message.author.id)
        if user_id in self.cooldowns:
            if datetime.now() < self.cooldowns[user_id]:
                return
                
        self.cooldowns[user_id] = datetime.now() + timedelta(seconds=60)
        
        # 隨機給予 15-25 經驗值
        xp = random.randint(15, 25)
        level_up = await self.add_xp(message.author.id, message.guild.id, xp)
        
        # 如果升級了，發送通知
        if level_up:
            user_data = self.get_user_data(message.author.id, message.guild.id)
            await self.send_level_up_notification(message.author, user_data['level'], message.guild)

    @app_commands.command(name='level', description='查看你的等級資訊')
    async def level(self, interaction: discord.Interaction):
        """查看等級資訊指令"""
        user_data = self.get_user_data(interaction.user.id, interaction.guild_id)
        current_xp = user_data['xp']
        level = user_data['level']
        total_xp = user_data['total_xp']
        messages = user_data['messages']
        next_level_xp = self.get_xp_for_level(level)
        
        # 檢查是否為管理員
        is_admin = interaction.user.guild_permissions.administrator
        title_prefix = "👑" if is_admin else "📊"
        
        embed = discord.Embed(
            title=f"{title_prefix} {interaction.user.name} 的等級資訊",
            color=discord.Color.gold() if is_admin else discord.Color.blue()
        )
        
        # 進度條
        progress = (current_xp / next_level_xp) * 20
        progress_bar = '█' * int(progress) + '░' * (20 - int(progress))
        
        embed.add_field(
            name="等級進度", 
            value=f"等級: {level}\n"
                  f"經驗值: {current_xp}/{next_level_xp}\n"
                  f"進度: [{progress_bar}] {(current_xp/next_level_xp)*100:.1f}%", 
            inline=False
        )
        
        embed.add_field(
            name="統計資訊",
            value=f"總經驗值: {total_xp}\n發送訊息數: {messages}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rank", description="查看自己或其他人的等級")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        """查看等級狀態"""
        if member is None:
            member = interaction.user
            
        user_data = self.get_user_data(member.id, interaction.guild_id)
        next_level_xp = self.get_xp_for_level(user_data['level'])
        current_xp = user_data['xp']
        
        progress = (current_xp / next_level_xp) * 100
        
        embed = discord.Embed(title="等級資訊", color=discord.Color.blue())
        embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="等級", value=str(user_data['level']), inline=True)
        embed.add_field(name="經驗值", value=f"{current_xp}/{next_level_xp}", inline=True)
        embed.add_field(name="總經驗值", value=str(user_data['total_xp']), inline=True)
        embed.add_field(name="進度", value=f"{progress:.1f}%", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="顯示伺服器等級排行榜")
    async def leaderboard(self, interaction: discord.Interaction):
        """顯示排行榜"""
        guild_id = str(interaction.guild_id)
        if guild_id not in self.user_data:
            await interaction.response.send_message("目前還沒有任何等級記錄！", ephemeral=True)
            return
            
        # 獲取所有用戶資料並排序
        guild_data = self.user_data[guild_id]
        sorted_users = sorted(guild_data.items(), 
                            key=lambda x: (x[1]['level'], x[1]['xp']),
                            reverse=True)[:10]
        
        embed = discord.Embed(title="🏆 等級排行榜", color=discord.Color.gold())
        
        for index, (user_id, data) in enumerate(sorted_users, 1):
            try:
                member = await interaction.guild.fetch_member(int(user_id))
                name = member.display_name
            except:
                name = f"未知用戶 ({user_id})"
                
            embed.add_field(
                name=f"#{index} {name}",
                value=f"等級: {data['level']} | 經驗值: {data['xp']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="set_level_channel",
        description="設定等級通知頻道（僅限管理員使用）"
    )
    async def set_level_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        """設定等級通知頻道"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 此指令僅限管理員使用！", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        self.level_channels[guild_id] = channel.id
        self.save_config()

        await interaction.response.send_message(
            f"✅ 已設定 {channel.mention} 為等級通知頻道！",
            ephemeral=True
        )

    @app_commands.command(
        name="clear_level_channel",
        description="清除等級通知頻道設定（僅限管理員使用）"
    )
    async def clear_level_channel(self, interaction: discord.Interaction):
        """清除等級通知頻道設定"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 此指令僅限管理員使用！", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        if guild_id in self.level_channels:
            del self.level_channels[guild_id]
            self.save_config()
            await interaction.response.send_message("✅ 已清除等級通知頻道設定！", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ 此伺服器尚未設定等級通知頻道。", ephemeral=True)

    @app_commands.command(
        name="toggle_level_system",
        description="開啟或關閉伺服器的等級系統（僅限管理員使用）"
    )
    async def toggle_level_system(self, interaction: discord.Interaction):
        """開啟或關閉伺服器的等級系統"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 此指令僅限管理員使用！", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        
        # 檢查目前狀態並切換
        if guild_id in self.disabled_guilds:
            self.disabled_guilds.remove(guild_id)
            status = "✅ 已開啟"
        else:
            self.disabled_guilds.add(guild_id)
            status = "❌ 已關閉"
            
        self.save_config()
        
        embed = discord.Embed(
            title="⚙️ 等級系統設定",
            description=f"{status}此伺服器的等級系統。",
            color=discord.Color.blue() if guild_id not in self.disabled_guilds else discord.Color.red()
        )
        
        if guild_id in self.disabled_guilds:
            embed.add_field(
                name="系統狀態",
                value="成員在此伺服器中發送訊息將不再獲得經驗值和等級提升。",
                inline=False
            )
        else:
            embed.add_field(
                name="系統狀態",
                value="成員在此伺服器中發送訊息將獲得經驗值和等級提升。",
                inline=False
            )
            
        embed.set_footer(text="注意：此設定不會影響已有的等級數據。")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="level_system_status",
        description="查看伺服器等級系統的開啟狀態"
    )
    async def level_system_status(self, interaction: discord.Interaction):
        """查看等級系統狀態"""
        guild_id = str(interaction.guild_id)
        
        is_enabled = guild_id not in self.disabled_guilds
        
        embed = discord.Embed(
            title="⚙️ 等級系統狀態",
            description=f"此伺服器的等級系統目前為: {'✅ 開啟' if is_enabled else '❌ 關閉'}",
            color=discord.Color.blue() if is_enabled else discord.Color.red()
        )
        
        if not is_enabled:
            embed.add_field(
                name="如何開啟",
                value="管理員可以使用 `/toggle_level_system` 指令來開啟等級系統。",
                inline=False
            )
        else:
            embed.add_field(
                name="如何關閉",
                value="管理員可以使用 `/toggle_level_system` 指令來關閉等級系統。",
                inline=False
            )
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))