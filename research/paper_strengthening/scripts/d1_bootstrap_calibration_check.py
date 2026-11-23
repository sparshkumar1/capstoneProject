"""
Monte Carlo calibration check of D1's topic-mean-of-means percentile bootstrap
(V7 §2 estimator), under D1's EXACT confirmatory cluster-size structure
(31 topics, 67 questions: 19 singletons, six size-2 topics, one each of
size 3/4/5, three size-8 topics), simulated under a TRUE NULL (no real
effect). This is a pure statistical-methodology check on synthetic random
numbers -- it calls no model, generates no benchmark item, and makes no
claim about the evaluator. It exists only to check whether the bootstrap
procedure itself is well-calibrated for this specific cluster structure,
replacing a general literature citation with design-specific evidence.

Checked conditions:
  - i.i.d. N(0,1) per-question noise (no between-topic heterogeneity)
  - two-level null: topic effect ~ N(0, tau) + N(0,1) question noise,
    tau in {0, 0.3, 0.6} -- a nuisance between-topic variance component,
    with the true OVERALL mean still exactly 0
  - heavy-tailed noise (Student-t, df=3) under tau=0.3, as a robustness
    check against the Gaussian assumption
"""
import numpy as np

SIZES = [1] * 19 + [2] * 6 + [3, 4, 5] + [8, 8, 8]
assert len(SIZES) == 31 and sum(SIZES) == 67

# N_OUTER=3000 (an earlier version of this script) was underpowered: it
# returned 0.0507 for the tau=0 condition, misleadingly close to nominal by
# Monte Carlo chance alone (MC SE ~0.004 at that N). Re-run at N_OUTER=12000
# (MC SE ~0.002) before trusting any of these rates -- this comment and the
# discrepancy are kept deliberately, as a documented lesson, not scrubbed.
N_OUTER = 12000
B_INNER = 2000


def one_sim(rng, tau: float, dist: str = "normal") -> bool:
    topic_effects = rng.normal(0, tau, size=31)
    topic_vals = []
    for t, s in zip(topic_effects, SIZES):
        noise = rng.normal(0, 1, size=s) if dist == "normal" else rng.standard_t(df=3, size=s)
        topic_vals.append(t + noise)
    topic_means = np.array([v.mean() for v in topic_vals])
    idx = rng.integers(0, 31, size=(B_INNER, 31))
    boot_means = topic_means[idx].mean(axis=1)
    p_value = np.mean(boot_means <= 0)  # one-sided, matches P1-i's rejection rule direction
    return p_value <= 0.05


def run(tau: float, dist: str, seed: int):
    rng = np.random.default_rng(seed)
    rejections = sum(one_sim(rng, tau, dist) for _ in range(N_OUTER))
    rate = rejections / N_OUTER
    se = (rate * (1 - rate) / N_OUTER) ** 0.5
    return rate, se


if __name__ == "__main__":
    print(f"N_OUTER={N_OUTER}, B_INNER={B_INNER}, nominal alpha=0.05\n")
    for tau in (0.0, 0.3, 0.6):
        rate, se = run(tau, "normal", seed=2026 + int(tau * 10))
        print(f"tau={tau:<4} normal noise : Type-I rate={rate:.4f}  95% MC CI=[{rate-1.96*se:.4f}, {rate+1.96*se:.4f}]")
    rate, se = run(0.3, "t3", seed=31415)
    print(f"tau=0.3 heavy-tailed(t,df=3): Type-I rate={rate:.4f}  95% MC CI=[{rate-1.96*se:.4f}, {rate+1.96*se:.4f}]")
