# Bibliography / References

IEEE numbered style, per `Report-Guidelines.pdf` §14. **Verification status is marked per entry** — this project's citation-integrity rule requires every reference to trace to a verified source, not be assumed accurate.

**2026-11-13 correction pass:** a fresh, independent live-search re-check (not a repeat of the prior pass, an
additional one) of all 15 entries below found that three had NOT actually been verified accurately by the earlier
pass despite being marked "independently re-verified": [2] had the wrong first-author initial (real author is
Pedro C. Mendonça, not "D. Mendonça") and was missing its volume/issue/article number; [5] (Argos) is dated more
precisely as its confirmed arXiv submission (arXiv:2512.03438, 2025) rather than the vague "Microsoft Research
publication, 2026"; [14] (Chen et al.) was cited as "Proc. ACM ICMI, 2017" but the real, DOI-confirmed publication
is ICMI **'16** (2016). All three are corrected below. [13] (Naim et al.) was also completed with its subtitle and
DOI (not previously wrong, just incomplete). See `FINAL_SOURCE_OF_TRUTH_AND_RECONCILIATION.md`, Finding 3, for the
full verification record (sources checked for every one of the 15 entries, not just these four).

**Independently re-verified via live search in this phase (Chapter 3):**

[1] A. Karjus et al., "Machine-Assisted Grading of Nationwide School-Leaving Essay Exams with LLMs and Statistical NLP," arXiv:2601.16314, 2026.

[2] P. C. Mendonça, F. Quintal, and F. Mendonça, "Evaluating LLMs for Automated Scoring in Formative Assessments," *Applied Sciences*, vol. 15, no. 5, Art. no. 2787, 2025, doi: 10.3390/app15052787.

[3] Y. Wang et al., "AutoSCORE: Enhancing Automated Scoring with Multi-Agent Large Language Models via Structured Component Recognition," arXiv:2509.21910, 2025.

[4] K. Zhu, H. Du et al., "MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents," in *Proc. 63rd Annual Meeting of the Association for Computational Linguistics (ACL)*, vol. 1, pp. 8580–8622, 2025.

[5] Microsoft Research, "Argos: Multimodal Reinforcement Learning with Agentic Verifier for AI Agents," arXiv:2512.03438, 2025. **Note:** cited for its general grounding-reduces-hallucination principle only; its actual scope (multimodal visual/robotics RL verification) differs from how a prior draft of this report's literature review mischaracterized it (as an LLM-text-evaluation framework) — see Chapter 3 §3.4 for the correction.

**Resolved 2026-11-13 (previously flagged as unverified — see Chapter 3 §3.1, §3.4):**

[6] G. Sun, R. Yu, L. Yin, Y. Yang, B. Zhang, and Z. Xu, "CoMAI: A Collaborative Multi-Agent Framework for Robust and Equitable Interview Evaluation," arXiv:2603.16215, 2026. **Replaces** the originally-cited, unlocatable "Wu et al. (2026)" avatar-based interview-evaluation paper.

*(The originally-cited "Auctores Online (2025)" entry is removed — could not be located under any plausible title/author via live search; "Auctores" is a known low-oversight open-access publishing platform name. All subsequent entries renumbered down by one to close the gap.)*

**Carried forward from the Phase-2 report's existing bibliography (`revised_report_v5.pdf`, Ch.8) — foundational, well-established works not independently re-searched in this phase, but consistent with this report's technical content as verified against the actual codebase in Chapter 10:**

[7] D. J. Weiss, "Improving measurement quality and efficiency with adaptive testing," *Applied Psychological Measurement*, vol. 6, no. 4, pp. 473–492, 1982.

[8] J. R. Anderson, A. T. Corbett, K. R. Koedinger, and R. Pelletier, "Cognitive tutors: Lessons learned," *The Journal of the Learning Sciences*, vol. 4, no. 2, pp. 167–207, 1995.

[9] A. T. Corbett and J. R. Anderson, "Knowledge tracing: Modeling the acquisition of procedural knowledge," *User Modeling and User-Adapted Interaction*, vol. 4, no. 4, pp. 253–278, 1994.

[10] A. Graves, M. G. Bellemare, J. Menick, R. Munos, and K. Kavukcuoglu, "Automated curriculum learning for neural networks," in *Proc. ICML*, 2017.

[11] R. Portelas, C. Colas, L. Weng, K. Hofmann, and P. Y. Oudeyer, "Automatic curriculum learning for deep RL: A short survey," in *Proc. IJCAI*, 2020.

[12] I. Naim, M. I. Tanveer, D. Gildea, and M. E. Hoque, "Automated prediction and analysis of job interview performance: The role of what you say and how you say it," in *Proc. 11th IEEE Int. Conf. Workshops Automatic Face and Gesture Recognition (FG)*, 2015, doi: 10.1109/FG.2015.7163127.

[13] L. Chen, G. Feng, C. W. Leong, B. Lehman, and M. Martin-Raugh, "Automated scoring of interview videos using doc2vec multimodal feature extraction paradigm," in *Proc. 18th ACM Int. Conf. Multimodal Interaction (ICMI '16)*, 2016, doi: 10.1145/2993148.2993203.

[14] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, "Proximal policy optimization algorithms," arXiv:1707.06347, 2017.

[15] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," in *Proc. EMNLP*, 2019.

[16] J. Johnson, M. Douze, and H. Jégou, "Billion-scale similarity search with GPUs," *IEEE Transactions on Big Data*, vol. 7, no. 3, pp. 535–547, 2019.
