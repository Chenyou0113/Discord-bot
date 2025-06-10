#!/usr/bin/env python3
"""
驗證 Gemini 模型修復腳本
檢查 search_commands.py 中是否已正確更新模型名稱
"""

import os
import re

def verify_gemini_fix():
    """驗證 Gemini 模型修復"""
    
    # 檢查 search_commands.py 文件
    search_commands_path = "cogs/search_commands.py"
    
    if not os.path.exists(search_commands_path):
        print("❌ 錯誤: search_commands.py 文件未找到")
        return False
    
    try:
        with open(search_commands_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否還有舊的 gemini-pro 模型
        if 'gemini-pro' in content:
            print("❌ 發現舊的 'gemini-pro' 模型名稱")
            
            # 找出具體位置
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'gemini-pro' in line:
                    print(f"   第 {i} 行: {line.strip()}")
            return False
        
        # 檢查是否使用了新的模型名稱
        new_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash']
        found_new_model = False
        
        for model in new_models:
            if model in content:
                print(f"✅ 找到新模型: {model}")
                found_new_model = True
                
                # 找出具體位置
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if model in line:
                        print(f"   第 {i} 行: {line.strip()}")
                break
        
        if not found_new_model:
            print("❌ 未找到任何新的 Gemini 模型名稱")
            return False
        
        print("\n✅ Gemini 模型修復驗證成功!")
        return True
        
    except Exception as e:
        print(f"❌ 讀取文件時發生錯誤: {e}")
        return False

def check_bot_status():
    """檢查 Bot 狀態"""
    print("\n📊 Bot 狀態檢查:")
    
    # 檢查 log 文件
    if os.path.exists("bot.log"):
        print("✅ 找到 bot.log 文件")
        
        # 讀取最新的幾行日誌
        try:
            with open("bot.log", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print("\n📝 最新的 5 行日誌:")
            for line in lines[-5:]:
                line = line.strip()
                if line:
                    if "ERROR" in line:
                        print(f"❌ {line}")
                    elif "INFO" in line:
                        print(f"ℹ️  {line}")
                    else:
                        print(f"   {line}")
                        
        except Exception as e:
            print(f"❌ 讀取日誌文件時發生錯誤: {e}")
    else:
        print("⚠️  未找到 bot.log 文件")

if __name__ == "__main__":
    print("🔍 驗證 Gemini 模型修復...")
    print("=" * 50)
    
    success = verify_gemini_fix()
    check_bot_status()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 修復驗證完成! 模型已正確更新。")
        print("💡 建議: 重新啟動 Bot 以確保使用新配置。")
    else:
        print("❌ 修復驗證失敗! 需要進一步檢查。")
