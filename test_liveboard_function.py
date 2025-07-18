#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試捷運即時電子看板功能
"""

import os
import sys
import asyncio
import aiohttp
import ssl
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def test_metro_liveboard():
    """測試捷運即時電子看板API"""
    print("🚇 測試捷運即時電子看板API...")
    
    # 檢查環境變數
    client_id = os.getenv('TDX_CLIENT_ID')
    client_secret = os.getenv('TDX_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ TDX API 憑證未設定！")
        return False
    
    print(f"✅ TDX_CLIENT_ID: {client_id[:10]}...")
    print(f"✅ TDX_CLIENT_SECRET: {client_secret[:10]}...")
    
    # 設定SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context)
    ) as session:
        
        # 取得access token
        print("\n🔑 取得Access Token...")
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        try:
            async with session.post(token_url, data=token_data) as response:
                if response.status == 200:
                    token_info = await response.json()
                    access_token = token_info.get('access_token')
                    if access_token:
                        print(f"✅ 成功取得Access Token: {access_token[:20]}...")
                        
                        # 測試各個捷運系統的即時電子看板
                        metro_systems = {
                            'TRTC': {
                                'name': '台北捷運',
                                'url': 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/TRTC?%24top=30&%24format=JSON'
                            },
                            'KRTC': {
                                'name': '高雄捷運', 
                                'url': 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KRTC?%24top=30&%24format=JSON'
                            },
                            'KLRT': {
                                'name': '高雄輕軌',
                                'url': 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KLRT?%24top=30&%24format=JSON'
                            }
                        }
                        
                        headers = {
                            'Authorization': f'Bearer {access_token}',
                            'Accept': 'application/json'
                        }
                        
                        success_count = 0
                        
                        for system_code, system_info in metro_systems.items():
                            print(f"\n📱 測試 {system_info['name']} 即時電子看板...")
                            
                            try:
                                async with session.get(system_info['url'], headers=headers) as liveboard_response:
                                    if liveboard_response.status == 200:
                                        liveboard_data = await liveboard_response.json()
                                        print(f"  ✅ API回應正常，資料筆數: {len(liveboard_data)}")
                                        
                                        if liveboard_data and len(liveboard_data) > 0:
                                            # 分析第一筆資料結構
                                            first_station = liveboard_data[0]
                                            print(f"  📊 資料欄位: {list(first_station.keys())}")
                                            
                                            # 檢查關鍵欄位
                                            station_name = first_station.get('StationName', {})
                                            if isinstance(station_name, dict):
                                                station_name_zh = station_name.get('Zh_tw', '未知')
                                            else:
                                                station_name_zh = str(station_name)
                                            
                                            print(f"  🚉 範例車站: {station_name_zh}")
                                            
                                            # 檢查LiveBoards資料
                                            live_boards = first_station.get('LiveBoards', [])
                                            if live_boards:
                                                print(f"  🚆 該站有 {len(live_boards)} 班列車資訊")
                                                if len(live_boards) > 0:
                                                    first_train = live_boards[0]
                                                    destination = first_train.get('DestinationStationName', {})
                                                    if isinstance(destination, dict):
                                                        dest_name = destination.get('Zh_tw', '未知')
                                                    else:
                                                        dest_name = str(destination)
                                                    enter_time = first_train.get('EnterTime', '未知')
                                                    print(f"    ➤ 範例列車: 往{dest_name} ({enter_time})")
                                            else:
                                                print(f"  ℹ️ 該站目前沒有列車資訊")
                                            
                                            success_count += 1
                                        else:
                                            print(f"  ℹ️ 目前 {system_info['name']} 沒有即時電子看板資料")
                                            
                                    else:
                                        print(f"  ❌ API請求失敗: {liveboard_response.status}")
                                        if liveboard_response.status == 404:
                                            print(f"  ⚠️ {system_info['name']} 可能不支援即時電子看板API")
                                        
                            except Exception as e:
                                print(f"  ❌ 連接錯誤: {str(e)}")
                        
                        print(f"\n📊 測試結果: {success_count}/{len(metro_systems)} 個系統測試成功")
                        return success_count > 0
                        
                    else:
                        print("❌ Token回應中沒有access_token")
                else:
                    print(f"❌ Token請求失敗: {response.status}")
                    text = await response.text()
                    print(f"回應內容: {text}")
                    
        except Exception as e:
            print(f"❌ 連接錯誤: {str(e)}")
    
    return False

def check_liveboard_implementation():
    """檢查即時電子看板功能的實作"""
    print("🔍 檢查即時電子看板功能實作...")
    
    file_path = os.path.join('cogs', 'info_commands_fixed_v4_clean.py')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查必要的方法和指令
        checks = [
            ('fetch_metro_liveboard', '📱 取得即時電子看板方法'),
            ('format_metro_liveboard', '📊 格式化電子看板方法'),
            ("@app_commands.command(name='即時電子看板'", '📱 即時電子看板指令'),
            ('LiveBoard/TRTC', '🚇 台北捷運電子看板API'),
            ('LiveBoard/KRTC', '🚇 高雄捷運電子看板API'),
            ('LiveBoard/KLRT', '🚋 高雄輕軌電子看板API'),
            ('StationName', '🚉 車站名稱欄位處理'),
            ('LiveBoards', '🚆 列車資訊處理'),
            ('EnterTime', '⏰ 到站時間處理'),
        ]
        
        results = []
        for check_text, description in checks:
            if check_text in content:
                print(f"✅ {description}")
                results.append(True)
            else:
                print(f"❌ {description}")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        success_rate = (success_count / total_count) * 100
        
        print(f"\n📊 實作檢查結果: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        return success_rate >= 80
        
    except FileNotFoundError:
        print(f"❌ 找不到檔案: {file_path}")
        return False
    except Exception as e:
        print(f"❌ 檢查時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 開始測試捷運即時電子看板功能...\n")
    
    # 檢查實作
    impl_ok = check_liveboard_implementation()
    
    if impl_ok:
        # 測試API連接
        api_ok = asyncio.run(test_metro_liveboard())
        
        print(f"\n🏁 最終結果:")
        print(f"   實作狀態: {'✅ 通過' if impl_ok else '❌ 未通過'}")
        print(f"   API測試: {'✅ 通過' if api_ok else '❌ 未通過'}")
        
        if impl_ok and api_ok:
            print("\n🎉 即時電子看板功能已準備完成，可以測試使用！")
            print("\n使用方式:")
            print("1. 運行機器人: python bot.py")
            print("2. 在Discord中使用指令:")
            print("   - /即時電子看板 : 查詢捷運車站即時到離站資訊")
        else:
            print("\n⚠️ 還有問題需要解決才能正常使用")
    else:
        print("\n❌ 實作不完整，無法進行API測試")
    
    print("\n🏁 測試完成")
