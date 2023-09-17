from TetrisBattle.envs.tetris_env import TetrisSingleEnv
from AgentTest3Weight0 import Agent

if __name__ == "__main__":

    env = TetrisSingleEnv(gridchoice="none", obs_type="grid", mode="")
    done = False
    ob = env.reset()
    # agent = CustomAgent.Agent(0)
    agent = Agent(0)
    while not done:
        action = agent.choose_action(ob)
        ob, reward, done, infos = env.step(action)