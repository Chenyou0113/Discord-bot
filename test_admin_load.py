import discord
from discord.ext import commands
import os
import sys
import importlib
import asyncio
import logging

# 設置日誌
logging.basicConfig(
    level=logging.DEBUG,  # 使用 DEBUG 級別以獲取所有日誌
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('test_admin_load.log', 'w', 'utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 配置基本的機器人
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 嘗試載入 admin_commands_fixed
async def test_load():
    try:
        logger.info("嘗試載入 admin_commands_fixed 模組...")
        
        # 先檢查文件是否存在
        file_path = "cogs/admin_commands_fixed.py"
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return
            
        logger.info(f"文件存在: {file_path}")
        
        # 查看模組是否已在路徑中
        if "cogs.admin_commands_fixed" in sys.modules:
            logger.info("模組已在系統路徑中，嘗試重新載入")
            try:
                importlib.reload(sys.modules["cogs.admin_commands_fixed"])
                logger.info("重新載入模組成功")
            except Exception as reload_error:
                logger.error(f"重新載入模組失敗: {str(reload_error)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # 嘗試載入擴展
        try:
            logger.info("使用 load_extension 載入模組...")
            await bot.load_extension("cogs.admin_commands_fixed")
            logger.info("成功載入 admin_commands_fixed 擴展！")
        except Exception as e:
            logger.error(f"載入擴展失敗: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # 嘗試直接導入模組
            try:
                logger.info("嘗試直接導入模組...")
                from cogs import admin_commands_fixed
                logger.info("成功直接導入模組")
                
                # 查找必要的類和方法
                if hasattr(admin_commands_fixed, "AdminCommands"):
                    logger.info("找到 AdminCommands 類")
                else:
                    logger.error("模組中沒有 AdminCommands 類")
                    
                if hasattr(admin_commands_fixed, "setup"):
                    logger.info("找到 setup 方法")
                    
                    # 嘗試手動設置
                    try:
                        cog = admin_commands_fixed.AdminCommands(bot)
                        bot.add_cog(cog)
                        logger.info("手動添加 cog 成功")
                    except Exception as cog_error:
                        logger.error(f"手動添加 cog 失敗: {str(cog_error)}")
                else:
                    logger.error("模組中沒有 setup 方法")
            except Exception as import_error:
                logger.error(f"直接導入模組失敗: {str(import_error)}")
                import traceback
                logger.error(traceback.format_exc())
                
    except Exception as e:
        logger.error(f"測試過程中發生未知錯誤: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
# 主運行函數
async def main():
    await test_load()
    
# 執行
try:
    logger.info("開始測試載入 admin_commands_fixed")
    asyncio.run(main())
    logger.info("測試完成")
except Exception as e:
    logger.error(f"執行測試時發生錯誤: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
