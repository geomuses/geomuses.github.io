"""
Chrome Dino Run — Firefox 版 Python 自动控制脚本
==================================================
Firefox 无法直接访问 chrome://dino，
本脚本改用第三方镜像页面：
    https://chromedino.com   （完全复刻，JS Runner API 相同）

依赖安装:
    pip install selenium webdriver-manager

运行方式:
    python dino_firefox.py [mode]

    mode:
        manual  — 打开游戏，手动玩（默认）
        auto    — AI 自动避障（读取障碍物坐标）
        demo    — 演示跳跃 / 蹲下动作序列
"""

import sys
import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager


# ─────────────────────────────────────────────────────────────────────────────
# 游戏页面（Firefox 无法访问 chrome://dino，使用第三方完整复刻）
# ─────────────────────────────────────────────────────────────────────────────
DINO_URL = "https://chromedino.com"


# ─────────────────────────────────────────────────────────────────────────────
# 浏览器启动
# ─────────────────────────────────────────────────────────────────────────────
def create_driver(headless: bool = False) -> webdriver.Firefox:
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.set_preference("media.volume_scale", "0.0")   # 静音

    service = Service(GeckoDriverManager().install())
    driver  = webdriver.Firefox(service=service, options=options)
    driver.set_window_size(1100, 650)
    return driver


# ─────────────────────────────────────────────────────────────────────────────
# DinoController
# ─────────────────────────────────────────────────────────────────────────────
class DinoController:
    """
    封装所有对 Dino 游戏的控制与状态读取。
    chromedino.com 与 chrome://dino 共享同一份 Runner.js，
    JS API 完全相同。
    """

    # ── JS 状态读取片段 ──────────────────────────────────────────────────────
    _JS_RUNNER   = "return typeof Runner !== 'undefined' && Runner.instance_ !== null;"
    _JS_CRASHED  = "return Runner.instance_.crashed;"
    _JS_PLAYING  = "return Runner.instance_.playing;"
    _JS_SPEED    = "return Runner.instance_.currentSpeed;"
    _JS_SCORE    = "return Runner.instance_.distanceMeter.digits;"
    _JS_OBSTACLES = """
        return Runner.instance_.horizon.obstacles.map(function(o){
            return {
                type:  o.typeConfig.type,
                xPos:  o.xPos,
                yPos:  o.yPos,
                width: o.width,
                speed: o.speed
            };
        });
    """

    def __init__(self, driver: webdriver.Firefox):
        self.driver   = driver
        self.body     = None
        self._ducking = False

    # ── 打开游戏 ──────────────────────────────────────────────────────────────
    def open(self):
        self.driver.get(DINO_URL)
        print(f"[DinoController] 正在加载：{DINO_URL}")

        # 等待页面完全加载（最多 15 秒）
        for _ in range(30):
            time.sleep(0.5)
            if self._js_ready():
                break
        else:
            print("[警告] Runner 未能在预期时间内就绪，尝试继续...")

        self.body = self.driver.find_element(By.TAG_NAME, "body")
        print("[DinoController] 页面就绪 ✓")

    def _js_ready(self) -> bool:
        try:
            return bool(self.driver.execute_script(self._JS_RUNNER))
        except Exception:
            return False

    # ── 基本动作 ──────────────────────────────────────────────────────────────
    def start(self):
        """按空格启动游戏"""
        self.body.send_keys(Keys.SPACE)
        print("[Action] ▶  开始游戏")
        time.sleep(0.4)

    def jump(self):
        """跳跃"""
        self.body.send_keys(Keys.ARROW_UP)
        print("[Action] ↑  跳跃")

    def duck_start(self):
        """按住 ↓ 开始蹲下"""
        ac = ActionChains(self.driver)
        ac.key_down(Keys.ARROW_DOWN).perform()
        self._ducking = True
        print("[Action] ↓  蹲下（按住）")

    def duck_end(self):
        """松开 ↓ 站起"""
        ac = ActionChains(self.driver)
        ac.key_up(Keys.ARROW_DOWN).perform()
        self._ducking = False
        print("[Action] ↑  起身（松开）")

    def duck_for(self, seconds: float = 0.4):
        """蹲下 seconds 秒后自动起身"""
        self.duck_start()
        time.sleep(seconds)
        self.duck_end()

    # ── 状态读取 ──────────────────────────────────────────────────────────────
    def is_crashed(self) -> bool:
        try:
            return bool(self.driver.execute_script(self._JS_CRASHED))
        except Exception:
            return False

    def is_playing(self) -> bool:
        try:
            return bool(self.driver.execute_script(self._JS_PLAYING))
        except Exception:
            return False

    def get_speed(self) -> float:
        try:
            return float(self.driver.execute_script(self._JS_SPEED))
        except Exception:
            return 0.0

    def get_score(self) -> str:
        try:
            digits = self.driver.execute_script(self._JS_SCORE)
            return "".join(str(d) for d in digits)
        except Exception:
            return "00000"

    def get_obstacles(self) -> list:
        try:
            return self.driver.execute_script(self._JS_OBSTACLES) or []
        except Exception:
            return []

    def restart(self):
        """碰撞后重新开始"""
        self.body.send_keys(Keys.SPACE)
        self._ducking = False
        print("[Action] ↺  重新开始")
        time.sleep(0.5)


