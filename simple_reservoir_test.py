#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試水庫指令配置
"""

import os
import sys

def test_reservoir_config():
    """簡單測試水庫指令配置"""
    print("🔍 測試水庫指令配置...")
    
    try:
        # 切換工作目錄
        os.chdir(r"c:\Users\xiaoy\Desktop\Discord bot")
        
        # 測試水庫模組導入
        print("📦 測試水庫模組導入...")
        import cogs.reservoir_commands
        print("✅ 水庫模組導入成功")
        
        # 讀取 bot.py 檢查配置
        print("📋 檢查 bot.py 配置...")
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        if 'cogs.reservoir_commands' in bot_content:
            print("✅ 水庫指令已加入 bot.py 配置")
        else:
            print("❌ 水庫指令未在 bot.py 中")
            return False
        
        # 檢查水庫指令檔案
        print("📝 檢查水庫指令檔案...")
        reservoir_file = 'cogs/reservoir_commands.py'
        if os.path.exists(reservoir_file):
            print("✅ 水庫指令檔案存在")
            
            # 檢查檔案內容
            with open(reservoir_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'ReservoirCommands' in content:
                print("✅ ReservoirCommands 類別存在")
            else:
                print("❌ 找不到 ReservoirCommands 類別")
                return False
            
            if '@app_commands.command' in content:
                print("✅ 包含應用程式指令")
            else:
                print("❌ 找不到應用程式指令")
                return False
            
        else:
            print("❌ 水庫指令檔案不存在")
            return False
        
        print("\n🎯 水庫指令功能：")
        print("  - /reservoir: 查詢水庫水情")  
        print("  - /reservoir_list: 顯示水庫列表")
        print("  - 支援主要水庫查詢")
        print("  - 資料來源: 經濟部水利署")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_reservoir_config()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 水庫指令配置測試成功！")
        print("✅ 所有配置正確")
        print("🚀 準備好啟動機器人測試")
    else:
        print("❌ 配置測試失敗")
        print("🔧 需要檢查上方錯誤並修復")
