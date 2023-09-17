from Env1.envs.tetris_env import TetrisDoubleEnv
# from AgentTest import Agent
# import AgentTest3Weight0
# import AgentTest3

env = TetrisDoubleEnv(gridchoice="none", obs_type="grid", mode="")

done = False
state = env.reset()
agent_list = [AgentTest3Weight0.Agent(0), AgentTest3.Agent(1)]

while not done:
    # img = env.render(mode='rgb_array') # img is rgb array, you need to render this or can check my colab notebook in readme file
    action = agent_list[env.game_interface.getCurrentPlayerID()].choose_action(state)
    state, reward, done, _ = env.step(action)
    env.take_turns()
