"""闪烁的红色粒子爱心。

运行：python beating_heart.py
按 Esc 或关闭窗口退出。仅使用 Python 标准库，无需安装第三方库。
"""

import math
import random
import time
import tkinter as tk
from bisect import bisect_left
from typing import NamedTuple


# 可以修改粒子数量、心跳速度和窗口大小。
WIDTH, HEIGHT = 900, 820
BACKGROUND = "#000000"
PARTICLE_COUNT = 18000
BEATS_PER_MINUTE = 72
FPS = 30
TWINKLE_GROUPS = 256


def heart_outline(count=2400):
    """按弧长取点，让粒子在心形尖角附近也能均匀分布。"""
    samples = []
    for i in range(2401):
        angle = math.tau * i / 2400
        x = 16 * math.sin(angle) ** 3
        y = -(13 * math.cos(angle) - 5 * math.cos(2 * angle)
              - 2 * math.cos(3 * angle) - math.cos(4 * angle))
        samples.append((x, y))

    # 将图形包围盒的中心移到原点，方便居中缩放。
    center_y = (min(y for _, y in samples) + max(y for _, y in samples)) / 2
    samples = [(x, y - center_y) for x, y in samples]
    distances = [0.0]
    for first, second in zip(samples, samples[1:]):
        distances.append(distances[-1] + math.hypot(
            second[0] - first[0], second[1] - first[1]))

    points = []
    for i in range(count):
        target = distances[-1] * i / count
        index = max(1, bisect_left(distances, target))
        fraction = ((target - distances[index - 1])
                    / (distances[index] - distances[index - 1]))
        x1, y1 = samples[index - 1]
        x2, y2 = samples[index]
        points.append((x1 + (x2 - x1) * fraction,
                       y1 + (y2 - y1) * fraction))
    return points


def heartbeat(elapsed):
    """每次心跳包含一次主跳和一次轻跳，随后平缓回落。"""
    phase = (elapsed * BEATS_PER_MINUTE / 60) % 1.0
    main_beat = math.exp(-((phase - 0.20) / 0.09) ** 2)
    light_beat = math.exp(-((phase - 0.40) / 0.09) ** 2)
    return 0.96 + 0.105 * main_beat + 0.045 * light_beat


class Particle(NamedTuple):
    x: float
    y: float
    size: int
    brightness: int
    group: int
    drift: float
    halo: bool


