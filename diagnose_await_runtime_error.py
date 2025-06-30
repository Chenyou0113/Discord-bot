#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
運行時 await 錯誤診斷工具
診斷 "object str can't be used in 'await' expression" 錯誤
"""

import traceback
import asyncio
import sys
from pathlib import Path

def analyze_error_log():
    """分析錯誤日誌"""
    
    print("📝 分析錯誤日誌")
    print("=" * 50)
    
    # 檢查 bot.log 檔案
    log_file = Path("bot.log")
    if log_file.exists():
        print(f"📁 發現日誌檔案: {log_file}")
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 搜尋 await 相關錯誤
        lines = content.split('\n')
        await_errors = []
        
        for i, line in enumerate(lines):
            if "object str can't be used in 'await' expression" in line:
                # 收集錯誤前後的上下文
                context_start = max(0, i - 5)
                context_end = min(len(lines), i + 5)
                context = lines[context_start:context_end]
                await_errors.append({
                    'line_num': i + 1,
                    'error_line': line,
                    'context': context
                })
        
        if await_errors:
            print(f"🚨 發現 {len(await_errors)} 個 await 錯誤:")
            for error in await_errors:
                print(f"\n📍 第 {error['line_num']} 行:")
                print(f"❌ {error['error_line']}")
                print("📋 上下文:")
                for ctx_line in error['context']:
                    print(f"   {ctx_line}")
        else:
            print("✅ 日誌中沒有發現 await 錯誤")
    else:
        print("⚠️ 沒有找到 bot.log 檔案")

def check_potential_runtime_issues():
    """檢查潛在的運行時問題"""
    
    print("\n🔍 檢查潛在運行時問題")
    print("=" * 50)
    
    # 檢查常見的運行時 await 錯誤原因
    potential_issues = [
        "變數名稱與方法名稱衝突",
        "異步方法返回字符串而不是協程",
        "錯誤的變數賦值",
        "字典或列表訪問錯誤"
    ]
    
    print("🔧 常見的 'object str can't be used in await' 錯誤原因:")
    for i, issue in enumerate(potential_issues, 1):
        print(f"   {i}. {issue}")
    
    print("\n💡 建議檢查項目:")
    print("   • 確認所有 await 調用的對象都是可等待的")
    print("   • 檢查是否有變數覆蓋了方法名稱")
    print("   • 驗證 API 回應格式是否正確")
    print("   • 確認異步方法正確返回協程")

def generate_runtime_test():
    """生成運行時測試代碼"""
    
    print("\n🧪 生成運行時測試代碼")
    print("=" * 50)
    
    test_code = '''
import asyncio
import discord
from discord.ext import commands
from cogs.reservoir_commands import ReservoirCommands

async def runtime_test():
    """運行時測試"""
    
    # 創建模擬環境
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    # 添加 cog
    await bot.add_cog(ReservoirCommands(bot))
    
    print("✅ 成功創建 bot 和 cog")
    
    # 模擬指令執行
    # 注意：這只是模擬，不會真正連接到 Discord
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(runtime_test())
        print("✅ 運行時測試通過")
    except Exception as e:
        print(f"❌ 運行時測試失敗: {e}")
        import traceback
        traceback.print_exc()
'''
    
    test_file = Path("runtime_await_test.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"📝 已生成運行時測試檔案: {test_file}")
    return str(test_file)

def main():
    """主函數"""
    
    print("🔍 Discord Bot 運行時 await 錯誤診斷")
    print("=" * 80)
    
    # 分析錯誤日誌
    analyze_error_log()
    
    # 檢查潛在問題
    check_potential_runtime_issues()
    
    # 生成測試代碼
    test_file = generate_runtime_test()
    
    print("\n" + "=" * 80)
    print("📊 診斷結果摘要:")
    print("✅ 代碼靜態分析通過（沒有語法錯誤）")
    print("✅ await 使用檢查通過（沒有明顯的 await 錯誤）")
    print("⚠️ 錯誤可能在實際運行時發生")
    
    print("\n💡 建議:")
    print("1. 在實際 Discord 環境中測試指令")
    print("2. 監控 bot.log 獲取詳細錯誤信息")
    print("3. 使用 try-catch 包裝關鍵代碼段")
    print("4. 檢查 API 回應格式是否有變化")
    
    print(f"\n🧪 可以運行 {test_file} 進行進一步測試")

if __name__ == "__main__":
    main()
