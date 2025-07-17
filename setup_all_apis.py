#!/usr/bin/env python3
"""
API 密鑰統一設定工具
用於安全地設定所有 API 密鑰到環境變數中
"""

import os
import sys

def setup_all_api_keys():
    """設定所有 API 密鑰到 .env 檔案"""
    print("🔐 API 密鑰統一設定工具")
    print("=" * 60)
    
    # 檢查是否存在 .env 檔案
    env_file = ".env"
    env_example_file = ".env.example"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example_file):
            print(f"📄 複製 {env_example_file} 到 {env_file}")
            with open(env_example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            print(f"❌ 找不到 {env_example_file} 檔案")
            return False
    
    # 讀取現有的 .env 檔案內容
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📝 讀取 {env_file} 檔案")
    
    # 定義需要設定的 API 密鑰
    api_configs = {
        'DISCORD_TOKEN': {
            'name': 'Discord Bot Token',
            'required': True,
            'description': '從 Discord Developer Portal 取得',
            'url': 'https://discord.com/developers/applications',
            'format': 'MTxxxxxxxxx... (約70字元)',
            'steps': [
                '1. 前往 Discord Developer Portal',
                '2. 創建新應用程式 → Bot',
                '3. 複製 Bot Token'
            ]
        },
        'CWA_API_KEY': {
            'name': '中央氣象署 API 密鑰',
            'required': True,
            'description': '從中央氣象署開放資料平臺取得',
            'url': 'https://opendata.cwa.gov.tw/',
            'format': 'CWA-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
            'steps': [
                '1. 前往中央氣象署開放資料平臺',
                '2. 註冊帳號並登入',
                '3. 前往「會員中心」→「API金鑰管理」',
                '4. 申請新的 API 金鑰'
            ]
        },
        'TDX_CLIENT_ID': {
            'name': 'TDX Client ID',
            'required': True,
            'description': '從 TDX 運輸資料流通服務平臺取得',
            'url': 'https://tdx.transportdata.tw/',
            'format': 'xxxxxxxxx-xxxx-xxxx-xxxx',
            'steps': [
                '1. 前往 TDX 運輸資料流通服務平臺',
                '2. 註冊帳號並登入',
                '3. 前往「應用程式管理」',
                '4. 創建新應用程式',
                '5. 取得 Client ID'
            ]
        },
        'TDX_CLIENT_SECRET': {
            'name': 'TDX Client Secret',
            'required': True,
            'description': '從 TDX 運輸資料流通服務平臺取得 (與 Client ID 配對)',
            'url': 'https://tdx.transportdata.tw/',
            'format': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
            'steps': [
                '1. 在 TDX 平臺的應用程式管理中',
                '2. 查看您創建的應用程式',
                '3. 取得 Client Secret'
            ]
        },
        'AQI_API_KEY': {
            'name': '環保署 AQI API 密鑰',
            'required': False,
            'description': '用於空氣品質查詢功能 (可選)',
            'url': 'https://data.epa.gov.tw/',
            'format': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
            'steps': [
                '1. 前往環保署開放資料平臺',
                '2. 註冊帳號並申請 API 金鑰',
                '3. 用於空氣品質資料查詢'
            ]
        },
        'GOOGLE_API_KEY': {
            'name': 'Google API Key',
            'required': False,
            'description': '用於 AI 聊天功能 (可選)',
            'url': 'https://console.cloud.google.com/',
            'format': 'AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            'steps': [
                '1. 前往 Google Cloud Console',
                '2. 啟用 Gemini API',
                '3. 創建 API 金鑰'
            ]
        }
    }
    
    updated_keys = []
    
    for key, config in api_configs.items():
        print(f"\n📋 設定 {config['name']}")
        print("-" * 40)
        
        # 檢查是否已存在此密鑰
        current_value = None
        has_key = False
        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                current_value = line.split('=', 1)[1].strip()
                has_key = True
                break
        
        # 如果已有有效值，詢問是否更新
        if has_key and current_value and not current_value.startswith('your_'):
            print(f"✅ 發現已設定的 {key}")
            print(f"   當前值: {current_value[:20]}...")
            
            if config['required']:
                update = input("是否要更新此密鑰？(y/N): ").lower()
                if update != 'y':
                    print("⏩ 跳過更新")
                    continue
            else:
                print("⏩ 可選密鑰已設定，跳過")
                continue
        
        # 如果是必需的密鑰但未設定
        if config['required'] and (not has_key or not current_value or current_value.startswith('your_')):
            print(f"❌ 必需的密鑰 {key} 未設定")
        elif not config['required']:
            skip = input(f"是否要設定可選的 {config['name']}？(y/N): ").lower()
            if skip != 'y':
                print("⏩ 跳過可選密鑰")
                continue
        
        # 顯示申請指南
        print(f"\n📖 {config['name']} 申請指南:")
        print(f"🌐 網址: {config['url']}")
        print(f"📝 格式: {config['format']}")
        print("📋 步驟:")
        for step in config['steps']:
            print(f"   {step}")
        print()
        
        # 輸入新密鑰
        while True:
            new_value = input(f"請輸入 {config['name']}: ").strip()
            
            if not new_value:
                if config['required']:
                    print("❌ 此密鑰為必需，不能為空")
                    continue
                else:
                    print("⏩ 跳過可選密鑰")
                    break
            
            # 簡單的格式驗證
            if key == 'DISCORD_TOKEN' and not (new_value.startswith('MT') and len(new_value) > 50):
                print("⚠️  警告: Discord Token 通常以 'MT' 開頭且長度較長")
                confirm = input("確定要使用此 Token 嗎？(y/N): ").lower()
                if confirm != 'y':
                    continue
            
            if key == 'CWA_API_KEY' and not new_value.startswith('CWA-'):
                print("⚠️  警告: CWA API 密鑰通常以 'CWA-' 開頭")
                confirm = input("確定要使用此密鑰嗎？(y/N): ").lower()
                if confirm != 'y':
                    continue
            
            if key.startswith('TDX_') and len(new_value) < 20:
                print("⚠️  警告: TDX 憑證長度似乎太短")
                confirm = input("確定要使用此憑證嗎？(y/N): ").lower()
                if confirm != 'y':
                    continue
            
            break
        
        if not new_value:
            continue
        
        # 更新 .env 檔案
        if has_key:
            # 更新現有的密鑰
            for i, line in enumerate(lines):
                if line.startswith(f'{key}='):
                    lines[i] = f"{key}={new_value}\n"
                    break
        else:
            # 新增密鑰
            lines.append(f"{key}={new_value}\n")
        
        updated_keys.append(key)
        print(f"✅ {config['name']} 已設定")
    
    # 寫回檔案
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"\n🎉 API 密鑰設定完成！")
        print(f"📝 更新的密鑰: {', '.join(updated_keys) if updated_keys else '無'}")
        
        # 測試設定
        print("\n🧪 測試環境變數設定...")
        from dotenv import load_dotenv
        load_dotenv()
        
        test_results = {}
        for key in api_configs:
            test_value = os.getenv(key)
            test_results[key] = bool(test_value and not test_value.startswith('your_'))
        
        print("📊 測試結果:")
        for key, config in api_configs.items():
            status = "✅" if test_results[key] else "❌"
            required_text = "(必需)" if config['required'] else "(可選)"
            print(f"   {status} {config['name']} {required_text}")
        
        # 檢查必需的密鑰
        missing_required = [key for key, config in api_configs.items() 
                          if config['required'] and not test_results[key]]
        
        if missing_required:
            print(f"\n⚠️  仍缺少必需的密鑰: {', '.join(missing_required)}")
            print("請重新執行此工具設定缺少的密鑰")
            return False
        else:
            print("\n✅ 所有必需的密鑰已正確設定！")
            print("\n💡 使用提示:")
            print("- 請勿將 .env 檔案提交到版本控制系統")
            print("- 定期更換 API 密鑰以確保安全")
            print("- 執行 'python security_check.py' 檢查安全性")
            return True
        
    except Exception as e:
        print(f"❌ 寫入檔案時發生錯誤: {e}")
        return False