class ParticleHeart:
    """生成固定粒子群；每一帧只改变位置和亮度，避免随机噪点抖动。"""

    def __init__(self, count=PARTICLE_COUNT):
        rng = random.Random(520)
        outline = heart_outline()
        self.particles = []
        for i in range(count):
            x, y = rng.choice(outline)
            fraction = i / count
            halo = fraction < 0.14
            if halo:
                # 轮廓外侧的小光点：疏散、较暗，随心跳向外轻轻扩散。
                spread = 1.02 + min(rng.expovariate(11), 0.34)
                jitter = 0.55
                brightness = rng.randint(90, 215)
                drift = rng.uniform(0.4, 1.1)
            elif fraction < 0.36:
                # 内部保留大量黑色空隙，中心只铺少量星点。
                spread = math.sqrt(rng.random()) * 0.91
                jitter = 0.16
                brightness = rng.randint(145, 250)
                drift = rng.uniform(0.15, 0.45)
            else:
                # 有厚度的粒子边缘，没有连线，也没有规则排列的圆圈。
                spread = min(1.07, max(0.78, rng.gauss(0.95, 0.052)))
                jitter = 0.15
                brightness = rng.randint(205, 255)
                drift = rng.uniform(0.08, 0.30)
            x = x * spread + rng.gauss(0, jitter)
            y = y * spread + rng.gauss(0, jitter)
            choice = rng.random()
            size = 0 if choice < 0.30 else (1 if choice < 0.94 else 2)
            if halo and choice < 0.88:
                size = 0
            self.particles.append(Particle(
                x, y, size, brightness, rng.randrange(TWINKLE_GROUPS), drift, halo))

        self.oscillators = [
            (rng.uniform(1.8, 5.0), rng.uniform(0, math.tau))
            for _ in range(TWINKLE_GROUPS)
        ]
        # 红色核心配上很弱的周边光晕，保留细颗粒感。
        palette = [bytes((i, int(0.13 * i + 52 * (i / 255) ** 6),
                          int(0.19 * i + 42 * (i / 255) ** 6)))
                   for i in range(256)]
        patterns = [
            [(0, 0, 1.0)],
            [(0, 0, 1.0), (1, 0, 0.90), (0, 1, 0.90), (1, 1, 0.65)],
            [(0, 0, 1.0), (-1, 0, 0.46), (1, 0, 0.46),
             (0, -1, 0.46), (0, 1, 0.46), (-1, -1, 0.10),
             (1, -1, 0.10), (-1, 1, 0.10), (1, 1, 0.10)],
        ]
        self.sprites = [
            [[(dx, dy, palette[int(level * strength)])
              for dx, dy, strength in pattern] for level in range(256)]
            for pattern in patterns
        ]

    def render(self, elapsed, width=WIDTH, height=HEIGHT):
        """返回 RGB 像素；直接绘制细小光点，不叠加模糊的实心爱心。"""
        pixels = bytearray(width * height * 3)
        unit = min(width, height) / 46
        scale = unit * heartbeat(elapsed)
        # 外围粒子的响应稍慢，使心跳带出轻微的扩散感。
        halo_scale = unit * (heartbeat(elapsed - 0.09) + 0.012)
        motion = []
        for speed, phase in self.oscillators:
            wave = math.sin(elapsed * speed + phase)
            twinkle = (wave + 1) / 2
            light = 0.65 + 0.28 * twinkle + 0.23 * twinkle ** 16
            motion.append((light, math.sin(elapsed * 0.8 + phase),
                           math.cos(elapsed * 0.65 + phase * 1.7)))

        center_x, center_y = width / 2, height / 2
        for particle in self.particles:
            light, drift_x, drift_y = motion[particle.group]
            local_scale = halo_scale if particle.halo else scale
            # 漂移幅度很小，主体始终保持清楚的心形。
            x = round(center_x + particle.x * local_scale
                      + drift_x * particle.drift * unit * 0.24)
            y = round(center_y + particle.y * local_scale
                      + drift_y * particle.drift * unit * 0.24)
            if not (1 <= x < width - 2 and 1 <= y < height - 2):
                continue
            level = min(255, int(particle.brightness * light))
            for dx, dy, color in self.sprites[particle.size][level]:
                offset = ((y + dy) * width + x + dx) * 3
                # 重叠时保留更亮的光点，避免暗粒子盖住亮粒子。
                if color[0] > pixels[offset]:
                    pixels[offset:offset + 3] = color
        return pixels


class BeatingHeart:
    def __init__(self, root):
        self.root = root
        self.root.title("闪烁的红色粒子爱心 · Esc 退出")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.minsize(420, 420)
        self.root.configure(bg=BACKGROUND)
        self.canvas = tk.Canvas(root, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.heart = ParticleHeart()
        self.image = None
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW)
        self.started = time.perf_counter()
        self.timer = None
        self.root.bind("<Escape>", self.close)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.timer = self.root.after(30, self.animate)

    def animate(self):
        frame_start = time.perf_counter()
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        # 大窗口中保持合适的渲染尺寸，避免每帧创建过大的图像。
        render_width, render_height = min(width, 1100), min(height, 1000)
        pixels = self.heart.render(frame_start - self.started,
                                   render_width, render_height)
        header = f"P6\n{render_width} {render_height}\n255\n".encode("ascii")
        self.image = tk.PhotoImage(data=header + pixels, format="PPM")
        self.canvas.itemconfigure(self.image_item, image=self.image)
        self.canvas.coords(self.image_item, (width - render_width) // 2,
                           (height - render_height) // 2)
        spent_ms = (time.perf_counter() - frame_start) * 1000
        self.timer = self.root.after(max(1, round(1000 / FPS - spent_ms)),
                                    self.animate)

    def close(self, event=None):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        self.root.destroy()


def main():
    root = tk.Tk()
    BeatingHeart(root)
    root.mainloop()


if __name__ == "__main__":
    main()
