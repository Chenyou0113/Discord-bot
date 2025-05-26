#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 用於驗證 info_commands_fixed_v4.py 模組
# 檔案路徑：C:\Users\xiaoy\Desktop\Discord bot\verify_info_module.py

import sys
import traceback

print("Python 版本:", sys.version)
print("測試匯入 info_commands_fixed_v4 模組...\n")

try:
    from cogs import info_commands_fixed_v4
    print("✅ 成功匯入 info_commands_fixed_v4 模組")
    # 嘗試訪問一些重要的類或方法來確認模組完整性
    if hasattr(info_commands_fixed_v4, 'InfoCommands'):
        print("✅ 模組包含 InfoCommands 類")
    else:
        print("❌ 模組缺少 InfoCommands 類")
        
    if hasattr(info_commands_fixed_v4, 'WeatherView'):
        print("✅ 模組包含 WeatherView 類")
    else:
        print("❌ 模組缺少 WeatherView 類")
        
    # 檢查天氣表情符號字典
    if hasattr(info_commands_fixed_v4, 'WEATHER_EMOJI'):
        print(f"✅ 模組包含 WEATHER_EMOJI 字典 (含 {len(info_commands_fixed_v4.WEATHER_EMOJI)} 個項目)")
    else:
        print("❌ 模組缺少 WEATHER_EMOJI 字典")
        
    print("\n模組基本結構檢查完成！")
    
except Exception as e:
    print(f"❌ 匯入模組時發生錯誤: {str(e)}")
    print("\n詳細錯誤信息:")
    traceback.print_exc()
    
print("\n驗證完成")
