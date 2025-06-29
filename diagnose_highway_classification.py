#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷國道監視器分類問題
"""

import asyncio
import sys
import os

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnose_highway_classification():
    """診斷國道監視器分類問題"""
    print("🔍 診斷國道監視器分類問題")
    print("=" * 60)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 建立實例
        reservoir_cog = ReservoirCommands(None)
        
        # 獲取公路監視器資料
        print("📡 獲取公路監視器資料...")
        cameras = await reservoir_cog._get_highway_cameras()
        
        if not cameras:
            print("❌ 無法獲取監視器資料")
            return False
        
        print(f"✅ 獲得 {len(cameras)} 個監視器資料")
        
        # 分析前100個監視器的資料結構
        print(f"\n📊 分析監視器資料結構...")
        
        sample_cameras = cameras[:20]  # 檢查前20個
        
        for i, camera in enumerate(sample_cameras):
            road_name = camera.get('RoadName', '')
            surveillance_desc = camera.get('SurveillanceDescription', '')
            road_class = camera.get('RoadClass', '')
            road_id = camera.get('RoadID', '')
            
            # 使用現有分類方法
            road_type = reservoir_cog._classify_road_type(camera)
            
            print(f"\n{i+1}. 監視器資訊:")
            print(f"   RoadName: {road_name}")
            print(f"   SurveillanceDescription: {surveillance_desc}")
            print(f"   RoadClass: {road_class}")
            print(f"   RoadID: {road_id}")
            print(f"   分類結果: {road_type}")
            
            # 檢查是否有國道關鍵字但被誤分類
            desc_lower = surveillance_desc.lower()
            if any(keyword in desc_lower for keyword in ['國道', '國1', '國3', '國5', 'freeway', 'highway', '高速公路']):
                if road_type != 'national':
                    print(f"   ⚠️ 疑似誤分類：含國道關鍵字但分類為 {road_type}")
                else:
                    print(f"   ✅ 正確分類為國道")
            
            # 檢查快速公路誤判
            if any(keyword in desc_lower for keyword in ['快速', '台62', '台64', '台68']):
                if road_type == 'national':
                    print(f"   ⚠️ 疑似誤分類：含快速公路關鍵字但分類為國道")
                else:
                    print(f"   ✅ 正確分類為非國道")
        
        # 統計分類結果
        print(f"\n📈 統計所有監視器分類結果...")
        classification_stats = {
            'national': 0,
            'provincial': 0,
            'freeway': 0,
            'general': 0
        }
        
        # 記錄可能的誤分類案例
        misclassified_examples = []
        
        for camera in cameras:
            road_type = reservoir_cog._classify_road_type(camera)
            classification_stats[road_type] += 1
            
            # 檢查疑似誤分類
            desc_lower = camera.get('SurveillanceDescription', '').lower()
            road_name = camera.get('RoadName', '').lower()
            
            # 國道關鍵字但非國道分類
            if (any(keyword in desc_lower for keyword in ['國道', '國1', '國3', '國5', 'freeway', 'highway', '高速公路']) and 
                road_type != 'national'):
                misclassified_examples.append({
                    'camera': camera,
                    'expected': 'national',
                    'actual': road_type,
                    'reason': '含國道關鍵字'
                })
            
            # 快速公路關鍵字但分類為國道
            elif (any(keyword in desc_lower for keyword in ['快速', '台62', '台64', '台68']) and 
                  road_type == 'national'):
                misclassified_examples.append({
                    'camera': camera,
                    'expected': 'freeway',
                    'actual': road_type,
                    'reason': '含快速公路關鍵字'
                })
        
        print(f"分類統計:")
        print(f"  🛣️ 國道: {classification_stats['national']}")
        print(f"  🛤️ 省道: {classification_stats['provincial']}")
        print(f"  🏎️ 快速公路: {classification_stats['freeway']}")
        print(f"  🚗 一般道路: {classification_stats['general']}")
        
        if misclassified_examples:
            print(f"\n⚠️ 發現 {len(misclassified_examples)} 個疑似誤分類案例:")
            for i, example in enumerate(misclassified_examples[:10]):  # 顯示前10個
                camera = example['camera']
                print(f"\n{i+1}. {example['reason']}:")
                print(f"   描述: {camera.get('SurveillanceDescription', '')}")
                print(f"   道路名: {camera.get('RoadName', '')}")
                print(f"   預期: {example['expected']} → 實際: {example['actual']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 診斷失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函數"""
    success = await diagnose_highway_classification()
    
    if success:
        print(f"\n💡 建議修正:")
        print("1. 調整國道判斷優先級")
        print("2. 改進快速公路關鍵字匹配")
        print("3. 加強道路名稱解析")
    else:
        print(f"\n❌ 診斷失敗")

if __name__ == "__main__":
    asyncio.run(main())
