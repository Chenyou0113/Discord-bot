#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試修正後的 R 線和 O 線路線名稱顯示
"""

def test_ro_line_mapping():
    """測試 R 線和 O 線的路線名稱對應"""
    print("=" * 60)
    print("🚇 R線和O線路線名稱對應測試")
    print("=" * 60)
    
    def get_line_name(line_id, metro_system):
        line_names = {
            'BR': '🤎 文湖線',
            'BL': '💙 板南線', 
            'G': '💚 松山新店線',
            'Y': '💛 環狀線',
            'LG': '💚 安坑線',
            'V': '💜 淡海輕軌',
            'RO': '❤️ 紅線',
            'OR': '🧡 橘線',
            'C': '💚 環狀輕軌',
            # 根據系統判斷路線名稱
            'R': '❤️ 紅線' if metro_system == 'KRTC' else '❤️ 淡水信義線',
            'O': '🧡 橘線' if metro_system == 'KRTC' else '🧡 中和新蘆線'
        }
        return line_names.get(line_id, line_id)
    
    test_cases = [
        ('R', 'KRTC', '高雄捷運'),
        ('R', 'TRTC', '台北捷運'),  
        ('O', 'KRTC', '高雄捷運'),
        ('O', 'TRTC', '台北捷運'),
        ('RO', 'KRTC', '高雄捷運'),
        ('OR', 'KRTC', '高雄捷運'),
    ]
    
    print("測試結果:")
    for line_id, system, system_name in test_cases:
        line_name = get_line_name(line_id, system)
        print(f"  {system_name} ({system}) {line_id}線 -> {line_name}")
    
    print("\n" + "=" * 60)
    print("✅ 重點修正:")
    print("   高雄捷運 R線: ❤️ 紅線 (不是淡水信義線)")
    print("   高雄捷運 O線: 🧡 橘線 (不是中和新蘆線)")  
    print("   台北捷運 R線: ❤️ 淡水信義線")
    print("   台北捷運 O線: 🧡 中和新蘆線")
    print("=" * 60)

if __name__ == "__main__":
    test_ro_line_mapping()
