#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最簡單的啟動測試
"""

print("🧪 開始簡單測試...")

try:
    import os
    import sys
    from dotenv import load_dotenv
    
    # 設定工作目錄
    os.chdir(r"c:\Users\xiaoy\Desktop\Discord bot")
    print("✅ 工作目錄設定完成")
    
    # 載入環境變數
    load_dotenv()
    print("✅ 環境變數載入完成")
    
    # 檢查 Token
    token = os.getenv('DISCORD_TOKEN')
    if token:
        print("✅ Discord Token 存在")
    else:
        print("❌ Discord Token 不存在")
        exit(1)
    
    # 測試導入機器人模組
    print("📦 測試導入機器人模組...")
    from bot import CustomBot
    print("✅ 機器人模組導入成功")
    
    # 創建機器人實例
    print("🤖 創建機器人實例...")
    bot = CustomBot()
    print("✅ 機器人實例創建成功")
    
    # 檢查初始配置
    print(f"📋 初始配置:")
    print(f"  - 要載入的擴展數: {len(bot.initial_extensions)}")
    print(f"  - 目前 Cogs: {len(bot.cogs)}")
    print(f"  - 目前指令: {len(bot.tree._global_commands)}")
    
    print("\n🎉 基本測試通過！")
    print("🚀 機器人可以正常初始化")
    
except Exception as e:
    print(f"❌ 測試失敗: {str(e)}")
    import traceback
    print(f"錯誤詳情: {traceback.format_exc()}")

print("\n測試完成！")
