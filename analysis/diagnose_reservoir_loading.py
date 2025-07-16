#!/usr/bin/env python3
"""
診斷 reservoir_commands 載入問題
"""
import sys
import os
import importlib

# 切換到機器人目錄
os.chdir(r'C:\Users\xiaoy\Desktop\Discord bot')
sys.path.insert(0, '.')

print("🔍 診斷 reservoir_commands cog 載入問題")
print("=" * 60)

# 1. 檢查文件是否存在
print("1️⃣ 檢查文件存在性...")
reservoir_file = 'cogs/reservoir_commands.py'
if os.path.exists(reservoir_file):
    print(f"✅ {reservoir_file} 存在")
    size = os.path.getsize(reservoir_file)
    print(f"   文件大小: {size:,} bytes")
else:
    print(f"❌ {reservoir_file} 不存在")
    exit(1)

# 2. 語法檢查
print("\n2️⃣ 語法檢查...")
try:
    with open(reservoir_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    compile(content, reservoir_file, 'exec')
    print("✅ 語法檢查通過")
except SyntaxError as e:
    print(f"❌ 語法錯誤: {e}")
    print(f"   行號: {e.lineno}")
    print(f"   偏移: {e.offset}")
    exit(1)

# 3. 模組導入測試
print("\n3️⃣ 模組導入測試...")
try:
    # 清除模組快取
    module_name = 'cogs.reservoir_commands'
    if module_name in sys.modules:
        del sys.modules[module_name]
    
    # 嘗試導入
    from cogs.reservoir_commands import ReservoirCommands
    print("✅ 成功導入 ReservoirCommands")
    
    # 檢查是否有 setup 函數
    if hasattr(sys.modules[module_name], 'setup'):
        print("✅ setup 函數存在")
    else:
        print("❌ setup 函數不存在")
    
except Exception as e:
    print(f"❌ 模組導入失敗: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 4. 檢查指令數量
print("\n4️⃣ 檢查指令數量...")
import re
commands = re.findall(r'@app_commands\.command\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
print(f"✅ 找到 {len(commands)} 個指令:")
for cmd in commands:
    print(f"  - {cmd}")

# 5. 檢查類別定義
print("\n5️⃣ 檢查類別定義...")
classes = re.findall(r'class\s+(\w+)', content)
print(f"✅ 找到 {len(classes)} 個類別:")
for cls in classes:
    print(f"  - {cls}")

# 6. 檢查機器人是否正在運行
print("\n6️⃣ 檢查機器人運行狀態...")
try:
    import psutil
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = proc.info['cmdline']
                if cmdline and any('bot.py' in arg for arg in cmdline):
                    python_processes.append(proc.info['pid'])
        except:
            pass
    
    if python_processes:
        print(f"✅ 找到 {len(python_processes)} 個機器人進程: {python_processes}")
    else:
        print("⚠️ 沒有找到機器人進程")
        
except ImportError:
    print("⚠️ 無法檢查進程狀態（需要 psutil）")

# 7. 檢查日誌文件
print("\n7️⃣ 檢查日誌文件...")
if os.path.exists('bot.log'):
    print("✅ bot.log 存在")
    
    # 讀取最後50行
    with open('bot.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if lines:
        print(f"   總行數: {len(lines)}")
        print("   最近的載入相關日誌:")
        
        recent_lines = lines[-50:]
        reservoir_lines = [line.strip() for line in recent_lines 
                          if 'reservoir' in line.lower() or 'cog' in line.lower()]
        
        if reservoir_lines:
            for line in reservoir_lines[-10:]:  # 最後10行相關日誌
                print(f"   📝 {line}")
        else:
            print("   ⚠️ 沒有找到 reservoir 相關日誌")
    else:
        print("   ⚠️ 日誌文件為空")
else:
    print("❌ bot.log 不存在")

# 8. 建議修復方案
print("\n8️⃣ 建議修復方案...")
print("如果 reservoir_commands 沒有載入，請嘗試:")
print("1. 重新啟動機器人: python bot.py")
print("2. 檢查 bot.log 中的載入錯誤訊息")
print("3. 確認所有依賴模組已安裝")
print("4. 如果仍有問題，嘗試手動重新載入 cog")

print("\n" + "=" * 60)
print("🎯 診斷完成！")
