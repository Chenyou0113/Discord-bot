#!/usr/bin/env python3
"""
安全性檢查工具
檢查專案中是否有硬編碼的 API 密鑰或敏感資訊
"""

import os
import re
import sys
from pathlib import Path

def scan_for_hardcoded_secrets():
    """掃描專案中的硬編碼密鑰"""
    print("🔒 安全性檢查工具")
    print("=" * 50)
    
    # 定義要檢查的模式
    patterns = [
        (r'CWA-[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}', 'CWA API 密鑰'),
        (r'AIza[0-9A-Za-z_-]{35}', 'Google API 密鑰'),
        (r'[Bb]ot\s+[A-Za-z0-9_-]{59}\.[A-Za-z0-9_-]{1,}\.[A-Za-z0-9_-]{27,}', 'Discord Bot Token'),
        (r'authorization\s*=\s*["\']CWA-[^"\']+["\']', 'CWA 授權字串'),
        (r'api_key\s*=\s*["\']CWA-[^"\']+["\']', 'CWA API 密鑰變數'),
        (r'client_id\s*=\s*["\'][a-z0-9-]+["\']', 'TDX Client ID'),
        (r'client_secret\s*=\s*["\'][a-f0-9-]{36}["\']', 'TDX Client Secret'),
        (r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'UUID 格式密鑰'),
        (r'xiaoyouwu5-[a-f0-9-]+', '特定 TDX Client ID'),
        (r'94650864-6a80-4c58-83ce-fd13e7ef0504', '特定 AQI API 密鑰'),
    ]
    
    # 要檢查的檔案類型
    file_extensions = ['.py', '.txt', '.md', '.json', '.yml', '.yaml']
    
    # 要忽略的目錄
    ignore_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.env'}
    
    findings = []
    
    # 遍歷專案目錄
    for root, dirs, files in os.walk('.'):
        # 移除要忽略的目錄
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # 檢查檔案擴展名
            if not any(file.endswith(ext) for ext in file_extensions):
                continue
            
            # 跳過 .env 檔案（預期包含密鑰）
            if file in ['.env', '.env.local', '.env.production']:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 檢查每個模式
                for pattern, description in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        findings.append({
                            'file': file_path,
                            'line': line_num,
                            'type': description,
                            'match': match.group()[:50] + '...' if len(match.group()) > 50 else match.group()
                        })
            
            except Exception as e:
                print(f"⚠️  無法讀取檔案 {file_path}: {e}")
    
    # 報告結果
    if findings:
        print(f"❌ 發現 {len(findings)} 個可能的安全性問題:")
        print()
        
        for finding in findings:
            print(f"📁 檔案: {finding['file']}")
            print(f"📍 行號: {finding['line']}")
            print(f"🔑 類型: {finding['type']}")
            print(f"💡 內容: {finding['match']}")
            print("-" * 50)
        
        print("\n⚠️  建議:")
        print("1. 將所有密鑰移動到 .env 檔案中")
        print("2. 使用環境變數讀取密鑰: os.getenv('API_KEY')")
        print("3. 確保 .env 檔案在 .gitignore 中")
        print("4. 絕不將密鑰提交到版本控制系統")
        
        return False
    else:
        print("✅ 未發現硬編碼的敏感資訊")
        print("🎉 安全性檢查通過！")
        return True

def check_env_file_security():
    """檢查 .env 檔案的安全性設定"""
    print("\n🔍 .env 檔案安全性檢查")
    print("-" * 30)
    
    # 檢查 .env 檔案是否存在
    if os.path.exists('.env'):
        print("✅ .env 檔案存在")
        
        # 檢查 .gitignore 是否包含 .env
        gitignore_path = '.gitignore'
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            if '.env' in gitignore_content:
                print("✅ .env 檔案已在 .gitignore 中")
            else:
                print("❌ .env 檔案未在 .gitignore 中")
                print("   建議: 在 .gitignore 中加入 '.env'")
        else:
            print("⚠️  .gitignore 檔案不存在")
            print("   建議: 創建 .gitignore 檔案並加入 '.env'")
        
        # 檢查檔案權限 (Unix/Linux 系統)
        if os.name != 'nt':  # 非 Windows 系統
            stat_info = os.stat('.env')
            permissions = oct(stat_info.st_mode)[-3:]
            if permissions == '600':
                print("✅ .env 檔案權限設定正確 (600)")
            else:
                print(f"⚠️  .env 檔案權限: {permissions}")
                print("   建議: 執行 'chmod 600 .env' 限制檔案權限")
    else:
        print("❌ .env 檔案不存在")
        print("   請複製 .env.example 並設定您的密鑰")

def check_required_env_vars():
    """檢查必要的環境變數"""
    print("\n🔧 環境變數檢查")
    print("-" * 20)
    
    required_vars = ['DISCORD_TOKEN', 'CWA_API_KEY', 'TDX_CLIENT_ID', 'TDX_CLIENT_SECRET']
    optional_vars = ['GOOGLE_API_KEY', 'AQI_API_KEY']
    
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        
        missing_required = []
        for var in required_vars:
            value = os.getenv(var)
            if value and value != f'your_{var.lower()}_here':
                print(f"✅ {var}: 已設定")
            else:
                print(f"❌ {var}: 未設定或使用預設值")
                missing_required.append(var)
        
        for var in optional_vars:
            value = os.getenv(var)
            if value and value != f'your_{var.lower()}_here':
                print(f"✅ {var}: 已設定 (可選)")
            else:
                print(f"⚪ {var}: 未設定 (可選)")
        
        if missing_required:
            print(f"\n❌ 缺少必要的環境變數: {', '.join(missing_required)}")
            print("💡 執行 'python setup_all_apis.py' 來設定所有必要的 API 密鑰")
            return False
        else:
            print("\n✅ 所有必要的環境變數已設定")
            return True
    else:
        print("❌ .env 檔案不存在，無法檢查環境變數")
        return False

if __name__ == "__main__":
    print("🛡️  Discord 氣象機器人 - 安全性檢查工具")
    print("=" * 60)
    
    # 執行各項檢查
    secrets_ok = scan_for_hardcoded_secrets()
    check_env_file_security()
    env_vars_ok = check_required_env_vars()
    
    print("\n" + "=" * 60)
    if secrets_ok and env_vars_ok:
        print("🎉 所有安全性檢查通過！")
        sys.exit(0)
    else:
        print("⚠️  發現安全性問題，請檢查上述建議")
        sys.exit(1)
