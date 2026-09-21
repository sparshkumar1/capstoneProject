"""Derive the ICETC page-economy version of Paper 1 from paper1/manuscript.md (v2) by applying only
prose cuts to redundant material. Limitations, oracle design, matrix, results and threat model are untouched."""
import re, sys
SRC = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts\paper1\manuscript.md"
DST = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts\venue\icetc2026\ICETC_PORT_MANUSCRIPT.md"
t = open(SRC, encoding="utf-8").read()

def sub_para(start, new):
    global t
    pat = re.compile(r"^" + re.escape(start) + r".*?$", re.M)
    assert len(pat.findall(t)) == 1, start
    t = pat.sub(lambda m: new, t)

# header
t = re.sub(r"<!-- PAPER 1 MANUSCRIPT v2.*?-->\n", "<!-- ICETC 2026 PORT (page-economy version) derived from paper1/manuscript.md v2 by audit_v2/_make_icetc_port.py. Prose cuts only; see ICETC_PAGE_BUDGET.md for the list. Not yet placed in the IEEE template. -->\n", t, count=1)

# the port stays author-neutral: names are injected only into the master copy by venue/ICETC_P1/build_icetc_docx.py
t = re.sub(r"^\*\*Authors \(author-identifying master.*$", "*Authors and affiliations: withheld in this draft (anonymity rule of the target venue not verified).*", t, flags=re.M)

# Introduction paragraph 2 and 3 condensed
sub_para("Existing work supplies methods for each part:",
         "Existing work supplies methods for each part: sandbox evaluation with fixed programs or adaptive agents judged by host-side signals [1]–[3], [6], [7]; fault injection for services and LLM-agent systems [8]–[10]; and studies of manipulation of LLM graders [11]–[13]. What is less explicit, for one implemented pipeline, is a property-by-property statement of what was demonstrated, with which oracle, on which system and in which environment, and where the test cannot tell. Each concern here becomes a named property, a test condition, an oracle that does not rely on the component under test and, where possible, a deliberately weakened control that shows the oracle can register a failure.")
sub_para("We ran three campaigns:",
         "We ran three campaigns: containment of nine attack programs in the code sandbox (X1-C), fault injection for failure handling (X1-A), and a fixed-turn invariance test of score-related observables against language-model-written feedback (X1-B-I). Every scenario was repeated five times as a deterministic repeatability check, not a random sample; no inferential statistics are attached.")

# Related work: two paragraphs -> one
m = re.search(r"## II\. Related Work\n\n.*?\n\n## III\.", t, re.S)
assert m
t = t.replace(m.group(0), "## II. Related Work\n\n"
 "Containers share the host kernel, and containment depends on configuration and threat model [3]. Sandbox benchmarks score escape by host flag retrieval, with deliberately introduced weaknesses [1], or by outcomes observed by test code across 51 manually written cases [2]; a comparative study separates pass, fail, partial, inconclusive and skipped verdicts [3]; commentary recommends state checks and canary tokens over an agent's own report [6], [7]; a framework proposes composing evidence into a bounded claim [4]; and a survey attributes high denylist failure rates to a third-party study [5]. Injecting named faults is established for services [8] and has been applied to LLM-based agent systems [9], [10], whose evaluations concern task success; separating model output from privileged actions is an established pattern [11]; and studies of LLM-based grading report that injected instructions can change grades [12], [13]. The present study applies fixed programs, host-side observables, weakened controls and bounded verdicts to one shipped configuration and to one model-text channel. It does not measure escape capability against adaptive attackers.\n\n## III.")

# Discussion paragraphs condensed
sub_para("**Executor status as oracle.**",
         "**Executor status as oracle.** In this harness the status string was identical across contained and breached runs for five attacks (SEC-02, -05, -07, -08 and -09; for the CPU loop only the execution time differed), consistent with the advice to check state rather than trust reported outcomes [6], [7]; this does not show that status strings are uninformative in general.")
sub_para("**Model authority.**",
         "**Model authority.** Grader-injection studies [11]–[13] concern models that grade; here the model does not grade, and the question is whether its text reaches score observables. The evidence covers one channel, with fixed evaluator output, 36 single-sentence injections and unseeded generation.")
sub_para("The study reports observed behaviour of specified scenarios",
         "The study reports observed behaviour of specified scenarios on named systems; it is closer to dependability testing of a pipeline with security-relevant components than to a security evaluation, makes no adversary-capability claim and carries no proof.")

# Section VIII condensed (keeps the not-public, not-independent-reproduction and AI statements)
m = re.search(r"## VIII\. Reproducibility and Artifact Availability\n\n.*?\n\n## IX\.", t, re.S)
assert m
t = t.replace(m.group(0), "## VIII. Reproducibility and Artifact Availability\n\n"
 "Harness scripts, protocols, per-run records, output hashes and the environment record are stored in the project repository, which is not publicly released in this draft; output directories are write-once and each harness checks the tagged blobs against the SUT tag. Timings are machine-dependent and model generation is unseeded, so only counts are reproducible. Artifact availability is not independent reproduction, which has not been performed.\n\n## IX.")

# acknowledgments (IEEE requires AI-generated-content disclosure in the acknowledgments section)
ack = ("\n## Acknowledgment\n\n"
       "[TO BE FINALIZED BY THE AUTHORS AGAINST THE ICETC/IEEE POLICY — see cross/AI_USE_DISCLOSURE_DRAFT.md. IEEE's policy for conference submissions (Author Center, read 2026-09-21) states that AI-generated content, including text, figures, images and code, shall be disclosed in the acknowledgments section, identifying the AI system and the sections concerned and briefly the level of use; editing and grammar use is outside the policy but disclosure is recommended.]\n")
t = t.replace("\n## References\n", ack + "\n## References\n", 1)
t = t.replace("](../figures/", "](../../figures/")
open(DST, "w", encoding="utf-8").write(t)
body = re.sub(r"<!--.*?-->", "", t, flags=re.S).split("## References")[0]
print("ICETC port body words:", len(body.split()))
ab = re.search(r"\*\*Abstract—\*\* (.*?)\n", t).group(1)
print("abstract words:", len(ab.split()))
