#!/usr/bin/env python3
"""
分析新的 XML CCTV API 資料結構
URL: https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml
"""

import requests
import xml.etree.ElementTree as ET
import json
from typing import Dict, List, Any

def fetch_xml_cctv_data() -> str:
    """
    取得 XML CCTV 資料
    """
    try:
        url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
        print(f"正在請求 XML API: {url}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"API 回應狀態碼: {response.status_code}")
        print(f"內容類型: {response.headers.get('content-type', 'unknown')}")
        print(f"回應內容長度: {len(response.text)} 字符")
        
        return response.text
        
    except Exception as e:
        print(f"取得 XML CCTV 資料時發生錯誤: {e}")
        return ""

def parse_xml_structure(xml_content: str) -> Dict[str, Any]:
    """
    解析 XML 結構並分析欄位
    """
    try:
        # 解析 XML
        root = ET.fromstring(xml_content)
        
        # 定義命名空間
        namespace = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
        
        # 分析根元素
        print(f"根元素: {root.tag}")
        print(f"命名空間: {root.attrib}")
        
        # 取得基本資訊
        update_time = root.find('ns:UpdateTime', namespace)
        update_interval = root.find('ns:UpdateInterval', namespace)
        authority_code = root.find('ns:AuthorityCode', namespace)
        link_version = root.find('ns:LinkVersion', namespace)
        
        print(f"\n== 基本資訊 ==")
        print(f"更新時間: {update_time.text if update_time is not None else 'N/A'}")
        print(f"更新間隔: {update_interval.text if update_interval is not None else 'N/A'}")
        print(f"機關代碼: {authority_code.text if authority_code is not None else 'N/A'}")
        print(f"版本: {link_version.text if link_version is not None else 'N/A'}")
        
        # 分析 CCTV 資料
        cctvs = root.find('ns:CCTVs', namespace)
        if cctvs is None:
            print("\n找不到 CCTVs 元素")
            return {}
        
        cctv_list = cctvs.findall('ns:CCTV', namespace)
        print(f"\n== CCTV 監視器資料 ==")
        print(f"總監視器數量: {len(cctv_list)}")
        
        # 分析前幾個監視器的欄位結構
        sample_cctvs = []
        for i, cctv in enumerate(cctv_list[:5]):  # 取前 5 個作為樣本
            cctv_data = {}
            
            # 取得所有子元素
            for child in cctv:
                tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                cctv_data[tag_name] = child.text
            
            sample_cctvs.append(cctv_data)
            
            print(f"\n--- 監視器 {i+1} ---")
            for key, value in cctv_data.items():
                print(f"{key}: {value}")
        
        # 統計所有欄位
        all_fields = set()
        for cctv in cctv_list:
            for child in cctv:
                tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                all_fields.add(tag_name)
        
        print(f"\n== 所有可用欄位 ==")
        for field in sorted(all_fields):
            print(f"- {field}")
        
        # 分析地點資訊
        print(f"\n== 地點資訊分析 ==")
        location_fields = []
        for cctv in cctv_list[:10]:  # 取前 10 個分析
            location_info = {}
            for child in cctv:
                tag_name = child.tag.replace('{http://traffic.transportdata.tw/standard/traffic/schema/}', '')
                if any(keyword in tag_name.lower() for keyword in ['location', 'position', 'address', 'road', 'section']):
                    location_info[tag_name] = child.text
            
            if location_info:
                location_fields.append(location_info)
        
        for i, location in enumerate(location_fields):
            print(f"\n位置資訊 {i+1}:")
            for key, value in location.items():
                print(f"  {key}: {value}")
        
        return {
            "total_count": len(cctv_list),
            "sample_data": sample_cctvs,
            "all_fields": list(all_fields),
            "location_fields": location_fields
        }
        
    except Exception as e:
        print(f"解析 XML 時發生錯誤: {e}")
        return {}

def analyze_image_urls(xml_content: str) -> None:
    """
    分析圖片 URL 格式
    """
    try:
        root = ET.fromstring(xml_content)
        namespace = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
        
        cctvs = root.find('ns:CCTVs', namespace)
        if cctvs is None:
            return
        
        cctv_list = cctvs.findall('ns:CCTV', namespace)
        
        print(f"\n== 圖片 URL 分析 ==")
        image_urls = []
        stream_urls = []
        
        for cctv in cctv_list[:10]:  # 取前 10 個分析
            video_image_url = cctv.find('ns:VideoImageURL', namespace)
            video_stream_url = cctv.find('ns:VideoStreamURL', namespace)
            
            if video_image_url is not None and video_image_url.text:
                image_urls.append(video_image_url.text)
            
            if video_stream_url is not None and video_stream_url.text:
                stream_urls.append(video_stream_url.text)
        
        print(f"圖片 URL 樣本:")
        for i, url in enumerate(image_urls[:5]):
            print(f"  {i+1}: {url}")
        
        print(f"\n串流 URL 樣本:")
        for i, url in enumerate(stream_urls[:5]):
            print(f"  {i+1}: {url}")
        
    except Exception as e:
        print(f"分析圖片 URL 時發生錯誤: {e}")

def main():
    """
    主函數
    """
    print("=== XML CCTV API 資料結構分析 ===")
    
    # 取得 XML 資料
    xml_content = fetch_xml_cctv_data()
    if not xml_content:
        print("無法取得 XML 資料，分析結束")
        return
    
    print(f"\nXML 內容前 500 字符:")
    print(xml_content[:500])
    print("...")
    
    # 解析 XML 結構
    analysis_result = parse_xml_structure(xml_content)
    
    # 分析圖片 URL
    analyze_image_urls(xml_content)
    
    # 儲存分析結果
    if analysis_result:
        with open('xml_cctv_analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        print(f"\n分析結果已儲存至 xml_cctv_analysis_result.json")
    
    print("\n=== 分析完成 ===")

if __name__ == "__main__":
    main()
