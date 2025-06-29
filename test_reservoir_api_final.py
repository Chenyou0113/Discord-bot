#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水庫水情 API 的最終版本
API 端點: https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=1602CA19-B224-4CC3-AA31-11B1B124530F
"""

import requests
import json
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_reservoir_api():
    """測試水庫水情 API"""
    print("🏞️ 測試水庫水情 API...")
    print("=" * 50)
    
    # API 端點
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=1602CA19-B224-4CC3-AA31-11B1B124530F"
    
    try:
        print(f"📡 請求 API: {api_url}")
        
        # 發送請求
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        print(f"✅ HTTP 狀態碼: {response.status_code}")
        print(f"📊 回應大小: {len(response.content)} bytes")
        print(f"🔤 編碼: {response.encoding}")
        
        # 處理 UTF-8 BOM 問題
        raw_text = response.content.decode('utf-8-sig')
        
        # 解析 JSON
        data = json.loads(raw_text)
        
        print(f"📋 資料筆數: {len(data)}")
        
        # 分析資料結構
        if data:
            print("\n🔍 資料結構分析:")
            first_item = data[0]
            print(f"📋 第一筆資料的欄位:")
            
            for key, value in first_item.items():
                print(f"  {key}: {value} ({type(value).__name__})")
            
            print("\n📈 範例資料 (前 3 筆):")
            for i, item in enumerate(data[:3], 1):
                print(f"\n  {i}. {item.get('ReservoirName', 'N/A')}")
                print(f"     蓄水量: {item.get('EffectiveCapacity', 'N/A')} 萬立方公尺")
                print(f"     蓄水率: {item.get('Percentage', 'N/A')}%")
                print(f"     更新時間: {item.get('ReservoirInfo', {}).get('UpdateTime', 'N/A')}")
        
        # 儲存完整資料供參考
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reservoir_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 完整資料已儲存至: {filename}")
        
        # 分析重要欄位
        print("\n🎯 重要欄位分析:")
        
        if data:
            # 取得所有可能的欄位
            all_keys = set()
            for item in data[:10]:  # 檢查前10筆
                all_keys.update(item.keys())
            
            print(f"📋 發現的欄位 ({len(all_keys)} 個):")
            for key in sorted(all_keys):
                print(f"  - {key}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路請求錯誤: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_reservoir_api()
    
    print("\n🎯 下一步:")
    if success:
        print("  ✅ API 測試成功")
        print("  📝 可以開始開發 Discord 指令")
        print("  🔧 建議建立 cogs/reservoir_commands.py")
    else:
        print("  ❌ API 測試失敗")
        print("  🔍 需要檢查網路連線或 API 狀態")
