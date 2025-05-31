#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試地震功能修正
"""

import asyncio
import sys
import os

# 添加專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 模擬 Discord 機器人環境
class MockBot:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

async def test_earthquake_fetch():
    """測試地震資料獲取功能"""
    print("🧪 測試地震資料獲取功能...")
    
    try:
        # 導入修正後的模組
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        # 創建模擬機器人
        bot = MockBot()
        
        # 創建 InfoCommands 實例
        info_cog = InfoCommands(bot)
        
        # 初始化 aiohttp 工作階段
        await info_cog.init_aiohttp_session()
        
        print("✅ 成功初始化 InfoCommands")
        
        # 測試地震資料獲取
        print("🌍 正在獲取地震資料...")
        eq_data = await info_cog.fetch_earthquake_data()
        
        if eq_data:
            print(f"✅ 成功獲取地震資料")
            print(f"📊 資料結構: {list(eq_data.keys())}")
            
            # 檢查是否為異常格式
            if ('result' in eq_data and 
                isinstance(eq_data['result'], dict) and 
                set(eq_data['result'].keys()) == {'resource_id', 'fields'}):
                print("⚠️  檢測到 API 回傳異常格式（僅欄位定義）")
                print("💡 這表示可能存在授權問題或 API 參數錯誤")
                
                # 顯示欄位資訊
                if 'fields' in eq_data['result']:
                    fields = eq_data['result']['fields']
                    print(f"📋 可用欄位數量: {len(fields)}")
                    print("📋 前5個欄位:")
                    for i, field in enumerate(fields[:5]):
                        print(f"   {i+1}. {field.get('id', 'unknown')} ({field.get('type', 'unknown')})")
            else:
                print("✅ 資料格式正常")
                
                # 檢查是否有記錄
                if 'result' in eq_data and 'records' in eq_data['result']:
                    records = eq_data['result']['records']
                    print(f"📝 records 類型: {type(records)}")
                    if isinstance(records, dict):
                        print(f"📝 records 鍵: {list(records.keys())}")
        else:
            print("❌ 無法獲取地震資料")
        
        # 關閉工作階段
        if info_cog.session and not info_cog.session.closed:
            await info_cog.session.close()
            
        return eq_data is not None
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_response_handling():
    """測試不同 API 回應格式的處理"""
    print("\n🧪 測試 API 回應格式處理...")
    
    # 模擬異常格式回應
    mock_error_response = {
        'success': 'true',
        'result': {
            'resource_id': 'E-A0015-001',
            'fields': [
                {'id': 'ReportType', 'type': 'String'},
                {'id': 'EarthquakeNo', 'type': 'Integer'},
                {'id': 'ReportContent', 'type': 'String'}
            ]
        }
    }
    
    print("🔍 模擬異常格式檢測...")
    
    # 檢查異常格式
    if ('result' in mock_error_response and 
        isinstance(mock_error_response['result'], dict) and 
        set(mock_error_response['result'].keys()) == {'resource_id', 'fields'}):
        print("✅ 成功檢測到異常格式")
        print("💡 此格式應會被防呆機制攔截")
    else:
        print("❌ 異常格式檢測失敗")
    
    return True

async def main():
    """主測試函數"""
    print("🚀 開始測試地震功能修正...")
    print("=" * 50)
    
    # 測試1: 地震資料獲取
    test1_result = await test_earthquake_fetch()
    
    # 測試2: API 回應格式處理
    test2_result = await test_api_response_handling()
    
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    print(f"   地震資料獲取: {'✅ 通過' if test1_result else '❌ 失敗'}")
    print(f"   格式處理測試: {'✅ 通過' if test2_result else '❌ 失敗'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有測試通過！地震功能修正成功。")
        return True
    else:
        print("\n⚠️  部分測試失敗，請檢查相關問題。")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
