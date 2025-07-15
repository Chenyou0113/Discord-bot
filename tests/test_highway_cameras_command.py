#!/usr/bin/env python3
"""
測試完整的 highway_cameras 指令功能
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

# 模擬 Discord interaction
class MockInteraction:
    def __init__(self):
        self.response_deferred = False
        self.followup_messages = []
    
    class Response:
        def __init__(self, interaction):
            self.interaction = interaction
        
        async def defer(self):
            self.interaction.response_deferred = True
            print("✅ 回應已延遲")
    
    class Followup:
        def __init__(self, interaction):
            self.interaction = interaction
        
        async def send(self, content=None, embed=None):
            if embed:
                print(f"📤 Discord Embed 回應:")
                print(f"  標題: {embed.title}")
                print(f"  描述: {embed.description}")
                print(f"  顏色: {hex(embed.color)}")
                if embed.fields:
                    for field in embed.fields:
                        print(f"  欄位: {field.name} = {field.value}")
                if hasattr(embed, 'image') and embed.image:
                    print(f"  圖片: {embed.image.url}")
                if hasattr(embed, 'footer') and embed.footer:
                    print(f"  頁腳: {embed.footer.text}")
            else:
                print(f"📤 Discord 回應: {content}")
    
    def __init__(self):
        self.response = self.Response(self)
        self.followup = self.Followup(self)

async def test_highway_cameras_command():
    """測試 highway_cameras 指令"""
    
    print("=== 測試 highway_cameras 指令 ===")
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        import discord
        
        # 創建 ReservoirCommands 實例
        cog = ReservoirCommands(None)
        
        # 測試案例
        test_cases = [
            {'county': '基隆', 'road_type': None, 'desc': '基隆縣市篩選'},
            {'county': '新北', 'road_type': '台62線', 'desc': '新北 + 台62線'},
            {'county': None, 'road_type': '台1線', 'desc': '只選台1線'},
            {'county': '台北', 'road_type': None, 'desc': '台北縣市篩選'},
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. 測試案例: {test_case['desc']}")
            print(f"   縣市: {test_case['county']}, 道路類型: {test_case['road_type']}")
            
            # 創建模擬的 interaction
            interaction = MockInteraction()
            
            try:
                # 呼叫 highway_cameras 指令的實際方法
                await cog.highway_cameras.callback(
                    cog,
                    interaction, 
                    county=test_case['county'], 
                    road_type=test_case['road_type']
                )
                print("✅ 指令執行成功")
                
            except Exception as e:
                print(f"❌ 指令執行失敗: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n=== 測試完成 ===")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_highway_cameras_command())
