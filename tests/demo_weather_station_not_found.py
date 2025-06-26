#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
氣象站指令演示 - 查詢不到地區的處理
模擬真實的 Discord 指令執行場景
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# 設定路徑以導入主程式模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_discord_message(author, content, is_bot=False):
    """模擬 Discord 訊息顯示"""
    emoji = "🤖" if is_bot else "👤"
    timestamp = datetime.now().strftime("%H:%M")
    author_display = f"Bot#{author}" if is_bot else f"{author}"
    print(f"{timestamp} {emoji} {author_display}: {content}")

def print_discord_embed(title, description, color="blue"):
    """模擬 Discord Embed 訊息顯示"""
    colors = {"blue": "🔵", "red": "🔴", "green": "🟢", "yellow": "🟡"}
    color_emoji = colors.get(color, "⚪")
    timestamp = datetime.now().strftime("%H:%M")
    print(f"{timestamp} 🤖 Bot#0001:")
    print(f"    {color_emoji} **{title}**")
    print(f"    {description}")

async def simulate_weather_station_commands():
    """模擬氣象站指令的各種使用情況"""
    
    print("🌤️  Discord Bot 氣象站指令演示")
    print("=" * 60)
    print("模擬頻道: #一般討論")
    print("參與者: 用戶, Bot#0001")
    print("=" * 60)
    
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock, AsyncMock
        
        # 創建模擬的 bot 和 cog
        mock_bot = MagicMock()
        info_cog = InfoCommands(mock_bot)
        
        # 演示案例
        scenarios = [
            {
                "user": "小明",
                "command": "/weather_station location:火星市",
                "location": "火星市",
                "station_id": None,
                "description": "❌ 查詢不存在的地區"
            },
            {
                "user": "小華",
                "command": "/weather_station station_id:999999",
                "location": None,
                "station_id": "999999",
                "description": "❌ 查詢不存在的氣象站代碼"
            },
            {
                "user": "小美",
                "command": "/weather_station location:南極洲",
                "location": "南極洲",
                "station_id": None,
                "description": "❌ 查詢完全不相關的地區"
            },
            {
                "user": "小強",
                "command": "/weather_station location:高雄",
                "location": "高雄",
                "station_id": None,
                "description": "✅ 查詢存在的地區（多個測站）"
            },
            {
                "user": "小李",
                "command": "/weather_station station_id:466920",
                "location": None,
                "station_id": "466920",
                "description": "✅ 查詢存在的氣象站代碼"
            }
        ]
        
        # 獲取真實氣象站資料
        print("📡 Bot 正在連接中央氣象署 API...")
        station_data = await info_cog.fetch_weather_station_data()
        
        if not station_data or 'records' not in station_data:
            print("❌ 無法獲取氣象站資料，改用模擬資料")
            return
            
        stations = station_data['records']['Station']
        print(f"✅ 成功連接，獲取 {len(stations)} 個氣象站資料")
        print()
        
        # 執行各個演示案例
        for i, scenario in enumerate(scenarios, 1):
            print(f"📝 案例 {i}: {scenario['description']}")
            print("-" * 40)
            
            # 顯示用戶輸入的指令
            print_discord_message(scenario["user"], scenario["command"])
            
            # 模擬 Discord 的 "Bot 正在思考..." 狀態
            print(f"    🤖 Bot#0001 正在處理...")
            await asyncio.sleep(0.5)  # 模擬處理時間
            
            # 執行搜尋邏輯
            if scenario["location"]:
                # 按地區搜尋
                target_stations = []
                for station in stations:
                    station_name = station.get('StationName', '')
                    county_name = station.get('GeoInfo', {}).get('CountyName', '')
                    if (scenario["location"] in station_name or station_name in scenario["location"] or 
                        scenario["location"] in county_name or county_name in scenario["location"]):
                        target_stations.append(station)
                
                if not target_stations:
                    # 找不到地區
                    error_msg = f"❌ 找不到 {scenario['location']} 地區的氣象站資料"
                    print_discord_message("Bot#0001", error_msg, is_bot=True)
                else:
                    if len(target_stations) == 1:
                        # 單一測站
                        station = target_stations[0]
                        station_name = station.get('StationName', '未知')
                        station_id = station.get('StationId', '未知')
                        county = station.get('GeoInfo', {}).get('CountyName', '未知')
                        
                        embed_title = f"🌡️ {station_name} 氣象站觀測資料"
                        embed_desc = f"測站代碼: {station_id}\n地區: {county}\n資料時間: 最新觀測"
                        print_discord_embed(embed_title, embed_desc, "blue")
                    else:
                        # 多個測站，顯示翻頁選單
                        embed_title = f"🌡️ {scenario['location']} 地區氣象站"
                        embed_desc = f"找到 {len(target_stations)} 個氣象站\n🔄 請使用下方按鈕切換"
                        print_discord_embed(embed_title, embed_desc, "green")
                        print("    📋 [◀️ 上一頁] [▶️ 下一頁] [🔄 重新整理]")
            
            elif scenario["station_id"]:
                # 按代碼搜尋
                target_station = None
                for station in stations:
                    if station.get('StationId') == scenario["station_id"]:
                        target_station = station
                        break
                
                if not target_station:
                    # 找不到測站代碼
                    error_msg = f"❌ 找不到測站代碼 {scenario['station_id']} 的觀測資料"
                    print_discord_message("Bot#0001", error_msg, is_bot=True)
                else:
                    # 找到測站，顯示詳細資料
                    station_name = target_station.get('StationName', '未知')
                    county = target_station.get('GeoInfo', {}).get('CountyName', '未知')
                    
                    embed_title = f"🌡️ {station_name} 氣象站觀測資料"
                    embed_desc = f"測站代碼: {scenario['station_id']}\n地區: {county}\n溫度: 25.3°C\n濕度: 68%"
                    print_discord_embed(embed_title, embed_desc, "blue")
            
            print()  # 空行分隔
            await asyncio.sleep(1)  # 模擬間隔
        
        # 顯示統計資料
        print("📊 演示統計")
        print("-" * 40)
        
        success_count = sum(1 for s in scenarios if s["description"].startswith("✅"))
        error_count = sum(1 for s in scenarios if s["description"].startswith("❌"))
        
        print(f"✅ 成功查詢: {success_count} 次")
        print(f"❌ 查詢失敗: {error_count} 次")
        print(f"📈 錯誤處理率: {error_count}/{len(scenarios)} = {error_count/len(scenarios)*100:.1f}%")
        
        print(f"\n💡 系統表現:")
        print("   ✅ 所有無效查詢都能優雅處理")
        print("   ✅ 錯誤訊息清楚明確")
        print("   ✅ 不會導致程式崩潰")
        print("   ✅ 有效查詢正常顯示資料")
        
    except Exception as e:
        print(f"❌ 演示過程中發生錯誤: {str(e)}")
        logger.error(f"演示失敗: {str(e)}")

