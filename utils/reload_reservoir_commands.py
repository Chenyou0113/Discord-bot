#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動重新載入 reservoir_commands cog
用於修復 reservoir_commands 沒有載入的問題
"""

import asyncio
import importlib
import sys
import os
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def reload_reservoir_commands():
    """重新載入 reservoir_commands cog"""
    print("=" * 60)
    print("手動重新載入 reservoir_commands cog")
    print("=" * 60)
    
    try:
        # 檢查檔案是否存在
        cog_file = os.path.join(os.path.dirname(__file__), 'cogs', 'reservoir_commands.py')
        print(f"檢查檔案: {cog_file}")
        
        if not os.path.exists(cog_file):
            print("❌ reservoir_commands.py 檔案不存在!")
            return
        
        print("✅ reservoir_commands.py 檔案存在")
        
        # 嘗試載入模組
        print("\n正在測試載入 reservoir_commands 模組...")
        try:
            # 如果模組已經載入，先卸載
            if 'cogs.reservoir_commands' in sys.modules:
                print("移除舊的模組引用...")
                del sys.modules['cogs.reservoir_commands']
            
            # 重新載入模組
            from cogs import reservoir_commands
            importlib.reload(reservoir_commands)
            
            print("✅ 模組載入成功")
            
            # 檢查模組內容
            print("\n檢查模組內容:")
            print(f"  - 模組路徑: {reservoir_commands.__file__}")
            
            # 檢查是否有 setup 函數
            if hasattr(reservoir_commands, 'setup'):
                print("  - ✅ 找到 setup 函數")
            else:
                print("  - ❌ 沒有找到 setup 函數")
            
            # 檢查 ReservoirCommands 類別
            if hasattr(reservoir_commands, 'ReservoirCommands'):
                print("  - ✅ 找到 ReservoirCommands 類別")
                
                # 檢查指令
                reservoir_class = reservoir_commands.ReservoirCommands
                commands = []
                
                for attr_name in dir(reservoir_class):
                    attr = getattr(reservoir_class, attr_name)
                    if hasattr(attr, '__wrapped__') and hasattr(attr, 'name'):
                        commands.append(attr.name)
                
                print(f"  - 找到 {len(commands)} 個指令: {', '.join(commands)}")
                
            else:
                print("  - ❌ 沒有找到 ReservoirCommands 類別")
            
            print("\n✅ reservoir_commands 模組測試完成")
            
        except Exception as e:
            print(f"❌ 模組載入失敗: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        # 現在嘗試手動執行 setup 函數（模擬 bot 載入過程）
        print("\n" + "=" * 40)
        print("模擬 bot 載入過程...")
        print("=" * 40)
        
        # 創建模擬 bot 物件
        class MockBot:
            def __init__(self):
                self.cogs = {}
                self.tree = MockCommandTree()
            
            async def add_cog(self, cog):
                self.cogs[cog.__class__.__name__] = cog
                print(f"✅ 已添加 cog: {cog.__class__.__name__}")
                
                # 檢查 cog 的指令
                commands = []
                for attr_name in dir(cog):
                    attr = getattr(cog, attr_name)
                    if hasattr(attr, '__wrapped__') and hasattr(attr, 'name'):
                        commands.append(attr.name)
                
                if commands:
                    print(f"  - 指令: {', '.join(commands)}")
                else:
                    print("  - 沒有找到指令")
        
        class MockCommandTree:
            def __init__(self):
                self.commands = []
            
            def add_command(self, command):
                self.commands.append(command)
                print(f"  - 添加指令到樹: {command.name if hasattr(command, 'name') else str(command)}")
        
        # 創建模擬 bot
        mock_bot = MockBot()
        
        try:
            # 執行 setup 函數
            await reservoir_commands.setup(mock_bot)
            
            print(f"✅ setup 函數執行完成")
            print(f"  - 已載入的 cogs: {list(mock_bot.cogs.keys())}")
            
        except Exception as e:
            print(f"❌ setup 函數執行失敗: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("測試完成")
        print("=" * 60)
        
        # 提供解決方案
        print("\n解決方案建議:")
        print("1. 如果測試通過，問題可能是機器人沒有正確載入 cog")
        print("2. 請檢查 bot.py 中的 cog 載入列表")
        print("3. 重新啟動機器人")
        print("4. 檢查機器人日誌中的錯誤訊息")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(reload_reservoir_commands())
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
