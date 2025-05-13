import discord
import platform
import sys
import datetime
from discord import app_commands
from discord.ext import commands
import logging
import psutil  # 新增此模組來監控系統資源
import asyncio
import google.generativeai as genai
import time
from datetime import timedelta

logger = logging.getLogger(__name__)

def get_size(bytes):
    """轉換記憶體大小格式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.datetime.now()
        self.bot.startup_channels = {}

    async def _check_admin(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 此指令僅限管理員使用！", ephemeral=True)
            return False
        return True

    async def _announce_to_all_guilds(self, embed: discord.Embed):
        """發送公告到所有伺服器的系統訊息頻道"""
        for guild in self.bot.guilds:
            # 尋找適合發送系統訊息的頻道
            channel = discord.utils.find(
                lambda c: isinstance(c, discord.TextChannel) and 
                         c.permissions_for(guild.me).send_messages and
                         ("一般" in c.name or 
                          "通知" in c.name or 
                          "公告" in c.name or
                          "系統" in c.name or
                          c == guild.system_channel),
                guild.channels
            )
            if channel:
                try:
                    await channel.send(embed=embed)
                except Exception:
                    continue

    @app_commands.command(name="shutdown", description="關閉機器人 (僅限管理員使用)")
    async def shutdown(self, interaction: discord.Interaction):
        """關閉機器人"""
        try:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ 此指令僅限管理員使用！", ephemeral=True)
                return
                
            # 使用defer而不是直接發送訊息，避免互動超時
            await interaction.response.defer(ephemeral=True)
            logger.info(f'管理員 {interaction.user} 執行了關閉指令')
            
            # 發送關機公告到系統監控頻道
            embed = discord.Embed(
                title="🛑 系統監控通知",
                description="機器人正在關閉...\n若需要重新啟動，請聯絡管理員。",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"管理員: {interaction.user}")
            
            # 先通知用戶操作已開始
            await interaction.followup.send("🛑 正在關閉機器人...", ephemeral=True)
            
            # 發送到每個伺服器的系統監控頻道
            notification_tasks = []
            for guild in self.bot.guilds:
                channel = discord.utils.find(
                    lambda c: isinstance(c, discord.TextChannel) and 
                             c.permissions_for(guild.me).send_messages and
                             "系統" in c.name and "監控" in c.name,
                    guild.channels
                )
                if channel:
                    try:
                        # 將發送操作添加到任務列表但不等待
                        task = asyncio.create_task(channel.send(embed=embed))
                        notification_tasks.append(task)
                    except Exception as e:
                        logger.error(f'創建發送關機訊息任務到 {guild.name} 的系統監控頻道時發生錯誤: {str(e)}')
            
            # 等待所有通知任務完成，但設定超時時間
            try:
                await asyncio.wait_for(asyncio.gather(*notification_tasks, return_exceptions=True), timeout=2.5)
            except asyncio.TimeoutError:
                logger.warning("部分關機通知可能未發送完成，但將繼續關閉流程")
            
            # 嘗試再次通知用戶
            try:
                await interaction.followup.send("✅ 系統通知已發送，機器人即將關閉！", ephemeral=True)
            except Exception:
                pass  # 忽略可能的報錯，因為我們即將關閉機器人
                
            # 稍微延遲後關閉機器人
            await asyncio.sleep(0.5)
            
            # 關閉機器人
            await self.bot.close()
            
        except Exception as e:
            logger.error(f'關閉時發生錯誤: {str(e)}')
            try:
                await interaction.followup.send(f"❌ 關閉過程發生錯誤: {str(e)}", ephemeral=True)
            except:
                pass

    @app_commands.command(name="status", description="顯示機器人的運行狀態")
    async def status(self, interaction: discord.Interaction):
        """顯示機器人運行狀態"""
        if not await self._check_admin(interaction):
            return

        # 計算運行時間
        current_time = datetime.datetime.now()
        uptime = current_time - self.start_time
        
        # 獲取系統資源使用情況
        process = psutil.Process()
        memory_use = process.memory_info().rss
        cpu_percent = process.cpu_percent(interval=0.1)

        embed = discord.Embed(
            title="🤖 機器人狀態",
            color=discord.Color.blue(),
            timestamp=current_time
        )
        
        # 基本資訊
        embed.add_field(
            name="🔰 基本資訊",
            value=f"""
            **名稱:** {self.bot.user}
            **ID:** {self.bot.user.id}
            **延遲:** {round(self.bot.latency * 1000)}ms
            **上線時間:** {uptime.days}天 {uptime.seconds//3600}時 {(uptime.seconds//60)%60}分
            """,
            inline=False
        )
        
        # 系統資訊
        embed.add_field(
            name="💻 系統資訊",
            value=f"""
            **OS:** {platform.system()} {platform.release()}
            **Python:** {platform.python_version()}
            **Discord.py:** {discord.__version__}
            **CPU使用率:** {cpu_percent}%
            **記憶體使用:** {get_size(memory_use)}
            """,
            inline=False
        )
        
        # 統計資訊
        total_members = sum(len(guild.members) for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        
        embed.add_field(
            name="📊 統計資訊",
            value=f"""
            **伺服器數:** {len(self.bot.guilds)}
            **頻道數:** {total_channels}
            **使用者數:** {total_members}
            """,
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
        embed.set_footer(text=f"請求者: {interaction.user} | 伺服器時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="send", description="發送訊息到指定頻道（僅限管理員）")
    @app_commands.describe(
        channel="要發送訊息的頻道",
        message="要發送的訊息內容"
    )
    async def send_message(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel,
        message: str
    ):
        """發送訊息到指定頻道"""
        if not await self._check_admin(interaction):
            return
        
        try:
            await channel.send(message)
            await interaction.response.send_message(
                f"✅ 訊息已發送到 {channel.mention}",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ 無法發送訊息到該頻道！請確認機器人有足夠的權限。",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"發送訊息時發生錯誤: {str(e)}")
            await interaction.response.send_message(
                "❌ 發送訊息時發生錯誤！",
                ephemeral=True
            )

    @app_commands.command(name="admin_monitor", description="顯示即時系統資源使用狀況（僅限管理員）")
    async def monitor(self, interaction: discord.Interaction):
        """顯示即時系統資源監控資訊（僅限管理員）"""
        if not await self._check_admin(interaction):
            return

        # 獲取系統資源資訊
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        process = psutil.Process()
        process_memory = process.memory_info().rss

        # 獲取網路資訊
        net_io = psutil.net_io_counters()
        bytes_sent = get_size(net_io.bytes_sent)
        bytes_recv = get_size(net_io.bytes_recv)

        embed = discord.Embed(
            title="📊 系統監控儀表板",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        # CPU 資訊
        embed.add_field(
            name="💻 CPU",
            value=f"""
            **使用率:** {cpu_percent}%
            **核心數:** {psutil.cpu_count()} 個
            **處理程序數:** {len(psutil.pids())} 個
            """,
            inline=False
        )

        # 記憶體資訊
        embed.add_field(
            name="🔰 記憶體",
            value=f"""
            **系統總記憶體:** {get_size(memory.total)}
            **已使用:** {get_size(memory.used)} ({memory.percent}%)
            **可用:** {get_size(memory.available)}
            **機器人使用:** {get_size(process_memory)}
            """,
            inline=False
        )

        # 硬碟資訊
        embed.add_field(
            name="💾 硬碟",
            value=f"""
            **總容量:** {get_size(disk.total)}
            **已使用:** {get_size(disk.used)} ({disk.percent}%)
            **可用:** {get_size(disk.free)}
            """,
            inline=False
        )

        # 網路資訊
        embed.add_field(
            name="🌐 網路",
            value=f"""
            **上傳量:** {bytes_sent}
            **下載量:** {bytes_recv}
            **延遲:** {round(self.bot.latency * 1000)}ms
            """,
            inline=False
        )

        # 運行資訊
        uptime = datetime.datetime.now() - self.start_time
        embed.add_field(
            name="⚙️ 運行資訊",
            value=f"""
            **上線時間:** {uptime.days}天 {uptime.seconds//3600}時 {(uptime.seconds//60)%60}分
            **Python 版本:** {platform.python_version()}
            **Discord.py:** {discord.__version__}
            """,
            inline=False
        )

        embed.set_footer(text=f"請求者: {interaction.user} | 更新時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set_startup_channel", description="設定機器人啟動時發送訊息的頻道（僅限管理員）")
    @app_commands.describe(
        channel="選擇要接收機器人啟動訊息的頻道"
    )
    async def set_startup_channel(
        self, 
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        """設定機器人啟動時發送訊息的頻道"""
        if not await self._check_admin(interaction):
            return
        
        # 確認機器人有權限在該頻道發送訊息
        if not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(
                "❌ 機器人沒有在該頻道發送訊息的權限！請選擇其他頻道或授予權限。",
                ephemeral=True
            )
            return
        
        # 儲存頻道設定
        self.bot.startup_channels[interaction.guild.id] = channel.id
        
        # 測試發送訊息
        try:
            test_embed = discord.Embed(
                title="✅ 測試訊息",
                description="這是一則測試訊息。未來機器人啟動時會在此頻道發送通知。",
                color=discord.Color.green()
            )
            await channel.send(embed=test_embed)
            
            await interaction.response.send_message(
                f"✅ 已成功設定啟動訊息頻道為 {channel.mention}\n已發送測試訊息以供確認。",
                ephemeral=True
            )
            logger.info(f'管理員 {interaction.user} 已設定伺服器 {interaction.guild.name} 的啟動訊息頻道為 {channel.name}')
        except Exception as e:
            logger.error(f'設定啟動訊息頻道時發生錯誤: {str(e)}')
            await interaction.response.send_message(
                "❌ 設定過程發生錯誤！請確認機器人權限是否正確。",
                ephemeral=True
            )

    @app_commands.command(name="clear_startup_channel", description="清除機器人啟動訊息頻道的設定（僅限管理員）")
    async def clear_startup_channel(self, interaction: discord.Interaction):
        """清除啟動訊息頻道的設定"""
        if not await self._check_admin(interaction):
            return
        
        # 檢查是否有設定要清除
        if interaction.guild.id not in self.bot.startup_channels:
            await interaction.response.send_message(
                "❌ 此伺服器尚未設定特定的啟動訊息頻道。",
                ephemeral=True
            )
            return
        
        # 清除設定
        del self.bot.startup_channels[interaction.guild.id]
        
        await interaction.response.send_message(
            "✅ 已清除啟動訊息頻道設定。機器人將恢復使用預設的頻道選擇邏輯。",
            ephemeral=True
        )
        logger.info(f'管理員 {interaction.user} 已清除伺服器 {interaction.guild.name} 的啟動訊息頻道設定')

    async def _send_restart_message(self, guild: discord.Guild) -> None:
        """發送重啟訊息到指定伺服器的系統監控頻道"""
        # 先檢查是否有特定設定的啟動頻道
        channel_id = self.bot.startup_channels.get(guild.id)
        channel = None
        
        if channel_id:
            channel = guild.get_channel(channel_id)
        
        # 如果沒有設定或找不到頻道，尋找包含「系統」和「監控」的頻道
        if not channel:
            channel = discord.utils.find(
                lambda c: isinstance(c, discord.TextChannel) and 
                          c.permissions_for(guild.me).send_messages and
                          "系統" in c.name and "監控" in c.name,
                guild.channels
            )
        
        # 如果找到適合的頻道，發送訊息
        if channel:
            try:
                embed = discord.Embed(
                    title="🔄 系統監控通知",
                    description="機器人正在重啟，請稍候...",
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"重啟時間: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                await channel.send(embed=embed)
                logger.info(f'已發送重啟訊息到 {guild.name} 的頻道 {channel.name}')
            except Exception as e:
                logger.error(f'無法發送重啟訊息到 {guild.name} 的頻道: {str(e)}')

    async def emergency_restart(self, ctx):
        """緊急重啟功能"""
        if ctx.author.guild_permissions.administrator:
            await ctx.send("🔄 執行緊急重啟...")
            logger.info(f'管理員 {ctx.author} 執行了緊急重啟')
            try:
                # 發送重啟通知到每個伺服器的系統監控頻道
                embed = discord.Embed(
                    title="🔄 系統監控通知",
                    description="機器人正在執行緊急重啟...\n請稍候片刻！",
                    color=discord.Color.yellow()
                )
                embed.set_footer(text=f"管理員: {ctx.author} | 時間: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                
                for guild in self.bot.guilds:
                    # 尋找系統監控頻道
                    channel = discord.utils.find(
                        lambda c: isinstance(c, discord.TextChannel) and 
                                 c.permissions_for(guild.me).send_messages and
                                 "系統" in c.name and "監控" in c.name,
                        guild.channels
                    )
                    if channel:
                        try:
                            await channel.send(embed=embed)
                        except:
                            continue
                
                await asyncio.sleep(2)
                await self.bot.close()
                
            except Exception as e:
                logger.error(f'緊急重啟時發生錯誤: {str(e)}')
                await ctx.send("❌ 重啟過程發生錯誤！")
        else:
            await ctx.send("❌ 此指令僅限管理員使用！")

    @app_commands.command(name="dev", description="開發者工具（僅限管理員）")
    @app_commands.describe(
        object_type="要查詢的對象類型",
        object_id="對象ID（如未提供則使用當前頻道/使用者）",
        detail_level="詳細程度（基本、中等、全部）"
    )
    @app_commands.choices(
        object_type=[
            app_commands.Choice(name="使用者", value="user"),
            app_commands.Choice(name="頻道", value="channel"),
            app_commands.Choice(name="伺服器", value="guild"),
            app_commands.Choice(name="身分組", value="role"),
            app_commands.Choice(name="訊息", value="message"),
            app_commands.Choice(name="貼圖", value="emoji"),
        ],
        detail_level=[
            app_commands.Choice(name="基本", value="basic"),
            app_commands.Choice(name="中等", value="medium"),
            app_commands.Choice(name="全部", value="all"),
        ]
    )
    async def dev_tools(
        self,
        interaction: discord.Interaction,
        object_type: str,
        object_id: str = None,
        detail_level: str = "basic"
    ):
        """開發者工具 - 提供類似 Discord 開發者模式的功能"""
        if not await self._check_admin(interaction):
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # 根據類型獲取對象
            target_object = None
            
            if object_type == "user":
                if object_id:
                    target_object = self.bot.get_user(int(object_id))
                    if not target_object:
                        try:
                            target_object = await self.bot.fetch_user(int(object_id))
                        except:
                            pass
                else:
                    target_object = interaction.user
                    
            elif object_type == "channel":
                if object_id:
                    target_object = self.bot.get_channel(int(object_id))
                else:
                    target_object = interaction.channel
                    
            elif object_type == "guild":
                if object_id:
                    target_object = self.bot.get_guild(int(object_id))
                else:
                    target_object = interaction.guild
                    
            elif object_type == "role":
                if object_id:
                    target_object = interaction.guild.get_role(int(object_id))
                    
            elif object_type == "message":
                if object_id:
                    try:
                        # 嘗試解析 channel_id-message_id 格式
                        if '-' in object_id:
                            channel_id, msg_id = object_id.split('-')
                            channel = self.bot.get_channel(int(channel_id))
                            if channel:
                                try:
                                    target_object = await channel.fetch_message(int(msg_id))
                                except:
                                    pass
                        else:
                            # 假設是當前頻道的消息
                            try:
                                target_object = await interaction.channel.fetch_message(int(object_id))
                            except:
                                pass
                    except:
                        pass
                        
            elif object_type == "emoji":
                if object_id:
                    for guild in self.bot.guilds:
                        emoji = discord.utils.get(guild.emojis, id=int(object_id))
                        if emoji:
                            target_object = emoji
                            break
            
            if not target_object:
                await interaction.followup.send(f"❌ 找不到指定的 {object_type} 對象。請檢查 ID 是否正確。", ephemeral=True)
                return
                
            # 創建嵌入訊息
            embed = discord.Embed(
                title=f"🔧 開發者查詢：{object_type.capitalize()}",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            # 獲取基本信息
            basic_info = {}
            
            # 所有對象都有 ID
            basic_info["ID"] = f"`{target_object.id}`"
            
            # 對象類型特定的屬性
            if object_type == "user":
                basic_info["名稱"] = target_object.name
                basic_info["建立時間"] = target_object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                basic_info["機器人"] = "是" if target_object.bot else "否"
                
                if detail_level in ["medium", "all"]:
                    basic_info["個人頭像"] = target_object.avatar.url if target_object.avatar else "無"
                    basic_info["橫幅顏色"] = str(target_object.accent_color) if target_object.accent_color else "無"
                
                if detail_level == "all":
                    member = interaction.guild.get_member(target_object.id)
                    if member:
                        basic_info["伺服器暱稱"] = member.nick or "無"
                        basic_info["加入時間"] = member.joined_at.strftime('%Y-%m-%d %H:%M:%S') if member.joined_at else "未知"
                        basic_info["頂層身分組"] = member.top_role.name if len(member.roles) > 1 else "無"
                        basic_info["身分組數量"] = str(len(member.roles) - 1)  # 減去 @everyone
                    
            elif object_type == "channel":
                basic_info["名稱"] = target_object.name
                basic_info["類型"] = str(target_object.type).replace("ChannelType.", "")
                basic_info["位置"] = str(target_object.position) if hasattr(target_object, "position") else "N/A"
                
                if detail_level in ["medium", "all"]:
                    if hasattr(target_object, "category") and target_object.category:
                        basic_info["分類"] = target_object.category.name
                    if hasattr(target_object, "topic") and target_object.topic:
                        basic_info["主題"] = target_object.topic
                    if hasattr(target_object, "slowmode_delay"):
                        basic_info["慢速模式"] = f"{target_object.slowmode_delay}秒" if target_object.slowmode_delay > 0 else "關閉"
                
                if detail_level == "all" and hasattr(target_object, "overwrites"):
                    overwrites = len(target_object.overwrites)
                    basic_info["權限覆蓋數"] = str(overwrites)
            
            elif object_type == "guild":
                basic_info["名稱"] = target_object.name
                basic_info["擁有者"] = f"{target_object.owner.name} (ID: {target_object.owner_id})" if target_object.owner else f"ID: {target_object.owner_id}"
                basic_info["成員數"] = str(target_object.member_count)
                basic_info["建立時間"] = target_object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                
                if detail_level in ["medium", "all"]:
                    basic_info["表情符號數量"] = str(len(target_object.emojis))
                    basic_info["頻道數量"] = str(len(target_object.channels))
                    basic_info["身分組數量"] = str(len(target_object.roles))
                    basic_info["加成等級"] = str(target_object.premium_tier)
                    basic_info["加成數量"] = str(target_object.premium_subscription_count)
                
                if detail_level == "all":
                    basic_info["區域"] = str(target_object.region) if hasattr(target_object, "region") else "N/A"
                    basic_info["驗證等級"] = str(target_object.verification_level)
                    basic_info["明確內容過濾"] = str(target_object.explicit_content_filter)
                    basic_info["預設通知"] = str(target_object.default_notifications)
            
            elif object_type == "role":
                basic_info["名稱"] = target_object.name
                basic_info["顏色"] = str(target_object.color)
                basic_info["位置"] = str(target_object.position)
                basic_info["可提及"] = "是" if target_object.mentionable else "否"
                
                if detail_level in ["medium", "all"]:
                    basic_info["分開顯示"] = "是" if target_object.hoist else "否"
                    basic_info["管理員權限"] = "是" if target_object.permissions.administrator else "否"
                
                if detail_level == "all":
                    permissions = []
                    for perm, value in target_object.permissions:
                        if value:
                            permissions.append(perm)
                    basic_info["關鍵權限"] = ", ".join(permissions[:5]) + (f"...及{len(permissions)-5}個更多" if len(permissions) > 5 else "")
                    basic_info["成員數量"] = str(len([m for m in interaction.guild.members if target_object in m.roles]))
            
            elif object_type == "message":
                basic_info["作者"] = f"{target_object.author.name} (ID: {target_object.author.id})"
                basic_info["頻道"] = f"{target_object.channel.name} (ID: {target_object.channel.id})"
                basic_info["發送時間"] = target_object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                basic_info["內容長度"] = f"{len(target_object.content)} 字元" if target_object.content else "0 字元"
                
                if detail_level in ["medium", "all"]:
                    # 只顯示前50個字符以避免太長
                    content = target_object.content[:50] + "..." if len(target_object.content) > 50 else target_object.content
                    basic_info["內容預覽"] = f"`{content}`" if content else "（無文字內容）"
                    basic_info["附件數量"] = str(len(target_object.attachments))
                    basic_info["嵌入數量"] = str(len(target_object.embeds))
                
                if detail_level == "all":
                    basic_info["提及用戶數"] = str(len(target_object.mentions))
                    basic_info["提及身分組數"] = str(len(target_object.role_mentions))
                    basic_info["提及頻道數"] = str(len(target_object.channel_mentions))
                    basic_info["被釘選"] = "是" if target_object.pinned else "否"
            
            elif object_type == "emoji":
                basic_info["名稱"] = target_object.name
                basic_info["動態"] = "是" if target_object.animated else "否"
                basic_info["可用"] = "是" if target_object.available else "否"
                
                if detail_level in ["medium", "all"]:
                    basic_info["URL"] = target_object.url
                    basic_info["伺服器"] = target_object.guild.name
                
                if detail_level == "all":
                    basic_info["建立時間"] = target_object.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(target_object, "created_at") else "未知"
                    basic_info["受限制"] = "是" if target_object.managed else "否"
            
            # 添加基本信息到嵌入
            for key, value in basic_info.items():
                embed.add_field(name=key, value=value, inline=True)
                
            # 添加操作指南
            embed.add_field(
                name="📋 複製 ID",
                value=f"`{target_object.id}`",
                inline=False
            )
            
            # 添加簡單的使用提示
            tips = []
            if object_type == "user":
                tips.append(f"<@{target_object.id}> - 提及此用戶")
            elif object_type == "channel":
                tips.append(f"<#{target_object.id}> - 提及此頻道")
            elif object_type == "role" and target_object.mentionable:
                tips.append(f"<@&{target_object.id}> - 提及此身分組")
                
            if tips:
                embed.add_field(
                    name="💡 使用提示",
                    value="\n".join(tips),
                    inline=False
                )
                
            # 如果有頭像或圖像，添加到嵌入
            if object_type == "user" and target_object.avatar:
                embed.set_thumbnail(url=target_object.avatar.url)
            elif object_type == "guild" and target_object.icon:
                embed.set_thumbnail(url=target_object.icon.url)
            elif object_type == "emoji":
                embed.set_thumbnail(url=target_object.url)
                
            embed.set_footer(text=f"查詢詳細程度: {detail_level} | 執行者: {interaction.user}")
            
            # 發送嵌入訊息
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"開發者工具執行錯誤: {str(e)}")
            await interaction.followup.send(
                f"❌ 執行開發者工具時發生錯誤: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="get_id", description="獲取Discord對象的ID（僅限管理員）")
    @app_commands.describe(
        user="要獲取ID的用戶",
        channel="要獲取ID的頻道",
        role="要獲取ID的身分組"
    )
    async def get_id(
        self,
        interaction: discord.Interaction,
        user: discord.User = None,
        channel: discord.abc.GuildChannel = None,
        role: discord.Role = None
    ):
        """快速獲取Discord對象的ID"""
        if not await self._check_admin(interaction):
            return

        embed = discord.Embed(
            title="🔍 Discord ID查詢",
            description="以下是您請求的ID資訊",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        # 添加伺服器ID
        embed.add_field(
            name="🏠 當前伺服器",
            value=f"名稱: {interaction.guild.name}\nID: `{interaction.guild.id}`",
            inline=False
        )
        
        # 添加請求者ID
        embed.add_field(
            name="👤 您的資訊",
            value=f"名稱: {interaction.user.name}\nID: `{interaction.user.id}`",
            inline=False
        )
        
        # 添加頻道ID
        current_channel = channel or interaction.channel
        embed.add_field(
            name="📝 頻道資訊",
            value=f"名稱: {current_channel.name}\nID: `{current_channel.id}`",
            inline=False
        )
        
        # 如果有指定用戶
        if user:
            embed.add_field(
                name="👥 指定用戶",
                value=f"名稱: {user.name}\nID: `{user.id}`",
                inline=False
            )
            
        # 如果有指定身分組
        if role:
            embed.add_field(
                name="🏷️ 指定身分組",
                value=f"名稱: {role.name}\nID: `{role.id}`",
                inline=False
            )
        
        # 添加使用提示
        embed.add_field(
            name="💡 使用提示",
            value="複製ID後可用於機器人指令、開發者工具或進行故障排除",
            inline=False
        )
            
        embed.set_footer(text=f"執行者: {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))