# ─────────────────────────────────────────────────────────────────────────────
# 模式 1：演示动作序列
# ─────────────────────────────────────────────────────────────────────────────
def demo_mode(ctrl: DinoController):
    print("\n=== DEMO 模式：自动演示跳跃 / 蹲下 ===\n")
    ctrl.open()
    ctrl.start()
    time.sleep(1)

    sequence = [
        ("jump", None),
        ("jump", None),
        ("duck", 0.5),
        ("jump", None),
        ("duck", 0.8),
        ("jump", None),
        ("jump", None),
        ("duck", 0.4),
        ("duck", 0.6),
        ("jump", None),
    ]

    for idx, (act, param) in enumerate(sequence):
        if ctrl.is_crashed():
            print("撞到了！Demo 提前结束")
            break
        label = f"蹲 {param}s" if act == "duck" else "跳"
        print(f"  步骤 {idx+1:02d}: {label}")
        if act == "jump":
            ctrl.jump()
        else:
            ctrl.duck_for(param)
        time.sleep(random.uniform(0.7, 1.3))

    print(f"\nDemo 结束，最终分数：{ctrl.get_score()}")


# ─────────────────────────────────────────────────────────────────────────────
# 模式 2：AI 自动避障
# ─────────────────────────────────────────────────────────────────────────────
def auto_mode(ctrl: DinoController, max_games: int = 5):
    """
    规则 AI：
      障碍物类型     | 动作
      仙人掌        | x < 触发距离 → jump()
      低飞鸟        | x < 触发距离 → duck_for()
      高飞鸟        | 跑过不操作

    触发距离 = BASE + speed × 系数（速度越快越早触发）
    """
    print("\n=== AUTO 模式：AI 自动控制（最多 %d 局）===\n" % max_games)
    ctrl.open()
    ctrl.start()
    time.sleep(0.8)

    TRIGGER_BASE   = 280   # 基础触发 x 阈值（像素）
    SPEED_FACTOR   = 9     # 每单位速度增加的像素
    DUCK_Y_CUTOFF  = 80    # 鸟 yPos > 此值 → 低飞 → 需要蹲
    COOLDOWN       = 0.28  # 动作冷却（秒）

    last_action = 0.0
    game_count  = 0

    try:
        while game_count < max_games:
            # ── 检测碰撞 ──
            if ctrl.is_crashed():
                score = ctrl.get_score()
                spd   = ctrl.get_speed()
                print(f"\n  [碰撞] 第 {game_count+1} 局  分数={score}  速度={spd:.1f}")
                game_count += 1
                if game_count < max_games:
                    time.sleep(1.2)
                    ctrl.restart()
                    time.sleep(0.8)
                    last_action = 0.0
                continue

            now       = time.time()
            speed     = ctrl.get_speed()
            obstacles = ctrl.get_obstacles()
            trigger   = TRIGGER_BASE + speed * SPEED_FACTOR

            for obs in obstacles:
                x = obs.get("xPos", 9999)
                if x > trigger:
                    continue                    # 还太远，忽略

                if (now - last_action) < COOLDOWN:
                    break                       # 冷却中，不再处理

                otype = obs.get("type", "")
                y_pos = obs.get("yPos", 0)

                if otype == "PTERODACTYL":
                    if y_pos > DUCK_Y_CUTOFF:   # 低飞鸟
                        print(f"  [AI] 蹲下  鸟 yPos={y_pos:.0f}  x={x:.0f}")
                        ctrl.duck_for(0.45)
                        last_action = now
                    # 高飞鸟直接跑过，不操作
                else:                           # 仙人掌
                    if ctrl._ducking:
                        ctrl.duck_end()
                    print(f"  [AI] 跳跃  仙人掌 x={x:.0f}  speed={speed:.1f}")
                    ctrl.jump()
                    last_action = now
                break   # 每帧只处理最近一个障碍物

            # 若远离障碍物则自动起身
            if ctrl._ducking:
                near = [o for o in obstacles if o.get("xPos", 9999) < trigger + 120]
                if not near:
                    ctrl.duck_end()

            time.sleep(0.018)   # ~55 Hz

    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        if ctrl._ducking:
            ctrl.duck_end()
        print(f"\nAuto 结束，共完成 {game_count} 局")


# ─────────────────────────────────────────────────────────────────────────────
# 模式 3：手动模式
# ─────────────────────────────────────────────────────────────────────────────
def manual_mode(ctrl: DinoController):
    print("\n=== MANUAL 模式：在浏览器中手动游玩 ===")
    print(f"已打开：{DINO_URL}")
    print("脚本会监控分数和碰撞，碰撞后自动打印结果。")
    print("按 Ctrl+C 退出。\n")
    ctrl.open()
    ctrl.start()

    try:
        game = 1
        while True:
            if ctrl.is_crashed():
                score = ctrl.get_score()
                spd   = ctrl.get_speed()
                print(f"[第 {game} 局结束]  分数={score}  最终速度={spd:.1f}")
                game += 1
                time.sleep(2)
                ctrl.restart()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n退出")


# ─────────────────────────────────────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────────────────────────────────────
def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "manual").lower()
    if mode not in ("manual", "auto", "demo"):
        print("未知模式，可选：manual | auto | demo")
        sys.exit(1)

    print("=" * 50)
    print(f"  Dino Controller — Firefox 版")
    print(f"  模式: {mode.upper()}")
    print(f"  目标: {DINO_URL}")
    print("=" * 50)
    print("正在启动 Firefox...")

    driver = create_driver(headless=False)
    ctrl   = DinoController(driver)

    try:
        if mode == "demo":
            demo_mode(ctrl)
        elif mode == "auto":
            auto_mode(ctrl, max_games=5)
        else:
            manual_mode(ctrl)
    finally:
        input("\n按 Enter 关闭浏览器...")
        driver.quit()
        print("已关闭，再见！")


if __name__ == "__main__":
    main()
