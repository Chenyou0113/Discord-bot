#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試縣市名稱標準化修復
"""

def _normalize_county_name(county):
    """標準化縣市名稱 - 擴充版本"""
    if not county or county == '未知縣市':
        return '未知縣市'
    
    # 先清理可能的空白字符
    county = str(county).strip()
    if not county:
        return '未知縣市'
    
    # 擴充的縣市名稱對應表
    county_mapping = {
        # 繁體轉簡體對應
        '臺北市': '台北市',
        '臺中市': '台中市', 
        '臺南市': '台南市',
        '臺東縣': '台東縣',
        '臺北縣': '新北市',  # 舊名
        
        # 政府機關名稱標準化
        '新北市政府': '新北市',
        '台北市政府': '台北市',
        '桃園市政府': '桃園市',
        '台中市政府': '台中市',
        '台南市政府': '台南市',
        '高雄市政府': '高雄市',
        
        # 舊縣市名稱對應
        '桃園縣': '桃園市',
        '台中縣': '台中市',
        '台南縣': '台南市',
        '高雄縣': '高雄市',
        
        # 可能的變體
        '新竹市政府': '新竹市',
        '新竹縣政府': '新竹縣',
        '苗栗縣政府': '苗栗縣',
        '彰化縣政府': '彰化縣',
        '南投縣政府': '南投縣',
        '雲林縣政府': '雲林縣',
        '嘉義市政府': '嘉義市',
        '嘉義縣政府': '嘉義縣',
        '屏東縣政府': '屏東縣',
        '宜蘭縣政府': '宜蘭縣',
        '花蓮縣政府': '花蓮縣',
        '澎湖縣政府': '澎湖縣',
        '金門縣政府': '金門縣',
        '連江縣政府': '連江縣',
        
        # 可能出現的英文或其他格式
        'Taipei': '台北市',
        'New Taipei': '新北市',
        'Taoyuan': '桃園市',
        'Taichung': '台中市',
        'Tainan': '台南市',
        'Kaohsiung': '高雄市',
    }
    
    # 首先檢查完全匹配
    if county in county_mapping:
        return county_mapping[county]
    
    # 標準化處理
    normalized = county
    
    # 移除可能的後綴詞（如"政府"、"市政府"等）
    suffixes_to_remove = ['政府', '市政府', '縣政府']
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
            break
    
    # 確保包含 "市" 或 "縣"
    if normalized and not normalized.endswith(('市', '縣')):
        # 根據常見縣市添加後綴
        cities = ['台北', '臺北', '新北', '桃園', '台中', '臺中', '台南', '臺南', '高雄', '新竹']
        counties = ['新竹', '苗栗', '彰化', '南投', '雲林', '嘉義', '屏東', '宜蘭', '花蓮', '台東', '臺東', '澎湖', '金門', '連江']
        
        if normalized in cities:
            # 特殊處理新竹（既有市也有縣）
            if normalized == '新竹':
                # 保持原樣，讓後續邏輯決定
                pass
            else:
                normalized += '市'
        elif normalized in counties:
            normalized += '縣'
    
    # 再次檢查對應表（處理可能新增後綴後的情況）
    if normalized in county_mapping:
        return county_mapping[normalized]
    
    return normalized

def test_county_normalization():
    """測試縣市名稱標準化"""
    test_cases = [
        # (輸入, 預期輸出)
        ('臺北市', '台北市'),
        ('臺中市', '台中市'),
        ('臺南市', '台南市'),
        ('臺東縣', '台東縣'),
        ('新北市政府', '新北市'),
        ('台北市政府', '台北市'),
        ('桃園縣', '桃園市'),
        ('桃園', '桃園市'),
        ('新竹', '新竹'),  # 特殊情況，保持原樣
        ('苗栗', '苗栗縣'),
        ('彰化', '彰化縣'),
        ('高雄', '高雄市'),
        ('Taipei', '台北市'),
        ('', '未知縣市'),
        ('未知縣市', '未知縣市'),
        ('新北市', '新北市'),  # 已經正確的格式
        ('花蓮縣政府', '花蓮縣'),
    ]
    
    print("=== 縣市名稱標準化測試 ===")
    all_passed = True
    
    for input_county, expected in test_cases:
        result = _normalize_county_name(input_county)
        status = "✅" if result == expected else "❌"
        
        print(f"{status} '{input_county}' -> '{result}' (預期: '{expected}')")
        
        if result != expected:
            all_passed = False
    
    print(f"\n測試結果: {'全部通過' if all_passed else '部分失敗'}")
    return all_passed

if __name__ == "__main__":
    test_county_normalization()
