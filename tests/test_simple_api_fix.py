#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的 API 修復測試
"""

import sys
import os
import asyncio
import logging

# 設置編碼
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_api_fix():
    """測試 API 修復"""
    
    print("=== Bot API 修復測試 ===")
    
    try:
        # 匯入修復後的 InfoCommands
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock
        
        # 創建模擬 Bot
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.id = 123456789
        
        # 初始化 InfoCommands
        info_commands = InfoCommands(mock_bot)
        await info_commands.cog_load()
        
        print("OK: Bot 初始化成功")
        
        # 測試一般地震資料
        print("正在測試一般地震資料獲取...")
        normal_data = await info_commands.fetch_earthquake_data(small_area=False)
        
        if normal_data:
            print("OK: 一般地震資料獲取成功")
            
            # 檢查資料結構
            if 'records' in normal_data:
                records = normal_data['records']
                print("OK: 使用有認證模式 (根級別 records)")
            elif 'result' in normal_data and 'records' in normal_data.get('result', {}):
                records = normal_data['result']['records']
                print("OK: 使用無認證模式 (result.records)")
            else:
                print("ERROR: 無法識別資料結構")
                return False
            
            if records and 'Earthquake' in records and records['Earthquake']:
                earthquake = records['Earthquake'][0]
                eq_no = earthquake.get('EarthquakeNo', 'N/A')
                eq_type = earthquake.get('ReportType', 'N/A')
                print(f"OK: 地震編號 {eq_no}, 類型 {eq_type}")
                print("SUCCESS: 地震資料解析正常")
            else:
                print("ERROR: 地震資料結構不完整")
                return False
        else:
            print("ERROR: 無法獲取地震資料")
            return False
        
        print("\n=== 測試結果 ===")
        print("SUCCESS: API 修復驗證通過!")
        print("建議: 可以重新啟動 Bot 測試實際功能")
        
        return True
        
    except Exception as e:
        print(f"ERROR: 測試失敗 - {str(e)}")
        return False
    
    finally:
        # 清理資源
        if 'info_commands' in locals() and hasattr(info_commands, 'session'):
            if info_commands.session and not info_commands.session.closed:
                await info_commands.session.close()

if __name__ == "__main__":
    result = asyncio.run(test_api_fix())
    sys.exit(0 if result else 1)
