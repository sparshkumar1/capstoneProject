"""
Metamorphic Testing Suite for PREPAIred Technical Evaluator.
Validates 5 metamorphic relations:
- MG-1: Paraphrase Invariance (|Delta score| <= 0.10)
- MG-2: Irrelevant Text Addition (Delta score <= 0.05, no ungrounded inflation)
- MG-3: Keyword Stuffing Resistance (R <= 0.30 dampens S2, score <= 0.50)
- MG-4: Concept Deletion (Monotonic drop: Delta score < 0)
- MG-5: Negation Inversion (Severe penalty: Delta score <= -0.20)
"""
import csv
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from services.evaluator.app import evaluate, get_rubric

TEST_CASES = [
    {
        "case_id": "META-01",
        "qid": 1,
        "question": "Explain your logic to find the two indices in an array that sum up to a target value.",
        "baseline_answer": "We maintain a hash map from visited numbers to their array indices. While iterating through the array, for each number x, we compute complement = target - x. If the complement exists in the map, we return its index along with the current index. Otherwise, we store x and its index in the map.",
        "transformations": {
            "MG-1_paraphrase": "A hash table is utilized to record elements previously traversed alongside their corresponding positions. During a single pass over the array, we calculate the difference between the target and the current item. If this difference is already stored in the hash table, we immediately output both indices. If not, the current number is mapped to its index.",
            "MG-2_irrelevant_addition": "We maintain a hash map from visited numbers to their array indices. While iterating through the array, for each number x, we compute complement = target - x. If the complement exists in the map, we return its index along with the current index. Otherwise, we store x and its index in the map. In my spare time I enjoy competitive programming and playing chess with friends on weekends.",
            "MG-3_keyword_injection": "Hash map indices complement target lookup array O(N) single pass dictionary key value pair.",
            "MG-4_concept_deletion": "We iterate through the array. For each number x we check if something exists. Otherwise we continue scanning until the end.",
            "MG-5_negation_inversion": "Do not use a hash map or record past numbers because lookups are useless. Instead randomly pick two array indices and assert they will always sum to the target without checking."
        }
    },
    {
        "case_id": "META-02",
        "qid": 3,
        "question": "Describe the approach to reverse a singly linked list in-place.",
        "baseline_answer": "Initialize three pointers: prev as NULL, curr as head, and next_node as NULL. While curr is not NULL, store curr->next in next_node, then redirect curr->next to prev. Move prev forward to curr, and curr forward to next_node. When curr reaches NULL, prev is the new head of the reversed list.",
        "transformations": {
            "MG-1_paraphrase": "Set up a previous pointer to NULL and current pointer to head. As long as current is not NULL, save current.next in a temporary reference, redirect current.next to point back to previous, advance previous to current, and advance current to the saved reference. Finally return previous as the new head.",
            "MG-2_irrelevant_addition": "Initialize three pointers: prev as NULL, curr as head, and next_node as NULL. While curr is not NULL, store curr->next in next_node, then redirect curr->next to prev. Move prev forward to curr, and curr forward to next_node. When curr reaches NULL, prev is the new head. Linked lists are fundamental pointer-based linear data structures commonly taught in sophomore CS courses.",
            "MG-3_keyword_injection": "Three pointers prev curr next pointer redirection in-place O(1) memory head update reverse singly linked list.",
            "MG-4_concept_deletion": "Initialize three pointers: prev as NULL, curr as head, and next_node as NULL. Walk through the list until reaching NULL.",
            "MG-5_negation_inversion": "Never change pointer directions because modifying curr->next creates severe memory leaks. Instead leave all forward pointers completely untouched and claim the list is reversed."
        }
    },
    {
        "case_id": "META-03",
        "qid": 10,
        "question": "Explain the BFS (Level Order) traversal logic for a binary tree.",
        "baseline_answer": "Breadth-first search traverses the tree level by level using a FIFO queue. We start by enqueueing the root node. While the queue is not empty, we dequeue a node, process its value, and enqueue its left child and right child if they are not null. This ensures all nodes at depth d are visited before depth d+1.",
        "transformations": {
            "MG-1_paraphrase": "Level order traversal processes nodes layer by layer utilizing a first-in first-out queue. Initially, push the tree root onto the queue. In a loop until the queue is drained, pop the front node, record it, and push both its non-null left and right child pointers into the queue.",
            "MG-2_irrelevant_addition": "Breadth-first search traverses the tree level by level using a FIFO queue. We start by enqueueing the root node. While the queue is not empty, we dequeue a node, process its value, and enqueue its left child and right child if they are not null. This ensures all nodes at depth d are visited before depth d+1. Binary search trees have worst-case height O(N) when degenerate.",
            "MG-3_keyword_injection": "Queue FIFO level order breadth first search root left child right child depth order traversal enqueue dequeue.",
            "MG-4_concept_deletion": "Level order traversal visits all nodes in the tree. We start at the root node and visit nodes one after another.",
            "MG-5_negation_inversion": "BFS never uses a queue; it uses a recursive call stack that dives deep into the leftmost leaf first and explicitly avoids visiting nodes level by level."
        }
    }
]

