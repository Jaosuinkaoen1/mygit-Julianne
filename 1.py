# 无需安装第三方库，保存为 love.py 后运行。
# 动画顺序：沿轨迹弹出窗口 → 组成爱心 → 爱心消失 → 随机弹窗。
# 按 Esc 或关闭任意弹窗，即可退出整个程序。

import math
import random
import tkinter as tk


MESSAGES = [
    "我想你了",
    "想你在身边",
    "怎么会不喜欢呢",
    "天凉了多穿衣服",
    "每天开心",
    "你会忘了我吗",
    "我忘不掉你啊",
    "少抽烟少喝酒少熬夜",
    "记得好好吃饭",
    "愿你每天都有好心情",
]

COLORS = [
    "#FF69B4",
    "#FFB6C1",
    "#87CEEB",
    "#90EE90",
    "#FFFACD",
    "#FFC0CB",
    "#B0E0E6",
    "#D8BFD8",
]

HEART_COUNT = 80
HEART_INTERVAL = 45       # 爱心弹窗间隔，毫秒
HEART_SCALE = 0.65        # 爱心占可用屏幕空间的比例
HEART_WIDTH_RATIO = 0.65  # 在原宽度基础上收窄，适合宽屏显示
HEART_HOLD = 2200         # 完整爱心停留时间
DISAPPEAR_INTERVAL = 12   # 爱心窗口依次消失的间隔
RANDOM_COUNT = 90         # 随机弹窗数量
RANDOM_INTERVAL = 110     # 随机弹窗间隔


class LoveWindows:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        self.width = min(190, max(140, self.screen_w // 8))
        self.height = min(82, max(64, self.screen_h // 12))

        self.windows = []
        self.closed = False

        self.root.bind_all("<Escape>", self.quit)
        self.root.after(300, self.start_heart)

    def quit(self, event=None):
        if self.closed:
            return
        self.closed = True
        self.root.destroy()

    def popup(self, x, y):
        if self.closed:
            return

        x = max(0, min(int(x), self.screen_w - self.width - 12))
        y = max(0, min(int(y), self.screen_h - self.height - 65))

        window = tk.Toplevel(self.root)
        window.withdraw()
        window.title(" ")
        window.resizable(False, False)
        window.attributes("-topmost", True)
        window.protocol("WM_DELETE_WINDOW", self.quit)
        window.bind("<Escape>", self.quit)

        window.geometry(
            f"{self.width}x{self.height}+{x}+{y}"
        )

        color = random.choice(COLORS)
        window.configure(bg=color)

        label = tk.Label(
            window,
            text=random.choice(MESSAGES),
            bg=color,
            fg="#222222",
            font=("Microsoft YaHei", 12),
            wraplength=self.width - 12,
            justify="center",
        )
        label.pack(expand=True, fill="both", padx=4, pady=4)

        window.deiconify()
        window.lift()

        self.windows.append(window)

    def heart_points(self):
        # 预留原生标题栏和任务栏空间，避免爱心超出屏幕。
        left = 25
        top = 45
        available_w = self.screen_w - self.width - 2 * left - 15
        available_h = self.screen_h - self.height - 2 * top - 80

        available_w = max(1, available_w)
        available_h = max(1, available_h)
        heart_w = available_w * HEART_SCALE * HEART_WIDTH_RATIO
        heart_h = available_h * HEART_SCALE
        left += (available_w - heart_w) / 2
        top += (available_h - heart_h) / 2

        # 先密集采样，再按实际距离均匀取点，避免曲线各处速度不一致。
        samples = []

        # 从左侧开始，依次经过左上弧、中心凹口、右上弧和底部。
        sample_count = 1000
        for i in range(sample_count + 1):
            t = -math.pi / 2 + 2 * math.pi * i / sample_count

            hx = 16 * math.sin(t) ** 3
            hy = (
                13 * math.cos(t)
                - 5 * math.cos(2 * t)
                - 2 * math.cos(3 * t)
                - math.cos(4 * t)
            )

            x = left + (hx + 16) / 32 * heart_w
            y = top + (12 - hy) / 29 * heart_h

            samples.append((x, y))

        distances = [0.0]
        for previous, current in zip(samples, samples[1:]):
            distances.append(distances[-1] + math.dist(previous, current))

        points = []
        segment = 1
        for i in range(HEART_COUNT):
            target = distances[-1] * i / HEART_COUNT
            while segment < len(distances) - 1 and distances[segment] < target:
                segment += 1
            span = distances[segment] - distances[segment - 1]
            fraction = (target - distances[segment - 1]) / span if span else 0
            x0, y0 = samples[segment - 1]
            x1, y1 = samples[segment]
            points.append((x0 + fraction * (x1 - x0), y0 + fraction * (y1 - y0)))

        return points

    def start_heart(self):
        self.points = self.heart_points()
        self.show_heart_point(0)

    def show_heart_point(self, index):
        if self.closed:
            return

        if index < len(self.points):
            self.popup(*self.points[index])
            self.root.after(
                HEART_INTERVAL,
                self.show_heart_point,
                index + 1,
            )
        else:
            self.root.after(HEART_HOLD, self.remove_heart)

    def remove_heart(self):
        if self.closed:
            return

        if self.windows:
            window = self.windows.pop()
            if window.winfo_exists():
                window.destroy()
            self.root.after(DISAPPEAR_INTERVAL, self.remove_heart)
        else:
            self.root.after(450, self.show_random, 0)

    def show_random(self, index):
        if self.closed or index >= RANDOM_COUNT:
            return

        x = random.randint(
            12, max(12, self.screen_w - self.width - 24)
        )
        y = random.randint(
            35, max(35, self.screen_h - self.height - 90)
        )

        self.popup(x, y)
        self.root.after(
            RANDOM_INTERVAL,
            self.show_random,
            index + 1,
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    LoveWindows().run()