def check_current_setup():
    """檢查當前的 API 設定狀況"""
    print("🔍 檢查當前 API 設定狀況...")
    
    if not os.path.exists('.env'):
        print("❌ .env 檔案不存在")
        return
    
    print("✅ .env 檔案存在")
    
    # 檢查環境變數
    from dotenv import load_dotenv
    load_dotenv()
    
    api_keys = {
        'DISCORD_TOKEN': 'Discord Bot Token (必需)',
        'CWA_API_KEY': '中央氣象署 API 密鑰 (必需)',
        'TDX_CLIENT_ID': 'TDX Client ID (必需)',
        'TDX_CLIENT_SECRET': 'TDX Client Secret (必需)',
        'AQI_API_KEY': 'AQI API 密鑰 (可選)',
        'GOOGLE_API_KEY': 'Google API Key (可選)'
    }
    
    for key, description in api_keys.items():
        value = os.getenv(key)
        if value and not value.startswith('your_'):
            print(f"✅ {description}: 已設定 ({value[:15]}...)")
        else:
            print(f"❌ {description}: 未設定")

if __name__ == "__main__":
    print("🤖 Discord 氣象機器人 - API 密鑰統一設定工具")
    print("=" * 70)
    
    # 檢查當前設定
    check_current_setup()
    print()
    
    # 詢問是否要設定
    if input("是否要設定 API 密鑰？(Y/n): ").lower() not in ['n', 'no']:
        success = setup_all_api_keys()
        if success:
            print("\n🎉 設定完成！您現在可以重新啟動機器人了。")
        else:
            print("\n⚠️  部分設定未完成，請檢查並重新執行。")
    else:
        print("⏩ 跳過設定")
