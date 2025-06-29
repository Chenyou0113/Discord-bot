#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 機器人快速啟動指南
執行此腳本來啟動完整的 Discord 氣象機器人
包含所有水庫查詢功能
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def print_banner():
    """顯示啟動橫幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                  Discord 氣象機器人                          ║
║                   完整水庫查詢系統                          ║
║                      v2.0.0 最終版                         ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_requirements():
    """檢查必要檔案和環境"""
    print("🔍 檢查系統需求...")
    
    # 檢查核心檔案
    required_files = [
        "bot.py",
        "cogs/reservoir_commands.py",
        "requirements.txt",
        ".env"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  缺少必要檔案: {', '.join(missing_files)}")
        if ".env" in missing_files:
            print("💡 請確保 .env 檔案包含正確的 Discord Bot Token")
        return False
    
    return True

def show_available_commands():
    """顯示可用指令清單"""
    commands = [
        ("🏞️ 水庫水情", "/reservoir [水庫名稱]", "查詢台灣水庫即時水情"),
        ("🔧 營運狀況", "/reservoir_operation [水庫名稱]", "查詢水庫營運詳情"),
        ("📋 基本資料", "/reservoir_info [水庫名稱]", "查詢水庫基本建設資訊"),
        ("📹 防災影像", "/water_cameras [地區名稱]", "查詢水利防災監控影像"),
        ("📝 水庫清單", "/reservoir_list", "顯示所有支援的水庫"),
        ("🌡️ 天氣查詢", "/weather [地點]", "查詢天氣資訊"),
        ("🌀 雷達回波", "/radar [地點]", "查詢雷達回波圖"),
        ("💨 空氣品質", "/air_quality [地點]", "查詢空氣品質"),
        ("🌡️ 溫度監測", "/temperature [地點]", "查詢溫度監測")
    ]
    
    print("\n📋 機器人支援的指令:")
    print("=" * 60)
    
    for emoji_name, command, description in commands:
        print(f"{emoji_name}")
        print(f"  指令: {command}")
        print(f"  功能: {description}")
        print()

def show_supported_reservoirs():
    """顯示支援的水庫清單"""
    reservoirs = [
        "石門水庫", "翡翠水庫", "曾文水庫", "日月潭水庫",
        "德基水庫", "鯉魚潭水庫", "南化水庫", "牡丹水庫",
        "烏山頭水庫", "白河水庫", "阿公店水庫", "仁義潭水庫",
        "蘭潭水庫", "明德水庫", "永和山水庫", "寶山水庫",
        "寶山第二水庫", "新山水庫", "湖山水庫", "石岡壩"
    ]
    
    print("🏞️ 支援查詢的主要水庫:")
    print("=" * 40)
    
    for i, reservoir in enumerate(reservoirs, 1):
        print(f"{i:2d}. {reservoir}")
        if i % 4 == 0:  # 每 4 個換行
            print()

def create_startup_log():
    """創建啟動日志"""
    log_data = {
        "startup_time": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": [
            "水庫水情查詢",
            "水庫營運狀況",
            "水庫基本資料",
            "水利防災影像",
            "天氣查詢",
            "雷達回波",
            "空氣品質監測",
            "溫度監測"
        ],
        "status": "ready_to_launch"
    }
    
    with open("startup_log.json", "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def main():
    """主程序"""
    print_banner()
    
    # 檢查系統需求
    if not check_requirements():
        print("\n❌ 系統檢查失敗，請修復問題後重新啟動")
        sys.exit(1)
    
    print("\n✅ 系統檢查通過！")
    
    # 顯示功能資訊
    show_available_commands()
    show_supported_reservoirs()
    
    # 創建啟動日志
    create_startup_log()
    
    print("\n🚀 準備啟動 Discord 機器人...")
    print("=" * 60)
    print("💡 啟動提示:")
    print("  1. 確保網路連接正常")
    print("  2. Discord Bot Token 已正確設定")
    print("  3. 機器人已被邀請到 Discord 伺服器")
    print("  4. 機器人擁有適當的權限")
    print("\n⏰ 機器人啟動中，請稍候...")
    print("📝 啟動日誌將顯示在下方")
    print("=" * 60)
    
    # 啟動機器人
    try:
        subprocess.run([sys.executable, "bot.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 機器人已停止運行")
        print("👋 感謝使用 Discord 氣象機器人！")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 機器人啟動失敗: {e}")
        print("💡 請檢查錯誤訊息並修復問題")
        sys.exit(1)

if __name__ == "__main__":
    main()
