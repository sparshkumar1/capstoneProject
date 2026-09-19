import os
import json

os.makedirs('research/data/evaluator_benchmark', exist_ok=True)

cases = [
    {
        "id": "BM-01",
        "qid": 1,
        "topic": "Arrays & Hashing",
        "question": "Explain your logic to find the two indices in an array that sum up to a target value.",
        "reference_key_concepts": ["hash table / map", "complement / target minus num", "single pass O(N)", "index storage"],
        "variants": [
            {
                "variant_id": "BM-01-A",
                "category": "optimal_complete",
                "text": "We maintain a hash map mapping each visited number to its index. In a single pass through the array, for each element x, we compute complement = target - x. If complement is in the map, we return the stored index and current index. Otherwise, we insert x with its index. Time complexity is O(N) and space complexity is O(N).",
                "expected_grade": "Good",
                "min_expected_score": 0.70
            },
            {
                "variant_id": "BM-01-B",
                "category": "suboptimal_correct",
                "text": "We can use two nested loops to check every pair of elements (i, j). If array[i] + array[j] equals target, we return the pair of indices. This works and uses O(1) extra memory, but takes O(N^2) time which is slow on large inputs.",
                "expected_grade": "Average",
                "min_expected_score": 0.45
            },
            {
                "variant_id": "BM-01-C",
                "category": "adversarial_keyword_stuffing",
                "text": "Hash map lookup dictionary indices complement target array O(n) space hash table key value lookup insertion.",
                "expected_grade": "Poor",
                "max_expected_score": 0.45
            },
            {
                "variant_id": "BM-01-D",
                "category": "empty_or_refusal",
                "text": "I am not sure how to do this.",
                "expected_grade": "Poor",
                "max_expected_score": 0.35
            }
        ]
    },
    {
        "id": "BM-02",
        "qid": 3,
        "topic": "Linked Lists",
        "question": "Describe the approach to reverse a singly linked list in-place.",
        "reference_key_concepts": ["three pointers (prev, curr, next)", "pointer redirection", "in-place O(1) space", "head update"],
        "variants": [
            {
                "variant_id": "BM-02-A",
                "category": "optimal_complete",
                "text": "Initialize prev as NULL and curr as head. While curr is not NULL, store curr->next in a temporary pointer next_node. Redirect curr->next to prev. Then shift prev to curr and curr to next_node. When curr reaches NULL, prev is the new head. This reverses the list in O(N) time and O(1) auxiliary space.",
                "expected_grade": "Good",
                "min_expected_score": 0.70
            },
            {
                "variant_id": "BM-02-B",
                "category": "algorithmic_misconception",
                "text": "To reverse a linked list, allocate a new array of size N, copy all nodes into the array, and then print the array in reverse order.",
                "expected_grade": "Poor",
                "max_expected_score": 0.35
            },
            {
                "variant_id": "BM-02-C",
                "category": "verbose_superficial",
                "text": "Linked lists consist of nodes and pointers. Reversing them is very common in coding interviews because memory allocation is flexible and dynamic.",
                "expected_grade": "Poor",
                "max_expected_score": 0.35
            }
        ]
    },
    {
        "id": "BM-03",
        "qid": 10,
        "topic": "Binary Trees",
        "question": "Explain the BFS (Level Order) traversal logic for a binary tree.",
        "reference_key_concepts": ["FIFO queue", "enqueue root", "level-by-level processing", "enqueue left and right children"],
        "variants": [
            {
                "variant_id": "BM-03-A",
                "category": "optimal_complete",
                "text": "Level order traversal visits nodes level by level using a FIFO queue. We start by enqueueing the root. While the queue is not empty, we record the queue size for the level, dequeue each node, record its value, and enqueue its left and right children if they exist. This guarantees shallower levels are processed first in O(N) time.",
                "expected_grade": "Good",
                "min_expected_score": 0.70
            },
            {
                "variant_id": "BM-03-B",
                "category": "algorithmic_misconception",
                "text": "We use a LIFO stack. We push the root, pop it, and recursively visit left subtree then right subtree.",
                "expected_grade": "Poor",
                "max_expected_score": 0.40
            },
            {
                "variant_id": "BM-03-C",
                "category": "adversarial_keyword_stuffing",
                "text": "Queue FIFO level order breadth first search root left child right child traversal enqueue dequeue tree depth.",
                "expected_grade": "Poor",
                "max_expected_score": 0.45
            }
        ]
    },
    {
        "id": "BM-04",
        "qid": 41,
        "topic": "C Programming & Memory",
        "question": "What is a pointer in C and how do you declare one?",
        "reference_key_concepts": ["memory address", "dereference operator *", "address-of operator &", "type specifier"],
        "variants": [
            {
                "variant_id": "BM-04-A",
                "category": "optimal_complete",
                "text": "A pointer is a variable that stores the memory address of another variable. In C, it is declared using an asterisk with the base type, for example int *ptr. We assign an address using the address-of operator &x, and dereference the pointer using *ptr to access or modify the value at that address.",
                "expected_grade": "Good",
                "min_expected_score": 0.70
            },
            {
                "variant_id": "BM-04-B",
                "category": "off_topic",
                "text": "In C we have for loops, while loops, arrays, and standard libraries like stdio.h for console printing.",
                "expected_grade": "Poor",
                "max_expected_score": 0.25
            }
        ]
    }
]

out_path = 'research/data/evaluator_benchmark/benchmark_cases.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(cases, f, indent=2)

total_variants = sum(len(c["variants"]) for c in cases)
print(f"Generated {out_path} with {len(cases)} topics and {total_variants} variants.")
