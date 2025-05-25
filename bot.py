import os
import sys
import ssl
# 預先導入所有需要的discord模組，以避免後面出現discord變數問題
import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio
import aiohttp
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 設定 SSL 上下文
try:
    # 創建默認 SSL 上下文
    ssl_context = ssl.create_default_context()
    # 禁用主機名驗證
    ssl_context.check_hostname = False
    # 禁用證書驗證
    ssl_context.verify_mode = ssl.CERT_NONE
except Exception as e:
    logger.error(f'設定 SSL 時發生錯誤: {str(e)}')

# 載入環境變數
load_dotenv()

# 設定 API 金鑰
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    logger.error('錯誤: 找不到 GOOGLE_API_KEY 環境變數')
    logger.info('請確認您已經：')
    logger.info('1. 在專案根目錄創建 .env 檔案')
    logger.info('2. 在 .env 檔案中添加 GOOGLE_API_KEY=您的API金鑰')
    logger.info('3. 確保 .env 檔案已正確保存')
    exit(1)

# 初始化 Gemini
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    # 直接測試指定的模型
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logger.info('成功初始化 Gemini API')
except Exception as e:
    logger.error(f'初始化 Gemini API 時發生錯誤: {str(e)}')
    logger.info('請確認您的 API 金鑰是否有效')
    exit(1)

# 檢查 Token
token = os.getenv('DISCORD_TOKEN')
if not token:
    logger.error('錯誤: 找不到 DISCORD_TOKEN')
    exit(1)

# 設定機器人的必要權限
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.voice_states = True
intents.members = True  # 新增成員意圖

# 設定機器人權限
bot_permissions = discord.Permissions(
    # 基本權限
    send_messages=True,
    read_messages=True,
    embed_links=True,
    attach_files=True,
    read_message_history=True,
    # 應用程式指令權限
    use_application_commands=True,
    # 管理權限
    manage_messages=True,
    manage_channels=True,
    # 其他必要權限
    connect=True,
    speak=True,
    view_channel=True
)

class CustomBot(commands.Bot):
    def __init__(self):
        # 確保事件循環存在
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)            
        super().__init__(
            command_prefix='!',
            intents=intents,
            application_id=1357968654423162941,
            permissions=bot_permissions,
            proxy=None,
            proxy_auth=None,
            assume_unsync_clock=True
        )        # 初始化其他屬性        self._loaded_cogs = set()
        self.initial_extensions = [
            'cogs.admin_commands_fixed',
            'cogs.basic_commands',
            'cogs.info_commands_fixed_v4',
            'cogs.level_system',
            'cogs.monitor_system',
            'cogs.voice_system',
            'cogs.chat_commands'
        ]
        self.startup_channels = {}
        self._sync_in_progress = False
        self.connector = None
        
    async def setup_hook(self):
        """在機器人啟動時執行的設置"""
        try:
            # 初始化 aiohttp 連接器
            self.connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=10,
                force_close=True,
                enable_cleanup_closed=True
            )
            logger.info('成功初始化 aiohttp 連接器')
            
            # 載入所有 Cogs
            for extension in self.initial_extensions:
                try:
                    await self.load_extension(extension)
                    logger.info(f'已載入 {extension}')
                except Exception as e:
                    logger.error(f'載入 {extension} 時發生錯誤: {str(e)}')
            
            # 全局同步斜線指令
            logger.info('開始同步斜線指令...')
            await self.tree.sync()
            logger.info('斜線指令同步完成')
            
        except Exception as e:
            logger.error(f'設置過程中發生錯誤: {str(e)}')
            
    async def close(self):
        """在機器人關閉時清理資源"""
        if self.connector:
            await self.connector.close()
            logger.info('已關閉 aiohttp 連接器')
        await super().close()

# 創建機器人實例
bot = CustomBot()

