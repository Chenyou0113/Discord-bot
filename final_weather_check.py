#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
氣象測站功能最終確認報告
檢查所有相關文件和配置是否正確
"""

import os
import sys

def check_file_exists(filepath, description):
    """檢查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} 缺失: {filepath}")
        return False

def check_file_content(filepath, search_text, description):
    """檢查文件是否包含特定內容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - 未找到相關內容")
                return False
    except Exception as e:
        print(f"❌ {description} - 檢查失敗: {e}")
        return False

def main():
    print("=" * 80)
    print("氣象測站功能最終確認報告")
    print("=" * 80)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    checks = []
    
    # 1. 檢查核心文件
    print("\n📁 核心文件檢查:")
    checks.append(check_file_exists(os.path.join(base_path, "bot.py"), "主機器人文件"))
    checks.append(check_file_exists(os.path.join(base_path, "cogs", "weather_commands.py"), "氣象指令 Cog"))
    checks.append(check_file_exists(os.path.join(base_path, ".env"), "環境變數文件"))
    checks.append(check_file_exists(os.path.join(base_path, "requirements.txt"), "依賴套件文件"))
    
    # 2. 檢查 bot.py 配置
    print("\n⚙️  機器人配置檢查:")
    bot_py_path = os.path.join(base_path, "bot.py")
    checks.append(check_file_content(bot_py_path, "cogs.weather_commands", "bot.py 包含氣象 Cog 載入"))
    checks.append(check_file_content(bot_py_path, "initial_extensions", "bot.py 包含擴展載入配置"))
    
    # 3. 檢查氣象 Cog 內容
    print("\n🌤️  氣象 Cog 功能檢查:")
    weather_cog_path = os.path.join(base_path, "cogs", "weather_commands.py")
    checks.append(check_file_content(weather_cog_path, "weather_station", "包含 weather_station 指令"))
    checks.append(check_file_content(weather_cog_path, "weather_station_by_county", "包含 weather_station_by_county 指令"))
    checks.append(check_file_content(weather_cog_path, "weather_station_info", "包含 weather_station_info 指令"))
    checks.append(check_file_content(weather_cog_path, "fetch_station_data", "包含 API 資料獲取功能"))
    checks.append(check_file_content(weather_cog_path, "create_station_detail_embed", "包含詳細資訊 Embed 功能"))
    
    # 4. 檢查文檔
    print("\n📚 文檔檢查:")
    checks.append(check_file_exists(os.path.join(base_path, "WEATHER_STATION_GUIDE.md"), "使用說明文檔"))
    
    # 5. 檢查測試文件
    print("\n🧪 測試文件檢查:")
    checks.append(check_file_exists(os.path.join(base_path, "test_weather_api.py"), "API 測試腳本"))
    
    # 6. 檢查環境變數
    print("\n🔐 環境變數檢查:")
    env_path = os.path.join(base_path, ".env")
    checks.append(check_file_content(env_path, "CWA_API_KEY", "包含 CWA API 金鑰配置"))
    checks.append(check_file_content(env_path, "DISCORD_TOKEN", "包含 Discord Token 配置"))
    
    # 統計結果
    passed = sum(checks)
    total = len(checks)
    
    print("\n" + "=" * 80)
    print(f"檢查結果: {passed}/{total} 項通過")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 所有檢查通過！氣象測站功能已完整配置")
        print("\n📋 已實現的功能:")
        print("   • /weather_station [關鍵字] - 關鍵字搜尋測站")
        print("   • /weather_station_by_county [縣市] [狀態] - 縣市搜尋測站")
        print("   • /weather_station_info [測站編號] - 查詢特定測站詳細資訊")
        
        print("\n🚀 啟動機器人:")
        print("   python bot.py")
        
        print("\n💡 使用提示:")
        print("   1. 確保機器人已加入 Discord 伺服器")
        print("   2. 確保機器人有斜線指令權限")
        print("   3. 第一次查詢可能需要較長時間（API 資料快取）")
        print("   4. 查看 bot.log 了解執行狀況")
        
        print("\n📖 詳細說明:")
        print("   請參閱 WEATHER_STATION_GUIDE.md")
        
    else:
        print(f"\n❌ {total - passed} 項檢查失敗，請修正後重新檢查")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 80)
    if success:
        print("✅ 氣象測站功能準備就緒！")
    else:
        print("❌ 請修正問題後重新檢查")
    print("=" * 80)
