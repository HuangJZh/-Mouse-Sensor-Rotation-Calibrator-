import pynput.mouse as mouse
import numpy as np
import matplotlib.pyplot as plt
import threading
import time

class MouseSensorCalibrator:
    def __init__(self):
        self.points = []
        self.is_recording = False
        self.data_ready = False
        print("=== 鼠标传感器角度校准程序 (左键版) ===")
        print("操作说明：")
        print("1. 按住【鼠标左键】不放。")
        print("2. 凭肌肉记忆，尝试水平左右快速移动鼠标。")
        print("3. 松开【鼠标左键】。")
        print("4. 程序将计算角度并显示轨迹图。")
        print("5. 关闭弹出的图表窗口后，可以继续进行下一次测试。")
        print("----------------------------------")

    def on_move(self, x, y):
        if self.is_recording:
            self.points.append((x, y))

    def on_click(self, x, y, button, pressed):
        # === 修改点：检测左键 ===
        if button == mouse.Button.left:
            if pressed:
                self.points = [] # 清空旧数据
                self.is_recording = True
                print("\n[开始记录] 请左右移动鼠标...")
            else:
                self.is_recording = False
                # 只有数据点足够多才计算（防止点击关闭窗口时误触发）
                if len(self.points) > 10: 
                    self.data_ready = True
                else:
                    pass

    def calculate_and_plot(self):
        if not self.points:
            return

        data = np.array(self.points)
        x = data[:, 0]
        y = data[:, 1]
        
        # 视觉翻转Y轴
        y_visual = -y 

        try:
            # 线性回归拟合
            slope, intercept = np.polyfit(x, y, 1)
        except:
            print("计算出错，可能是数据异常。")
            return

        # 计算角度
        angle_rad = np.arctan(slope)
        angle_deg = np.degrees(angle_rad)

        print("-" * 30)
        print(f"拟合斜率: {slope:.5f}")
        print(f"检测到的偏转角度: {abs(angle_deg):.2f}°")
        
        if angle_deg > 0:
            print("结论：传感器【顺时针】歪了 (右边偏低)。")
            print(f"建议：在驱动中将角度调整 -{abs(angle_deg):.1f}° (逆时针修正)。")
        elif angle_deg < 0:
            print("结论：传感器【逆时针】歪了 (右边偏高)。")
            print(f"建议：在驱动中将角度调整 +{abs(angle_deg):.1f}° (顺时针修正)。")
        else:
            print("结论：完美水平！")

        # --- 绘图 ---
        plt.figure(figsize=(10, 6))
        plt.title(f"Mouse Trace (Correction: {-angle_deg:.2f} deg)")
        plt.scatter(x, y_visual, s=2, color='blue', label='Mouse Movement')
        
        y_fit = slope * x + intercept
        plt.plot(x, -y_fit, color='red', linewidth=2, label='Fitted Line')
        
        plt.xlabel("X Pixels")
        plt.ylabel("Y Pixels (Inverted)")
        plt.axis('equal')
        plt.legend()
        plt.grid(True)
        plt.show()

    def run(self):
        listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        listener.start()
        try:
            while True:
                if self.data_ready:
                    self.calculate_and_plot()
                    self.data_ready = False
                time.sleep(0.1)
        except KeyboardInterrupt:
            listener.stop()
            print("\n程序已退出。")

if __name__ == "__main__":
    calibrator = MouseSensorCalibrator()
    calibrator.run()