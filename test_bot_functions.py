#!/usr/bin/env python3
"""
機器人功能測試腳本
測試各個功能模組是否正常載入和工作
"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_info_commands():
    """測試資訊命令模組"""
    try:
        # 測試模組導入
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        print("✅ InfoCommands 模組載入成功")
        
        # 測試樣本資料解析
        if os.path.exists('sample_tsunami.json'):
            with open('sample_tsunami.json', 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
            
            # 檢查海嘯資料結構
            if 'records' in sample_data and 'Tsunami' in sample_data['records']:
                tsunami_records = sample_data['records']['Tsunami']
                print(f"✅ 海嘯資料結構正確，找到 {len(tsunami_records)} 筆記錄")
                
                # 檢查第一筆資料的必要欄位
                if tsunami_records and len(tsunami_records) > 0:
                    first_record = tsunami_records[0]
                    required_fields = ['ReportContent', 'ReportType']
                    missing_fields = [field for field in required_fields if field not in first_record]
                    
                    if not missing_fields:
                        print("✅ 海嘯資料欄位完整")
                    else:
                        print(f"⚠️ 海嘯資料缺少欄位: {missing_fields}")
                else:
                    print("⚠️ 海嘯資料為空")
            else:
                print("❌ 海嘯資料結構不正確")
        else:
            print("⚠️ 找不到 sample_tsunami.json 檔案")
              # 測試地震資料
        if os.path.exists('sample_earthquake.json'):
            try:
                with open('sample_earthquake.json', 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        eq_data = json.loads(content)
                        print("✅ 地震樣本資料載入成功")
                    else:
                        print("⚠️ sample_earthquake.json 檔案為空")
            except json.JSONDecodeError:
                print("⚠️ sample_earthquake.json 格式錯誤")
        else:
            print("⚠️ 找不到 sample_earthquake.json 檔案")
            
        return True
        
    except ImportError as e:
        print(f"❌ InfoCommands 模組載入失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        return False

async def test_other_modules():
    """測試其他模組"""
    modules = [
        ('cogs.admin_commands_fixed', 'AdminCommands'),
        ('cogs.basic_commands', 'BasicCommands'),
        ('cogs.level_system', 'LevelSystem'),
        ('cogs.monitor_system', 'MonitorSystem'),
        ('cogs.voice_system', 'VoiceSystem'),
        ('cogs.chat_commands', 'ChatCommands')
    ]
    
    results = []
    for module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {class_name} 模組載入成功")
            results.append(True)
        except Exception as e:
            print(f"❌ {class_name} 模組載入失敗: {e}")
            results.append(False)
    
    return all(results)

async def main():
    """主測試函數"""
    print("🔍 開始測試機器人功能模組...")
    print("=" * 50)
    
    # 測試資訊命令模組
    print("📊 測試資訊命令模組...")
    info_result = await test_info_commands()
    print()
    
    # 測試其他模組
    print("🔧 測試其他功能模組...")
    other_result = await test_other_modules()
    print()
    
    # 總結
    print("=" * 50)
    print("📋 測試結果總結:")
    print(f"資訊命令模組: {'✅ 正常' if info_result else '❌ 異常'}")
    print(f"其他功能模組: {'✅ 正常' if other_result else '❌ 異常'}")
    
    if info_result and other_result:
        print("\n🎉 所有模組測試通過！機器人功能正常")
        return True
    else:
        print("\n⚠️ 有模組測試失敗，請檢查相關問題")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ 測試腳本執行失敗: {e}")
        sys.exit(1)
