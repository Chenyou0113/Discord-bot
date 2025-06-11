#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整 Bot API 修復測試
測試修復後的 Bot 是否能正常獲取地震資料
"""

import sys
import os
import asyncio
import logging

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_bot_earthquake_api():
    """測試 Bot 的地震 API 功能"""
      print("Bot 測試修復後的地震 API 功能")
    print("=" * 60)
    
    try:
        # 模擬 Bot 環境
        from unittest.mock import MagicMock
        
        # 匯入修復後的 InfoCommands
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        # 創建模擬 Bot
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.id = 123456789
        
        # 初始化 InfoCommands
        info_commands = InfoCommands(mock_bot)
        await info_commands.cog_load()
          print("OK Bot 和 InfoCommands 初始化成功")
        
        # 測試一般地震資料獲取
        print("\n>> 測試一般地震資料獲取...")
        print("-" * 40)
        
        normal_data = await info_commands.fetch_earthquake_data(small_area=False)
        
        if normal_data:
            print("✅ 一般地震資料獲取成功")
            
            # 檢查資料結構
            records = None
            if 'records' in normal_data:
                records = normal_data['records']
                print("✅ 使用有認證模式資料結構 (根級別)")
            elif 'result' in normal_data and 'records' in normal_data.get('result', {}):
                records = normal_data['result']['records']
                print("✅ 使用無認證模式資料結構 (result.records)")
            
            if records and 'Earthquake' in records and records['Earthquake']:
                earthquake = records['Earthquake'][0]
                print(f"   📋 地震編號: {earthquake.get('EarthquakeNo', 'N/A')}")
                print(f"   📋 報告類型: {earthquake.get('ReportType', 'N/A')}")
                print(f"   📋 報告內容: {earthquake.get('ReportContent', 'N/A')[:100]}...")
                
                # 檢查地震詳細資訊
                if 'EarthquakeInfo' in earthquake:
                    eq_info = earthquake['EarthquakeInfo']
                    print(f"   🕒 發生時間: {eq_info.get('OriginTime', 'N/A')}")
                    print(f"   📍 震央位置: {eq_info.get('Epicenter', {}).get('Location', 'N/A')}")
                    print(f"   📊 地震規模: {eq_info.get('EarthquakeMagnitude', {}).get('MagnitudeValue', 'N/A')}")
                
                print("✅ 地震資料結構完整且正確")
            else:
                print("❌ 地震資料結構不完整")
                return False
        else:
            print("❌ 一般地震資料獲取失敗")
            return False
        
        # 測試小區域地震資料獲取
        print("\n🏘️ 測試小區域地震資料獲取...")
        print("-" * 40)
        
        small_data = await info_commands.fetch_earthquake_data(small_area=True)
        
        if small_data:
            print("✅ 小區域地震資料獲取成功")
            
            # 檢查資料結構
            records = None
            if 'records' in small_data:
                records = small_data['records']
                print("✅ 使用有認證模式資料結構 (根級別)")
            elif 'result' in small_data and 'records' in small_data.get('result', {}):
                records = small_data['result']['records']
                print("✅ 使用無認證模式資料結構 (result.records)")
            
            if records and 'Earthquake' in records and records['Earthquake']:
                earthquake = records['Earthquake'][0]
                print(f"   📋 地震編號: {earthquake.get('EarthquakeNo', 'N/A')}")
                print(f"   📋 報告類型: {earthquake.get('ReportType', 'N/A')}")
                print("✅ 小區域地震資料結構完整且正確")
            else:
                print("❌ 小區域地震資料結構不完整")
                return False
        else:
            print("❌ 小區域地震資料獲取失敗")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 所有測試通過！API 修復成功！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理資源
        if 'info_commands' in locals() and hasattr(info_commands, 'session'):
            if info_commands.session and not info_commands.session.closed:
                await info_commands.session.close()
                print("🧹 已清理網路會話資源")

async def main():
    """主函數"""
    success = await test_bot_earthquake_api()
    
    if success:
        print("\n🎯 修復驗證結果: ✅ API 功能完全正常")
        print("💡 建議: 可以重新啟動 Bot 測試實際功能")
    else:
        print("\n🎯 修復驗證結果: ❌ 仍有問題需要解決")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
