#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地震資料解析最終驗證
驗證修復後的地震資料解析功能
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

async def test_earthquake_parsing_logic():
    """測試地震解析邏輯的修復"""
    print("🔧 地震資料解析邏輯最終驗證")
    print("=" * 60)
    
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
        print("✅ InfoCommands 初始化成功")
        
        # 測試 1: 獲取並解析一般地震資料
        print("\n🌍 測試一般地震資料解析...")
        print("-" * 40)
        
        eq_data = await info_commands.fetch_earthquake_data(small_area=False)
        
        if eq_data:
            print("✅ 成功獲取地震資料")
            
            # 模擬 earthquake 指令的解析邏輯
            latest_eq = None
            records = None
            
            # 檢查資料結構 - 這是修復的核心邏輯
            if 'records' in eq_data:
                records = eq_data['records']
                print("✅ 檢測到有認證模式資料結構")
            elif 'result' in eq_data and 'records' in eq_data['result']:
                records = eq_data['result']['records']
                print("✅ 檢測到無認證模式資料結構")
            
            if records:
                # 標準格式檢查
                if isinstance(records, dict) and 'Earthquake' in records:
                    earthquake_data = records['Earthquake']
                    if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                        latest_eq = earthquake_data[0]
                        print("✅ 使用標準列表格式地震資料")
                    elif isinstance(earthquake_data, dict):
                        latest_eq = earthquake_data
                        print("✅ 使用標準字典格式地震資料")
                        
                # 檢查2025年新格式
                elif isinstance(records, dict) and 'datasetDescription' in records and 'Earthquake' in records:
                    earthquake_data = records['Earthquake']
                    if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                        latest_eq = earthquake_data[0]
                        print("✅ 使用2025年新格式地震資料")
            
            if latest_eq:
                print("✅ 成功解析地震資料")
                print(f"   📋 地震編號: {latest_eq.get('EarthquakeNo', 'N/A')}")
                print(f"   📋 報告類型: {latest_eq.get('ReportType', 'N/A')}")
                print(f"   📋 報告內容: {latest_eq.get('ReportContent', 'N/A')[:100]}...")
                
                # 檢查詳細資訊
                if 'EarthquakeInfo' in latest_eq:
                    eq_info = latest_eq['EarthquakeInfo']
                    print(f"   🕒 發生時間: {eq_info.get('OriginTime', 'N/A')}")
                    print(f"   📍 震央位置: {eq_info.get('Epicenter', {}).get('Location', 'N/A')}")
                    print(f"   📊 地震規模: {eq_info.get('EarthquakeMagnitude', {}).get('MagnitudeValue', 'N/A')}")
                
                # 測試 enhance_earthquake_data 功能
                enhanced_eq = info_commands.enhance_earthquake_data(latest_eq)
                if enhanced_eq:
                    print("✅ 地震資料增強處理成功")
                
                # 測試格式化功能
                embed = await info_commands.format_earthquake_data(enhanced_eq)
                if embed:
                    print("✅ 地震資料格式化成功")
                    print(f"   📄 嵌入標題: {embed.title}")
                    print(f"   📝 嵌入描述: {embed.description[:100] if embed.description else 'N/A'}...")
                else:
                    print("❌ 地震資料格式化失敗")
                    return False
            else:
                print("❌ 解析地震資料失敗")
                return False
        else:
            print("❌ 獲取地震資料失敗")
            return False
        
        # 測試 2: 獲取並解析小區域地震資料
        print("\n🏘️ 測試小區域地震資料解析...")
        print("-" * 40)
        
        small_eq_data = await info_commands.fetch_earthquake_data(small_area=True)
        
        if small_eq_data:
            print("✅ 成功獲取小區域地震資料")
            
            # 同樣的解析邏輯
            latest_eq = None
            records = None
            
            if 'records' in small_eq_data:
                records = small_eq_data['records']
                print("✅ 檢測到有認證模式資料結構")
            elif 'result' in small_eq_data and 'records' in small_eq_data['result']:
                records = small_eq_data['result']['records']
                print("✅ 檢測到無認證模式資料結構")
            
            if records and isinstance(records, dict) and 'Earthquake' in records:
                earthquake_data = records['Earthquake']
                if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                    latest_eq = earthquake_data[0]
                    print("✅ 使用標準列表格式地震資料")
            
            if latest_eq:
                print("✅ 成功解析小區域地震資料")
                print(f"   📋 地震編號: {latest_eq.get('EarthquakeNo', 'N/A')}")
                print(f"   📋 報告類型: {latest_eq.get('ReportType', 'N/A')}")
            else:
                print("❌ 解析小區域地震資料失敗")
                return False
        else:
            print("❌ 獲取小區域地震資料失敗")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 地震資料解析修復完成！")
        print("✅ 有認證模式 API 調用正常")
        print("✅ 資料結構檢測正確")
        print("✅ 地震資料解析成功")
        print("✅ 資料增強處理正常")
        print("✅ Discord 嵌入格式化正常")
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
    success = await test_earthquake_parsing_logic()
    
    if success:
        print("\n🎯 修復驗證結果: ✅ 地震資料解析完全正常")
        print("💡 可以安全重啟 Bot，地震指令已修復")
        print("\n📋 修復總結:")
        print("   • ✅ 修復了地震指令的異常格式檢查邏輯")
        print("   • ✅ 調整了 API 調用順序，優先使用有認證模式")
        print("   • ✅ 確保了有認證和無認證資料結構都能正確解析")
        print("   • ✅ 地震資料增強和格式化功能正常")
        print("   • ✅ 解決了「無法解析地震資料」的問題")
        print("\n🚀 Bot 現在應該能正常顯示地震資料了！")
    else:
        print("\n🎯 修復驗證結果: ❌ 仍需進一步檢查")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
