#!/usr/bin/env python3
"""
測試台鐵電子看板的進站時間計算功能
"""

import datetime

def test_arrival_time_calculation():
    """測試進站時間計算邏輯"""
    print("🧪 測試台鐵電子看板進站時間計算...")
    print("=" * 50)
    
    current_time = datetime.datetime.now()
    print(f"📅 當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 測試案例
    test_cases = [
        # (排定時間, 誤點分鐘, 預期狀態) - 使用接近當前時間的測試
        (f"{current_time.hour}:{current_time.minute + 1:02d}:00", 0, "即將進站"),
        (f"{current_time.hour}:{current_time.minute + 2:02d}:00", 0, "即將到達"),
        (f"{current_time.hour}:{current_time.minute + 5:02d}:00", 0, "即將到達"),
        (f"{current_time.hour}:{current_time.minute + 10:02d}:00", 2, "即將到達"),
        (f"{current_time.hour + 1}:{current_time.minute:02d}:00", 0, "正常班車"),
    ]
    
    for i, (scheduled_time, delay_mins, expected) in enumerate(test_cases, 1):
        try:
            # 解析排定到站時間
            today = current_time.date()
            arrival_datetime = datetime.datetime.combine(
                today, 
                datetime.datetime.strptime(scheduled_time, '%H:%M:%S').time()
            )
            
            # 如果排定時間已過，可能是明天的班車
            if arrival_datetime < current_time:
                arrival_datetime += datetime.timedelta(days=1)
            
            # 考慮誤點時間
            actual_arrival = arrival_datetime + datetime.timedelta(minutes=delay_mins)
            
            # 計算剩餘時間
            time_diff = actual_arrival - current_time
            
            if time_diff.total_seconds() <= 0:
                arrival_status = "🚆 **列車進站中**"
                time_until_arrival = ""
            elif time_diff.total_seconds() <= 120:  # 2分鐘內
                arrival_status = "🔥 **即將進站**"
                time_until_arrival = f"⏰ 還有 {int(time_diff.total_seconds() // 60)} 分鐘"
            elif time_diff.total_seconds() <= 900:  # 15分鐘內
                minutes = int(time_diff.total_seconds() // 60)
                arrival_status = "🟡 **即將到達**"
                time_until_arrival = f"⏰ 還有 {minutes} 分鐘"
            else:
                hours = int(time_diff.total_seconds() // 3600)
                minutes = int((time_diff.total_seconds() % 3600) // 60)
                arrival_status = "⏱️ **正常班車**"
                if hours > 0:
                    time_until_arrival = f"⏰ 還有 {hours} 小時 {minutes} 分鐘"
                else:
                    time_until_arrival = f"⏰ 還有 {minutes} 分鐘"
            
            print(f"測試 {i}: 排定 {scheduled_time}")
            print(f"  誤點: {delay_mins} 分鐘")
            print(f"  實際到站: {actual_arrival.strftime('%H:%M:%S')}")
            print(f"  狀態: {arrival_status}")
            print(f"  剩餘時間: {time_until_arrival}")
            print(f"  時間差: {time_diff}")
            print()
            
        except Exception as e:
            print(f"❌ 測試 {i} 發生錯誤: {str(e)}")
            print()
    
    print("🎉 台鐵電子看板進站時間計算測試完成！")

def test_time_display_formats():
    """測試不同時間顯示格式"""
    print("\n🕐 測試時間顯示格式...")
    print("=" * 30)
    
    # 測試不同的剩餘時間
    test_seconds = [
        15,      # 15秒 -> 即將進站
        45,      # 45秒 -> 即將進站
        90,      # 1.5分鐘 -> 即將進站
        150,     # 2.5分鐘 -> 即將到達
        300,     # 5分鐘 -> 即將到達
        900,     # 15分鐘 -> 即將到達
        1800,    # 30分鐘 -> 正常班車
        3600,    # 60分鐘 -> 正常班車
    ]
    
    for seconds in test_seconds:
        if seconds <= 0:
            status = "🚆 列車進站中"
            time_str = ""
        elif seconds <= 120:
            status = "🔥 即將進站"
            total_seconds = int(seconds)
            minutes = total_seconds // 60
            secs = total_seconds % 60
            if minutes > 0:
                time_str = f"⏰ 還有 {minutes} 分 {secs} 秒"
            else:
                time_str = f"⏰ 還有 {secs} 秒"
        elif seconds <= 900:
            status = "🟡 即將到達"
            total_seconds = int(seconds)
            minutes = total_seconds // 60
            secs = total_seconds % 60
            time_str = f"⏰ 還有 {minutes} 分 {secs} 秒"
        else:
            status = "⏱️ 正常班車"
            total_seconds = int(seconds)
            minutes = total_seconds // 60
            time_str = f"⏰ 還有 {minutes} 分鐘"
        
        print(f"{seconds}秒 -> {status} {time_str}")
    
    print("\n🚇 捷運時間顯示格式測試...")
    print("=" * 30)
    
    # 測試捷運的estimate_time格式
    metro_test_times = [15, 30, 60, 90, 120, 180, 300, 600]
    
    for estimate_time in metro_test_times:
        if estimate_time < 60:
            display = f"({estimate_time}秒)"
        elif estimate_time < 120:  # 2分鐘內顯示分秒
            minutes = estimate_time // 60
            seconds = estimate_time % 60
            display = f"({minutes}分{seconds}秒)"
        else:  # 超過2分鐘顯示分秒
            minutes = estimate_time // 60
            seconds = estimate_time % 60
            if seconds > 0:
                display = f"({minutes}分{seconds}秒)"
            else:
                display = f"({minutes}分鐘)"
        
        print(f"捷運 {estimate_time}秒 -> {display}")

if __name__ == "__main__":
    test_arrival_time_calculation()
    test_time_display_formats()