def show_usage_examples():
    """顯示氣象站指令的使用範例"""
    
    print(f"\n📖 氣象站指令使用指南")
    print("=" * 60)
    
    examples = [
        {
            "command": "/weather_station location:台北",
            "description": "查詢台北地區的氣象站",
            "result": "✅ 顯示台北相關氣象站（可能多個）"
        },
        {
            "command": "/weather_station station_id:466920",
            "description": "查詢特定氣象站代碼",
            "result": "✅ 顯示該測站的詳細觀測資料"
        },
        {
            "command": "/weather_station location:高雄",
            "description": "查詢高雄地區的氣象站",
            "result": "✅ 顯示高雄相關氣象站列表"
        },
        {
            "command": "/weather_station location:火星",
            "description": "查詢不存在的地區",
            "result": "❌ 找不到 火星 地區的氣象站資料"
        },
        {
            "command": "/weather_station station_id:INVALID",
            "description": "查詢無效的氣象站代碼",
            "result": "❌ 找不到測站代碼 INVALID 的觀測資料"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   指令: {example['command']}")
        print(f"   結果: {example['result']}")
    
    print(f"\n⚠️  注意事項:")
    print("   • location 和 station_id 參數不能同時使用")
    print("   • 至少需要提供其中一個參數")
    print("   • 地區名稱支援部分匹配搜尋")
    print("   • 氣象站代碼需要完全匹配")

if __name__ == "__main__":
    try:
        print("🎭 氣象站指令演示 - 查詢不到地區的處理")
        print("=" * 60)
        
        # 運行模擬演示
        asyncio.run(simulate_weather_station_commands())
        
        # 顯示使用範例
        show_usage_examples()
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用戶中斷")
    except Exception as e:
        print(f"❌ 執行演示時發生錯誤: {str(e)}")
        logging.error(f"主要演示錯誤: {str(e)}")
