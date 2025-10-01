#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修正捷運即時電子看板描述的腳本
只顯示實際有即時看板資料的3個系統
"""

import os
import re

def fix_metro_liveboard_descriptions():
    """修正捷運即時電子看板的系統描述"""
    
    file_path = 'cogs/info_commands_fixed_v4_clean.py'
    
    try:
        # 讀取檔案
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 原始的錯誤描述（包含所有9個系統）
        old_pattern = r'"🔵 \*\*臺北捷運\*\* - 文湖線、淡水信義線、板南線等\\n"\s*' \
                     r'"🟠 \*\*高雄捷運\*\* - 紅線、橘線\\n"\s*' \
                     r'"🟡 \*\*桃園捷運\*\* - 機場線、綠線\\n"[^"]*' \
                     r'"💚 \*\*安坑輕軌\*\* - 安坑線"'
        
        # 新的正確描述（只有3個有資料的系統）
        new_description = '''"🔵 **臺北捷運** - 文湖線、淡水信義線、板南線等\\n"
                      "🟠 **高雄捷運** - 紅線、橘線\\n"
                      "🟢 **高雄輕軌** - 環狀輕軌\\n\\n"
                      "ℹ️ **說明**：目前僅以上3個系統提供即時看板資料"'''
        
        # 執行替換
        if '桃園捷運' in content and '安坑輕軌' in content:
            # 手動定位和替換有問題的部分
            lines = content.split('\n')
            
            # 修正第一個位置 (metro_liveboard)
            for i, line in enumerate(lines):
                if '開始查詢捷運電子看板' in line:
                    # 找到這個指令的embed部分
                    j = i
                    while j < len(lines) and 'embed.add_field(' not in lines[j]:
                        j += 1
                    
                    if j < len(lines):
                        # 找到value開始的地方
                        while j < len(lines) and 'value="🔵' not in lines[j]:
                            j += 1
                        
                        if j < len(lines):
                            # 替換從這裡開始到inline=False的所有行
                            start_line = j
                            while j < len(lines) and 'inline=False' not in lines[j]:
                                j += 1
                            end_line = j
                            
                            # 重寫這個區域
                            new_lines = [
                                '                value="🔵 **臺北捷運** - 文湖線、淡水信義線、板南線等\\n"',
                                '                      "🟠 **高雄捷運** - 紅線、橘線\\n"',
                                '                      "🟢 **高雄輕軌** - 環狀輕軌",',
                                '                inline=False',
                                '            )',
                                '            embed.add_field(',
                                '                name="ℹ️ 說明",',
                                '                value="目前僅以上3個系統提供即時看板資料\\n其他捷運系統請使用新聞查詢功能",',
                                '                inline=False'
                            ]
                            
                            lines[start_line:end_line+1] = new_lines
                            break
            
            # 修正第二個位置 (metro_direction) 
            for i, line in enumerate(lines):
                if '開始查詢捷運方向電子看板' in line:
                    # 找到這個指令的embed部分
                    j = i
                    while j < len(lines) and '🚇 可用系統' not in lines[j]:
                        j += 1
                    
                    if j < len(lines):
                        j += 1  # 跳過name行
                        # 找到value開始的地方
                        while j < len(lines) and 'value="🔵' not in lines[j]:
                            j += 1
                        
                        if j < len(lines):
                            # 替換從這裡開始到inline=False的所有行
                            start_line = j
                            while j < len(lines) and 'inline=False' not in lines[j]:
                                j += 1
                            end_line = j
                            
                            # 重寫這個區域
                            new_lines = [
                                '                value="🔵 **臺北捷運** - 文湖線、淡水信義線、板南線等\\n"',
                                '                      "🟠 **高雄捷運** - 紅線、橘線\\n"',
                                '                      "🟢 **高雄輕軌** - 環狀輕軌\\n\\n"',
                                '                      "ℹ️ **說明**：目前僅以上3個系統提供即時看板資料",',
                                '                inline=False'
                            ]
                            
                            lines[start_line:end_line+1] = new_lines
                            break
            
            # 重新組合內容
            new_content = '\n'.join(lines)
            
            # 寫回檔案
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ 成功修正捷運即時電子看板的系統描述")
            print("📝 變更內容：")
            print("   - 移除了6個沒有即時看板資料的系統")
            print("   - 保留了3個有資料的系統：臺北捷運、高雄捷運、高雄輕軌")
            print("   - 新增了說明文字")
            
        else:
            print("⚠️  檔案中找不到需要修正的內容")
            
    except Exception as e:
        print(f"❌ 修正過程中發生錯誤: {e}")

if __name__ == "__main__":
    fix_metro_liveboard_descriptions()
