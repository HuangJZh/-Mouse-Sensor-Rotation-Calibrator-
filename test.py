import pynput.mouse as mouse
import numpy as np
import matplotlib.pyplot as plt
import time

class MouseSensorCalibrator:
    def __init__(self):
        self.points = []
        self.is_recording = False
        self.data_ready = False
        self.listener = None  # 将listener存为实例变量以便停止
        
        print("=== 鼠标传感器角度校准程序 (单次测试版) ===")
        print("操作说明：")
        print("1. 按住【鼠标左键】不放。")
        print("2. 凭肌肉记忆，尝试水平左右快速移动鼠标。")
        print("3. 松开【鼠标左键】。")
        print("4. 查看结果，关闭图表窗口后程序将自动退出。")
        print("----------------------------------")

    def on_move(self, x, y):
        if self.is_recording:
            self.points.append((x, y))

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            if pressed:
                self.points = [] 
                self.is_recording = True
                print("\n[开始记录] 请左右移动鼠标...")
            else:
                self.is_recording = False
                if len(self.points) > 10: 
                    self.data_ready = True
                    # 这里也可以选择返回 False 来停止监听，
                    # 但为了确保主线程能处理绘图，我们在主循环里停止比较稳妥
                else:
                    print("[提示] 移动距离太短，请重新按住测试。")

    def calculate_and_plot(self):
        if not self.points:
            return

        data = np.array(self.points)
        x = data[:, 0]
        y = data[:, 1]
        
        # 视觉翻转Y轴
        y_visual = -y 

        try:
            slope, intercept = np.polyfit(x, y, 1)
        except:
            print("计算出错，可能是数据异常。")
            return

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
        print("\n[完成] 正在显示图表，关闭窗口后程序退出。")
        plt.show() # 这是一个阻塞函数，直到你关闭窗口代码才会继续往下走

    def run(self):
        # 启动监听
        self.listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.listener.start()

        try:
            while True:
                # 只有当采集到有效数据后才进入处理逻辑
                if self.data_ready:
                    # 1. 停止监听鼠标，防止后续操作干扰
                    self.listener.stop()
                    
                    # 2. 计算并绘图 (plt.show会卡住在这里直到窗口关闭)
                    self.calculate_and_plot()
                    
                    # 3. 退出循环，结束程序
                    break 
                
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            if self.listener.is_alive():
                self.listener.stop()
            print("程序已结束。")

if __name__ == "__main__":
    calibrator = MouseSensorCalibrator()
    calibrator.run()