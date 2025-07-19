#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試TDX捷運即時電子看板API資料結構
"""

import os
import sys
import asyncio
import aiohttp
import ssl
import json
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def debug_metro_liveboard_api():
    """調試捷運即時電子看板API"""
    print("🔍 調試TDX捷運即時電子看板API...")
    
    # 檢查環境變數
    client_id = os.getenv('TDX_CLIENT_ID')
    client_secret = os.getenv('TDX_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ TDX API 憑證未設定！")
        return False
    
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
                        print(f"✅ 成功取得Access Token")
                        
                        # 測試台北捷運即時電子看板API
                        print("\n🚇 測試台北捷運即時電子看板API...")
                        metro_url = 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/TRTC?%24top=5&%24format=JSON'
                        
                        headers = {
                            'Authorization': f'Bearer {access_token}',
                            'Accept': 'application/json'
                        }
                        
                        async with session.get(metro_url, headers=headers) as metro_response:
                            if metro_response.status == 200:
                                metro_data = await metro_response.json()
                                print(f"✅ 成功取得台北捷運LiveBoard資料，共 {len(metro_data)} 筆")
                                
                                if metro_data and len(metro_data) > 0:
                                    print("\n📋 資料結構分析:")
                                    
                                    # 分析第一筆車站資料
                                    first_station = metro_data[0]
                                    print(f"🚉 第一個車站資料欄位: {list(first_station.keys())}")
                                    
                                    # 顯示車站基本資訊
                                    station_name = first_station.get('StationName', {})
                                    if isinstance(station_name, dict):
                                        station_name_zh = station_name.get('Zh_tw', '未知')
                                    else:
                                        station_name_zh = str(station_name)
                                    
                                    print(f"🏷️ 車站名稱: {station_name_zh}")
                                    print(f"🚇 路線ID: {first_station.get('LineID', '未知')}")
                                    
                                    # 分析LiveBoards資料
                                    live_boards = first_station.get('LiveBoards', [])
                                    print(f"🚆 LiveBoards數量: {len(live_boards)}")
                                    
                                    if live_boards and len(live_boards) > 0:
                                        print("\n📊 LiveBoard資料結構:")
                                        first_board = live_boards[0]
                                        print(f"   欄位: {list(first_board.keys())}")
                                        
                                        print("\n🔍 詳細LiveBoard內容:")
                                        for key, value in first_board.items():
                                            print(f"   {key}: {value} ({type(value).__name__})")
                                        
                                        # 檢查所有LiveBoard是否都沒有列車資訊
                                        has_train_info = False
                                        for i, board in enumerate(live_boards):
                                            enter_time = board.get('EnterTime', '')
                                            arrival_time = board.get('ArrivalTime', '')
                                            destination = board.get('DestinationStationName', {})
                                            
                                            if enter_time or arrival_time or destination:
                                                has_train_info = True
                                                print(f"\n🚆 LiveBoard {i+1}:")
                                                print(f"   EnterTime: {enter_time}")
                                                print(f"   ArrivalTime: {arrival_time}")
                                                print(f"   Destination: {destination}")
                                        
                                        if not has_train_info:
                                            print("\n⚠️ 所有LiveBoard都沒有具體的列車資訊")
                                    else:
                                        print("❌ 該車站沒有LiveBoard資料")
                                    
                                    # 檢查多個車站的情況
                                    print(f"\n📈 檢查所有 {len(metro_data)} 個車站的LiveBoard狀況:")
                                    stations_with_trains = 0
                                    total_trains = 0
                                    
                                    for i, station in enumerate(metro_data):
                                        station_name = station.get('StationName', {})
                                        if isinstance(station_name, dict):
                                            name = station_name.get('Zh_tw', f'車站{i+1}')
                                        else:
                                            name = str(station_name)
                                        
                                        live_boards = station.get('LiveBoards', [])
                                        train_count = len(live_boards)
                                        total_trains += train_count
                                        
                                        if train_count > 0:
                                            stations_with_trains += 1
                                            print(f"   🚉 {name}: {train_count} 班列車")
                                        else:
                                            print(f"   🚉 {name}: 無列車資訊")
                                    
                                    print(f"\n📊 統計結果:")
                                    print(f"   有列車資訊的車站: {stations_with_trains}/{len(metro_data)}")
                                    print(f"   總列車班次: {total_trains}")
                                    
                                    # 儲存完整資料供分析
                                    with open('debug_liveboard_data.json', 'w', encoding='utf-8') as f:
                                        json.dump(metro_data, f, ensure_ascii=False, indent=2)
                                    print(f"\n💾 完整資料已儲存到 debug_liveboard_data.json")
                                    
                                else:
                                    print("❌ 沒有取得任何LiveBoard資料")
                                
                                return True
                            else:
                                print(f"❌ LiveBoard API請求失敗: {metro_response.status}")
                                text = await metro_response.text()
                                print(f"回應內容: {text[:500]}...")
                    else:
                        print("❌ Token回應中沒有access_token")
                else:
                    print(f"❌ Token請求失敗: {response.status}")
                    
        except Exception as e:
            print(f"❌ 連接錯誤: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🧪 開始調試TDX捷運即時電子看板API...\n")
    
    success = asyncio.run(debug_metro_liveboard_api())
    
    if success:
        print("\n🎉 調試完成！請查看生成的 debug_liveboard_data.json 檔案")
        print("\n💡 建議:")
        print("1. 檢查 LiveBoard 資料是否在特定時間才有內容")
        print("2. 確認 API 回傳的欄位名稱是否正確")
        print("3. 查看是否需要其他參數來取得即時資料")
    else:
        print("\n❌ 調試失敗，請檢查API設定")
    
    print("\n🏁 調試結束")
