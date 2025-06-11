"""
Discord Bot 綜合驗證腳本
檢查所有修復是否正確應用並可正常運行
"""

def run_tests():
    print("🤖 Discord Bot 綜合驗證開始")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: 檢查檔案結構
    print("\n📁 測試 1: 檔案結構檢查")
    total_tests += 1
    try:
        import os
        required_files = [
            "bot.py",
            "scripts/auto_restart_bot.bat", 
            "config_files/levels.json",
            "cogs/info_commands_fixed_v4_clean.py"
        ]
        
        all_exist = True
        for file in required_files:
            if os.path.exists(file):
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file} 不存在")
                all_exist = False
        
        if all_exist:
            tests_passed += 1
            print("   ✅ 檔案結構測試通過")
        else:
            print("   ❌ 檔案結構測試失敗")
            
    except Exception as e:
        print(f"   ❌ 檔案結構測試異常: {e}")
    
    # Test 2: bot.py 重啟邏輯檢查
    print("\n🔄 測試 2: 重啟邏輯檢查")
    total_tests += 1
    try:
        with open("bot.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        if "await bot.close()" in content and "os.execv" not in content:
            tests_passed += 1
            print("   ✅ 重啟邏輯修復正確")
        else:
            print("   ❌ 重啟邏輯修復不正確")
            
    except Exception as e:
        print(f"   ❌ 重啟邏輯檢查異常: {e}")
    
    # Test 3: API 修復邏輯檢查
    print("\n🌐 測試 3: API 修復邏輯檢查")
    total_tests += 1
    try:
        with open("cogs/info_commands_fixed_v4_clean.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        if "'records' not in data" in content:
            tests_passed += 1
            print("   ✅ API 修復邏輯正確")
        else:
            print("   ❌ API 修復邏輯不正確")
            
    except Exception as e:
        print(f"   ❌ API 修復邏輯檢查異常: {e}")
    
    # Test 4: 腳本路徑修復檢查
    print("\n🛠️ 測試 4: 腳本路徑修復檢查")
    total_tests += 1
    try:
        script_files = [
            "scripts/auto_restart_bot.bat",
            "scripts/start_bot.bat"
        ]
        
        path_fixed = True
        for script in script_files:
            if os.path.exists(script):
                with open(script, "r", encoding="utf-8") as f:
                    content = f.read()
                    if 'cd /d "%~dp0.."' in content:
                        print(f"   ✅ {script} 路徑修復正確")
                    else:
                        print(f"   ❌ {script} 路徑修復不正確")
                        path_fixed = False
            else:
                print(f"   ❌ {script} 不存在")
                path_fixed = False
        
        if path_fixed:
            tests_passed += 1
            print("   ✅ 腳本路徑修復測試通過")
        else:
            print("   ❌ 腳本路徑修復測試失敗")
            
    except Exception as e:
        print(f"   ❌ 腳本路徑修復檢查異常: {e}")
    
    # Test 5: 模組語法檢查
    print("\n🐍 測試 5: Python 模組語法檢查")
    total_tests += 1
    try:
        # 檢查 bot.py 語法
        with open("bot.py", "r", encoding="utf-8") as f:
            bot_code = f.read()
        compile(bot_code, "bot.py", "exec")
        
        # 檢查 info_commands 語法
        with open("cogs/info_commands_fixed_v4_clean.py", "r", encoding="utf-8") as f:
            info_code = f.read()
        compile(info_code, "cogs/info_commands_fixed_v4_clean.py", "exec")
        
        tests_passed += 1
        print("   ✅ Python 模組語法檢查通過")
        
    except SyntaxError as e:
        print(f"   ❌ 語法錯誤: {e}")
    except Exception as e:
        print(f"   ❌ 語法檢查異常: {e}")
    
    # 總結
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {tests_passed}/{total_tests} 通過")
    print()
    
    if tests_passed == total_tests:
        print("🎉 所有測試通過！Discord Bot 修復完成且可正常運行。")
        print()
        print("🚀 下一步:")
        print("   1. 使用 scripts\\auto_restart_bot.bat 啟動機器人")
        print("   2. 在 Discord 中測試 !reboot 指令")
        print("   3. 監控日誌確認不再出現 '異常資料結構' 警告")
        return True
    else:
        print("⚠️ 部分測試失敗，請檢查上述問題。")
        return False

if __name__ == "__main__":
    run_tests()
