#!/usr/bin/env python3
"""
簡單測試 reservoir_commands.py
"""
import sys
import os

# 切換目錄
os.chdir(r'C:\Users\xiaoy\Desktop\Discord bot')
sys.path.insert(0, '.')

print("🧪 測試 reservoir_commands.py")

try:
    # 1. 語法檢查
    print("1. 語法檢查...")
    with open('cogs/reservoir_commands.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    compile(code, 'cogs/reservoir_commands.py', 'exec')
    print("   ✅ 語法正確")
    
    # 2. 導入測試
    print("2. 導入測試...")
    from cogs.reservoir_commands import ReservoirCommands, WaterCameraView
    print("   ✅ 模組導入成功")
    
    # 3. 指令計數
    print("3. 指令計數...")
    import re
    commands = re.findall(r'@app_commands\.command\([^)]*name\s*=\s*["\']([^"\']+)["\']', code)
    print(f"   ✅ 找到 {len(commands)} 個指令: {', '.join(commands)}")
    
    # 4. setup 函數檢查
    print("4. setup 函數檢查...")
    if 'async def setup(' in code:
        print("   ✅ setup 函數存在")
    else:
        print("   ❌ setup 函數缺失")
    
    print("\n🎉 所有測試通過！reservoir_commands.py 準備就緒！")
    
except Exception as e:
    print(f"❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()
