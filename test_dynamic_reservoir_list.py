#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新的動態水庫列表功能
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 匯入水庫指令類別
from cogs.reservoir_commands import ReservoirCommands

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
    
    async def response_defer(self):
        """模擬 defer 回應"""
        print("✅ 已發送 defer 回應")
    
    async def response_send_message(self, **kwargs):
        """模擬發送回應"""
        self.response_sent = True
        self.response_data = kwargs
        if 'embed' in kwargs:
            embed = kwargs['embed']
            print(f"📤 發送回應:")
            print(f"   標題: {embed.title}")
            print(f"   描述: {embed.description}")
            print(f"   顏色: {embed.color}")
            for field in embed.fields:
                print(f"   欄位: {field.name}")
                print(f"   內容: {field.value[:200]}..." if len(field.value) > 200 else f"   內容: {field.value}")
    
    async def followup_send(self, **kwargs):
        """模擬發送後續回應"""
        self.followup_sent = True
        self.followup_data = kwargs
        if 'embed' in kwargs:
            embed = kwargs['embed']
            print(f"📤 發送後續回應:")
            print(f"   標題: {embed.title}")
            print(f"   描述: {embed.description}")
            print(f"   顏色: {embed.color}")
            if hasattr(embed, 'footer') and embed.footer:
                print(f"   頁尾: {embed.footer.text}")
            for field in embed.fields:
                print(f"   欄位: {field.name}")
                content = field.value[:300] + "..." if len(field.value) > 300 else field.value
                print(f"   內容: {content}")
                print("   " + "-" * 50)

    class MockResponse:
        def __init__(self, interaction):
            self.interaction = interaction
        
        async def defer(self):
            await self.interaction.response_defer()
        
        async def send_message(self, **kwargs):
            await self.interaction.response_send_message(**kwargs)
    
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
        self.response = self.MockResponse(self)
        self.followup = self.MockFollowup(self)

async def test_reservoir_list_command():
    """測試新的水庫列表指令"""
    print("=" * 60)
    print("測試動態水庫列表功能")
    print("=" * 60)
    
    try:
        # 建立模擬物件
        bot = MockBot()
        reservoir_commands = ReservoirCommands(bot)
        
        # 測試各種參數組合
        test_cases = [
            {"show_type": "major", "region": "all", "name": "主要水庫（全部地區）"},
            {"show_type": "top20", "region": "all", "name": "前20大水庫"},
            {"show_type": "major", "region": "north", "name": "北部主要水庫"},
            {"show_type": "all", "region": "all", "name": "完整列表（前50）"}
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 測試案例 {i}: {test_case['name']}")
            print("-" * 40)
            
            interaction = MockInteraction()
            
            try:
                # 直接調用方法而不是透過裝飾器
                await reservoir_commands.reservoir_list.callback(
                    reservoir_commands,
                    interaction, 
                    show_type=test_case["show_type"],
                    region=test_case["region"]
                )
                
                if interaction.followup_sent:
                    print("✅ 指令執行成功")
                else:
                    print("❌ 沒有發送後續回應")
                    
            except Exception as e:
                print(f"❌ 測試失敗: {str(e)}")
                import traceback
                traceback.print_exc()
            
            print("\n" + "=" * 40)
            
            # 避免請求過於頻繁
            await asyncio.sleep(2)
    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_api_connection():
    """測試 API 連線"""
    print("\n🔌 測試 API 連線...")
    
    try:
        bot = MockBot()
        reservoir_commands = ReservoirCommands(bot)
        
        data = await reservoir_commands.get_reservoir_data()
        
        if data:
            print(f"✅ API 連線成功，取得 {len(data)} 筆資料")
            
            # 檢查前幾筆資料
            valid_count = 0
            for item in data[:10]:
                reservoir_id = item.get('ReservoirIdentifier', '')
                capacity = item.get('EffectiveWaterStorageCapacity', '')
                if reservoir_id and capacity:
                    try:
                        capacity_value = float(capacity)
                        if capacity_value > 0:
                            valid_count += 1
                            print(f"   水庫 {reservoir_id}: 容量 {capacity_value:.1f}萬m³")
                    except:
                        pass
            
            print(f"✅ 前10筆中有 {valid_count} 筆有效資料")
        else:
            print("❌ API 連線失敗")
    
    except Exception as e:
        print(f"❌ API 測試失敗: {str(e)}")

def main():
    """主函數"""
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def run_tests():
        await test_api_connection()
        await test_reservoir_list_command()
    
    asyncio.run(run_tests())
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
