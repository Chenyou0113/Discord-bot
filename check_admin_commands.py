import sys
import os
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 確保 cogs 目錄在路徑中
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    logger.info("嘗試導入 admin_commands_fixed 模組...")
    from cogs import admin_commands_fixed
    logger.info("成功導入 admin_commands_fixed 模組！")
    
    # 檢查必要的類和函數是否存在
    if hasattr(admin_commands_fixed, 'AdminCommands'):
        logger.info("找到 AdminCommands 類")
    else:
        logger.error("admin_commands_fixed 模組中沒有 AdminCommands 類")
    
    if hasattr(admin_commands_fixed, 'setup'):
        logger.info("找到 setup 函數")
    else:
        logger.error("admin_commands_fixed 模組中沒有 setup 函數")
    
except Exception as e:
    logger.error(f"導入 admin_commands_fixed 模組時發生錯誤: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
