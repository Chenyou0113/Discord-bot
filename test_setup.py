# 測試機器人基本功能
import os
import sys

print("=== Discord 機器人測試 ===")
print(f"Python 版本: {sys.version}")

try:
    import discord
    print(f"✅ Discord.py 版本: {discord.__version__}")
except ImportError as e:
    print(f"❌ Discord.py 導入失敗: {e}")
    sys.exit(1)

try:
    import google.generativeai
    print("✅ Google Generative AI 導入成功")
except ImportError as e:
    print(f"❌ Google Generative AI 導入失敗: {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv 載入成功")
    
    # 檢查環境變數
    discord_token = os.getenv('DISCORD_TOKEN')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    
    if discord_token and discord_token != 'your_discord_bot_token_here':
        print("✅ DISCORD_TOKEN 已配置")
    else:
        print("❌ DISCORD_TOKEN 未配置或使用預設值")
        print("請編輯 .env 文件並設定您的實際 Discord Token")
    
    if google_api_key and google_api_key != 'your_google_api_key_here':
        print("✅ GOOGLE_API_KEY 已配置")
    else:
        print("❌ GOOGLE_API_KEY 未配置或使用預設值")
        print("請編輯 .env 文件並設定您的實際 Google API Key")
        
except Exception as e:
    print(f"❌ 環境變數載入失敗: {e}")

print("\n=== 檔案檢查 ===")
required_files = [
    'bot.py',
    'cogs/basic_commands.py',
    'cogs/admin_commands_fixed.py',
    'cogs/info_commands_fixed_v4_clean.py',
    'cogs/level_system.py',
    'cogs/monitor_system.py',
    'cogs/voice_system.py',
    'cogs/chat_commands.py'
]

for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} 缺失")

print("\n=== 測試完成 ===")
print("如果所有項目都顯示 ✅，您的機器人應該可以正常啟動")
print("如果有 ❌ 項目，請先解決這些問題")
