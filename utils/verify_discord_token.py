#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot Token 驗證工具
檢查 Token 是否有效並提供修復建議
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

async def verify_discord_token():
    """驗證 Discord Bot Token 是否有效"""
    print("🔍 Discord Bot Token 驗證工具")
    print("=" * 50)
    
    # 載入環境變數
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ 未找到 DISCORD_TOKEN 環境變數")
        print("請檢查 .env 檔案是否存在且包含 DISCORD_TOKEN")
        return False
    
    print(f"📝 找到 Token: {token[:30]}...")
    
    # 檢查 Token 格式
    if not token.startswith('MT') or len(token) < 50:
        print("❌ Token 格式不正確")
        print("Discord Bot Token 應該：")
        print("  - 以 'MT' 開頭")
        print("  - 長度約 70 個字符")
        print("  - 格式：MTxxxxx.xxxxxx.xxxxxxxxx")
        return False
    
    # 嘗試驗證 Token
    try:
        headers = {
            'Authorization': f'Bot {token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discord.com/api/v10/users/@me', headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Token 驗證成功！")
                    print(f"🤖 機器人名稱: {data.get('username', 'Unknown')}")
                    print(f"🆔 機器人 ID: {data.get('id', 'Unknown')}")
                    return True
                elif response.status == 401:
                    print("❌ Token 無效或過期")
                    print("📋 解決方案：")
                    print("1. 前往 Discord Developer Portal: https://discord.com/developers/applications")
                    print("2. 選擇您的應用程式")
                    print("3. 進入 'Bot' 頁面")
                    print("4. 點擊 'Reset Token' 重新生成")
                    print("5. 複製新 Token 並更新 .env 檔案")
                    return False
                else:
                    print(f"❌ 驗證失敗，狀態碼: {response.status}")
                    response_text = await response.text()
                    print(f"回應: {response_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ 驗證過程發生錯誤: {e}")
        return False

async def check_bot_permissions():
    """檢查機器人所需權限"""
    print("\n🔐 機器人權限檢查清單")
    print("=" * 30)
    print("請確認您的機器人具有以下權限：")
    print("✓ Send Messages (發送訊息)")
    print("✓ Use Slash Commands (使用斜線指令)")
    print("✓ Embed Links (嵌入連結)")
    print("✓ Read Message History (讀取訊息歷史)")
    print("✓ Attach Files (附加檔案)")
    print("✓ Manage Messages (管理訊息) - 可選")

def generate_new_env_template():
    """生成新的 .env 範本"""
    template = """# Discord Bot Token
DISCORD_TOKEN=YOUR_NEW_BOT_TOKEN_HERE

# Google API Key (for AI Chat)
GOOGLE_API_KEY=your_google_api_key_here

# 中央氣象署 API 密鑰
CWA_API_KEY=your_cwa_api_key_here

# Google Search API 設定 (可選)
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# 其他設定
LOGGING_LEVEL=INFO

# 使用說明：
# 1. 將 YOUR_NEW_BOT_TOKEN_HERE 替換為您的新 Discord Bot Token
# 2. 將 your_cwa_api_key_here 替換為您的中央氣象署 API 密鑰
# 2. 確保 Token 格式正確：MTxxxxx.xxxxxx.xxxxxxxxx
# 3. 不要在 Token 前後添加引號或空格
"""
    
    with open('.env.new', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("\n📄 已生成新的 .env 範本: .env.new")
    print("請用新的 Token 更新後重新命名為 .env")

async def main():
    """主函式"""
    is_valid = await verify_discord_token()
    
    if not is_valid:
        print("\n🔧 修復步驟：")
        print("1. 重新生成 Discord Bot Token")
        print("2. 更新 .env 檔案")
        print("3. 重新執行此驗證工具")
        
        generate_new_env_template()
    
    await check_bot_permissions()
    
    print("\n" + "=" * 50)
    if is_valid:
        print("🎉 Token 驗證通過，可以啟動機器人！")
    else:
        print("⚠️ 請修復 Token 問題後再試")

if __name__ == "__main__":
    asyncio.run(main())
