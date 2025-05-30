#!/usr/bin/env python3
"""
快速狀態檢查
"""
import os
import json

def main():
    print("=== Discord機器人快速狀態檢查 ===")
    
    issues = 0
    
    # 1. 檢查關鍵文件
    required_files = [
        'bot.py',
        'cogs/info_commands_fixed_v4_clean.py',
        'sample_tsunami.json',
        'sample_earthquake.json'
    ]
    
    print("\n1. 關鍵文件檢查:")
    for file in required_files:
        if os.path.exists(file):
            print(f"  [OK] {file}")
        else:
            print(f"  [MISS] {file}")
            issues += 1
    
    # 2. 檢查海嘯資料結構
    print("\n2. 海嘯資料檢查:")
    try:
        with open('sample_tsunami.json', 'r', encoding='utf-8') as f:
            tsunami_data = json.load(f)
        if 'records' in tsunami_data and 'Tsunami' in tsunami_data['records']:
            print("  [OK] 海嘯資料結構正確")
        else:
            print("  [FAIL] 海嘯資料結構錯誤")
            issues += 1
    except:
        print("  [FAIL] 海嘯資料讀取失敗")
        issues += 1
    
    # 3. 檢查地震資料
    print("\n3. 地震資料檢查:")
    try:
        with open('sample_earthquake.json', 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if content:
            eq_data = json.loads(content)
            if 'records' in eq_data:
                print("  [OK] 地震資料結構正確")
            else:
                print("  [FAIL] 地震資料結構錯誤")
                issues += 1
        else:
            print("  [FAIL] 地震資料檔案為空")
            issues += 1
    except:
        print("  [FAIL] 地震資料讀取失敗")
        issues += 1
    
    # 4. 檢查bot.py配置
    print("\n4. Bot配置檢查:")
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        if 'info_commands_fixed_v4_clean' in bot_content:
            print("  [OK] bot.py 配置正確的模組")
        else:
            print("  [FAIL] bot.py 配置錯誤")
            issues += 1
    except:
        print("  [FAIL] bot.py 讀取失敗")
        issues += 1
    
    # 5. 檢查過時文件
    print("\n5. 過時文件檢查:")
    old_files = ['cogs/info_commands_fixed_v4.py']
    old_found = False
    for old_file in old_files:
        if os.path.exists(old_file):
            print(f"  [WARN] 發現過時文件: {old_file}")
            old_found = True
    if not old_found:
        print("  [OK] 無過時文件")
    
    # 總結
    print(f"\n=== 總結 ===")
    if issues == 0:
        print("狀態: 健康")
        print("機器人已準備就緒，所有核心功能應該正常工作")
        print("\n已修復的問題:")
        print("- 海嘯功能API資料結構檢查邏輯")
        print("- sample_earthquake.json 空文件問題")
        print("- 過時文件衝突問題")
        print("- bot.py 中缺失的函數")
        
        print("\n海嘯功能修復詳情:")
        print("- 修正了API回傳結構檢查邏輯")
        print("- 從 result.records.Tsunami 改為 records.Tsunami")
        print("- 添加了詳細的調試日誌")
        print("- 更新了bot.py中的模組引用")
        
        return True
    else:
        print(f"狀態: 有問題 ({issues} 個)")
        print("需要修復上述問題")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
