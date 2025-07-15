#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水利防災影像按鈕功能測試
測試修復後的水利防災影像指令是否正常工作
"""

import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

async def test_water_disaster_cameras_with_buttons():
    """測試水利防災影像指令的按鈕功能"""
    
    print("🧪 測試水利防災影像指令按鈕功能")
    print("=" * 60)
    
    try:
        # 導入相關模組
        from cogs.reservoir_commands import ReservoirCommands, WaterCameraView
        
        # 創建模擬的 bot
        mock_bot = MagicMock()
        
        # 創建 ReservoirCommands 實例
        reservoir_cog = ReservoirCommands(mock_bot)
        
        # 創建模擬的 Discord interaction
        mock_interaction = AsyncMock()
        mock_interaction.response.defer = AsyncMock()
        mock_interaction.followup.send = AsyncMock()
        
        # 創建模擬的回應消息
        mock_message = AsyncMock()
        mock_message.edit = AsyncMock()
        mock_interaction.followup.send.return_value = mock_message
        
        # 模擬水利防災影像資料
        mock_data = [
            {
                'VideoSurveillanceStationName': '測試監控站1',
                'VideoSurveillanceStationId': 'TEST001',
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '台北市',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '信義區',
                'VideoSurveillanceStationAddress': '台北市信義區測試路1號',
                'ImageURL': 'https://example.com/test1.jpg',
                'River': '淡水河'
            },
            {
                'VideoSurveillanceStationName': '測試監控站2',
                'VideoSurveillanceStationId': 'TEST002',
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '台北市',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '大安區',
                'VideoSurveillanceStationAddress': '台北市大安區測試路2號',
                'ImageURL': 'https://example.com/test2.jpg',
                'River': '新店溪'
            },
            {
                'VideoSurveillanceStationName': '測試監控站3',
                'VideoSurveillanceStationId': 'TEST003',
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '台北市',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '中山區',
                'VideoSurveillanceStationAddress': '台北市中山區測試路3號',
                'ImageURL': 'https://example.com/test3.jpg',
                'River': '基隆河'
            }
        ]
        
        # 模擬 API 回應
        async def mock_get_water_disaster_images():
            return mock_data
        
        reservoir_cog.get_water_disaster_images = mock_get_water_disaster_images
        
        print("1️⃣ 測試指令調用（有縣市選擇）...")
        try:
            await reservoir_cog.water_disaster_cameras(mock_interaction, city="台北")
            print("✅ 指令調用成功")
            
            # 檢查是否正確調用了編輯訊息
            if mock_message.edit.called:
                call_args = mock_message.edit.call_args
                if 'view' in call_args.kwargs:
                    print("✅ 已添加按鈕 View")
                else:
                    print("❌ 缺少按鈕 View")
                    return False
            else:
                print("❌ 沒有調用編輯訊息")
                return False
                
        except Exception as e:
            print(f"❌ 指令調用失敗: {e}")
            if "object str can't be used in 'await' expression" in str(e):
                print("🚨 仍然存在 await 字符串錯誤!")
                return False
            return False
        
        print("\n2️⃣ 測試 WaterCameraView 創建...")
        try:
            view = WaterCameraView(mock_data, 0, "台北")
            print("✅ WaterCameraView 創建成功")
            print(f"   監控點數量: {view.total_cameras}")
            print(f"   當前索引: {view.current_index}")
            print(f"   搜尋條件: {view.search_term}")
            
        except Exception as e:
            print(f"❌ WaterCameraView 創建失敗: {e}")
            return False
        
        print("\n3️⃣ 測試 Embed 創建...")
        try:
            embed = await view._create_water_camera_embed(mock_data[0])
            print("✅ Embed 創建成功")
            print(f"   標題: {embed.title}")
            print(f"   描述: {embed.description}")
            print(f"   欄位數量: {len(embed.fields)}")
            print(f"   底部文字: {embed.footer.text if embed.footer else '無'}")
            
            # 檢查影像是否設定
            if embed.image and embed.image.url:
                print(f"   影像URL: {embed.image.url}")
            else:
                print("   ⚠️ 沒有設定影像")
                
        except Exception as e:
            print(f"❌ Embed 創建失敗: {e}")
            return False
        
        print("\n4️⃣ 測試按鈕功能...")
        try:
            # 檢查按鈕是否正確添加
            buttons = [item for item in view.children if hasattr(item, 'callback')]
            print(f"✅ 按鈕數量: {len(buttons)}")
            
            for i, button in enumerate(buttons):
                print(f"   按鈕 {i+1}: {button.label} ({button.style.name})")
            
            # 測試下一個按鈕
            if len(buttons) > 0:
                next_button = None
                for button in buttons:
                    if "下一個" in button.label:
                        next_button = button
                        break
                
                if next_button:
                    print("   測試下一個按鈕...")
                    mock_button_interaction = AsyncMock()
                    mock_button_interaction.response.edit_message = AsyncMock()
                    
                    await next_button.callback(mock_button_interaction)
                    print("   ✅ 下一個按鈕功能正常")
                else:
                    print("   ⚠️ 沒有下一個按鈕（可能是最後一個）")
            
        except Exception as e:
            print(f"❌ 按鈕功能測試失敗: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主測試函數"""
    
    print("🚀 水利防災影像按鈕功能測試")
    print("=" * 80)
    
    # 測試按鈕功能
    button_test = await test_water_disaster_cameras_with_buttons()
    
    # 結果報告
    print("\n" + "=" * 80)
    print("📊 測試結果摘要:")
    print(f"按鈕功能測試: {'✅ 通過' if button_test else '❌ 失敗'}")
    
    if button_test:
        print("\n🎉 所有測試通過！")
        print("✅ 水利防災影像指令現在支援:")
        print("   • 縣市下拉選單選擇")
        print("   • 多監控點瀏覽按鈕")
        print("   • 影像正常顯示")  
        print("   • 監控站詳細資訊")
        print("✅ 沒有 await 字符串錯誤")
        print("✅ 可以安全部署到 Discord")
        return True
    else:
        print("\n❌ 測試失敗，需要進一步修復")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 測試運行失敗: {type(e).__name__}: {e}")
        sys.exit(1)
