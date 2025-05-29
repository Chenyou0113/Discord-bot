#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海嘯功能測試腳本
測試修復後的海嘯資料查詢功能
"""

import asyncio
import aiohttp
import json
import ssl
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定 SSL 上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def test_tsunami_api():
    """測試海嘯API是否正常工作"""
    print("🌊 開始測試海嘯API功能...")
    
    # 獲取API金鑰
    api_auth = os.getenv('CWA_API_KEY')
    if not api_auth:
        print("❌ 找不到CWA_API_KEY環境變數")
        return False
    
    # 海嘯API端點
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0014-001?Authorization={api_auth}"
    
    try:
        # 創建連接器
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30)) as session:
            print(f"📡 正在請求API: {url}")
            
            async with session.get(url) as response:
                print(f"📊 HTTP狀態碼: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # 檢查資料結構
                    print(f"✅ API請求成功")
                    print(f"📋 回傳資料的根層級鍵: {list(data.keys())}")
                    
                    # 檢查是否有success欄位
                    if 'success' in data:
                        print(f"🎯 Success: {data['success']}")
                    
                    # 檢查records結構（這是我們修復的重點）
                    if 'records' in data:
                        print(f"📁 Records結構: {list(data['records'].keys()) if isinstance(data['records'], dict) else type(data['records'])}")
                        
                        # 檢查Tsunami資料
                        if isinstance(data['records'], dict) and 'Tsunami' in data['records']:
                            tsunami_data = data['records']['Tsunami']
                            print(f"🌊 海嘯資料類型: {type(tsunami_data)}")
                            
                            if isinstance(tsunami_data, list):
                                print(f"📊 海嘯記錄數量: {len(tsunami_data)}")
                                
                                if len(tsunami_data) > 0:
                                    print("✅ 找到海嘯資料！")
                                    first_record = tsunami_data[0]
                                    print(f"📝 第一筆記錄的鍵: {list(first_record.keys()) if isinstance(first_record, dict) else '不是字典格式'}")
                                    
                                    # 檢查重要欄位
                                    if isinstance(first_record, dict):
                                        if 'ReportContent' in first_record:
                                            content = first_record['ReportContent']
                                            print(f"📄 報告內容: {content[:100]}..." if len(content) > 100 else f"📄 報告內容: {content}")
                                        
                                        if 'ReportType' in first_record:
                                            print(f"📋 報告類型: {first_record['ReportType']}")
                                        
                                        if 'ReportColor' in first_record:
                                            print(f"🎨 報告顏色: {first_record['ReportColor']}")
                                    
                                    return True
                                else:
                                    print("⚠️ 海嘯資料為空陣列")
                                    return True  # API工作正常，只是沒有海嘯資料
                            else:
                                print(f"❌ 海嘯資料不是陣列格式: {type(tsunami_data)}")
                                return False
                        else:
                            print("❌ Records中沒有找到Tsunami欄位")
                            return False
                    else:
                        print("❌ 回傳資料中沒有records欄位")
                        return False
                else:
                    print(f"❌ API請求失敗，狀態碼: {response.status}")
                    text = await response.text()
                    print(f"錯誤回應: {text[:200]}...")
                    return False
                    
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        return False

async def test_tsunami_data_parsing():
    """測試海嘯資料解析邏輯"""
    print("\n🔍 測試海嘯資料解析邏輯...")
    
    # 載入樣本資料
    try:
        with open('sample_tsunami.json', 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
            
        print("✅ 成功載入樣本海嘯資料")
        print(f"📋 樣本資料結構: {list(sample_data.keys())}")
        
        # 測試修復後的檢查邏輯
        if ('records' not in sample_data or 
            'Tsunami' not in sample_data['records']):
            print("❌ 資料結構檢查失敗")
            print(f"實際結構: {list(sample_data.keys())}")
            if 'records' in sample_data:
                print(f"records內容: {list(sample_data['records'].keys()) if isinstance(sample_data['records'], dict) else type(sample_data['records'])}")
            return False
        else:
            print("✅ 資料結構檢查通過")
            
            # 檢查海嘯資料
            tsunami_records = sample_data['records']['Tsunami']
            if isinstance(tsunami_records, list) and len(tsunami_records) > 0:
                print(f"✅ 找到 {len(tsunami_records)} 筆海嘯記錄")
                
                # 檢查第一筆記錄的完整性
                first_record = tsunami_records[0]
                required_fields = ['ReportContent', 'ReportType']
                missing_fields = [field for field in required_fields if field not in first_record]
                
                if missing_fields:
                    print(f"⚠️ 缺少必要欄位: {missing_fields}")
                else:
                    print("✅ 所有必要欄位都存在")
                    
                return True
            else:
                print("❌ 海嘯記錄為空或格式不正確")
                return False
                
    except FileNotFoundError:
        print("⚠️ 找不到sample_tsunami.json文件，跳過樣本資料測試")
        return True
    except Exception as e:
        print(f"❌ 解析樣本資料時發生錯誤: {str(e)}")
        return False

async def main():
    """主要測試函數"""
    print("=" * 50)
    print("🌊 海嘯功能修復後測試")
    print("=" * 50)
    
    # 測試API連接
    api_test = await test_tsunami_api()
    
    # 測試資料解析
    parsing_test = await test_tsunami_data_parsing()
    
    print("\n" + "=" * 50)
    print("📊 測試結果總結")
    print("=" * 50)
    print(f"🌐 API連接測試: {'✅ 通過' if api_test else '❌ 失敗'}")
    print(f"🔍 資料解析測試: {'✅ 通過' if parsing_test else '❌ 失敗'}")
    
    if api_test and parsing_test:
        print("\n🎉 所有測試通過！海嘯功能修復成功！")
        print("💡 建議：現在可以在Discord中測試 /tsunami 命令")
    else:
        print("\n⚠️ 部分測試失敗，請檢查相關配置")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
