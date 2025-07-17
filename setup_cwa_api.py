#!/usr/bin/env python3
"""
CWA API 密鑰設定工具
用於安全地將中央氣象署 API 密鑰加入到環境變數中
"""

import os
import sys

def setup_cwa_api_key():
    """設定 CWA API 密鑰到 .env 檔案"""
    print("🔐 CWA API 密鑰設定工具")
    print("=" * 50)
    
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
    
    # 檢查是否已存在 CWA_API_KEY
    has_cwa_key = False
    for i, line in enumerate(lines):
        if line.startswith('CWA_API_KEY='):
            if 'your_cwa_api_key_here' not in line:
                print("✅ 發現已設定的 CWA_API_KEY")
                current_key = line.split('=')[1].strip()
                print(f"   當前密鑰: {current_key[:15]}...")
                
                update = input("是否要更新密鑰？(y/N): ").lower()
                if update != 'y':
                    print("⏩ 跳過更新")
                    return True
            has_cwa_key = True
            break
    
    # 提示用戶輸入 API 密鑰
    print("\n📋 如何取得 CWA API 密鑰:")
    print("1. 前往 https://opendata.cwa.gov.tw/")
    print("2. 註冊帳號並登入")
    print("3. 前往「會員中心」→「API金鑰管理」")
    print("4. 申請新的 API 金鑰")
    print("5. 複製取得的密鑰 (格式類似: CWA-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)")
    print()
    
    while True:
        api_key = input("請輸入您的 CWA API 密鑰: ").strip()
        
        if not api_key:
            print("❌ 密鑰不能為空")
            continue
        
        if not api_key.startswith('CWA-'):
            print("⚠️  警告: CWA API 密鑰通常以 'CWA-' 開頭")
            confirm = input("確定要使用此密鑰嗎？(y/N): ").lower()
            if confirm != 'y':
                continue
        
        if len(api_key) < 20:
            print("⚠️  警告: 密鑰長度似乎太短")
            confirm = input("確定要使用此密鑰嗎？(y/N): ").lower()
            if confirm != 'y':
                continue
        
        break
    
    # 更新 .env 檔案
    if has_cwa_key:
        # 更新現有的密鑰
        for i, line in enumerate(lines):
            if line.startswith('CWA_API_KEY='):
                lines[i] = f"CWA_API_KEY={api_key}\n"
                break
    else:
        # 新增密鑰
        # 尋找合適的位置插入 (Google API Key 之後)
        insert_pos = len(lines)
        for i, line in enumerate(lines):
            if line.startswith('GOOGLE_API_KEY='):
                insert_pos = i + 1
                break
        
        lines.insert(insert_pos, f"CWA_API_KEY={api_key}\n")
    
    # 寫回檔案
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ CWA API 密鑰已成功設定到 {env_file}")
        print(f"   密鑰: {api_key[:15]}...")
        
        # 測試設定
        print("\n🧪 測試設定...")
        os.environ['CWA_API_KEY'] = api_key
        
        from dotenv import load_dotenv
        load_dotenv()
        
        test_key = os.getenv('CWA_API_KEY')
        if test_key == api_key:
            print("✅ 環境變數設定測試通過")
        else:
            print("❌ 環境變數設定測試失敗")
            return False
        
        print("\n🎉 設定完成！現在您可以安全地使用 CWA API 功能了")
        print("\n⚠️  重要提醒:")
        print("- 請勿將 .env 檔案提交到版本控制系統")
        print("- 請妥善保管您的 API 密鑰")
        print("- 如果密鑰洩露，請立即到 CWA 網站重新申請")
        
        return True
        
    except Exception as e:
        print(f"❌ 寫入檔案時發生錯誤: {e}")
        return False

def check_current_setup():
    """檢查當前的設定狀況"""
    print("🔍 檢查當前設定狀況...")
    
    # 檢查 .env 檔案
    if os.path.exists('.env'):
        print("✅ .env 檔案存在")
        
        # 檢查環境變數
        from dotenv import load_dotenv
        load_dotenv()
        
        cwa_key = os.getenv('CWA_API_KEY')
        discord_token = os.getenv('DISCORD_TOKEN')
        
        if cwa_key:
            print(f"✅ CWA_API_KEY 已設定: {cwa_key[:15]}...")
        else:
            print("❌ CWA_API_KEY 未設定")
        
        if discord_token:
            print(f"✅ DISCORD_TOKEN 已設定: {discord_token[:15]}...")
        else:
            print("❌ DISCORD_TOKEN 未設定")
    else:
        print("❌ .env 檔案不存在")

if __name__ == "__main__":
    print("🤖 Discord 氣象機器人 - CWA API 設定工具")
    print("=" * 60)
    
    # 檢查當前設定
    check_current_setup()
    print()
    
    # 詢問是否要設定
    if input("是否要設定 CWA API 密鑰？(Y/n): ").lower() not in ['n', 'no']:
        success = setup_cwa_api_key()
        if success:
            print("\n✅ 設定完成！您現在可以重新啟動機器人了。")
        else:
            print("\n❌ 設定失敗，請檢查錯誤訊息並重試。")
    else:
        print("⏩ 跳過設定")
