#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試機器人載入溫度命令模組
驗證溫度分布指令是否正確註冊
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

async def test_bot_loading():
    """測試機器人載入"""
    try:
        # 檢查必要檔案
        required_files = [
            'bot.py',
            'cogs/temperature_commands.py',
            '.env'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                logger.error(f"缺少必要檔案: {file_path}")
                return False
        
        logger.info("✅ 所有必要檔案存在")
        
        # 嘗試導入模組
        try:
            from cogs.temperature_commands import TemperatureCommands
            logger.info("✅ 成功導入 TemperatureCommands")
        except ImportError as e:
            logger.error(f"❌ 導入 TemperatureCommands 失敗: {e}")
            return False
        
        # 檢查 bot.py 中是否有溫度命令
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
            if 'temperature_commands' in bot_content:
                logger.info("✅ bot.py 中已包含 temperature_commands")
            else:
                logger.error("❌ bot.py 中未包含 temperature_commands")
                return False
        
        logger.info("✅ 機器人載入測試通過")
        return True
        
    except Exception as e:
        logger.error(f"測試機器人載入時發生錯誤: {e}")
        return False

async def main():
    """主測試函數"""
    logger.info("開始測試機器人載入溫度命令模組")
    
    success = await test_bot_loading()
    
    if success:
        logger.info("✅ 所有測試通過，機器人可以正常載入溫度命令")
        logger.info("指令說明:")
        logger.info("  /temperature - 查詢台灣溫度分布狀態")
        logger.info("功能特色:")
        logger.info("  • 即時溫度資料查詢")
        logger.info("  • 全台測站溫度統計")
        logger.info("  • 最高/最低溫度顯示")
        logger.info("  • 互動式重新整理按鈕")
        logger.info("  • 30分鐘快取機制")
    else:
        logger.error("❌ 測試失敗，請檢查相關設定")
    
    logger.info("測試完成")

if __name__ == "__main__":
    asyncio.run(main())
