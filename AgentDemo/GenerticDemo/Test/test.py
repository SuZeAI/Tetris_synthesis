import time

from Agent import Agent
from TetrisBattle.envs.tetris_env import *
ag = Agent(1)

env = TetrisSingleEnv(mode="suze", obs_type="grid")
ob = env.reset()
done = False
while not done:
    ob, reward, done, infos = env.step(ag.choose_action(ob))

time.sleep(100)