def run_metamorphic_suite():
    records = []
    summary_by_relation = {
        "MG-1_paraphrase": {"total": 0, "passed": 0, "deltas": []},
        "MG-2_irrelevant_addition": {"total": 0, "passed": 0, "deltas": []},
        "MG-3_keyword_injection": {"total": 0, "passed": 0, "scores": []},
        "MG-4_concept_deletion": {"total": 0, "passed": 0, "deltas": []},
        "MG-5_negation_inversion": {"total": 0, "passed": 0, "deltas": []},
    }

    print("Running Metamorphic Testing Suite across evaluation relations...\n")

    for tc in TEST_CASES:
        rubric = get_rubric(tc["qid"])
        base_res = evaluate(tc["question"], tc["baseline_answer"], rubric)
        base_score = base_res["technical_correctness"]
        base_r = base_res["reasoning_quality"]
        base_s2 = base_res["concept_coverage"]

        for rel, trans_text in tc["transformations"].items():
            trans_res = evaluate(tc["question"], trans_text, rubric)
            trans_score = trans_res["technical_correctness"]
            trans_r = trans_res["reasoning_quality"]
            trans_s2 = trans_res["concept_coverage"]
            delta = round(trans_score - base_score, 4)

            # Verification rule per metamorphic relation
            passed = False
            notes = ""
            if rel == "MG-1_paraphrase":
                # Semantics preserved: absolute score difference <= 0.10
                passed = abs(delta) <= 0.10
                notes = f"|Delta|={abs(delta):.4f} <= 0.10"
                summary_by_relation[rel]["deltas"].append(abs(delta))
            elif rel == "MG-2_irrelevant_addition":
                # Irrelevant text: score should not inflate significantly (delta <= 0.05)
                passed = delta <= 0.05
                notes = f"Delta={delta:+.4f} <= +0.05"
                summary_by_relation[rel]["deltas"].append(delta)
            elif rel == "MG-3_keyword_injection":
                # Keyword stuffing without logic: R <= 0.30 dampens S2; score must remain <= 0.50
                passed = trans_score <= 0.50
                notes = f"Score={trans_score:.4f} <= 0.50 (R={trans_r:.3f}, S2={trans_s2:.3f})"
                summary_by_relation[rel]["scores"].append(trans_score)
            elif rel == "MG-4_concept_deletion":
                # Concept deletion: score must drop monotonically
                passed = delta < 0
                notes = f"Delta={delta:+.4f} < 0"
                summary_by_relation[rel]["deltas"].append(delta)
            elif rel == "MG-5_negation_inversion":
                # Negation inversion: score must drop by at least 0.20
                passed = delta <= -0.20
                notes = f"Delta={delta:+.4f} <= -0.20"
                summary_by_relation[rel]["deltas"].append(delta)

            summary_by_relation[rel]["total"] += 1
            if passed:
                summary_by_relation[rel]["passed"] += 1

            records.append({
                "case_id": tc["case_id"],
                "qid": tc["qid"],
                "relation": rel,
                "base_score": base_score,
                "transformed_score": trans_score,
                "delta": delta,
                "base_reasoning": base_r,
                "trans_reasoning": trans_r,
                "passed": passed,
                "notes": notes
            })
            print(f"[{tc['case_id']}] {rel:<25} Base={base_score:.4f} Trans={trans_score:.4f} Delta={delta:+.4f} -> {'PASS' if passed else 'FAIL'} ({notes})")

    # Save results to CSV
    os.makedirs("research/results", exist_ok=True)
    csv_path = "research/results/metamorphic_tests.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    print(f"\nSaved CSV: {csv_path}")

    # Save raw JSON
    os.makedirs("research/raw", exist_ok=True)
    raw_path = "research/raw/metamorphic_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({"tests": records, "summary": summary_by_relation}, f, indent=2)
    print(f"Saved Raw JSON: {raw_path}")

    # Generate Markdown Table
    os.makedirs("research/tables", exist_ok=True)
    md_path = "research/tables/metamorphic_results.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Metamorphic Robustness Testing Results (EXP-EVAL-5)\n\n")
        f.write("Metamorphic relation testing evaluating semantic invariance, monotonicity, and adversarial resistance:\n\n")
        f.write("| Metamorphic Relation | Description | Expected Constraint | Pass Rate | Mean Metric | Verdict |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: | :---: |\n")
        
        rel_descriptions = {
            "MG-1_paraphrase": ("Paraphrase Invariance", "|Delta score| <= 0.10", f"Mean |Delta| = {sum(summary_by_relation['MG-1_paraphrase']['deltas'])/len(summary_by_relation['MG-1_paraphrase']['deltas']):.4f}"),
            "MG-2_irrelevant_addition": ("Irrelevant Text Addition", "Delta score <= +0.05", f"Mean Delta = {sum(summary_by_relation['MG-2_irrelevant_addition']['deltas'])/len(summary_by_relation['MG-2_irrelevant_addition']['deltas']):+.4f}"),
            "MG-3_keyword_injection": ("Keyword Stuffing Resistance", "Score <= 0.50 (Dampened)", f"Mean Score = {sum(summary_by_relation['MG-3_keyword_injection']['scores'])/len(summary_by_relation['MG-3_keyword_injection']['scores']):.4f}"),
            "MG-4_concept_deletion": ("Concept Deletion Monotonicity", "Delta score < 0", f"Mean Delta = {sum(summary_by_relation['MG-4_concept_deletion']['deltas'])/len(summary_by_relation['MG-4_concept_deletion']['deltas']):+.4f}"),
            "MG-5_negation_inversion": ("Falsification / Negation Inversion", "Delta score <= -0.20", f"Mean Delta = {sum(summary_by_relation['MG-5_negation_inversion']['deltas'])/len(summary_by_relation['MG-5_negation_inversion']['deltas']):+.4f}")
        }
        
        for rel, (title, constraint, metric_str) in rel_descriptions.items():
            tot = summary_by_relation[rel]["total"]
            pas = summary_by_relation[rel]["passed"]
            rate = (pas / tot) * 100.0 if tot > 0 else 0.0
            verdict = "**PASS**" if pas == tot else "**PARTIAL**"
            f.write(f"| **{title}** | {rel} | `{constraint}` | {pas}/{tot} ({rate:.1f}%) | {metric_str} | {verdict} |\n")

        f.write("\n## Detailed Test Case Executions\n\n")
        f.write("| Case ID | Relation | Base Score | Transformed | Delta | Base R | Trans R | Verdict | Notes |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")
        for r in records:
            status = "**PASS**" if r["passed"] else "**FAIL**"
            f.write(f"| {r['case_id']} | `{r['relation']}` | {r['base_score']:.4f} | {r['transformed_score']:.4f} | {r['delta']:+.4f} | {r['base_reasoning']:.3f} | {r['trans_reasoning']:.3f} | {status} | {r['notes']} |\n")

    print(f"Saved Markdown Table: {md_path}")

if __name__ == "__main__":
    run_metamorphic_suite()
