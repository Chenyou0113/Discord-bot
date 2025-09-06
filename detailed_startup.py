import sys
import logging
import os

# 設置日誌
logging.basicConfig(
    level=logging.DEBUG,  # 使用 DEBUG 級別以獲取所有日誌
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('detailed_bot_startup.log', 'w', 'utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 啟動主程式
try:
    logging.info("開始啟動機器人，使用詳細日誌...")
    
    # 載入主模組
    import bot
    logging.info("成功導入 bot 模組")
    
    # 執行主函數
    if hasattr(bot, 'main'):
        logging.info("找到 main 函數，開始執行...")
        bot.main()
    else:
        logging.error("bot 模組中沒有 main 函數")
        
except Exception as e:
    logging.error(f"啟動機器人時發生錯誤: {str(e)}")
    import traceback
    logging.error(traceback.format_exc())
