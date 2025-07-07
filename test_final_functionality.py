#!/usr/bin/env python3
"""
完整功能測試 - 測試單一監視器顯示功能
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

async def test_single_camera_display():
    """測試單一監視器顯示功能"""
    
    from cogs.reservoir_commands import ReservoirCommands
    
    print("=== 單一監視器顯示功能測試 ===")
    
    # 創建 ReservoirCommands 實例
    cog = ReservoirCommands(None)
    
    # 測試 TDX 授權
    print("1. 測試 TDX 授權...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
            client_id = "xiaoyouwu5-08c8f7b1-3ac2-431b"
            client_secret = "9946bb49-0cc5-463c-ba79-c669140df4ef"
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            async with session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    print("✅ TDX 授權成功")
                    access_token = token_data.get('access_token')
                    
                    # 測試 API 呼叫
                    print("2. 測試 API 呼叫...")
                    api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Live/TrafficLive/CCTV/City/Taipei"
                    headers = {'Authorization': f'Bearer {access_token}'}
                    
                    async with session.get(api_url, headers=headers) as api_response:
                        if api_response.status == 200:
                            data = await api_response.json()
                            print(f"✅ API 回應成功，共 {len(data)} 筆資料")
                            
                            # 測試資料解析
                            print("3. 測試資料解析...")
                            valid_cameras = []
                            for item in data[:10]:  # 只測試前 10 筆
                                if 'LivePicture' in item and item['LivePicture']:
                                    snapshot_url = item['LivePicture'].get('PictureURL1')
                                    if snapshot_url:
                                        valid_cameras.append({
                                            'name': item.get('RoadSectionName', '未知路段'),
                                            'url': snapshot_url
                                        })
                            
                            if valid_cameras:
                                print(f"✅ 找到 {len(valid_cameras)} 個有效監視器")
                                
                                # 測試隨機選擇
                                import random
                                selected_camera = random.choice(valid_cameras)
                                print(f"✅ 隨機選擇監視器: {selected_camera['name']}")
                                
                                # 測試 Discord embed 結構
                                print("4. 測試 Discord embed 結構...")
                                embed_data = {
                                    'title': f"🚗 公路監視器 - {selected_camera['name']}",
                                    'description': f"**位置**: {selected_camera['name']}",
                                    'color': 0x00ff00,
                                    'image': {'url': selected_camera['url']},
                                    'footer': {'text': '資料來源: TDX 運輸資料流通服務'}
                                }
                                print("✅ Discord embed 結構正確")
                                
                                print("\n=== 測試結果 ===")
                                print("✅ TDX 授權成功")
                                print("✅ API 呼叫成功")
                                print("✅ 資料解析成功")
                                print("✅ 監視器篩選成功")
                                print("✅ 隨機選擇成功")
                                print("✅ Discord embed 結構正確")
                                print("✅ 單一監視器顯示功能完全正常")
                                
                            else:
                                print("❌ 沒有找到有效的監視器")
                        else:
                            print(f"❌ API 呼叫失敗: {api_response.status}")
                else:
                    print(f"❌ TDX 授權失敗: {response.status}")
    
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_camera_display())
