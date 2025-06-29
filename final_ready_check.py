#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終系統就緒驗證
確認所有水庫功能已正確整合
"""

import os
import sys

def main():
    print("🔍 Discord 機器人最終驗證")
    print("=" * 50)
    
    # 核心檔案檢查
    core_files = {
        "bot.py": "機器人主程式",
        "cogs/reservoir_commands.py": "水庫指令模組",
        "requirements.txt": "依賴項目清單"
    }
    
    print("📋 核心檔案檢查:")
    all_files_ok = True
    
    for file_path, description in core_files.items():
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} - {description}")
        else:
            print(f"  ❌ {file_path} - {description}")
            all_files_ok = False
    
    # 檢查水庫指令檔案內容
    print("\n🏞️ 水庫功能檢查:")
    
    if os.path.exists("cogs/reservoir_commands.py"):
        with open("cogs/reservoir_commands.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        feature_checks = [
            ("ReservoirCommands 類別", "class ReservoirCommands"),
            ("setup 函數", "async def setup(bot)"),
            ("水庫水情指令", "@app_commands.command(name=\"reservoir\""),
            ("水庫營運指令", "@app_commands.command(name=\"reservoir_operation\""),
            ("水庫資料指令", "@app_commands.command(name=\"reservoir_info\""),
            ("防災影像指令", "@app_commands.command(name=\"water_cameras\""),
            ("水庫清單指令", "@app_commands.command(name=\"reservoir_list\"")
        ]
        
        for check_name, search_text in feature_checks:
            if search_text in content:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                all_files_ok = False
    else:
        print("  ❌ 水庫指令檔案不存在")
        all_files_ok = False
    
    # 檢查機器人主程式是否載入水庫模組
    print("\n🤖 機器人整合檢查:")
    
    if os.path.exists("bot.py"):
        with open("bot.py", "r", encoding="utf-8") as f:
            bot_content = f.read()
        
        if "cogs.reservoir_commands" in bot_content:
            print("  ✅ 水庫模組已載入到機器人")
        else:
            print("  ❌ 水庫模組未載入到機器人")
            all_files_ok = False
    
    # 最終狀態報告
    print("\n" + "=" * 50)
    print("📊 最終驗證結果:")
    print("=" * 50)
    
    if all_files_ok:
        print("🎉 系統完全就緒！")
        print("\n✅ 所有功能檢查通過")
        print("✅ 水庫查詢系統完整")
        print("✅ 機器人整合正確")
        
        print("\n🚀 下一步操作:")
        print("  1. 確認 Discord Bot Token 已設定")
        print("  2. 執行 'python launch_bot.py' 啟動機器人")
        print("  3. 或直接執行 'python bot.py'")
        
        print("\n📋 可用的水庫指令:")
        commands = [
            "/reservoir [水庫名稱] - 查詢水庫水情",
            "/reservoir_operation [水庫名稱] - 查詢營運狀況", 
            "/reservoir_info [水庫名稱] - 查詢基本資料",
            "/water_cameras [地區] - 查詢防災影像",
            "/reservoir_list - 顯示水庫清單"
        ]
        
        for cmd in commands:
            print(f"  • {cmd}")
            
        return True
    else:
        print("❌ 系統檢查發現問題")
        print("\n💡 建議修復步驟:")
        print("  1. 檢查缺失的檔案")
        print("  2. 確認程式碼完整性")
        print("  3. 重新執行此驗證程式")
        
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n📈 驗證結果: {'通過' if success else '失敗'}")
    sys.exit(0 if success else 1)
