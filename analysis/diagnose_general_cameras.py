#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷「無法取得一般監視器的資料」問題
"""

import requests
import json
import ssl
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_general_cameras_apis():
    """測試一般監視器的各種 API"""
    
    print("🔍 診斷一般監視器資料獲取問題")
    print("="*50)
    
    # 1. 測試省道監視器 API
    print("\n1️⃣ 測試省道監視器 API")
    api_url = "https://tisvcloud.freeway.gov.tw/api/v1/road/camera/snapshot/info/all"
    
    try:
        response = requests.get(api_url, timeout=30, verify=False)
        print(f"   狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ JSON 解析成功")
                print(f"   資料類型: {type(data)}")
                print(f"   資料長度: {len(data) if isinstance(data, list) else 'N/A'}")
                
                if isinstance(data, list) and data:
                    first_item = data[0]
                    print(f"   第一筆資料欄位: {list(first_item.keys()) if isinstance(first_item, dict) else 'N/A'}")
                    
                    # 檢查是否有 Devices
                    if 'Devices' in first_item:
                        devices = first_item['Devices']
                        print(f"   Devices 數量: {len(devices)}")
                        if devices:
                            device = devices[0]
                            print(f"   第一個 Device 欄位: {list(device.keys())}")
                    
            except json.JSONDecodeError:
                print(f"   ❌ JSON 解析失敗")
                print(f"   回應內容前 200 字: {response.text[:200]}")
        else:
            print(f"   ❌ API 請求失敗: {response.status_code}")
            print(f"   錯誤內容: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ 請求異常: {e}")
    
    # 2. 測試替代 API
    print("\n2️⃣ 測試交通部運輸資料流通服務平台")
    
    alternative_apis = [
        "https://traffic.transportdata.tw/api/basic/v2/Camera/CameraInfo/Road/City?format=json",
        "https://traffic.transportdata.tw/api/basic/v2/Traffic/Live/CCTV/Road/City?format=json",
    ]
    
    for i, api_url in enumerate(alternative_apis, 1):
        print(f"\n   測試 API {i}: {api_url[:50]}...")
        
        try:
            # 有些 API 需要 headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            
            response = requests.get(api_url, timeout=30, verify=False, headers=headers)
            print(f"   狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON 解析成功")
                    print(f"   資料類型: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"   清單長度: {len(data)}")
                        if data:
                            print(f"   第一筆欄位: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                    elif isinstance(data, dict):
                        print(f"   字典鍵值: {list(data.keys())}")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ JSON 解析失敗")
            else:
                print(f"   ❌ 狀態碼: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 請求異常: {e}")
    
    # 3. 測試政府開放資料平台
    print("\n3️⃣ 測試政府開放資料平台")
    gov_apis = [
        "https://data.gov.tw/api/v2/rest/datastore/116220",  # CCTV資料
        "https://data.gov.tw/api/v1/rest/datastore/116220",  # 舊版API
    ]
    
    for i, api_url in enumerate(gov_apis, 1):
        print(f"\n   測試政府 API {i}: {api_url}")
        
        try:
            response = requests.get(api_url, timeout=30, verify=False)
            print(f"   狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON 解析成功")
                    
                    if 'result' in data:
                        result = data['result']
                        print(f"   result 類型: {type(result)}")
                        if 'records' in result:
                            records = result['records']
                            print(f"   records 數量: {len(records)}")
                            if records:
                                print(f"   第一筆欄位: {list(records[0].keys())}")
                    
                except json.JSONDecodeError:
                    print(f"   ❌ JSON 解析失敗")
            else:
                print(f"   ❌ 狀態碼: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 請求異常: {e}")

def diagnose_specific_issue():
    """診斷具體問題"""
    
    print("\n" + "="*50)
    print("🔧 問題診斷")
    
    # 檢查網路連線
    print("\n🌐 檢查網路連線...")
    try:
        response = requests.get("https://www.google.com", timeout=10, verify=False)
        if response.status_code == 200:
            print("   ✅ 網路連線正常")
        else:
            print(f"   ⚠️ 網路連線異常，狀態碼: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 網路連線失敗: {e}")
    
    # 檢查 SSL 設定
    print("\n🔒 檢查 SSL 設定...")
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        print("   ✅ SSL 上下文建立成功")
    except Exception as e:
        print(f"   ❌ SSL 設定有問題: {e}")

def provide_solutions():
    """提供解決方案"""
    
    print("\n" + "="*50)
    print("💡 可能的解決方案")
    
    solutions = [
        "1. 檢查 API 是否已停用或遷移",
        "2. 嘗試使用不同的 API 端點",
        "3. 檢查是否需要 API 金鑰或認證",
        "4. 確認防火牆或代理伺服器設定",
        "5. 聯繫 API 提供者確認服務狀態",
        "6. 考慮使用快取機制降低失敗影響",
        "7. 實作多個備用 API 來源",
        "8. 添加更詳細的錯誤處理和日誌"
    ]
    
    for solution in solutions:
        print(f"   {solution}")

if __name__ == "__main__":
    test_general_cameras_apis()
    diagnose_specific_issue()
    provide_solutions()
    
    print("\n" + "="*50)
    print("📊 診斷完成")
    print("請檢查上述測試結果，找出無法取得資料的具體原因。")
