#!/usr/bin/env python3
"""
重新啟動機器人並檢查指令同步
"""
import os
import sys
import asyncio
import subprocess
import time
from datetime import datetime

def kill_existing_bots():
    """停止現有的機器人進程"""
    try:
        # Windows: 停止所有 python.exe 進程
        result = subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                              capture_output=True, text=True)
        print(f"🛑 停止現有 Python 進程: {result.returncode}")
        time.sleep(2)
    except Exception as e:
        print(f"停止進程時發生錯誤: {e}")

def start_bot_and_monitor():
    """啟動機器人並監控日誌"""
    try:
        print("🚀 啟動機器人...")
        
        # 切換到機器人目錄
        os.chdir(r'C:\Users\xiaoy\Desktop\Discord bot')
        
        # 清空日誌文件
        try:
            with open('bot.log', 'w', encoding='utf-8') as f:
                f.write(f"=== 機器人重新啟動 {datetime.now()} ===\n")
        except:
            pass
        
        # 啟動機器人（後台進程）
        process = subprocess.Popen([
            sys.executable, 'bot.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        
        print(f"📝 機器人進程 ID: {process.pid}")
        
        # 等待機器人啟動
        print("⏳ 等待機器人初始化...")
        time.sleep(10)
        
        # 檢查進程是否還在運行
        if process.poll() is None:
            print("✅ 機器人進程正在運行")
        else:
            print("❌ 機器人進程已停止")
            stdout, stderr = process.communicate()
            print(f"標準輸出: {stdout}")
            print(f"錯誤輸出: {stderr}")
            return False
        
        # 監控日誌
        print("📊 監控啟動日誌...")
        monitor_startup_logs()
        
        return True
        
    except Exception as e:
        print(f"❌ 啟動機器人時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def monitor_startup_logs():
    """監控啟動日誌"""
    try:
        # 等待日誌寫入
        time.sleep(5)
        
        with open('bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找關鍵信息
        print("\n📋 啟動日誌摘要:")
        relevant_lines = []
        
        for line in lines[-100:]:  # 最後100行
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                '成功啟動', '已成功上線', '載入', 'cog', '同步', 'sync', 
                '指令', 'command', 'reservoir', '錯誤', 'error'
            ]):
                relevant_lines.append(line)
        
        if relevant_lines:
            for line in relevant_lines[-20:]:  # 最後20行相關信息
                print(f"  {line}")
        else:
            print("  ⚠️ 沒有找到相關日誌信息")
            # 顯示最後幾行
            print("  最後幾行日誌:")
            for line in lines[-10:]:
                print(f"    {line.strip()}")
    
    except Exception as e:
        print(f"❌ 讀取日誌時發生錯誤: {e}")

def main():
    """主函數"""
    print("🔧 Discord 機器人重啟與指令同步檢查")
    print("=" * 60)
    
    # 1. 停止現有機器人
    print("1️⃣ 停止現有機器人...")
    kill_existing_bots()
    
    # 2. 檢查 reservoir_commands.py
    print("\n2️⃣ 檢查 reservoir_commands.py...")
    try:
        with open('cogs/reservoir_commands.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'async def setup(' in content:
            print("   ✅ setup 函數存在")
        else:
            print("   ❌ setup 函數缺失")
            return
        
        # 檢查指令數量
        import re
        commands = re.findall(r'@app_commands\.command\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
        print(f"   ✅ 找到 {len(commands)} 個指令")
        
    except Exception as e:
        print(f"   ❌ 檢查失敗: {e}")
        return
    
    # 3. 啟動機器人
    print("\n3️⃣ 啟動機器人...")
    success = start_bot_and_monitor()
    
    if success:
        print("\n✅ 機器人已重新啟動！")
        print("💡 請到 Discord 檢查 slash 指令是否已更新")
        print("💡 如需檢查詳細日誌，請執行: Get-Content bot.log -Tail 50")
    else:
        print("\n❌ 機器人啟動失敗，請檢查錯誤信息")

if __name__ == "__main__":
    main()
