# from keras.models import Sequential
# from keras.layers import Dense, Flatten
# from keras.models import load_model
# from keras.optimizers import Adam
# import numpy as np
# model = Sequential()
# arr = [
#     np.array([
#         [1, 1, 1, 1],
#         [1, 1, 1, 1],
#         [1, 1, 1, 1]
#     ]).T,
#     np.array([2, 2, 2]),
#     np.array([
#         [3, 3, 3],
#         [3, 3, 3],
#         [3, 3, 3]
#     ]),
#     np.array([4, 4, 4]),
#     np.array(
#         [5, 5, 5]
#     ).reshape(3, 1),
#     np.array([3])
# ]
# import os
# root = os.path.abspath(os.path.dirname(__file__))
# model.add(Dense(units=3, input_dim=4, activation="relu"))
# model.add(Dense(units=3, activation="relu"))
# model.add(Dense(units=1, activation="linear"))
# model.compile(loss="mse", optimizer=Adam(learning_rate=0.01))
# model.set_weights(arr)
# # # print(model.summary())
# print(model.get_weights())
# # print(model.save("model.h5"))
# # arr = load_model('model.h5')
# print(model.predict(np.array([1, 2, 3, 4]).reshape(1, 4))[0])
# from TetrisBattle.envs.tetris_env import TetrisSingleEnv
# import numpy as np
# env = TetrisSingleEnv(obs_type="suze", mode="grid")
# a = env.reset()
#
#
# ob, _ , _ , _ = env.step(4)
#
# # print(np.array(np.array(ob).squeeze()[:20, 10:17]))