#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
降雨雷達功能驗證腳本
快速驗證降雨雷達相關功能是否正常
"""

import asyncio
import sys
import os

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def verify_rainfall_radar():
    """驗證降雨雷達功能"""
    
    print("🌧️ 降雨雷達功能驗證")
    print("=" * 50)
    
    try:
        # 導入模組
        from cogs.radar_commands import RadarCommands
        print("✅ 模組導入成功")
        
        # 創建實例
        class MockBot:
            pass
        
        bot = MockBot()
        radar_cog = RadarCommands(bot)
        print("✅ RadarCommands 實例建立成功")
        
        # 檢查API配置
        print("\n📋 API 配置檢查:")
        for station, config in radar_cog.rainfall_radar_apis.items():
            print(f"  {station}: {config['location']}")
        print("✅ API 配置正確")
        
        # 測試單一雷達站
        print("\n🔍 測試樹林雷達站...")
        data = await radar_cog.fetch_rainfall_radar_data("樹林")
        
        if data:
            print("✅ API 連線成功")
            
            # 測試資料解析
            radar_info = radar_cog.parse_rainfall_radar_data(data)
            if radar_info:
                print("✅ 資料解析成功")
                print(f"  觀測時間: {radar_info.get('datetime', 'N/A')}")
                print(f"  圖片連結: {'有' if radar_info.get('image_url') else '無'}")
                
                # 測試 Embed 建立
                embed = radar_cog.create_rainfall_radar_embed(radar_info, "樹林")
                print("✅ Embed 建立成功")
                print(f"  標題: {embed.title}")
                print(f"  欄位數: {len(embed.fields)}")
                
                return True
            else:
                print("❌ 資料解析失敗")
                return False
        else:
            print("❌ API 連線失敗")
            return False
            
    except Exception as e:
        print(f"❌ 驗證過程發生錯誤: {e}")
        return False

def main():
    """主函數"""
    try:
        success = asyncio.run(verify_rainfall_radar())
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 降雨雷達功能驗證成功！")
            print("\n✅ 功能狀態:")
            print("  - 模組導入正常")
            print("  - API 連線正常") 
            print("  - 資料解析正常")
            print("  - Embed 建立正常")
            print("\n💡 你現在可以使用 /rainfall_radar 指令！")
        else:
            print("❌ 降雨雷達功能驗證失敗")
            
        return success
        
    except Exception as e:
        print(f"❌ 執行驗證時發生錯誤: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
