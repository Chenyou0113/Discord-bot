#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水庫容量動態列表功能驗證報告
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# 設定日誌
logging.basicConfig(level=logging.WARNING)

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 匯入水庫指令類別
from cogs.reservoir_commands import ReservoirCommands

class MockBot:
    """模擬 Discord bot"""
    pass

class MockInteraction:
    """模擬 Discord interaction - 簡化版"""
    def __init__(self):
        self.response_sent = False
        self.followup_sent = False
        self.results = []
    
    async def response_defer(self):
        """模擬 defer 回應"""
        pass
    
    async def followup_send(self, **kwargs):
        """模擬發送後續回應"""
        self.followup_sent = True
        if 'embed' in kwargs:
            embed = kwargs['embed']
            self.results.append({
                'title': embed.title,
                'description': embed.description,
                'fields': len(embed.fields),
                'footer': embed.footer.text if hasattr(embed, 'footer') and embed.footer else None
            })

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
        self.results = []
        self.response = self.MockResponse(self)
        self.followup = self.MockFollowup(self)

async def test_reservoir_list_features():
    """測試水庫列表的各項功能"""
    
    print("=" * 80)
    print("🏞️ 水庫容量動態列表功能驗證")
    print("=" * 80)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 建立模擬物件
        bot = MockBot()
        reservoir_commands = ReservoirCommands(bot)
        
        # 首先測試 API 連線
        print("🔌 API 連線測試")
        print("-" * 40)
        
        data = await reservoir_commands.get_reservoir_data()
        if data:
            print(f"✅ API 連線成功")
            print(f"📊 資料筆數: {len(data)} 個水庫")
           
            # 統計有效資料
            valid_data = []
            for item in data:
                reservoir_id = item.get('ReservoirIdentifier', '')
                capacity = item.get('EffectiveWaterStorageCapacity', '')  
                if reservoir_id and capacity:
                    try:
                        capacity_value = float(capacity)
                        if capacity_value > 0:
                            valid_data.append({
                                'id': reservoir_id,
                                'capacity': capacity_value,
                                'name': reservoir_commands.reservoir_names.get(reservoir_id, f"水庫{reservoir_id}")
                            })
                    except:
                        continue
            
            print(f"📈 有效資料: {len(valid_data)} 筆")
            print(f"🏛️ 主要水庫: {len([d for d in valid_data if d['id'] in reservoir_commands.reservoir_names])} 個")
            
            # 顯示前5大水庫
            valid_data.sort(key=lambda x: x['capacity'], reverse=True)
            print("\n🏆 前5大水庫:")
            for i, reservoir in enumerate(valid_data[:5], 1):
                print(f"   {i}. {reservoir['name']} ({reservoir['id']}) - {reservoir['capacity']:.1f}萬m³")
            
        else:
            print("❌ API 連線失敗")
            return
        
        print("\n" + "=" * 80)
        print("🧪 指令功能測試")
        print("=" * 80)
        
        # 測試各種指令參數組合
        test_cases = [
            {
                "name": "主要水庫（全部地區）",
                "params": {"show_type": "major", "region": "all"},
                "description": "顯示所有主要水庫的容量資訊"
            },
            {
                "name": "前20大水庫",
                "params": {"show_type": "top20", "region": "all"},
                "description": "顯示台灣容量最大的20個水庫"
            },
            {
                "name": "北部主要水庫",
                "params": {"show_type": "major", "region": "north"},
                "description": "顯示北部地區的主要水庫"
            },
            {
                "name": "完整列表（前50）",
                "params": {"show_type": "all", "region": "all"},
                "description": "顯示所有水庫的容量資訊（限制前50個）"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 測試案例 {i}: {test_case['name']}")
            print(f"📄 說明: {test_case['description']}")
            print("-" * 60)
            
            interaction = MockInteraction()
            
            try:
                # 執行指令
                await reservoir_commands.reservoir_list.callback(
                    reservoir_commands,
                    interaction,
                    **test_case["params"]
                )
                
                if interaction.followup_sent and interaction.results:
                    result = interaction.results[0]
                    print(f"✅ 指令執行成功")
                    print(f"📊 標題: {result['title']}")
                    print(f"📝 描述: {result['description']}")
                    print(f"📑 欄位數量: {result['fields']}")
                    if result['footer']:
                        print(f"📅 更新時間: {result['footer']}")
                else:
                    print("❌ 指令執行失敗 - 沒有回應資料")
                
            except Exception as e:
                print(f"❌ 指令執行失敗: {str(e)}")
            
            # 稍微延遲避免請求過於頻繁
            await asyncio.sleep(1)
        
        print("\n" + "=" * 80)
        print("✅ 功能驗證完成")
        print("=" * 80)
        
        print("\n🎯 功能特色總結:")
        print("• 動態顯示所有水庫的即時容量資訊")
        print("• 支援多種顯示模式（主要水庫、前20大、完整列表）")
        print("• 支援地區篩選（北部、中部、南部、東部）")
        print("• 顯示水庫容量、水位、入流量等詳細資訊")
        print("• 自動分頁顯示，避免訊息過長")
        print("• 包含使用說明和相關指令提示")
        
        print("\n💡 使用方式:")
        print("• `/reservoir_list` - 顯示主要水庫")
        print("• `/reservoir_list show_type:前20大水庫` - 顯示前20大")
        print("• `/reservoir_list show_type:主要水庫 region:北部` - 北部主要水庫")
        print("• `/reservoir_list show_type:完整列表` - 顯示所有水庫（前50）")
        
    except Exception as e:
        print(f"❌ 驗證過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    asyncio.run(test_reservoir_list_features())

if __name__ == "__main__":
    main()
