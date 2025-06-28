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
    def __init__(self):        # 確保事件循環存在
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # 沒有運行中的事件循環，這是正常的
            pass
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            application_id=1357968654423162941,
            permissions=bot_permissions,
            proxy=None,
            proxy_auth=None,
            assume_unsync_clock=True
        )
          # 初始化其他屬性
        self._loaded_cogs = set()
        self.initial_extensions = [
            'cogs.admin_commands_fixed',
            'cogs.basic_commands',
            'cogs.info_commands_fixed_v4_clean',
            'cogs.level_system',
            'cogs.monitor_system',
            'cogs.voice_system',
            'cogs.chat_commands',
            'cogs.search_commands',
            'cogs.weather_commands',
            'cogs.air_quality_commands',
            'cogs.radar_commands',
            'cogs.temperature_commands'
        ]
        self.startup_channels = {}
        self._sync_in_progress = False
        self.connector = None
        
    async def setup_hook(self):
        """在機器人啟動時執行的設置 - 終極修復版本"""
        try:
            # 初始化 aiohttp 連接器
            self.connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=10,
                force_close=True,
                enable_cleanup_closed=True
            )
            logger.info('成功初始化 aiohttp 連接器')
            
            # 🔥 終極指令重複註冊修復方案
            logger.info('🔥 執行終極指令重複註冊修復...')
            
            # 階段1：核子級別清理
            logger.info('階段1: 核子級別清理...')
            
            # 1.1 完全重建命令樹
            logger.info('  1.1 重建命令樹...')
            old_tree = self.tree
            self.tree = app_commands.CommandTree(self)
            del old_tree
            
            # 1.2 清除連接中的所有應用程式指令快取
            if hasattr(self, '_connection') and self._connection:
                attrs_to_clear = [
                    '_application_commands',
                    '_global_application_commands', 
                    '_guild_application_commands'
                ]
                for attr in attrs_to_clear:
                    if hasattr(self._connection, attr):
                        getattr(self._connection, attr).clear()
                        logger.info(f'  已清除 _connection.{attr}')
            
            # 1.3 多輪徹底卸載 (5輪確保徹底清除)
            logger.info('  1.3 多輪徹底卸載...')
            for round_num in range(5):
                remaining_cogs = list(self.cogs.keys())
                remaining_extensions = [ext for ext in list(self.extensions.keys()) if ext.startswith('cogs.')]
                
                if not remaining_cogs and not remaining_extensions:
                    logger.info(f'    第{round_num+1}輪: 所有擴展已清除')
                    break
                
                logger.info(f'    第{round_num+1}輪: Cogs={len(remaining_cogs)}, Extensions={len(remaining_extensions)}')
                
                # 移除所有 Cogs
                for cog_name in remaining_cogs:
                    try:
                        self.remove_cog(cog_name)
                        logger.info(f'      移除 Cog: {cog_name}')
                    except Exception as e:
                        logger.warning(f'      移除 Cog {cog_name} 失敗: {str(e)}')
                
                # 卸載所有擴展
                for extension_name in remaining_extensions:
                    try:
                        await self.unload_extension(extension_name)
                        logger.info(f'      卸載擴展: {extension_name}')
                    except Exception as e:
                        logger.warning(f'      卸載擴展 {extension_name} 失敗: {str(e)}')
                
                await asyncio.sleep(0.5)
            
            # 1.4 清除 Python 模組快取
            logger.info('  1.4 清除 Python 模組快取...')
            import importlib
            modules_to_remove = [name for name in sys.modules.keys() if name.startswith('cogs.')]
            for module_name in modules_to_remove:
                try:
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                        logger.info(f'    清除模組快取: {module_name}')
                except Exception as e:
                    logger.warning(f'    清除模組快取 {module_name} 失敗: {str(e)}')
            
            # 1.5 強制垃圾回收
            logger.info('  1.5 強制垃圾回收...')
            import gc
            for i in range(3):
                collected = gc.collect()
                logger.info(f'    第{i+1}次垃圾回收: 清理 {collected} 個對象')
            
            # 1.6 清除載入記錄並等待
            self._loaded_cogs.clear()
            await asyncio.sleep(2)
            
            # 階段2：驗證清理結果
            logger.info('階段2: 驗證清理結果...')
            final_cogs = len(self.cogs)
            final_extensions = len([e for e in self.extensions.keys() if e.startswith('cogs.')])
            final_modules = len([name for name in sys.modules.keys() if name.startswith('cogs.')])
            
            logger.info(f'  清理後狀態: Cogs={final_cogs}, Extensions={final_extensions}, Modules={final_modules}')
            
            if final_cogs > 0 or final_extensions > 0:
                logger.error('❌ 清理不完全，仍有殘留！')
                return
            
            # 階段3：智慧型載入
            logger.info('階段3: 智慧型載入...')
            successful_loads = 0
            failed_loads = []
            
            for i, extension in enumerate(self.initial_extensions, 1):
                try:
                    logger.info(f'  載入 {extension} ({i}/{len(self.initial_extensions)})...')
                    
                    # 3.1 確保擴展不在字典中
                    if extension in self.extensions:
                        logger.warning(f'    ⚠️ {extension} 仍在擴展字典，強制移除')
                        try:
                            await self.unload_extension(extension)
                            await asyncio.sleep(0.2)
                        except:
                            pass
                    
                    # 3.2 預載入模組檢查
                    if extension in sys.modules:
                        logger.info(f'    🔄 模組 {extension} 已在快取中，重新載入')
                        importlib.reload(sys.modules[extension])
                    
                    # 3.3 載入擴展
                    await self.load_extension(extension)
                    self._loaded_cogs.add(extension)
                    successful_loads += 1
                    logger.info(f'    ✅ 成功載入 {extension}')
                    
                    # 3.4 載入間隔
                    await asyncio.sleep(0.4)
                    
                except commands.ExtensionAlreadyLoaded:
                    logger.warning(f'    ⚠️ {extension} 已載入，嘗試重新載入')
                    try:
                        await self.reload_extension(extension)
                        self._loaded_cogs.add(extension)
                        successful_loads += 1
                        logger.info(f'    ✅ 重新載入 {extension} 成功')
                    except Exception as reload_error:
                        logger.error(f'    ❌ 重新載入 {extension} 失敗: {str(reload_error)}')
                        failed_loads.append(extension)
                
                except Exception as e:
                    logger.error(f'    ❌ 載入 {extension} 失敗: {str(e)}')
                    failed_loads.append(extension)
            
            # 階段4：載入結果驗證
            logger.info('階段4: 載入結果驗證...')
            logger.info(f'  📊 載入統計: 成功 {successful_loads}/{len(self.initial_extensions)}')
            
            if failed_loads:
                logger.error(f'  ❌ 載入失敗: {", ".join(failed_loads)}')
            else:
                logger.info('  ✅ 所有擴展載入成功！')
            
            # 顯示載入的 Cogs
            loaded_cogs = list(self.cogs.keys())
            logger.info(f'  📋 已載入的 Cogs ({len(loaded_cogs)}): {", ".join(loaded_cogs)}')
            
            # 階段5：終極指令同步
            logger.info('階段5: 終極指令同步...')
            try:
                # 5.1 同步前檢查
                all_commands = self.tree._global_commands
                logger.info(f'  同步前指令數量: {len(all_commands)}')
                
                if all_commands:
                    pre_sync_names = [cmd.name for cmd in all_commands.values()]
                    logger.info(f'  待同步指令: {", ".join(pre_sync_names)}')
                
                # 5.2 執行同步
                synced_commands = await self.tree.sync()
                logger.info(f'  ✅ 指令同步完成，共同步 {len(synced_commands)} 個指令')
                
                if synced_commands:
                    synced_names = [cmd.name for cmd in synced_commands]
                    logger.info(f'  📋 已同步指令: {", ".join(synced_names)}')
                else:
                    logger.warning('  ⚠️ 沒有指令被同步')
                
            except Exception as sync_error:
                logger.error(f'  ❌ 指令同步失敗: {str(sync_error)}')
                import traceback
                logger.error(f'  同步錯誤詳情: {traceback.format_exc()}')
            
            # 階段6：最終狀態報告
            logger.info('階段6: 最終狀態報告...')
            logger.info(f'  🎯 最終統計:')
            logger.info(f'    載入的擴展: {len(self._loaded_cogs)}')
            logger.info(f'    活躍的 Cogs: {len(self.cogs)}')
            logger.info(f'    同步的指令: {len(synced_commands) if "synced_commands" in locals() else 0}')
            
            if successful_loads == len(self.initial_extensions) and not failed_loads:
                logger.info('🎉 終極修復完全成功！機器人已準備就緒！')
            else:
                logger.warning('⚠️ 修復過程中有部分問題，但機器人基本可用')
            
        except Exception as e:
            logger.error(f'❌ 終極修復過程發生嚴重錯誤: {str(e)}')
            import traceback
            logger.error(f'錯誤詳情: {traceback.format_exc()}')
            
    async def close(self):
        """在機器人關閉時清理資源"""
        if self.connector:
            await self.connector.close()
            logger.info('已關閉 aiohttp 連接器')
        await super().close()
    
    async def on_ready(self):
        """當機器人準備就緒時執行"""
        try:
            # 設定機器人狀態為「正在玩 C. Y.」
            activity = discord.Game(name="C. Y.")
            await self.change_presence(status=discord.Status.online, activity=activity)
            
            logger.info(f'機器人 {self.user} 已成功上線！')
            logger.info(f'機器人正在 {len(self.guilds)} 個伺服器中運行')
            logger.info('機器人狀態已設定為「正在玩 C. Y.」')
            
            # 顯示連接的伺服器列表
            for guild in self.guilds:
                logger.info(f'  - {guild.name} (ID: {guild.id}, 成員數: {guild.member_count})')
                
        except Exception as e:
            logger.error(f'設定機器人狀態時發生錯誤: {str(e)}')
    
    def _try_register_basic_commands(self):
        """嘗試手動註冊基本命令"""
        try:
            logger.info('正在嘗試手動註冊基本命令...')
            
            # 檢查並重新載入所有cogs的命令
            for cog_name, cog in self.cogs.items():
                if hasattr(cog, '__cog_app_commands__'):
                    for command in cog.__cog_app_commands__:
                        if command not in self.tree._global_commands:
                            self.tree.add_command(command)
                            logger.info(f'已重新註冊命令: {command.name} (來自 {cog_name})')
                
            logger.info('基本命令手動註冊完成')
            
        except Exception as e:
            logger.error(f'手動註冊基本命令時發生錯誤: {str(e)}')
    
    async def force_sync_commands(self, guild=None):
        """強制同步命令的輔助方法"""
        try:
            logger.info('開始強制同步命令...')
            
            # 清空並重新同步
            self.tree.clear_commands(guild=guild)
            await asyncio.sleep(1)
            
            # 手動註冊基本命令
            self._try_register_basic_commands()
            await asyncio.sleep(1)
            
            # 執行同步
            if guild:
                result = await self.tree.sync(guild=guild)
                logger.info(f'已同步 {len(result)} 個命令到伺服器 {guild.name}')
            else:
                result = await self.tree.sync()
                logger.info(f'已同步 {len(result)} 個全局命令')
                
            return result
            
        except Exception as e:
            logger.error(f'強制同步命令時發生錯誤: {str(e)}')
            return []

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
    
    # 優雅關閉機器人
    logger.info('機器人正在關閉，等待外部腳本重啟...')
    await bot.close()

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