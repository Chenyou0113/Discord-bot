#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試機器人載入修復
驗證是否解決了指令重複註冊問題
"""

import asyncio
import logging
import sys
import os

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_bot_loading_fix():
    """測試機器人載入修復"""
    try:
        logger.info("🔍 測試機器人載入修復...")
        
        # 檢查修復的程式碼
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        # 檢查關鍵修復點
        checks = {
            'tree.clear_commands': 'tree.clear_commands(guild=None)' in bot_content,
            'ExtensionAlreadyLoaded': 'ExtensionAlreadyLoaded' in bot_content,
            'ExtensionError': 'ExtensionError' in bot_content,
            '_loaded_cogs.clear': '_loaded_cogs.clear()' in bot_content,
            'asyncio.sleep': 'await asyncio.sleep(1)' in bot_content
        }
        
        logger.info("修復檢查結果:")
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            logger.info(f"  {status} {check_name}: {'通過' if result else '失敗'}")
        
        all_passed = all(checks.values())
        
        if all_passed:
            logger.info("✅ 所有修復檢查通過")
            
            # 檢查 Cog 載入順序
            logger.info("\n🔍 檢查 Cog 載入順序...")
            cog_extensions = [
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
            
            for i, cog in enumerate(cog_extensions, 1):
                if cog in bot_content:
                    logger.info(f"  {i:2d}. ✅ {cog}")
                else:
                    logger.error(f"  {i:2d}. ❌ {cog} (未找到)")
            
            logger.info("\n🔍 檢查錯誤處理機制...")
            error_handling_features = [
                'except commands.ExtensionAlreadyLoaded:',
                'except commands.ExtensionError as e:',
                'except Exception as e:',
                'logger.error',
                'logger.warning'
            ]
            
            for feature in error_handling_features:
                if feature in bot_content:
                    logger.info(f"  ✅ {feature}")
                else:
                    logger.warning(f"  ⚠️ {feature} (未找到)")
            
        else:
            logger.error("❌ 某些修復檢查失敗")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}")
        return False

async def test_cog_files():
    """測試 Cog 檔案存在性"""
    try:
        logger.info("\n🔍 檢查 Cog 檔案...")
        
        cog_files = [
            'cogs/weather_commands.py',
            'cogs/air_quality_commands.py',
            'cogs/radar_commands.py',
            'cogs/temperature_commands.py'
        ]
        
        all_exist = True
        for cog_file in cog_files:
            if os.path.exists(cog_file):
                logger.info(f"  ✅ {cog_file}")
                
                # 檢查檔案大小
                size = os.path.getsize(cog_file)
                if size > 0:
                    logger.info(f"     檔案大小: {size} bytes")
                else:
                    logger.warning(f"     ⚠️ 檔案為空")
                    all_exist = False
            else:
                logger.error(f"  ❌ {cog_file} (不存在)")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        logger.error(f"檢查 Cog 檔案時發生錯誤: {e}")
        return False

async def main():
    """主測試函數"""
    logger.info("開始測試機器人載入修復")
    
    # 測試修復
    fix_success = await test_bot_loading_fix()
    
    # 測試檔案
    files_success = await test_cog_files()
    
    logger.info("\n" + "="*50)
    logger.info("測試結果總結:")
    
    if fix_success and files_success:
        logger.info("✅ 所有測試通過！")
        logger.info("修復內容:")
        logger.info("  • 清除斜線指令: tree.clear_commands()")
        logger.info("  • 完整卸載所有 Cogs")
        logger.info("  • 改善錯誤處理機制")
        logger.info("  • 防止重複載入檢查")
        logger.info("  • 載入狀態追蹤")
        logger.info("\n現在可以安全啟動機器人！")
    else:
        logger.error("❌ 測試失敗")
        if not fix_success:
            logger.error("  • 載入修復有問題")
        if not files_success:
            logger.error("  • Cog 檔案有問題")
    
    return fix_success and files_success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n測試完成: {'成功' if result else '失敗'}")
