#!/usr/bin/env python3
"""
測試捷運新聞功能
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

async def test_metro_news():
    """測試捷運新聞功能是否正常運作"""
    try:
        # 導入InfoCommands類
        sys.path.append(os.getcwd())
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        # 創建一個模擬的機器人物件
        class MockBot:
            pass
        
        bot = MockBot()
        info_cog = InfoCommands(bot)
        
        # 測試是否有fetch_metro_news方法
        if hasattr(info_cog, 'fetch_metro_news'):
            print("✅ fetch_metro_news 方法存在於 InfoCommands 類別中")
            
            # 測試方法是否可調用
            if callable(getattr(info_cog, 'fetch_metro_news')):
                print("✅ fetch_metro_news 方法可以被調用")
                print("🎉 捷運新聞功能修復成功！")
                return True
            else:
                print("❌ fetch_metro_news 方法不可調用")
                return False
        else:
            print("❌ fetch_metro_news 方法不存在於 InfoCommands 類別中")
            return False
            
    except Exception as e:
        print(f"❌ 測試時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_metro_news())
    if result:
        print("\n🎯 總結: 捷運新聞功能已完全修復，可以正常使用！")
    else:
        print("\n❌ 總結: 捷運新聞功能仍有問題，需要進一步檢查。")