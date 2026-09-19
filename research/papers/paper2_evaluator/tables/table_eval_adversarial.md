# Adversarial Keyword-Stuffing Resistance (EXP-EVAL-2)

Evaluation of reasoning-conditioned concept dampening ($S_{2,\text{eff}} = S_2 \times 0.60$ when $R \le 0.30$):

| QID | Topic | Condition | $S_1$ | $S_2$ | $R$ (Reasoning) | $S_{2,\text{eff}}$ | Undampened | Final Score | Grade | Dampening Triggered? |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Q1 | Arrays & Hashing (Two Sum) | **Authentic Technical** | 0.433 | 1.000 | 0.643 | 1.000 | 0.736 | 0.737 | Good | No |
| Q1 | Arrays & Hashing (Two Sum) | **Keyword Stuffing** | 0.284 | 0.500 | 0.439 | 0.500 | 0.437 | 0.437 | Average | No |
| Q1 | Arrays & Hashing (Two Sum) | **Superficial** | 0.271 | 0.500 | 0.153 | 0.300 | 0.292 | 0.222 | Poor | YES (Triggered) |
| Q3 | Linked Lists (Reverse) | **Authentic Technical** | 0.521 | 1.000 | 0.726 | 1.000 | 0.721 | 0.721 | Good | No |
| Q3 | Linked Lists (Reverse) | **Keyword Stuffing** | 0.298 | 0.500 | 0.529 | 0.500 | 0.484 | 0.484 | Average | No |
| Q3 | Linked Lists (Reverse) | **Superficial** | 0.296 | 0.500 | 0.334 | 0.500 | 0.316 | 0.316 | Poor | No |
| Q10 | Binary Trees (BFS Traversal) | **Authentic Technical** | 0.471 | 1.000 | 0.654 | 1.000 | 0.748 | 0.748 | Good | No |
| Q10 | Binary Trees (BFS Traversal) | **Keyword Stuffing** | 0.469 | 0.750 | 0.588 | 0.750 | 0.627 | 0.600 | Good | No |
| Q10 | Binary Trees (BFS Traversal) | **Superficial** | 0.372 | 0.000 | 0.251 | 0.000 | 0.131 | 0.131 | Poor | YES (Triggered) |
| Q41 | C Programming (Pointers) | **Authentic Technical** | 0.631 | 0.750 | 0.446 | 0.750 | 0.500 | 0.500 | Average | No |
| Q41 | C Programming (Pointers) | **Keyword Stuffing** | 0.567 | 0.750 | 0.363 | 0.750 | 0.619 | 0.619 | Good | No |
| Q41 | C Programming (Pointers) | **Superficial** | 0.499 | 0.250 | 0.163 | 0.150 | 0.134 | 0.099 | Poor | YES (Triggered) |
| Q7 | Dynamic Programming (Climbing Stairs) | **Authentic Technical** | 0.203 | 0.000 | 0.407 | 0.000 | 0.264 | 0.264 | Poor | No |
| Q7 | Dynamic Programming (Climbing Stairs) | **Keyword Stuffing** | 0.104 | 0.000 | 0.307 | 0.000 | 0.169 | 0.169 | Poor | No |
| Q7 | Dynamic Programming (Climbing Stairs) | **Superficial** | 0.167 | 0.250 | 0.181 | 0.150 | 0.003 | 0.000 | Poor | YES (Triggered) |