# 定義重啟指令
@bot.command(name="reboot", aliases=["rb"])
async def reboot_command(ctx):
    """直接重啟機器人 (!reboot 或 !rb)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ 此指令僅限管理員使用！")
        return
        
    await ctx.send("🔄 正在準備重啟機器人，請稍候...")
    logger.info(f'管理員 {ctx.author} 從伺服器 {ctx.guild.name} 觸發了機器人重啟')
    
    # 獲取admin_commands cog
    admin_cog = bot.get_cog("AdminCommands")
    if admin_cog:
        # 發送重啟訊息到系統監控頻道
        await admin_cog._send_restart_message(ctx.guild)
        
        # 為所有伺服器發送重啟訊息
        for guild in bot.guilds:
            if guild.id != ctx.guild.id:  # 避免重複發送訊息到觸發重啟的伺服器
                await admin_cog._send_restart_message(guild)
    else:
        # 如果找不到admin_commands，直接使用一般訊息
        for guild in bot.guilds:
            channel = discord.utils.find(
                lambda c: isinstance(c, discord.TextChannel) and 
                        c.permissions_for(guild.me).send_messages and
                        "系統" in c.name and "監控" in c.name,
                guild.channels
            )
            if channel:
                try:
                    embed = discord.Embed(
                        title="🔄 系統監控通知",
                        description="機器人正在重啟，請稍候...",
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text=f"重啟時間: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                    await channel.send(embed=embed)
                except:
                    continue
    
    # 等待訊息發送完成
    await asyncio.sleep(2)
    
    # 系統重啟
    import os
    import sys
    
    logger.info('機器人正在重啟...')
    # 使用 Python 重啟程序
    os.execv(sys.executable, ['python'] + sys.argv)

# 定義同步指令
@bot.command(name="resync", aliases=["rs"])
async def resync_command(ctx):
    """強制同步斜線指令 (!resync 或 !rs)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ 此指令僅限管理員使用！")
        return
        
    await ctx.send("🔄 正在強制同步斜線指令，請稍候...")
    
    try:
        # 清空並重新同步指令
        logger.info('開始強制清空和重新同步斜線指令...')
        
        if bot._sync_in_progress:
            await ctx.send("⚠️ 已有同步程序在執行中，請稍後再試。")
            return
            
        bot._sync_in_progress = True
        
        try:
            # 方法1: 使用force_sync_commands方法
            result = await bot.force_sync_commands(ctx.guild)
            
            # 再次檢查命令
            if ctx.guild:
                commands = bot.tree.get_commands(guild=ctx.guild)
            else:
                commands = bot.tree.get_commands()
                
            command_names = [cmd.name for cmd in commands]
            logger.info(f'同步後的斜線指令 ({len(commands)}): {", ".join(command_names) if command_names else "無"}')
                
            await ctx.send(f"✅ 斜線指令同步完成！共同步了 {len(commands)} 個指令: {', '.join(command_names) if command_names else '無'}")
        except Exception as e:
            error_msg = f'强制同步命令過程中出現錯誤: {str(e)}'
            logger.error(error_msg)
            await ctx.send(f"❌ 同步過程發生錯誤: {str(e)}")
        finally:
            bot._sync_in_progress = False
            
    except Exception as e:
        logger.error(f'整體同步過程發生錯誤: {str(e)}')
        await ctx.send(f"❌ 同步過程發生嚴重錯誤: {str(e)}")

