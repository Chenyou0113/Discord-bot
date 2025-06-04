#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot 配置助手
幫助用戶設置 Discord Token 和 Google API Key
"""

import os
import re
from getpass import getpass

def validate_discord_token(token):
    """驗證 Discord Token 格式"""
    if not token or token.strip() == "":
        return False, "Token 不能為空"
    
    # Discord Bot Token 通常是 59-70 個字符的 Base64 字符串
    if len(token) < 50:
        return False, "Token 長度太短，請確認是否為完整的 Bot Token"
    
    # Discord Token 通常包含三個部分，用點分隔
    if token.count('.') < 2:
        return False, "Token 格式不正確，Discord Bot Token 應該包含兩個點"
    
    return True, "Token 格式看起來正確"

def validate_google_api_key(api_key):
    """驗證 Google API Key 格式"""
    if not api_key or api_key.strip() == "":
        return False, "API Key 不能為空"
    
    # Google API Key 通常是 39 個字符
    if len(api_key) < 30:
        return False, "API Key 長度太短"
    
    return True, "API Key 格式看起來正確"

def update_env_file():
    """更新 .env 文件"""
    env_path = ".env"
    
    print("=" * 50)
    print("        Discord Bot 配置助手")
    print("=" * 50)
    print()
    
    # 檢查是否存在 .env 文件
    if not os.path.exists(env_path):
        print("❌ 找不到 .env 文件")
        if os.path.exists(".env.example"):
            print("📋 發現 .env.example 文件，正在複製...")
            with open(".env.example", "r", encoding="utf-8") as f:
                content = f.read()
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ 已創建 .env 文件")
        else:
            print("❌ 也找不到 .env.example 文件")
            return False
    
    # 讀取當前配置
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    print("🔧 當前配置狀態：")
    
    # 檢查 Discord Token
    discord_configured = "DISCORD_TOKEN=your_discord_bot_token_here" not in content
    if discord_configured:
        print("✅ Discord Token 已配置")
    else:
        print("❌ Discord Token 未配置")
    
    # 檢查 Google API Key
    google_configured = "GOOGLE_API_KEY=your_google_api_key_here" not in content
    if google_configured:
        print("✅ Google API Key 已配置")
    else:
        print("❌ Google API Key 未配置")
    
    print()
    
    # 配置 Discord Token
    if not discord_configured:
        print("📝 配置 Discord Bot Token")
        print("如何獲取 Discord Bot Token:")
        print("1. 前往 https://discord.com/developers/applications")
        print("2. 選擇您的應用程式或創建新的")
        print("3. 在左側選單點擊 'Bot'")
        print("4. 在 'Token' 部分點擊 'Reset Token' 或 'Copy'")
        print("5. 複製完整的 Token")
        print()
        
        discord_token = input("請輸入您的 Discord Bot Token (或按 Enter 跳過): ").strip()
        
        if discord_token:
            is_valid, message = validate_discord_token(discord_token)
            if is_valid:
                print(f"✅ {message}")
                content = re.sub(
                    r'DISCORD_TOKEN=.*',
                    f'DISCORD_TOKEN={discord_token}',
                    content
                )
                print("✅ Discord Token 已更新")
            else:
                print(f"❌ {message}")
                print("Token 未更新，請檢查後重新執行此腳本")
    
    # 配置 Google API Key
    if not google_configured:
        print("\n📝 配置 Google Gemini API Key")
        print("如何獲取 Google API Key:")
        print("1. 前往 https://aistudio.google.com/app/apikey")
        print("2. 點擊 'Create API Key'")
        print("3. 選擇現有專案或創建新專案")
        print("4. 複製生成的 API Key")
        print()
        
        google_api_key = input("請輸入您的 Google API Key (或按 Enter 跳過): ").strip()
        
        if google_api_key:
            is_valid, message = validate_google_api_key(google_api_key)
            if is_valid:
                print(f"✅ {message}")
                content = re.sub(
                    r'GOOGLE_API_KEY=.*',
                    f'GOOGLE_API_KEY={google_api_key}',
                    content
                )
                print("✅ Google API Key 已更新")
            else:
                print(f"❌ {message}")
                print("API Key 未更新，請檢查後重新執行此腳本")
    
    # 寫入更新的內容
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("\n" + "=" * 50)
    print("配置完成！")
    
    # 最終檢查
    final_discord_configured = "DISCORD_TOKEN=your_discord_bot_token_here" not in content
    final_google_configured = "GOOGLE_API_KEY=your_google_api_key_here" not in content
    
    if final_discord_configured and final_google_configured:
        print("✅ 所有配置都已完成，您現在可以啟動機器人了！")
        print("💡 執行: start_bot_simple.bat")
        return True
    else:
        print("⚠️  部分配置尚未完成：")
        if not final_discord_configured:
            print("   - Discord Token 尚未配置")
        if not final_google_configured:
            print("   - Google API Key 尚未配置")
        print("💡 請重新執行此腳本完成配置")
        return False

if __name__ == "__main__":
    try:
        update_env_file()
    except KeyboardInterrupt:
        print("\n\n❌ 配置被取消")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
    
    input("\n按 Enter 鍵退出...")
