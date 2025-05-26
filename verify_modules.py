"""
此檔案用於驗證修復後的功能
"""

import asyncio
import sys
import os
import logging
import importlib
from datetime import datetime

# 設定日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("開始驗證修復後的功能")
        
        # 測試模組匯入
        logger.info("測試 info_commands_fixed_v4 模組匯入:")
        try:
            # 確保 cogs 目錄在搜尋路徑中
            if os.path.abspath('cogs') not in sys.path:
                sys.path.append(os.path.abspath('cogs'))
            
            # 嘗試匯入模組
            info_commands = importlib.import_module('info_commands_fixed_v4')
            logger.info("✅ 成功匯入 info_commands_fixed_v4 模組")
            
            # 檢查主要類別是否存在
            if hasattr(info_commands, 'InfoCommands'):
                logger.info("✅ InfoCommands 類別存在")
            else:
                logger.error("❌ InfoCommands 類別不存在")
                
            # 檢查主要方法是否存在
            if hasattr(info_commands, 'setup'):
                logger.info("✅ setup 函數存在")
            else:
                logger.error("❌ setup 函數不存在")
            
        except ImportError as e:
            logger.error(f"❌ 匯入模組失敗: {str(e)}")
        except Exception as e:
            logger.error(f"❌ 其他錯誤: {str(e)}")
        
        # 驗證 level_system.py 的改動
        logger.info("\n測試 level_system 模組匯入:")
        try:
            level_system = importlib.import_module('level_system')
            logger.info("✅ 成功匯入 level_system 模組")
            
            # 檢查 LevelSystem 類別是否存在
            if hasattr(level_system, 'LevelSystem'):
                logger.info("✅ LevelSystem 類別存在")
            else:
                logger.error("❌ LevelSystem 類別不存在")
                
            # 檢查命令是否存在
            level_system_class = level_system.LevelSystem
            if hasattr(level_system_class, 'leaderboard'):
                logger.info("✅ leaderboard 命令存在")
            else:
                logger.error("❌ leaderboard 命令不存在")
                
        except ImportError as e:
            logger.error(f"❌ 匯入 level_system 模組失敗: {str(e)}")
        except Exception as e:
            logger.error(f"❌ 其他錯誤: {str(e)}")
        
        logger.info("\n驗證完成")
        
    except Exception as e:
        logger.error(f"驗證過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
