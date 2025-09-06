# 此腳本只檢查語法，不執行任何代碼
import py_compile
import sys
import os

# 要檢查的文件
file_to_check = os.path.join('cogs', 'admin_commands_fixed.py')

# 顯示文件是否存在
print(f"檢查文件 {file_to_check} 是否存在...")
if os.path.exists(file_to_check):
    print(f"✓ 文件存在")
    
    # 檢查文件大小
    size = os.path.getsize(file_to_check)
    print(f"文件大小: {size} 字節")
    
    # 檢查語法
    print("檢查語法...")
    try:
        py_compile.compile(file_to_check, doraise=True)
        print("✓ 語法正確")
    except py_compile.PyCompileError as e:
        print(f"✗ 語法錯誤: {str(e)}")
        sys.exit(1)
        
    # 讀取並顯示前幾行和最後幾行
    try:
        with open(file_to_check, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if lines:
            print(f"\n前10行:")
            for i, line in enumerate(lines[:10]):
                print(f"{i+1}: {line.rstrip()}")
                
            print(f"\n最後10行:")
            for i, line in enumerate(lines[-10:]):
                print(f"{len(lines) - 10 + i + 1}: {line.rstrip()}")
                
            print("\n檢查重要功能:")
            # 檢查是否有setup函數
            setup_found = False
            for i, line in enumerate(lines):
                if line.strip().startswith("async def setup(") or line.strip().startswith("def setup("):
                    setup_found = True
                    print(f"✓ 在第 {i+1} 行找到setup函數: {line.strip()}")
                    
                    # 查找setup函數後幾行的內容
                    for j in range(i+1, min(i+5, len(lines))):
                        print(f"  {j+1}: {lines[j].strip()}")
                    break
            
            if not setup_found:
                print("✗ 沒有找到setup函數!")
                    
            # 檢查是否有AdminCommands類
            admin_class_found = False
            for i, line in enumerate(lines):
                if "class AdminCommands" in line:
                    admin_class_found = True
                    print(f"✓ 在第 {i+1} 行找到AdminCommands類: {line.strip()}")
                    break
                    
            if not admin_class_found:
                print("✗ 沒有找到AdminCommands類!")
    except Exception as e:
        print(f"讀取文件時出錯: {str(e)}")
else:
    print(f"✗ 文件不存在!")
    sys.exit(1)
