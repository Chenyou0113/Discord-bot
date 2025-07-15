#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終指令重複註冊修復測試
完全解決 CommandAlreadyRegistered 問題的終極方案
"""

import os
import sys
import asyncio
import logging
import aiohttp
import ssl
import gc
import importlib
from typing import Dict, List, Set

# 確保正確的模組導入路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('final_command_fix_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def analyze_command_conflicts():
    """分析可能的指令衝突"""
    print("🔍 分析可能的指令衝突...")
    
    cog_files = [
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
    
    command_registry = {}
    conflicts = []
    
    for cog_file in cog_files:
        try:
            # 動態導入模組
            module = importlib.import_module(cog_file)
            
            # 檢查模組中的類別
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, commands.Cog) and 
                    attr != commands.Cog):
                    
                    # 檢查類別中的方法
                    for method_name in dir(attr):
                        method = getattr(attr, method_name)
                        if hasattr(method, '__wrapped__'):
                            # 檢查是否有 app_commands.command 裝飾器
                            if hasattr(method, '__func__') and hasattr(method.__func__, 'callback'):
                                callback = method.__func__.callback
                                if hasattr(callback, 'name'):
                                    cmd_name = callback.name
                                    if cmd_name in command_registry:
                                        conflicts.append({
                                            'command': cmd_name,
                                            'original': command_registry[cmd_name],
                                            'conflict': f"{cog_file}.{attr_name}.{method_name}"
                                        })
                                        print(f"❌ 指令衝突: {cmd_name}")
                                        print(f"   原始位置: {command_registry[cmd_name]}")
                                        print(f"   衝突位置: {cog_file}.{attr_name}.{method_name}")
                                    else:
                                        command_registry[cmd_name] = f"{cog_file}.{attr_name}.{method_name}"
                                        print(f"✅ 指令註冊: {cmd_name} -> {cog_file}")
                        
        except Exception as e:
            print(f"⚠️ 分析 {cog_file} 時發生錯誤: {str(e)}")
    
    if conflicts:
        print(f"\n❌ 發現 {len(conflicts)} 個指令衝突!")
        return False
    else:
        print("\n✅ 沒有發現指令衝突!")
        return True

class UltimateBot(commands.Bot):
    """終極機器人實現，徹底解決指令重複註冊問題"""
    
    def __init__(self):
        # 設定機器人的必要權限
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.voice_states = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            application_id=1357968654423162941,
            assume_unsync_clock=True
        )
        
        # 追蹤載入狀態
        self._loaded_extensions: Set[str] = set()
        self._command_registry: Dict[str, str] = {}
        self._cog_registry: Dict[str, str] = {}
        
        # 擴展列表
        self.target_extensions = [
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
        
    async def nuclear_cleanup(self):
        """核子級別的清理 - 徹底清除所有可能的殘留"""
        logger.info("🧹 執行核子級別清理...")
        
        try:
            # 第1步：完全重建命令樹
            logger.info("1. 重建命令樹...")
            old_tree = self.tree
            self.tree = app_commands.CommandTree(self)
            del old_tree
            
            # 第2步：清除連接中的應用程式指令快取
            if hasattr(self, '_connection') and self._connection:
                if hasattr(self._connection, '_application_commands'):
                    self._connection._application_commands.clear()
                if hasattr(self._connection, '_global_application_commands'):
                    self._connection._global_application_commands.clear()
            
            # 第3步：多輪卸載 Cogs 和擴展
            for round_num in range(5):  # 增加到5輪
                logger.info(f"2.{round_num + 1} 卸載輪次 {round_num + 1}/5...")
                
                remaining_cogs = list(self.cogs.keys())
                remaining_extensions = [ext for ext in list(self.extensions.keys()) 
                                      if ext.startswith('cogs.')]
                
                if not remaining_cogs and not remaining_extensions:
                    logger.info(f"   ✅ 第 {round_num + 1} 輪：所有擴展已清除")
                    break
                
                logger.info(f"   剩餘 Cogs: {len(remaining_cogs)}, Extensions: {len(remaining_extensions)}")
                
                # 卸載所有 Cogs
                for cog_name in remaining_cogs:
                    try:
                        self.remove_cog(cog_name)
                        logger.info(f"   移除 Cog: {cog_name}")
                    except Exception as e:
                        logger.warning(f"   移除 Cog {cog_name} 失敗: {str(e)}")
                
                # 卸載所有擴展
                for extension_name in remaining_extensions:
                    try:
                        await self.unload_extension(extension_name)
                        logger.info(f"   卸載擴展: {extension_name}")
                    except Exception as e:
                        logger.warning(f"   卸載擴展 {extension_name} 失敗: {str(e)}")
                
                await asyncio.sleep(1)  # 等待清理完成
            
            # 第4步：清除 Python 模組快取
            logger.info("3. 清除 Python 模組快取...")
            modules_to_remove = []
            for module_name in sys.modules.keys():
                if module_name.startswith('cogs.'):
                    modules_to_remove.append(module_name)
            
            for module_name in modules_to_remove:
                try:
                    del sys.modules[module_name]
                    logger.info(f"   清除模組快取: {module_name}")
                except Exception as e:
                    logger.warning(f"   清除模組快取 {module_name} 失敗: {str(e)}")
            
            # 第5步：清除內部狀態
            self._loaded_extensions.clear()
            self._command_registry.clear()
            self._cog_registry.clear()
            
            # 第6步：強制垃圾回收
            logger.info("4. 執行垃圾回收...")
            for _ in range(3):
                collected = gc.collect()
                logger.info(f"   垃圾回收: 清理 {collected} 個對象")
            
            await asyncio.sleep(2)  # 等待所有清理完成
            
            # 驗證清理結果
            final_cogs = len(self.cogs)
            final_extensions = len([e for e in self.extensions.keys() if e.startswith('cogs.')])
            logger.info(f"✅ 清理完成: Cogs={final_cogs}, Extensions={final_extensions}")
            
            if final_cogs > 0 or final_extensions > 0:
                logger.error(f"❌ 清理未完全成功，仍有殘留！")
                return False
            else:
                logger.info("✅ 核子級別清理成功！")
                return True
                
        except Exception as e:
            logger.error(f"❌ 核子級別清理失敗: {str(e)}")
            import traceback
            logger.error(f"錯誤詳情: {traceback.format_exc()}")
            return False
    
    async def smart_load_extensions(self):
        """智慧型擴展載入 - 檢測並避免衝突"""
        logger.info("🚀 開始智慧型擴展載入...")
        
        successful_loads = 0
        failed_loads = []
        
        for i, extension in enumerate(self.target_extensions, 1):
            try:
                logger.info(f"載入 {extension} ({i}/{len(self.target_extensions)})...")
                
                # 檢查是否已經載入
                if extension in self._loaded_extensions:
                    logger.warning(f"   ⚠️ {extension} 已在載入清單中，跳過")
                    continue
                
                # 檢查是否仍在擴展字典中
                if extension in self.extensions:
                    logger.warning(f"   ⚠️ {extension} 仍在擴展字典中，強制卸載")
                    try:
                        await self.unload_extension(extension)
                        await asyncio.sleep(0.5)
                    except:
                        pass
                
                # 重新載入模組（如果存在於快取中）
                if extension in sys.modules:
                    logger.info(f"   🔄 重新載入模組: {extension}")
                    importlib.reload(sys.modules[extension])
                
                # 載入擴展
                await self.load_extension(extension)
                self._loaded_extensions.add(extension)
                successful_loads += 1
                logger.info(f"   ✅ 成功載入 {extension} ({successful_loads}/{len(self.target_extensions)})")
                
                # 載入間隔
                await asyncio.sleep(0.5)
                
            except commands.ExtensionAlreadyLoaded:
                logger.warning(f"   ⚠️ {extension} 已載入，嘗試重新載入")
                try:
                    await self.reload_extension(extension)
                    self._loaded_extensions.add(extension)
                    successful_loads += 1
                    logger.info(f"   ✅ 重新載入 {extension} 成功")
                except Exception as reload_error:
                    logger.error(f"   ❌ 重新載入 {extension} 失敗: {str(reload_error)}")
                    failed_loads.append(extension)
            
            except Exception as e:
                logger.error(f"   ❌ 載入 {extension} 失敗: {str(e)}")
                failed_loads.append(extension)
        
        # 載入結果報告
        logger.info(f"📊 載入完成: 成功 {successful_loads}/{len(self.target_extensions)}")
        if failed_loads:
            logger.error(f"❌ 載入失敗: {', '.join(failed_loads)}")
        
        return successful_loads, failed_loads
    
    async def ultimate_sync(self):
        """終極指令同步"""
        logger.info("🔄 開始終極指令同步...")
        
        try:
            # 在同步前先檢查命令樹狀態
            all_commands = self.tree._global_commands
            logger.info(f"同步前命令數量: {len(all_commands)}")
            
            if all_commands:
                command_names = [cmd.name for cmd in all_commands.values()]
                logger.info(f"待同步指令: {', '.join(command_names)}")
            
            # 執行同步
            synced_commands = await self.tree.sync()
            logger.info(f"✅ 指令同步完成，共同步 {len(synced_commands)} 個指令")
            
            if synced_commands:
                synced_names = [cmd.name for cmd in synced_commands]
                logger.info(f"已同步指令: {', '.join(synced_names)}")
            else:
                logger.warning("⚠️ 沒有指令被同步")
            
            return len(synced_commands)
            
        except Exception as sync_error:
            logger.error(f"❌ 指令同步失敗: {str(sync_error)}")
            import traceback
            logger.error(f"同步錯誤詳情: {traceback.format_exc()}")
            return 0
    
    async def setup_hook(self):
        """終極設置鉤子"""
        logger.info("🛠️ 執行終極設置...")
        
        try:
            # 步驟1：核子級別清理
            cleanup_success = await self.nuclear_cleanup()
            if not cleanup_success:
                logger.error("❌ 核子級別清理失敗，無法繼續")
                return
            
            # 步驟2：智慧型擴展載入
            successful, failed = await self.smart_load_extensions()
            if failed:
                logger.warning(f"⚠️ 有 {len(failed)} 個擴展載入失敗")
            
            # 步驟3：終極指令同步
            synced_count = await self.ultimate_sync()
            
            # 最終狀態報告
            logger.info("📋 最終狀態報告:")
            logger.info(f"   載入的擴展: {len(self._loaded_extensions)}")
            logger.info(f"   載入的 Cogs: {len(self.cogs)}")
            logger.info(f"   同步的指令: {synced_count}")
            
            if synced_count > 0:
                logger.info("✅ 終極設置成功完成！")
            else:
                logger.warning("⚠️ 終極設置完成但沒有同步任何指令")
                
        except Exception as e:
            logger.error(f"❌ 終極設置失敗: {str(e)}")
            import traceback
            logger.error(f"設置錯誤詳情: {traceback.format_exc()}")

async def test_ultimate_fix():
    """測試終極修復方案"""
    print("🧪 開始終極修復測試...")
    
    # 載入環境變數
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ 找不到 DISCORD_TOKEN，無法進行實際測試")
        return False
    
    # 分析指令衝突
    conflict_free = analyze_command_conflicts()
    if not conflict_free:
        print("❌ 發現指令衝突，請先解決衝突再進行測試")
        return False
    
    print("✅ 指令衝突分析通過，開始機器人測試...")
    
    try:
        # 創建機器人實例
        bot = UltimateBot()
        
        # 測試設置鉤子（不實際連接Discord）
        print("🧪 測試設置鉤子...")
        
        # 模擬設置過程
        await bot.nuclear_cleanup()
        successful, failed = await bot.smart_load_extensions()
        
        print(f"📊 測試結果:")
        print(f"   成功載入: {successful}")
        print(f"   載入失敗: {len(failed)}")
        print(f"   失敗列表: {failed}")
        
        if failed:
            print("❌ 有擴展載入失敗")
            return False
        else:
            print("✅ 所有擴展載入成功")
            return True
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🔥 Discord 機器人終極指令修復測試")
    print("=" * 50)
    
    # 執行測試
    success = asyncio.run(test_ultimate_fix())
    
    print("=" * 50)
    if success:
        print("✅ 終極修復測試成功！")
        print("🚀 可以嘗試啟動機器人了")
    else:
        print("❌ 終極修復測試失敗")
        print("🔧 需要進一步調查和修復")
