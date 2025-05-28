#!/usr/bin/env python3
"""
天氣預報功能測試腳本
測試天氣預報功能是否正常運作
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cogs.info_commands_fixed_v4 import InfoCommands
from discord.ext import commands
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

class MockBot:
    """模擬Discord Bot"""
    def __init__(self):
        self.guilds = []
        self.is_closed_flag = False
        
    def is_closed(self):
        return self.is_closed_flag
        
    async def wait_until_ready(self):
        pass

class MockLoop:
    """模擬事件循環"""
    def create_task(self, coro):
        return asyncio.create_task(coro)

async def test_weather_fetch():
    """測試天氣預報資料獲取功能"""
    print("=== 測試天氣預報資料獲取功能 ===")
    
    # 創建模擬bot
    bot = MockBot()
    bot.loop = MockLoop()
    
    # 初始化InfoCommands
    info_commands = InfoCommands(bot)
    
    try:
        # 初始化HTTP會話
        await info_commands.init_aiohttp_session()
        
        print("1. 測試天氣預報資料獲取...")
        weather_data = await info_commands.fetch_weather_data()
        
        if weather_data is None:
            print("❌ 失敗：無法獲取天氣預報資料")
        else:
            print("✅ 成功：獲取到天氣預報資料")
            
            # 檢查資料結構
            if 'records' in weather_data:
                print(f"   - 包含 records 欄位")
                if 'location' in weather_data['records']:
                    locations = weather_data['records']['location']
                    print(f"   - 包含 {len(locations)} 個地區的資料")
                    
                    # 列出前幾個地區
                    for i, loc in enumerate(locations[:5]):
                        print(f"     {i+1}. {loc.get('locationName', '未知地區')}")
                else:
                    print("   - 缺少 location 欄位")
            else:
                print("   - 缺少 records 欄位")
        
        print("\n2. 測試台北天氣格式化...")
        taipei_embed = await info_commands.format_weather_data("臺北市")
        
        if taipei_embed is None:
            print("❌ 失敗：無法格式化台北天氣資料")
        else:
            print("✅ 成功：台北天氣資料格式化成功")
            print(f"   - 標題: {taipei_embed.title}")
            print(f"   - 欄位數量: {len(taipei_embed.fields)}")
            
        print("\n3. 測試高雄天氣格式化...")
        kaohsiung_embed = await info_commands.format_weather_data("高雄市")
        
        if kaohsiung_embed is None:
            print("❌ 失敗：無法格式化高雄天氣資料")
        else:
            print("✅ 成功：高雄天氣資料格式化成功")
            print(f"   - 標題: {kaohsiung_embed.title}")
            print(f"   - 欄位數量: {len(kaohsiung_embed.fields)}")

    except Exception as e:
        print(f"❌ 錯誤：測試過程中發生異常: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理資源
        if info_commands.session and not info_commands.session.closed:
            await info_commands.session.close()

async def main():
    """主測試函數"""
    print("Discord機器人天氣預報功能測試")
    print("=" * 50)
    
    try:
        await test_weather_fetch()
        
        print("\n" + "=" * 50)
        print("✅ 天氣預報測試完成！")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生嚴重錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
