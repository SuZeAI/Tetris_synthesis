import pygame.display

from funcionplus import *
from TetrisBattle.envs.tetris_env import TetrisSingleEnv
from tqdm import tqdm
from DQN import *
import copy
import time
import numpy as np


if __name__ == "__main__":
    env = TetrisSingleEnv(mode="suzeai", obs_type="grid")
    ob = env.reset()
    current = [0, 0, 0, 0]
    epochs = 1500
    # for i in range(100):
    #     ob, _, done, _ = env.step(env.random_action())
    #     print(PIECE_NUM2TYPE[np.array(ob).squeeze()[:20, 10:17][1, :].argmax() + 1])
    #     time.sleep(1)
    #     if done:
    #         break

    agent = Agent(state_size=4, discount=0.98, replay_mem_size=20000,
                  minibatch_size=512, epsilon=1,
                  epsilon_stop_epsisode=1500, epsilon_min=1e-3,
                  learning_rate=1e-3, loss="mse",
                  optimizer=Adam, hidden_dims=[64, 64],
                  activations=["relu", "relu", "linear"]
                  )

    for epoch in tqdm(range(epochs)):
        ob = env.reset()
        current = [0, 0, 0, 0]
        done = False
        print("epoch:", epoch)
        while not done:
            grid = np.array(np.array(ob).squeeze()[:20, :10], dtype="int64")
            # feature = np.array(ob).squeeze()[:20, 10:17]
            piece, x, y = get_piece(ob)
            if not piece:
                break
            # piece = np.array(PIECES_DICT[PIECE_NUM2TYPE[feature[1, :].argmax() + 1]], dtype="int64")
            next_state = get_next_states(np.array(grid, dtype="int64"), np.array(piece, dtype="int64"))
            best_state = agent.get_best_state(next_state.values())
            best_action = None
            for action, state in next_state.items():
                if best_state == state:
                    best_action = action
                    break
            score = 0
            ls = []
            print(best_action, x)
            ls += [4 for i in range(best_action[1])]
            if best_action[0] > x:
                ls += [5 for i in range(best_action[0] - x)]
            else:
                ls += [6 for i in range(x - best_action[0])]
            ls += [2]
            print(ls)
            for i in ls:
                print(i)
                ob, reward, done, infos = env.step(i)
                pygame.display.update()
                score += reward
                # print(get_grid(ob))
                # time.sleep(0.5)
                if infos["is_fallen"]:
                    break

            if done:
                break

            agent.update_mem_replay(current, best_action, next_state[best_action], score, done)
            current = next_state[best_action]

        agent.trainModel(epochs=1)
        if env.accum_rewards >= 100:
            break



