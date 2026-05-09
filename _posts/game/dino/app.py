import time
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

class ChromeDinoEnv(gym.Env):
    """
    Chrome Dino 游戏自定义 Gym 环境
    """
    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, render_mode="human", headless=False):
        super(ChromeDinoEnv, self).__init__()

        # 定义动作空间: 0: 无操作, 1: 跳跃 (Up), 2: 蹲下 (Down)
        self.action_space = spaces.Discrete(3)

        # 定义观察空间: [当前速度, 障碍物xPos, 障碍物yPos, 障碍物width]
        # 使用 float32 兼容主流 RL 库
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0]), 
            high=np.array([100, 1000, 500, 200]), 
            dtype=np.float32
        )

        # Selenium 配置
        options = Options()
        if headless:
            ...
            # options.add_argument("--headless")
        # options.set_preference("media.volume_scale", "0.0")
        
        service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.set_window_size(1100, 650)
        self.url = "https://chromedino.com"
        
        self.body = None
        self._is_ducking = False
        self._load_game()

    def _load_game(self):
        self.driver.get(self.url)
        # 等待 Runner 加载
        while not self.driver.execute_script("return typeof Runner !== 'undefined'"):
            time.sleep(0.5)
        self.body = self.driver.find_element(By.TAG_NAME, "body")

    def _get_obs(self):
        """获取当前游戏状态"""
        # 获取最近的一个障碍物
        obs_data = self.driver.execute_script("""
            var runner = Runner.instance_;
            var obs = runner.horizon.obstacles[0];
            return {
                speed: runner.currentSpeed,
                xPos: obs ? obs.xPos : 1000,
                yPos: obs ? obs.yPos : 0,
                width: obs ? obs.width : 0
            };
        """)
        return np.array([
            obs_data['speed'],
            obs_data['xPos'],
            obs_data['yPos'],
            obs_data['width']
        ], dtype=np.float32)

    def reset(self, seed=None, options=None):
        """重置环境"""
        super().reset(seed=seed)
        
        # 如果已经结束，按空格重启；如果是首次启动，也按空格
        self.body.send_keys(Keys.SPACE)
        time.sleep(0.5) # 等待动画
        
        observation = self._get_obs()
        info = {}
        return observation, info

    def step(self, action):
        """执行动作并返回结果"""
        # 执行动作
        if action == 1: # Jump
            self.body.send_keys(Keys.ARROW_UP)
            if self._is_ducking: self._is_ducking = False
        elif action == 2: # Duck
            if not self._is_ducking:
                ActionChains(self.driver).key_down(Keys.ARROW_DOWN).perform()
                self._is_ducking = True
        else: # No-op or end ducking
            if self._is_ducking:
                ActionChains(self.driver).key_up(Keys.ARROW_DOWN).perform()
                self._is_ducking = False

        # 获取状态
        obs = self._get_obs()
        
        # 检测是否碰撞
        terminated = self.driver.execute_script("return Runner.instance_.crashed;")
        
        # 奖励机制
        # 存活每一帧给 0.1 奖励，碰撞扣 10 分
        reward = 0.1 if not terminated else -10.0
        
        truncated = False
        info = {"score": self.driver.execute_script("return Runner.instance_.distanceMeter.digits").join("")}
        
        return obs, reward, terminated, truncated, info

    def render(self):
        # 浏览器本身就是渲染窗口
        pass

    def close(self):
        if self.driver:
            self.driver.quit()

# --- 测试运行 ---
if __name__ == "__main__":
    env = ChromeDinoEnv(headless=False)
    
    for episode in range(3):
        obs, info = env.reset()
        done = False
        total_reward = 0
        
        print(f"开始第 {episode + 1} 局游戏...")
        
        while not done:
            # 这里可以用你的 AI 逻辑代替随机动作
            # 示例：简单的阈值判断
            if obs[1] < 150: # 如果障碍物 xPos < 150
                action = 1   # 跳
            else:
                action = 0   # 不动
                
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            if terminated or truncated:
                done = True
                print(f"游戏结束，总奖励: {total_reward:.2f}")
                time.sleep(1)

    env.close()