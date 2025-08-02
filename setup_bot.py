#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 機器人配置助手
幫助設定環境變數和同步指令
"""

import os
import sys

def create_env_file():
    """創建 .env 檔案"""
    print("🔧 Discord 機器人配置助手")
    print("=" * 50)
    
    if os.path.exists('.env'):
        print("📁 找到現有的 .env 檔案")
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'DISCORD_TOKEN' in content:
                print("✅ DISCORD_TOKEN 已設定")
                return True
            else:
                print("⚠️ .env 檔案存在但缺少 DISCORD_TOKEN")
    
    print("\n📝 請設定您的 Discord 機器人 Token:")
    print("1. 前往 https://discord.com/developers/applications")
    print("2. 選擇您的應用程式")
    print("3. 點擊左側 'Bot' 選項")
    print("4. 複製 Token")
    print()
    
    token = input("請輸入您的 Discord Bot Token: ").strip()
    
    if not token:
        print("❌ Token 不能為空")
        return False
    
    # 創建 .env 檔案
    env_content = f"""# Discord 機器人配置
DISCORD_TOKEN={token}

# Google API Key (如果需要 AI 功能)
GOOGLE_API_KEY=your_google_api_key_here
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ .env 檔案創建成功！")
        return True
        
    except Exception as e:
        print(f"❌ 創建 .env 檔案失敗: {str(e)}")
        return False

def check_cogs():
    """檢查 Cogs 檔案"""
    print("\n🔍 檢查 Cogs 檔案...")
    
    required_cogs = [
        'cogs/reservoir_commands.py',
        'cogs/weather_commands.py',
        'cogs/info_commands_fixed_v4_clean.py'
    ]
    
    all_exist = True
    for cog_file in required_cogs:
        if os.path.exists(cog_file):
            print(f"✅ {cog_file}")
        else:
            print(f"❌ {cog_file} 缺失")
            all_exist = False
    
    return all_exist

def show_available_commands():
    """顯示可用指令列表"""
    print("\n🎯 您的機器人將具備以下指令:")
    print("=" * 50)
    
    commands = [
        ("💧 水利相關", [
            "/水庫清單 - 查詢水庫資訊",
            "/水位資訊 - 河川水位查詢",
        ]),
        ("🌤️ 天氣相關", [
            "/weather - 天氣查詢",
        ]),
        ("🔧 管理功能", [
            "/check_permissions - 權限檢查",
        ]),
        ("ℹ️ 基本功能", [
            "/ping - 機器人延遲測試",
            "/help - 幫助資訊",
        ])
    ]
    
    for category, cmd_list in commands:
        print(f"\n{category}:")
        for cmd in cmd_list:
            print(f"   {cmd}")
    
    print("\n" + "=" * 50)

def main():
    """主函數"""
    print("🎮 Discord 機器人設定與指令同步工具")
    print("=" * 60)
    
    # 1. 檢查並創建 .env 檔案
    if not create_env_file():
        print("❌ 環境設定失敗，無法繼續")
        return
    
    # 2. 檢查 Cogs 檔案
    if not check_cogs():
        print("❌ 部分 Cogs 檔案缺失，可能影響功能")
    
    # 3. 顯示可用指令
    show_available_commands()
    
    # 4. 提供下一步指示
    print("🚀 下一步操作:")
    print("=" * 30)
    print("1. 運行指令同步:")
    print("   python sync_commands.py")
    print()
    print("2. 或直接啟動機器人:")
    print("   python bot.py")
    print()
    print("3. 確保機器人在 Discord 伺服器中有適當權限:")
    print("   - 使用斜線指令 (Use Application Commands)")
    print("   - 發送訊息 (Send Messages)")
    print("   - 嵌入連結 (Embed Links)")
    print("   - 檢視頻道 (View Channels)")
    print()
    print("4. 使用 /check_permissions 測試權限設定")
    print("=" * 30)
    
    response = input("\n是否要立即同步指令到 Discord？(y/n): ").lower().strip()
    
    if response == 'y':
        print("\n🔄 準備同步指令...")
        os.system("python sync_commands.py")
    else:
        print("\n📝 您可以稍後運行 'python sync_commands.py' 來同步指令")
    
    print("\n🎉 設定完成！祝您使用愉快！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用戶取消操作")
    except Exception as e:
        print(f"\n\n❌ 執行過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
