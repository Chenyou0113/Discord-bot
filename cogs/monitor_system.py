import discord
from discord import app_commands
from discord.ext import commands, tasks
import psutil
import datetime
import platform
import logging

logger = logging.getLogger(__name__)

class MonitorSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.monitor_channel_id = None
        self.monitor_task.start()

    def cog_unload(self):
        self.monitor_task.cancel()

    @app_commands.command(
        name='set_monitor_channel', 
        description='設定監控訊息要發送的頻道（僅限管理員）'
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_monitor_channel(self, interaction: discord.Interaction):
        """設定監控訊息要發送的頻道"""
        self.monitor_channel_id = interaction.channel_id
        await interaction.response.send_message(
            f"✅ 已設定此頻道 {interaction.channel.mention} 為監控訊息頻道！",
            ephemeral=True
        )
        logger.info(f'已設定監控頻道: {interaction.channel.name} ({interaction.channel_id})')

    @app_commands.command(
        name='monitor',
        description='顯示系統監控資訊（所有人都能使用）'
    )
    async def monitor(self, interaction: discord.Interaction):
        """顯示即時系統狀態報告"""
        try:
            await interaction.response.defer()
            
            # 獲取系統資訊
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 獲取機器人資訊
            guilds_count = len(self.bot.guilds)
            users_count = sum(guild.member_count for guild in self.bot.guilds)
            
            # 計算運行時間
            bot_start_time = datetime.datetime.fromtimestamp(psutil.Process().create_time())
            uptime = datetime.datetime.now() - bot_start_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{hours}小時 {minutes}分 {seconds}秒"
            
            # 建立嵌入訊息
            embed = discord.Embed(
                title="🤖 系統監控資訊",
                description="即時系統狀態報告",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            # 添加系統資訊
            embed.add_field(
                name="💻 系統資源",
                value=f"**CPU 使用率:** {cpu_percent}%\n"
                      f"**記憶體使用:** {memory.percent}%\n"
                      f"**硬碟使用:** {disk.percent}%\n"
                      f"**系統平台:** {platform.system()} {platform.release()}",
                inline=False
            )
            
            # 添加機器人資訊
            embed.add_field(
                name="🔧 機器人狀態",
                value=f"**延遲:** {round(self.bot.latency * 1000)}ms\n"
                      f"**伺服器數:** {guilds_count}\n"
                      f"**使用者數:** {users_count}\n"
                      f"**運行時間:** {uptime_str}",
                inline=False
            )
            
            # 添加圖表提示
            embed.set_footer(text=f"請求者: {interaction.user} • 使用 /monitor 隨時查看最新狀態")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"用戶 {interaction.user} 在 {interaction.guild.name} 使用了 monitor 指令")
            
        except Exception as e:
            logger.error(f"執行 monitor 指令時發生錯誤: {e}")
            await interaction.followup.send("❌ 顯示監控資訊時發生錯誤，請稍後再試。")

    @tasks.loop(seconds=600)
    async def monitor_task(self):
        if not self.monitor_channel_id:
            return

        channel = self.bot.get_channel(self.monitor_channel_id)
        if not channel:
            return

        try:
            # 獲取系統資訊
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 獲取機器人資訊
            guilds_count = len(self.bot.guilds)
            users_count = sum(guild.member_count for guild in self.bot.guilds)
            
            # 建立嵌入訊息
            embed = discord.Embed(
                title="🤖 系統監控資訊",
                description="即時系統狀態報告",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            # 添加系統資訊
            embed.add_field(
                name="💻 系統資源",
                value=f"""
                **CPU 使用率:** {cpu_percent}%
                **記憶體使用:** {memory.percent}%
                **硬碟使用:** {disk.percent}%
                **系統平台:** {platform.system()} {platform.release()}
                """,
                inline=False
            )
            
            # 添加機器人資訊
            embed.add_field(
                name="🔧 機器人狀態",
                value=f"""
                **延遲:** {round(self.bot.latency * 1000)}ms
                **伺服器數:** {guilds_count}
                **使用者數:** {users_count}
                **運行時間:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """,
                inline=False
            )

            await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"發送監控訊息時發生錯誤: {e}")

    @monitor_task.before_loop
    async def before_monitor_task(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(MonitorSystem(bot))