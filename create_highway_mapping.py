#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立公路局 AuthorityCode 縣市對照表
根據官方文件和實際資料分析
"""

def create_authority_code_mapping():
    """創建 AuthorityCode 縣市對照表"""
    
    # 根據交通部公路總局的業管機關簡碼對照表
    # 參考：https://motc-ptx.gitbook.io/tdx-zi-liao-shi-yong-kui-hua-bao-dian/data_notice/traffic_data/code/authority
    authority_code_mapping = {
        # 直轄市
        "TPE": "台北市",
        "NWT": "新北市", 
        "TYC": "桃園市",
        "TCN": "台中市",
        "TNN": "台南市",
        "KHH": "高雄市",
        
        # 縣市
        "KEE": "基隆市",
        "HSC": "新竹市", 
        "HST": "新竹縣",
        "MIA": "苗栗縣",
        "CHA": "彰化縣",
        "NTO": "南投縣",
        "YUN": "雲林縣",
        "CHY": "嘉義市",
        "CYT": "嘉義縣",
        "PTH": "屏東縣",
        "ILA": "宜蘭縣",
        "HUA": "花蓮縣",
        "TTT": "台東縣",
        "PEN": "澎湖縣",
        "JMN": "金門縣",
        "LIE": "連江縣",
        
        # 交通部公路總局（THB）及其分局
        "THB": "交通部公路總局",
        "THB-1R": "公路總局第一區養護工程處",  # 基隆、台北、新北
        "THB-2R": "公路總局第二區養護工程處",  # 桃園、新竹
        "THB-3R": "公路總局第三區養護工程處",  # 苗栗、台中、彰化、南投
        "THB-4R": "公路總局第四區養護工程處",  # 雲林、嘉義、台南
        "THB-5R": "公路總局第五區養護工程處",  # 高雄、屏東
        "THB-EO": "公路總局東部區養護工程處",  # 宜蘭、花蓮、台東
        
        # 國道高速公路局
        "FSW": "國道高速公路局",
        
        # 其他可能的代碼
        "MOT": "交通部",
        "MOTC": "交通部"
    }
    
    # 反向對照：從縣市名稱找 AuthorityCode
    county_to_authority = {}
    for code, county in authority_code_mapping.items():
        if county not in county_to_authority:
            county_to_authority[county] = []
        county_to_authority[county].append(code)
    
    # 區域分局對應的縣市（用於 SubAuthorityCode 篩選）
    region_county_mapping = {
        "THB-1R": ["基隆市", "台北市", "新北市"],
        "THB-2R": ["桃園市", "新竹市", "新竹縣"],
        "THB-3R": ["苗栗縣", "台中市", "彰化縣", "南投縣"],
        "THB-4R": ["雲林縣", "嘉義市", "嘉義縣", "台南市"],
        "THB-5R": ["高雄市", "屏東縣"],
        "THB-EO": ["宜蘭縣", "花蓮縣", "台東縣"]
    }
    
    return {
        "authority_code_mapping": authority_code_mapping,
        "county_to_authority": county_to_authority,
        "region_county_mapping": region_county_mapping
    }

def create_road_type_mapping():
    """創建道路類型對照表"""
    
    road_type_mapping = {
        # 國道
        "1": "國道",
        
        # 省道
        "2": "省道",
        
        # 縣道
        "3": "縣道",
        
        # 鄉道
        "4": "鄉道",
        
        # 特殊道路
        "5": "特殊道路",
        
        # 其他
        "6": "其他道路"
    }
    
    return road_type_mapping

if __name__ == "__main__":
    import json
    
    # 創建對照表
    authority_mapping = create_authority_code_mapping()
    road_mapping = create_road_type_mapping()
    
    # 合併所有對照表
    mapping_data = {
        "authority_mappings": authority_mapping,
        "road_type_mapping": road_mapping,
        "created_time": "2025-07-08T14:30:00",
        "description": "公路局 XML API 縣市與道路類型對照表"
    }
    
    # 儲存到檔案
    with open("highway_bureau_mapping.json", "w", encoding="utf-8") as f:
        json.dump(mapping_data, f, indent=2, ensure_ascii=False)
    
    print("✅ 對照表已創建：highway_bureau_mapping.json")
    
    # 顯示對照表摘要
    print(f"\n📊 縣市對照表摘要:")
    print(f"   - AuthorityCode 總數: {len(authority_mapping['authority_code_mapping'])}")
    print(f"   - 區域分局總數: {len(authority_mapping['region_county_mapping'])}")
    print(f"   - 道路類型總數: {len(road_mapping)}")
    
    print(f"\n🏛️ 主要縣市對照:")
    for code, county in list(authority_mapping['authority_code_mapping'].items())[:10]:
        print(f"   {code} -> {county}")
    
    print(f"\n🛣️ 道路類型對照:")
    for code, road_type in road_mapping.items():
        print(f"   {code} -> {road_type}")
