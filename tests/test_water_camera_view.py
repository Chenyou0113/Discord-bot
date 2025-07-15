#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新的水利監視器切換功能
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 匯入水庫指令類別
from cogs.reservoir_commands import ReservoirCommands, WaterCameraView

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockBot:
    """模擬 Discord bot"""
    pass

class MockInteraction:
    """模擬 Discord interaction"""
    def __init__(self):
        self.response_sent = False
        self.followup_sent = False
        self.response_data = None
        self.followup_data = None
        self.message = MockMessage()
    
    async def response_defer(self):
        """模擬 defer 回應"""
        print("✅ 已發送 defer 回應")
    
    async def followup_send(self, **kwargs):
        """模擬發送後續回應"""
        self.followup_sent = True
        self.followup_data = kwargs
        if 'embed' in kwargs:
            embed = kwargs['embed']
            print(f"📤 發送後續回應:")
            print(f"   標題: {embed.title}")
            print(f"   描述: {embed.description}")
            if hasattr(embed, 'image') and embed.image:
                print(f"   🖼️ 影像: {embed.image.url}")
            if hasattr(embed, 'footer') and embed.footer:
                print(f"   頁尾: {embed.footer.text}")
        
        if 'view' in kwargs:
            view = kwargs['view']
            print(f"   🎛️ 互動元件: {len(view.children)} 個按鈕")
            for i, button in enumerate(view.children):
                if hasattr(button, 'label'):
                    print(f"     按鈕 {i+1}: {button.label} ({'啟用' if not button.disabled else '禁用'})")

    class MockResponse:
        def __init__(self, interaction):
            self.interaction = interaction
        
        async def defer(self):
            await self.interaction.response_defer()
    
    class MockFollowup:
        def __init__(self, interaction):
            self.interaction = interaction
        
        async def send(self, **kwargs):
            await self.interaction.followup_send(**kwargs)
    
    def __init__(self):
        self.response_sent = False
        self.followup_sent = False
        self.response_data = None
        self.followup_data = None
        self.message = MockMessage()
        self.response = self.MockResponse(self)
        self.followup = self.MockFollowup(self)

class MockMessage:
    """模擬 Discord 訊息"""
    def __init__(self):
        self.id = 123456789

async def test_water_camera_view():
    """測試水利監視器 View 功能"""
    print("=" * 60)
    print("測試水利監視器切換功能")
    print("=" * 60)
    
    try:
        # 建立模擬物件
        bot = MockBot()
        reservoir_commands = ReservoirCommands(bot)
        
        # 測試 API 連線
        print("🔌 測試 API 連線...")
        image_data = await reservoir_commands.get_water_disaster_images()
        
        if not image_data:
            print("❌ API 連線失敗")
            return
        
        print(f"✅ API 連線成功，取得 {len(image_data)} 筆監控點資料")
        
        # 找出有影像的監控點
        valid_cameras = []
        for data in image_data:
            info = reservoir_commands.format_water_image_info(data)
            if info and info['image_url'] and info['image_url'] != 'N/A':
                valid_cameras.append(data)
        
        print(f"📸 有效監控點: {len(valid_cameras)} 個")
        
        if not valid_cameras:
            print("❌ 沒有找到有效的監控點")
            return
        
        # 取前5個監控點進行測試
        test_cameras = valid_cameras[:5]
        
        print(f"\n🧪 測試監控點:")
        for i, data in enumerate(test_cameras, 1):
            info = reservoir_commands.format_water_image_info(data)
            if info:
                print(f"   {i}. {info['station_name']} - {info['location']} - {info['river']}")
        
        # 建立 View 實例
        print(f"\n🎛️ 建立 WaterCameraView...")
        view = WaterCameraView(reservoir_commands, test_cameras, "測試地區")
        
        print(f"✅ View 建立成功")
        print(f"   監控點數量: {view.total_cameras}")
        print(f"   當前索引: {view.current_index}")
        print(f"   按鈕數量: {len(view.children)}")
        
        # 測試建立 embed
        print(f"\n📋 測試 Embed 建立...")
        for i in range(min(3, len(test_cameras))):
            embed = view.create_embed(i)
            if embed:
                print(f"✅ 第 {i+1} 個監控點 Embed 建立成功")
                print(f"   標題: {embed.title}")
                print(f"   描述: {embed.description[:100]}...")
                if hasattr(embed, 'image') and embed.image:
                    print(f"   影像: {embed.image.url[:50]}...")
                if hasattr(embed, 'footer') and embed.footer:
                    print(f"   頁尾: {embed.footer.text}")
            else:
                print(f"❌ 第 {i+1} 個監控點 Embed 建立失敗")
        
        # 測試指令執行
        print(f"\n🧪 測試指令執行...")
        
        test_locations = ["台南", "台北", "基隆"]
        
        for location in test_locations:
            print(f"\n📍 測試地區: {location}")
            print("-" * 30)
            
            interaction = MockInteraction()
            
            try:
                await reservoir_commands.water_disaster_cameras.callback(
                    reservoir_commands, interaction, location
                )
                
                if interaction.followup_sent:
                    print("✅ 指令執行成功")
                    if 'view' in interaction.followup_data:
                        print("✅ View 已附加到回應")
                else:
                    print("❌ 沒有發送回應")
                    
            except Exception as e:
                print(f"❌ 指令執行失敗: {str(e)}")
            
            # 稍微延遲
            await asyncio.sleep(1)
        
        print(f"\n✅ 所有測試完成")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_single_location():
    """測試單一地區的監控點"""
    print("\n" + "=" * 60)
    print("測試單一地區監控點功能")
    print("=" * 60)
    
    try:
        bot = MockBot()
        reservoir_commands = ReservoirCommands(bot)
        
        # 測試台南地區
        print("🧪 測試台南地區監控點...")
        
        image_data = await reservoir_commands.get_water_disaster_images()
        
        if not image_data:
            print("❌ 無法取得資料")
            return
        
        # 搜尋台南地區監控點
        found_cameras = []
        for data in image_data:
            loc = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
            if '台南' in loc:
                info = reservoir_commands.format_water_image_info(data)
                if info and info['image_url'] and info['image_url'] != 'N/A':
                    found_cameras.append(data)
        
        print(f"✅ 找到 {len(found_cameras)} 個台南地區有效監控點")
        
        if found_cameras:
            # 顯示前幾個監控點資訊
            for i, data in enumerate(found_cameras[:3], 1):
                info = reservoir_commands.format_water_image_info(data)
                if info:
                    print(f"   {i}. {info['station_name']}")
                    print(f"      位置: {info['location']}")
                    print(f"      河川: {info['river']}")
                    print(f"      狀態: {info['status']}")
                    print(f"      影像: {info['image_url'][:50]}...")
                    print()
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")

def main():
    """主函數"""
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def run_tests():
        await test_water_camera_view()
        await test_single_location()
    
    asyncio.run(run_tests())
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
