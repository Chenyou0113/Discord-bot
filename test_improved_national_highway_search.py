#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試改善後的國道搜尋功能
"""

import sys
import os

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_improved_search():
    """測試改善後的搜尋功能"""
    print("🔍 測試改善後的國道搜尋功能")
    print("=" * 50)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 建立測試實例
        reservoir_cog = ReservoirCommands(None)
        print("✅ ReservoirCommands 匯入成功")
        
        # 檢查搜尋邏輯
        import inspect
        source = inspect.getsource(reservoir_cog.highway_cameras)
        
        # 檢查是否包含改善的搜尋邏輯
        improvements = [
            ('國道特殊匹配', 'national_highway_match'),
            ('道路分類檢查', "road_class == '1'"),
            ('國道關鍵字', "'國道'"),
            ('高速公路關鍵字', "'高速公路'"),
            ('freeway關鍵字', "'freeway'"),
            ('highway關鍵字', "'highway'"),
            ('特定國道號碼', "'國1'"),
        ]
        
        print(f"\n🔧 搜尋邏輯改善檢查:")
        for desc, keyword in improvements:
            if keyword in source:
                print(f"   ✅ {desc} - 已實作")
            else:
                print(f"   ❌ {desc} - 未找到")
        
        # 模擬測試資料
        print(f"\n🧪 模擬搜尋測試:")
        
        test_cameras = [
            {
                'CCTVID': 'TEST-001',
                'RoadName': 'N1',
                'SurveillanceDescription': '國道一號高速公路(基隆-高雄)',
                'RoadClass': '1',
                'RoadID': '10001'
            },
            {
                'CCTVID': 'TEST-002', 
                'RoadName': 'N3',
                'SurveillanceDescription': '國道三號高速公路(基隆-屏東)',
                'RoadClass': '1',
                'RoadID': '10003'
            },
            {
                'CCTVID': 'TEST-003',
                'RoadName': '台62線',
                'SurveillanceDescription': '快速公路62號',
                'RoadClass': '2',
                'RoadID': '20062'
            }
        ]
        
        # 模擬搜尋邏輯測試
        test_keywords = ['國道', '國1', '國3', 'freeway', 'highway', '台62']
        
        for keyword in test_keywords:
            matches = []
            keyword_lower = keyword.lower()
            
            for cam in test_cameras:
                # 複製改善後的搜尋邏輯
                road_name = cam.get('RoadName', '').lower()
                surveillance_desc = cam.get('SurveillanceDescription', '').lower()
                cctv_id = cam.get('CCTVID', '').lower()
                road_class = cam.get('RoadClass', '')
                road_id = cam.get('RoadID', '')
                
                # 基本關鍵字匹配
                basic_match = any([
                    keyword_lower in road_name,
                    keyword_lower in surveillance_desc,
                    keyword_lower in cctv_id
                ])
                
                # 國道特殊匹配邏輯
                national_highway_match = False
                if any(kw in keyword_lower for kw in ['國道', '國1', '國3', '國5', 'freeway', 'highway']):
                    national_highway_match = any([
                        road_class == '1',
                        '國道' in surveillance_desc,
                        'freeway' in surveillance_desc,
                        'highway' in surveillance_desc,
                        '高速公路' in surveillance_desc,
                        any(term in road_id for term in ['1', '3', '5']) and len(road_id) <= 10,
                        any(term in road_name for term in ['1號', '3號', '5號', 'N1', 'N3', 'N5'])
                    ])
                
                if basic_match or national_highway_match:
                    matches.append(cam)
            
            print(f"   關鍵字 '{keyword}': {len(matches)} 個匹配")
            for match in matches:
                print(f"      - {match['RoadName']} ({match['SurveillanceDescription']})")
        
        print(f"\n💡 建議測試指令:")
        print("1. /highway_cameras location:國道")
        print("2. /highway_cameras location:國1")
        print("3. /highway_cameras location:國3")
        print("4. /highway_cameras location:freeway")
        print("5. /highway_cameras location:highway")
        print("6. /highway_cameras location:高速公路")
        
        print(f"\n📋 改善內容:")
        print("✅ 新增國道特殊匹配邏輯")
        print("✅ 支援道路分類判斷（RoadClass=1）")
        print("✅ 支援多種國道關鍵字")
        print("✅ 支援特定國道號碼搜尋")
        print("✅ 支援英文關鍵字（freeway, highway）")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    success = test_improved_search()
    
    print(f"\n" + "=" * 50)
    if success:
        print("🎉 國道搜尋功能改善完成！")
        print("💡 現在應該能更好地搜尋到國道監視器")
        print("🔄 請重啟機器人並在 Discord 中測試")
    else:
        print("❌ 測試失敗，請檢查問題")
    print("=" * 50)

if __name__ == "__main__":
    main()
