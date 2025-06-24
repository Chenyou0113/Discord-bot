#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單格式化測試
快速測試格式化是否有問題
"""

import sys
import os
import asyncio
import logging

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def simple_format_test():
    """簡單的格式化測試"""
    print("🔧 簡單格式化測試")
    print("=" * 40)
    
    try:        # 模擬地震數據 - 這應該是單個地震記錄，而不是完整的API響應
        sample_earthquake_data = {
            'EarthquakeNo': 11410032,
            'ReportType': '地震報告',
            'ReportContent': '06/12-00:01臺東縣近海發生規模5.0有感地震，最大震度花蓮縣石梯坪4級。',
            'EarthquakeInfo': {
                'OriginTime': '2024-06-12 00:01:35',
                'Source': '中央氣象署',
                'FocalDepth': 27.22,
                'Epicenter': {
                    'Location': '臺東縣政府東北方 43.4 公里 (位於臺東縣近海)',
                    'EpicenterLatitude': 23.43,
                    'EpicenterLongitude': 121.54
                },
                'EarthquakeMagnitude': {
                    'MagnitudeType': 'ML',
                    'MagnitudeValue': 5.0
                }
            },
            'Intensity': {
                'ShakingArea': [
                    {
                        'AreaDesc': '花蓮縣地區最大震度4級',
                        'CountyName': '花蓮縣',
                        'InfoStatus': '1',
                        'AreaIntensity': '4'
                    }
                ]
            }
        }
        
        print("✅ 創建了模擬地震數據")
        
        # 匯入格式化函數
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock
        
        # 創建最小化的 InfoCommands 實例
        mock_bot = MagicMock()
        info_commands = InfoCommands(mock_bot)
        
        print("✅ 創建 InfoCommands 實例")
          # 測試格式化函數
        print("\n📋 測試格式化...")
        try:
            formatted_embed = await info_commands.format_earthquake_data(sample_earthquake_data)
            
            if formatted_embed is None:
                print("❌ 格式化返回 None")
                return False
            else:
                print("✅ 格式化成功！")
                print(f"   標題: {formatted_embed.title}")
                print(f"   描述: {formatted_embed.description[:100] if formatted_embed.description else 'None'}...")
                print(f"   欄位數: {len(formatted_embed.fields)}")
                
                # 列出所有欄位
                for i, field in enumerate(formatted_embed.fields):
                    print(f"   欄位{i+1}: {field.name} = {field.value[:50]}...")
                
                return True
                
        except Exception as e:
            print(f"❌ 格式化時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    result = asyncio.run(simple_format_test())
    
    if result:
        print("\n🎯 測試結果: ✅ 格式化功能正常")
    else:
        print("\n🎯 測試結果: ❌ 格式化有問題")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
