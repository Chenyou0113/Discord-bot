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
from typing import Optional, Dict, Tuple, Any, List
from dotenv import load_dotenv
# 導入語言工具
from utils.language_utils import detect_language, get_response_in_language
# 導入 Gemini API 連接池工具
from utils.gemini_pool import generate_content, get_pool_stats

# 設定日誌
log_file = 'new_bot.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
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

# 初始化 Gemini API 連接池
# 注意：實際的初始化發生在導入 utils.gemini_pool 模塊時
try:
    # 導入 utils.gemini_pool 模塊時會自動創建連接池實例
    from utils.gemini_pool import get_pool_stats
    
    # 獲取連接池狀態以確認連接池已正確初始化
    pool_stats = get_pool_stats()
    pool_models = list(pool_stats.keys())
    
    logger.info(f'成功初始化 Gemini API 連接池，可用模型: {", ".join(pool_models)}')
except Exception as e:
    logger.error(f'初始化 Gemini API 連接池時發生錯誤: {str(e)}')
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
            'cogs.chat_system_fixed',
            'cogs.search_commands',
            'cogs.weather_commands',
            'cogs.air_quality_commands',
            'cogs.radar_commands',
            'cogs.temperature_commands',
            'cogs.reservoir_commands'
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
            
            # 階段1: 核子級別清理
            logger.info('階段1: 核子級別清理...')
            
            # 1.1 清除命令樹中的所有指令 (不重新創建命令樹)
            logger.info('  1.1 清除命令樹指令...')
            self.tree.clear_commands(guild=None)
            # 清除所有公會的指令
            for guild in self.guilds:
                self.tree.clear_commands(guild=guild)
            
            # 清除內部指令字典
            if hasattr(self.tree, '_global_commands'):
                self.tree._global_commands.clear()
            if hasattr(self.tree, '_guild_commands'):
                self.tree._guild_commands.clear()
            
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
            
            # 階段2: 驗證清理結果
            logger.info('階段2: 驗證清理結果...')
            final_cogs = len(self.cogs)
            final_extensions = len([e for e in self.extensions.keys() if e.startswith('cogs.')])
            final_modules = len([name for name in sys.modules.keys() if name.startswith('cogs.')])
            
            logger.info(f'  清理後狀態: Cogs={final_cogs}, Extensions={final_extensions}, Modules={final_modules}')
            
            if final_cogs > 0 or final_extensions > 0:
                logger.error('❌ 清理不完全，仍有殘留！')
                return
            
            # 階段3: 智慧型載入
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
            
            # 階段4: 載入結果驗證
            logger.info('階段4: 載入結果驗證...')
            logger.info(f'  📊 載入統計: 成功 {successful_loads}/{len(self.initial_extensions)}')
            
            if failed_loads:
                logger.error(f'  ❌ 載入失敗: {", ".join(failed_loads)}')
            else:
                logger.info('  ✅ 所有擴展載入成功！')
            
            # 顯示載入的 Cogs
            loaded_cogs = list(self.cogs.keys())
            logger.info(f'  📋 已載入的 Cogs ({len(loaded_cogs)}): {", ".join(loaded_cogs)}')
            
            # 階段5: 終極指令同步
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
            
            # 階段6: 最終狀態報告
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
            
    async def on_ready(self):
        """機器人準備就緒時執行"""
        # 顯示機器人資訊
        logger.info(f'機器人 {self.user} 已成功上線！')
        logger.info(f'機器人正在 {len(self.guilds)} 個伺服器中運行')
        
        # 設置機器人狀態
        await self.change_presence(
            activity=discord.Game(f'在 {len(self.guilds)} 個伺服器中遊玩'),
        )
        logger.info(f'機器人狀態已設定為「正在玩 在 {len(self.guilds)} 個伺服器中遊玩」')
        
        # 顯示所有伺服器資訊
        for guild in self.guilds:
            member_count = guild.member_count if guild.member_count else 0
            logger.info(f'  - {guild.name} (ID: {guild.id}, 成員數: {member_count})')
            
    async def on_guild_join(self, guild):
        """機器人加入新伺服器時執行"""
        logger.info(f'🎉 機器人已加入新伺服器：{guild.name} (ID: {guild.id})')
        member_count = guild.member_count if guild.member_count else 0
        logger.info(f'  伺服器資訊：成員數 {member_count}，擁有者 {guild.owner}')
        
        # 更新機器人狀態以反映新的伺服器數量
        await self.change_presence(activity=discord.Game(f'在 {len(self.guilds)} 個伺服器中遊玩'))
        logger.info(f'機器人狀態已更新為「正在玩 在 {len(self.guilds)} 個伺服器中遊玩」')
        
        # 嘗試發送歡迎訊息到系統頻道
        if guild.system_channel:
            embed = discord.Embed(
                title='感謝邀請我加入您的伺服器！',
                description='我是一個多功能機器人，提供天氣、地震、鐵路等資訊，以及其他實用功能！',
                color=discord.Color.blue()
            )
            embed.add_field(name='使用方式', value='使用斜線指令 `/` 開始使用機器人功能！', inline=False)
            embed.add_field(name='支援的功能', value='天氣查詢、地震資訊、台鐵時刻表、聊天、等級系統等', inline=False)
            embed.set_footer(text='如有任何問題或建議，請聯絡機器人開發者。')
            
            try:
                await guild.system_channel.send(embed=embed)
                logger.info(f'  已在 {guild.name} 的系統頻道發送歡迎訊息')
            except Exception as e:
                logger.error(f'  無法在 {guild.name} 發送歡迎訊息: {str(e)}')

# 實例化並運行機器人
def main():
    bot = CustomBot()
    
    # 添加全局錯誤處理
    @bot.event
    async def on_error(event, *args, **kwargs):
        logger.error(f"Discord 事件錯誤: {event}", exc_info=True)
    
    # 添加指令樹錯誤處理
    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"⏳ 此指令正在冷卻中，請在 {error.retry_after:.2f} 秒後再試。", ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("⛔ 您沒有執行此指令的權限。", ephemeral=True)
        else:
            logger.error(f"應用指令錯誤: {str(error)}")
            try:
                await interaction.response.send_message(f"❌ 發生錯誤: {str(error)}", ephemeral=True)
            except discord.errors.InteractionResponded:
                try:
                    await interaction.followup.send(f"❌ 發生錯誤: {str(error)}", ephemeral=True)
                except Exception as e:
                    logger.error(f"無法發送錯誤回覆: {str(e)}")
    
    # 運行機器人
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        logger.error("機器人登入失敗，請檢查 TOKEN 是否正確。")
    except Exception as e:
        logger.error(f"機器人運行時發生錯誤: {str(e)}")

if __name__ == '__main__':
    main()
