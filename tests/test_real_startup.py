#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接啟動測試 - 實際連接Discord驗證修復
"""

import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('startup_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """處理中斷信號"""
    print("\n🛑 收到中斷信號，正在安全關閉...")
    sys.exit(0)

async def main():
    """主函數"""
    print("🚀 Discord 機器人啟動測試")
    print("=" * 50)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 註冊信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 載入環境變數
        load_dotenv()
        token = os.getenv('DISCORD_TOKEN')
        
        if not token:
            print("❌ 找不到 DISCORD_TOKEN")
            return
        
        print("✅ 環境變數檢查通過")
        
        # 導入並創建機器人
        print("📦 導入機器人模組...")
        from bot import CustomBot
        
        print("🤖 創建機器人實例...")
        bot = CustomBot()
        
        print("🔗 嘗試連接到 Discord...")
        print("📋 預期載入的 Cogs:")
        for i, ext in enumerate(bot.initial_extensions, 1):
            print(f"   {i:2d}. {ext}")
        
        print("\n🚀 啟動機器人... (按 Ctrl+C 停止)")
        print("=" * 50)
        
        # 啟動機器人
        await bot.start(token)
        
    except KeyboardInterrupt:
        print("\n🛑 收到鍵盤中斷")
    except Exception as e:
        print(f"\n❌ 啟動過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
    finally:
        if 'bot' in locals():
            print("🧹 清理資源...")
            try:
                await bot.close()
            except:
                pass
        print("👋 測試結束")

if __name__ == "__main__":
    # 設定工作目錄
    os.chdir(r"c:\Users\xiaoy\Desktop\Discord bot")
    
    print("⚠️  注意: 這將實際連接到 Discord")
    print("⚠️  如果看到成功載入訊息，表示修復成功")
    print("⚠️  請在看到機器人上線後按 Ctrl+C 停止測試")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 測試已停止")
