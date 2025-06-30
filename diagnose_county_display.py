#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷縣市顯示問題
檢查水利防災監視器 API 回傳的縣市名稱欄位
"""

import aiohttp
import asyncio
import json
import ssl
from collections import Counter

async def diagnose_county_data():
    """診斷縣市資料"""
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print("=== 水利防災監視器 API 資料分析 ===")
                    print(f"總共 {len(data)} 筆資料")
                    
                    # 分析縣市欄位
                    counties = []
                    county_field_name = None
                    sample_data = None
                    
                    for item in data:
                        sample_data = item
                        # 尋找縣市相關欄位
                        for key, value in item.items():
                            if '縣市' in key or 'County' in key or 'Cities' in key:
                                county_field_name = key
                                counties.append(value)
                                break
                        if not county_field_name:
                            # 檢查常見的可能是縣市的欄位
                            for key in ['CountiesAndCitiesWhereTheMonitoringPointsAreLocated', 'Location', 'County']:
                                if key in item:
                                    county_field_name = key
                                    counties.append(item[key])
                                    break
                    
                    print(f"\n=== 縣市欄位名稱: {county_field_name} ===")
                    
                    if counties:
                        # 統計縣市分布
                        county_count = Counter(counties)
                        print(f"\n縣市分布統計:")
                        for county, count in county_count.most_common():
                            print(f"  {county}: {count} 個監控點")
                        
                        print(f"\n獨特縣市名稱 ({len(county_count)} 個):")
                        unique_counties = sorted(county_count.keys())
                        for county in unique_counties:
                            print(f"  '{county}'")
                    
                    # 顯示完整的欄位結構
                    print(f"\n=== 資料結構範例 ===")
                    if sample_data:
                        for key, value in sample_data.items():
                            print(f"  {key}: {value}")
                    
                    return data
                else:
                    print(f"API 請求失敗: {response.status}")
                    return None
        
    except Exception as e:
        print(f"診斷過程發生錯誤: {e}")
        return None

def analyze_county_normalization():
    """分析縣市名稱標準化需求"""
    print("\n=== 縣市名稱標準化建議 ===")
    
    # 常見的縣市名稱變異
    variations = {
        '臺北市': '台北市',
        '臺中市': '台中市', 
        '臺南市': '台南市',
        '臺東縣': '台東縣',
        '新北市政府': '新北市',
        '桃園縣': '桃園市',
    }
    
    print("建議的標準化對應:")
    for original, normalized in variations.items():
        print(f"  '{original}' -> '{normalized}'")

if __name__ == "__main__":
    print("開始診斷縣市顯示問題...")
    result = asyncio.run(diagnose_county_data())
    analyze_county_normalization()
    print("\n診斷完成")
