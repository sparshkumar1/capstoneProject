# X3-0c follow-up: sessions where PPO+G differs from Constant-Same+G

Of 125 PPO+G sessions (5 seeds x 25): final-action sequence differs in **50**; the executed difficulty path (after clipping to [1, 5]) differs in **25**; the session MAE differs in **5**. The earlier audit statement '5 of 125 sessions differ' therefore corresponds to the trajectory/outcome definition, not the action-sequence definition; sequences can differ (e.g. an Easier proposed at difficulty 1.0) without changing the executed trajectory.

Per training seed [action-sequence, path, MAE]: {"42": [10, 8, 3], "123": [10, 1, 0], "456": [10, 6, 1], "789": [10, 5, 0], "999": [10, 5, 1]}
