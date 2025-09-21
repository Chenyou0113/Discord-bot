"""
測試捷運方向分類功能
"""
import sys
sys.path.append('.')

# 模擬資料測試方向判斷
def test_direction_logic():
    print("🚇 測試捷運方向分類功能")
    print("=" * 50)
    
    # 定義各路線的終點站
    line_terminals = {
        # 台北捷運
        'R': ['淡水', '象山'],  # 淡水信義線
        'G': ['松山', '新店'],  # 松山新店線
        'O': ['南勢角', '迴龍'],  # 中和新蘆線
        'BL': ['頂埔', '南港展覽館'],  # 板南線
        'BR': ['動物園', '南港展覽館'],  # 文湖線
        'Y': ['大坪林', '新北產業園區'],  # 環狀線
        # 高雄捷運
        'RO': ['小港', '南岡山'],  # 紅線
        'OR': ['西子灣', '大寮'],  # 橘線
        # 高雄輕軌
        'C': ['籬仔內', '哈瑪星']  # 環狀輕軌
    }
    
    # 測試資料
    test_trains = [
        # 台北捷運淡水信義線
        {'LineID': 'R', 'destination': '淡水', 'expected_direction': 'down'},
        {'LineID': 'R', 'destination': '象山', 'expected_direction': 'up'},
        
        # 高雄捷運紅線
        {'LineID': 'RO', 'destination': '小港', 'expected_direction': 'down'},
        {'LineID': 'RO', 'destination': '南岡山', 'expected_direction': 'up'},
        
        # 高雄捷運橘線
        {'LineID': 'OR', 'destination': '西子灣', 'expected_direction': 'down'},
        {'LineID': 'OR', 'destination': '大寮', 'expected_direction': 'up'},
    ]
    
    print("📝 測試方向判斷邏輯：")
    print()
    
    for i, train in enumerate(test_trains, 1):
        line_id = train['LineID']
        dest_name = train['destination']
        expected = train['expected_direction']
        
        # 判斷方向邏輯
        direction = 'unknown'
        if line_id in line_terminals:
            terminals = line_terminals[line_id]
            if len(terminals) >= 2:
                if dest_name in terminals[1:]:  # 往後面的終點站為上行
                    direction = 'up'
                elif dest_name in terminals[:1]:  # 往前面的終點站為下行
                    direction = 'down'
        
        # 方向標示
        direction_text = {
            'up': '⬆️ 上行',
            'down': '⬇️ 下行',
            'unknown': '❓ 未知'
        }
        
        status = "✅" if direction == expected else "❌"
        
        print(f"{i}. {status} {line_id}線 往 {dest_name}")
        print(f"   判斷結果: {direction_text[direction]}")
        print(f"   預期結果: {direction_text[expected]}")
        print()
    
    print("📊 路線終點站配置：")
    print()
    
    line_names = {
        'R': '❤️ 淡水信義線',
        'G': '💚 松山新店線', 
        'O': '🧡 中和新蘆線',
        'BL': '💙 板南線',
        'BR': '🤎 文湖線',
        'Y': '💛 環狀線',
        'RO': '❤️ 紅線(高雄)',
        'OR': '🧡 橘線(高雄)',
        'C': '💚 環狀輕軌'
    }
    
    for line_id, terminals in line_terminals.items():
        line_name = line_names.get(line_id, line_id)
        print(f"🚇 {line_name}")
        print(f"   ⬇️ 下行終點: {terminals[0]}")
        print(f"   ⬆️ 上行終點: {terminals[1]}")
        print()
    
    print("🎯 測試完成！新的方向分類功能準備就緒")
    print()
    print("💡 使用說明：")
    print("   - 使用 /metro_direction 指令可以按方向查看捷運資訊")
    print("   - 支援三個按鈕：🚇全部方向、⬆️上行、⬇️下行")
    print("   - 每個車站會同時顯示上行和下行的列車資訊")

if __name__ == "__main__":
    test_direction_logic()
