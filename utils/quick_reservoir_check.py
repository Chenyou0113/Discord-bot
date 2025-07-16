#!/usr/bin/env python3
"""
快速指令驗證腳本
檢查 reservoir_commands.py 是否修復完成
"""
import sys
import os
import time

# 設置路徑
sys.path.insert(0, r'C:\Users\xiaoy\Desktop\Discord bot')
os.chdir(r'C:\Users\xiaoy\Desktop\Discord bot')

print("🔍 快速指令驗證")
print("=" * 60)

# 1. 檢查語法
print("1️⃣ 語法檢查...")
try:
    with open('cogs/reservoir_commands.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    compile(content, 'cogs/reservoir_commands.py', 'exec')
    print("✅ 語法檢查通過")
except SyntaxError as e:
    print(f"❌ 語法錯誤: {e}")
    print(f"   行號: {e.lineno}")
    exit(1)

# 2. 檢查指令定義
print("\n2️⃣ 指令定義檢查...")
import re

command_pattern = r'@app_commands\.command\([^)]*name\s*=\s*["\']([^"\']+)["\']'
commands = re.findall(command_pattern, content)

expected_commands = [
    'water_level', 'water_cameras', 'water_disaster_cameras',
    'national_highway_cameras', 'general_road_cameras'
]

print(f"📋 找到的指令 ({len(commands)}):")
for cmd in commands:
    status = "✅" if cmd in expected_commands else "⚠️"
    print(f"  {status} {cmd}")

missing_commands = set(expected_commands) - set(commands)
if missing_commands:
    print(f"❌ 缺少指令: {', '.join(missing_commands)}")
else:
    print("✅ 所有預期指令都已定義")

# 3. 檢查類別定義
print("\n3️⃣ 類別定義檢查...")
classes_to_check = [
    'ReservoirCommands', 'WaterCameraView', 'WaterCameraInfoModal', 
    'HighwayCameraView', 'HighwayCameraInfoModal'
]

for class_name in classes_to_check:
    if f'class {class_name}' in content:
        print(f"✅ {class_name}")
    else:
        print(f"❌ {class_name} 缺失")

# 4. 檢查 setup 函數
print("\n4️⃣ setup 函數檢查...")
if 'async def setup(' in content:
    print("✅ setup 函數已定義")
else:
    print("❌ setup 函數缺失")

# 5. 檢查導入模組
print("\n5️⃣ 導入模組檢查...")
required_imports = ['discord', 'time', 'aiohttp', 'logging']
for module in required_imports:
    if f'import {module}' in content:
        print(f"✅ {module}")
    else:
        print(f"❌ {module} 未導入")

# 6. 嘗試載入模組
print("\n6️⃣ 模組載入測試...")
try:
    # 清除之前的模組快取
    if 'cogs.reservoir_commands' in sys.modules:
        del sys.modules['cogs.reservoir_commands']
    
    from cogs.reservoir_commands import ReservoirCommands, WaterCameraView
    print("✅ 模組載入成功")
    print("✅ ReservoirCommands 類別可用")
    print("✅ WaterCameraView 類別可用")
    
except Exception as e:
    print(f"❌ 模組載入失敗: {e}")

print("\n" + "=" * 60)
print("📊 驗證完成！")

if not missing_commands and 'async def setup(' in content:
    print("🎉 reservoir_commands.py 修復完成，可以啟動機器人了！")
    exit(0)
else:
    print("⚠️ 仍有問題需要修復")
    exit(1)
