#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接測試縣市標準化功能 - 提取版本
"""

def _normalize_county_name(county):
    """標準化縣市名稱 - 擴充版本（提取自 reservoir_commands.py）"""
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

def simulate_water_camera_data_processing():
    """模擬水利監視器資料處理"""
    print("=== 模擬水利監視器縣市顯示問題修復 ===")
    
    # 模擬可能的 API 回傳縣市名稱
    problematic_counties = [
        '臺北市',           # 繁體
        '臺中市',           # 繁體
        '臺南市',           # 繁體
        '臺東縣',           # 繁體  
        '新北市政府',       # 帶政府後綴
        '台北市政府',       # 帶政府後綴
        '桃園縣',           # 舊名
        '台中縣',           # 舊名
        '高雄縣',           # 舊名
        '苗栗',             # 缺少後綴
        '彰化',             # 缺少後綴
        '南投',             # 缺少後綴
        '宜蘭',             # 缺少後綴
        '花蓮',             # 缺少後綴
        '新竹',             # 既有市也有縣
        '嘉義',             # 既有市也有縣
        '苗栗縣政府',       # 帶政府後綴的縣
        '彰化縣政府',       # 帶政府後綴的縣
        '',                 # 空字串
        None,               # None 值
        '未知縣市',         # 已知的未知值
    ]
    
    print("正在測試各種可能的縣市名稱格式...")
    
    all_results_good = True
    for county in problematic_counties:
        original = str(county) if county is not None else 'None'
        normalized = _normalize_county_name(county)
        
        # 檢查結果是否合理
        is_good = True
        if normalized == '未知縣市':
            if county not in [None, '', '未知縣市']:
                is_good = False
        elif not (normalized.endswith('市') or normalized.endswith('縣')):
            if normalized != '新竹' and normalized != '嘉義':  # 特殊情況
                is_good = False
        
        status = "✅" if is_good else "❌"
        print(f"{status} '{original}' -> '{normalized}'")
        
        if not is_good:
            all_results_good = False
    
    print(f"\n縣市名稱標準化結果: {'全部正確' if all_results_good else '有問題'}")
    
    # 模擬 format_water_image_info 的縣市處理
    print("\n=== 模擬訊息格式化 ===")
    
    sample_data = {
        'VideoSurveillanceStationName': '測試監控站',
        'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '臺北市',
        'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '中正區',
        'VideoSurveillanceStationAddress': '台北市中正區測試路123號',
        'BasinName': '淡水河',
        'ImageURL': 'http://test.com/image.jpg'
    }
    
    # 模擬格式化過程
    county = sample_data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
    normalized_county = _normalize_county_name(county)
    
    print(f"原始縣市: '{county}'")
    print(f"標準化後: '{normalized_county}'")
    print(f"預期在 Discord 訊息中顯示: 🏙️ 縣市：{normalized_county}")
    
    return all_results_good

def check_common_issues():
    """檢查常見問題"""
    print("\n=== 檢查常見縣市顯示問題 ===")
    
    issues = []
    
    # 問題1: 繁體字未轉換
    if _normalize_county_name('臺北市') != '台北市':
        issues.append("繁體字轉換問題")
    
    # 問題2: 政府後綴未移除
    if _normalize_county_name('新北市政府') != '新北市':
        issues.append("政府後綴移除問題")
    
    # 問題3: 舊縣市名稱未更新
    if _normalize_county_name('桃園縣') != '桃園市':
        issues.append("舊縣市名稱更新問題")
    
    # 問題4: 缺少後綴未補全
    if _normalize_county_name('苗栗') != '苗栗縣':
        issues.append("縣市後綴補全問題")
    
    if issues:
        print("發現以下問題:")
        for issue in issues:
            print(f"❌ {issue}")
        return False
    else:
        print("✅ 所有常見問題已修復")
        return True

if __name__ == "__main__":
    print("開始測試縣市顯示修復...")
    
    # 執行測試
    test1 = simulate_water_camera_data_processing()
    test2 = check_common_issues()
    
    overall_success = test1 and test2
    
    print(f"\n=== 最終結果 ===")
    print(f"縣市顯示修復: {'成功' if overall_success else '失敗'}")
    
    if overall_success:
        print("\n✅ 縣市顯示問題已修復！")
        print("主要改進:")
        print("- 繁體字自動轉換為簡體字")
        print("- 移除政府機關後綴")
        print("- 更新舊縣市名稱")
        print("- 自動補全缺少的市/縣後綴")
        print("- 處理特殊情況（如新竹市/縣）")
    else:
        print("\n❌ 仍有問題需要修復")