@bot.command(name="recreate_commands", aliases=["rc"])
async def recreate_commands(ctx):
    """完全重新創建所有命令 (!recreate_commands 或 !rc)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ 此指令僅限管理員使用！")
        return
        
    await ctx.send("🔄 正在重新創建所有命令，這可能需要一些時間...")
    
    try:
        if bot._sync_in_progress:
            await ctx.send("⚠️ 已有同步程序在執行中，請稍後再試。")
            return
            
        bot._sync_in_progress = True
        
        try:
            # 清空所有命令
            bot.tree.clear_commands(guild=None)
            for guild in bot.guilds:
                bot.tree.clear_commands(guild=guild)
                
            await asyncio.sleep(2)
                
            # 嘗試手動註冊基本命令
            bot._try_register_basic_commands()
            
            # 重新同步
            await asyncio.sleep(2)
            global_commands = await bot.tree.sync()
            
            # 同步到每個伺服器
            for guild in bot.guilds:
                try:
                    guild_commands = await bot.tree.sync(guild=guild)
                    logger.info(f'已同步 {len(guild_commands)} 個指令到伺服器 {guild.name}')
                except Exception as e:
                    logger.error(f'同步到伺服器 {guild.name} 時發生錯誤: {str(e)}')
                await asyncio.sleep(1)
                
            # 顯示結果
            commands = bot.tree.get_commands()
            command_names = [cmd.name for cmd in commands]
            
            await ctx.send(f"✅ 所有命令重新創建完成！全局指令: {len(commands)} 個\n命令: {', '.join(command_names) if command_names else '無'}")
            
        except Exception as e:
            error_msg = f'重新創建命令過程中出現錯誤: {str(e)}'
            logger.error(error_msg)
            await ctx.send(f"❌ 重新創建過程發生錯誤: {str(e)}")
        finally:
            bot._sync_in_progress = False
            
    except Exception as e:
        logger.error(f'整體重新創建過程發生錯誤: {str(e)}')
        await ctx.send(f"❌ 重新創建過程發生嚴重錯誤: {str(e)}")

@bot.command(name="fix_commands", aliases=["fc"])
async def fix_commands(ctx):
    """修復「未知整合」問題 (!fix_commands 或 !fc)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ 此指令僅限管理員使用！")
        return
        
    await ctx.send("🛠️ 正在嘗試修復「未知整合」問題，這可能需要一些時間...")
    
    try:
        if bot._sync_in_progress:
            await ctx.send("⚠️ 已有同步程序在執行中，請稍後再試。")
            return
            
        bot._sync_in_progress = True
        
        try:
            # 1. 完全清空所有命令
            logger.info('嘗試修復「未知整合」問題：完全清空所有命令')
            bot.tree.clear_commands(guild=None)
            
            for guild in bot.guilds:
                try:
                    bot.tree.clear_commands(guild=guild)
                    logger.info(f'已清空伺服器 {guild.name} 的指令')
                except Exception as e:
                    logger.error(f'清空伺服器 {guild.name} 指令時發生錯誤: {str(e)}')
            
            await asyncio.sleep(2)  # 等待命令清空生效
            
            # 2. 同步一次空指令樹以確保清空生效
            await bot.tree.sync()
            for guild in bot.guilds:
                try:
                    await bot.tree.sync(guild=guild)
                except Exception as e:
                    logger.error(f'同步空指令樹到伺服器 {guild.name} 時發生錯誤: {str(e)}')
            
            await ctx.send("🧹 所有命令已清空，正在重新註冊基本命令...")
            await asyncio.sleep(1)
            
            # 3. 手動註冊基本命令
            logger.info('嘗試手動註冊基本命令')
            bot._try_register_basic_commands()
            await asyncio.sleep(2)  # 等待註冊生效
            
            # 4. 強制重新同步
            global_commands = await bot.tree.sync()
            logger.info(f'全局指令同步完成: {len(global_commands)} 個指令')
            
            # 5. 同步到每個伺服器
            success_guilds = 0
            for guild in bot.guilds:
                try:
                    # 先複製全局命令到伺服器
                    bot.tree.copy_global_to(guild=guild)
                    await asyncio.sleep(0.5)
                    
                    # 同步到伺服器
                    guild_commands = await bot.tree.sync(guild=guild)
                    logger.info(f'已同步 {len(guild_commands)} 個指令到伺服器 {guild.name}')
                    success_guilds += 1
                except Exception as e:
                    logger.error(f'同步到伺服器 {guild.name} 時發生錯誤: {str(e)}')
                
                await asyncio.sleep(1)  # 避免API限制
            
            # 6. 最終檢查
            commands = bot.tree.get_commands()
            command_names = [cmd.name for cmd in commands]
            
            # 發送結果
            if len(commands) > 0:
                await ctx.send(f"✅ 修復完成！已成功註冊 {len(commands)} 個全局指令，並同步到 {success_guilds} 個伺服器。\n"
                            f"指令列表: {', '.join(f'`/{name}`' for name in command_names)}\n"
                            f"👉 請完全退出並重新啟動 Discord 以使修復生效。")
            else:
                await ctx.send("❌ 修復似乎未能成功，仍然沒有註冊的指令。請嘗試以下步驟：\n"
                            "1. 重啟機器人 (`!reboot`)\n"
                            "2. 確保機器人擁有必要權限\n"
                            "3. 重新邀請機器人到伺服器")
            
        except Exception as e:
            error_msg = f'修復命令過程中出現錯誤: {str(e)}'
            logger.error(error_msg)
            await ctx.send(f"❌ 修復過程發生錯誤: {str(e)}")
        finally:
            bot._sync_in_progress = False
            
    except Exception as e:
        logger.error(f'整體修復過程發生錯誤: {str(e)}')
        await ctx.send(f"❌ 修復過程發生嚴重錯誤: {str(e)}")

# 運行機器人
try:
    bot.run(token)
except Exception as e:
    logger.error(f'機器人啟動失敗: {str(e)}')
    exit(1)