import csv
import json
from pathlib import Path

out_dir = Path("research/data/evaluator_benchmark")
out_dir.mkdir(parents=True, exist_ok=True)

# 8 Topics across DSA & Systems, with 8 balanced cases per topic = 64 total cases
topics_data = [
    {
        "qid": 1, "topic": "Arrays & Hashing", "question": "Explain your logic to find the two indices in an array that sum up to a target value.",
        "ref": "Use a hash map to store visited elements and their indices. In a single pass, check if target minus current element exists in the map.",
        "concepts": ["hash table / dictionary", "complement (target - num)", "single-pass O(N) time", "index lookup"],
        "cases": [
            ("BM-001", "concise_correct", "Use a hash table to store number-to-index mappings. For each x in the array, check if target - x is already in the map. If found, return both indices; otherwise insert x. Runs in O(N) time and O(N) space."),
            ("BM-002", "verbose_correct", "We begin by initializing an empty associative array or hash map that will keep track of all elements we have inspected so far along with their corresponding 0-indexed positions. We then iterate through the input list from left to right. At each iteration, we calculate the required complement by subtracting the current value from the target sum. We perform a constant-time lookup in our hash map. If the complement is present, we immediately output a tuple containing the stored index and our current index. If it is not present, we record the current value and its index into the map to be referenced by future elements. This guarantees linear time complexity O(n) while utilizing O(n) auxiliary memory."),
            ("BM-003", "suboptimal_correct", "Run two nested loops from i = 0 to n and j = i + 1 to n. Check if arr[i] + arr[j] equals the target. If so, return i and j. This requires O(1) extra space but has O(N^2) quadratic time complexity."),
            ("BM-004", "partial_incomplete", "You can use a hash map to look up numbers quickly while iterating through the array."),
            ("BM-005", "verbose_wrong", "To solve two sum efficiently, we must first sort the array using quicksort in O(n log n) time. Then we compute the mathematical average of all numbers, subtract the mean from the target, and perform binary search on the lower half of the array. This finds the exact matching pair in O(log n) additional time."),
            ("BM-006", "keyword_stuffed", "Hash map array indices complement lookup dictionary key value O(N) linear time insertion collision resolution target difference."),
            ("BM-007", "misconception", "We can find the two sum in O(1) time without extra memory by simply calculating target modulo 2 and indexing directly into the array."),
            ("BM-008", "contradictory", "Use a hash map to store visited numbers for O(1) lookups, but hash maps do not allow lookups and you have to search the entire array linearly every single time.")
        ]
    },
    {
        "qid": 3, "topic": "Linked Lists", "question": "Describe the approach to reverse a singly linked list in-place.",
        "ref": "Maintain three pointers: prev (NULL), curr (head), and next_node. Iterate through the list, saving curr->next, pointing curr->next to prev, then advancing prev and curr.",
        "concepts": ["three pointers (prev, curr, next)", "pointer redirection (curr->next = prev)", "in-place O(1) space", "head update"],
        "cases": [
            ("BM-009", "concise_correct", "Initialize prev to NULL and curr to head. Loop while curr is not NULL: cache curr->next in next_temp, redirect curr->next to prev, move prev to curr, and advance curr to next_temp. Return prev as the new head."),
            ("BM-010", "verbose_correct", "Reversing a singly linked list in-place requires redirecting every node's next pointer toward its predecessor without allocating auxiliary heap memory. We initialize three pointer variables: prev initialized to NULL, curr initialized to the list head, and a temporary pointer next_node. In a while loop that executes as long as curr is not NULL, we first preserve the remainder of the list by assigning next_node = curr->next. We then redirect curr->next to prev, effectively reversing the link. Next, we advance prev to curr, and curr to next_node. Upon loop termination, curr is NULL and prev points to the original tail, which is now the new head of the reversed list. Space complexity is O(1) and time complexity is O(N)."),
            ("BM-011", "partial_incomplete", "We walk along the linked list and point each node backwards toward the previous node until reaching the end."),
            ("BM-012", "incorrect", "We swap the first and last elements using array indexing list[0] and list[n-1], then increment and decrement inward."),
            ("BM-013", "verbose_wrong", "To reverse a singly linked list in-place, we allocate a secondary doubly linked list with forward and backward pointers. We push each node from the original list into a stack, allocate fresh memory for N new nodes, and pop from the stack to construct the reversed list in O(N) additional memory."),
            ("BM-014", "keyword_stuffed", "Three pointers prev curr next pointer redirection in-place O(1) space auxiliary head update reverse singly linked list null termination."),
            ("BM-015", "misconception", "You can reverse a singly linked list by simply following the backward pointers from each node's prev property."),
            ("BM-016", "paraphrase", "Set previous to null and pointer current to head. While current exists, hold current's following node, point current's forward link to previous, shift previous forward, and shift current forward. When finished, previous is the start.")
        ]
    },
    {
        "qid": 10, "topic": "Trees & BFS", "question": "Explain the BFS (Level Order) traversal logic for a binary tree.",
        "ref": "Use a FIFO queue. Enqueue the root, then while the queue is not empty, dequeue a node, visit it, and enqueue its left and right children.",
        "concepts": ["FIFO queue", "enqueue root", "level-by-level traversal", "enqueue left and right children"],
        "cases": [
            ("BM-017", "concise_correct", "Breadth-first search traverses level by level using a FIFO queue. Push the root to the queue. While queue is non-empty, pop the front node, record its value, and push its non-null left and right children into the queue."),
            ("BM-018", "verbose_correct", "Level order traversal explores a tree hierarchy breadth-first, visiting all nodes at depth d before proceeding to depth d+1. This is implemented using a First-In-First-Out (FIFO) queue data structure. If the root is null, we return immediately. Otherwise, we enqueue the root node. In a while loop running while the queue is not empty, we determine the number of nodes in the current level. For each node in that level, we dequeue it, append its value to our level results, and enqueue its left child if non-null, followed by its right child if non-null. The FIFO property ensures shallower nodes are dequeued before deeper nodes, running in O(N) time and O(W) auxiliary space where W is max tree width."),
            ("BM-019", "partial_incomplete", "Level order traversal uses a queue to visit the nodes level by level starting from the root."),
            ("BM-020", "incorrect", "BFS uses a recursive function that dives down the left subtree to the deepest leaf before backtracking."),
            ("BM-021", "verbose_wrong", "Breadth-first search on a binary tree is performed using a LIFO stack. We push the root node, then pop it and push its right child followed by its left child, recursively drilling down the leftmost path until a leaf is reached, then popping back up."),
            ("BM-022", "keyword_stuffed", "FIFO queue level order traversal breadth first search root enqueue dequeue left child right child depth width tree traversal."),
            ("BM-023", "misconception", "BFS can be performed using simple recursion without any queue data structure because function call stacks are FIFO."),
            ("BM-024", "contradictory", "BFS uses a FIFO queue to visit nodes level by level, but instead of visiting children next, it visits the parent nodes of the root recursively.")
        ]
    },
    {
        "qid": 41, "topic": "C Pointers & Memory", "question": "What is a pointer in C and how do you declare one?",
        "ref": "A pointer is a variable that stores the memory address of another variable. Declared using an asterisk with base type, e.g. int *ptr.",
        "concepts": ["memory address storage", "asterisk * dereference / declaration", "address-of & operator", "data type specification"],
        "cases": [
            ("BM-025", "concise_correct", "A pointer in C is a variable that stores the memory address of another variable. It is declared with the base type followed by an asterisk, like int *ptr;."),
            ("BM-026", "verbose_correct", "In C, a pointer is a distinct variable type whose value represents the memory address of another variable, array, or allocated memory block. Pointers provide direct memory access, enabling dynamic memory allocation, pass-by-reference semantics in functions, and efficient data structure manipulation. To declare a pointer, you specify the data type of the value being pointed to, followed by an asterisk dereference symbol and the pointer variable name, such as int *ptr; or char *str;. The address-of operator & is used to assign an address to the pointer (&variable), and the asterisk * is used as the dereference operator to read or write the value at that address (*ptr)."),
            ("BM-027", "partial_incomplete", "A pointer holds an address in memory. You declare it using an asterisk."),
            ("BM-028", "incorrect", "A pointer is an integer variable that holds the total size of your program's executable code."),
            ("BM-029", "verbose_wrong", "A pointer in C is a special function that points to other functions in the operating system. You declare one by writing pointer function_name() and compiling with the -O3 flag to link memory tables."),
            ("BM-030", "keyword_stuffed", "Memory address pointer declaration asterisk int *p dereference operator address-of ampersand heap stack byte allocation."),
            ("BM-031", "misconception", "Declaring int *p allocates heap memory automatically for an integer without needing malloc or an existing variable address."),
            ("BM-032", "paraphrase", "Pointers hold memory locations of objects rather than direct values. In C, writing int *p creates a pointer capable of holding an integer address.")
        ]
    },
    {
        "qid": 7, "topic": "Dynamic Programming", "question": "How do you determine the number of distinct ways to climb n stairs if you can take 1 or 2 steps?",
        "ref": "Use DP with recurrence dp[n] = dp[n-1] + dp[n-2], base cases dp[1]=1, dp[2]=2. Space can be optimized to O(1) using two variables.",
        "concepts": ["recurrence relation dp[n] = dp[n-1] + dp[n-2]", "base cases dp[1]=1, dp[2]=2", "overlapping subproblems / optimal substructure", "space optimization O(1)"],
        "cases": [
            ("BM-033", "concise_correct", "This is the Fibonacci sequence. The number of ways to reach step n is dp[n] = dp[n-1] + dp[n-2], with base cases dp[1] = 1 and dp[2] = 2. We can compute this iteratively in O(N) time and O(1) space using two variables."),
            ("BM-034", "verbose_correct", "The climbing stairs problem models optimal substructure and overlapping subproblems. To reach step n, you can arrive either from step n-1 by taking a 1-step or from step n-2 by taking a 2-step. Therefore, total distinct ways satisfies the recurrence relation ways(n) = ways(n-1) + ways(n-2). The base cases are ways(1) = 1 (only one 1-step) and ways(2) = 2 (1+1 or 2). A naive recursive solution exhibits O(2^N) exponential time due to recomputing identical states. By applying bottom-up tabulation or dynamic programming, we compute ways from 3 to n iteratively in O(N) time. Furthermore, since we only need the prior two states, we optimize auxiliary memory to O(1) by maintaining two scalar variables."),
            ("BM-035", "suboptimal_correct", "Use simple recursion: ways(n) = ways(n-1) + ways(n-2) with base cases 1 and 2. This is correct in logic but takes exponential O(2^n) time without memoization."),
            ("BM-036", "partial_incomplete", "You can use dynamic programming because the number of ways to get to step n depends on the two previous steps."),
            ("BM-037", "verbose_wrong", "To solve climbing stairs, generate a complete binary tree of all step paths, convert the tree to an adjacency matrix, and run Dijkstra's shortest path algorithm with weights equal to 1 or 2 to find the total paths in O(V^2) time."),
            ("BM-038", "keyword_stuffed", "Dynamic programming recurrence relation dp[n-1] + dp[n-2] base cases memoization bottom up tabulation Fibonacci O(N) time O(1) space."),
            ("BM-039", "misconception", "Because you can take 1 or 2 steps, the total number of ways to climb n stairs is always n factorial divided by 2."),
            ("BM-040", "contradictory", "The recurrence is dp[n] = dp[n-1] + dp[n-2], but to compute it you must multiply dp[n-1] by dp[n-2] and divide by the step size.")
        ]
    },
    {
        "qid": 15, "topic": "Graphs & DFS", "question": "Explain how Depth First Search (DFS) detects a cycle in a directed graph.",
        "ref": "Use a 3-color state (unvisited, visiting/in-stack, visited). A cycle exists if DFS encounters a node currently in the recursion stack (visiting).",
        "concepts": ["recursion stack / visiting state", "3-state coloring (white/gray/black)", "back-edge detection", "visited set"],
        "cases": [
            ("BM-041", "concise_correct", "In a directed graph, DFS detects cycles by maintaining a recursion stack state. Nodes are marked: unvisited, currently visiting (in stack), or visited. If DFS encounters a neighbor marked as currently visiting, a back-edge exists, indicating a cycle."),
            ("BM-042", "verbose_correct", "Cycle detection in directed graphs requires distinguishing back-edges from cross-edges or forward-edges. We implement DFS using a three-state coloring scheme: White (unvisited), Gray (currently visiting in the active recursion call stack), and Black (fully processed and exited). We iterate through all vertices to handle disconnected components. When exploring a vertex v, we mark it Gray. For each directed neighbor u of v, if u is Gray, we have found an edge pointing back to an ancestor in the active recursion stack, which conclusively proves a cycle exists. If u is White, we recursively explore it. After inspecting all outgoing edges from v, we mark v Black. Time complexity is O(V + E) and space complexity is O(V) for the recursion stack and state array."),
            ("BM-043", "partial_incomplete", "We run DFS and keep track of visited nodes. If we visit a node that was already visited, there might be a cycle."),
            ("BM-044", "incorrect", "Count the total number of edges in the graph. If E > V, the directed graph is guaranteed to have a cycle regardless of edge directions."),
            ("BM-045", "verbose_wrong", "To detect cycles in a directed graph, compute the topological sort using BFS Kahn's algorithm, but instead of tracking in-degrees, compute all shortest paths with Floyd-Warshall and check if any diagonal element is positive."),
            ("BM-046", "keyword_stuffed", "DFS directed graph cycle detection recursion stack three colors white gray black back-edge visiting visited O(V+E) time."),
            ("BM-047", "misconception", "In a directed graph, encountering any previously visited node always indicates a cycle, exactly like in undirected graphs."),
            ("BM-048", "paraphrase", "Cycle detection in directed networks tracks vertices on the current path. When DFS reaches a vertex that is already an active ancestor on the current search path, a cycle is confirmed.")
        ]
    },
    {
        "qid": 22, "topic": "Binary Search", "question": "Explain the binary search algorithm and its preconditions.",
        "ref": "Binary search finds a target in a sorted collection by repeatedly halving the search range. Precondition: the collection must be sorted or monotonically ordered.",
        "concepts": ["sorted / monotonic precondition", "divide and conquer / halving range", "mid calculation (low + (high-low)/2)", "O(log N) time"],
        "cases": [
            ("BM-049", "concise_correct", "Binary search requires the input array to be sorted. It maintains low and high pointers, computes mid = low + (high - low)/2, compares array[mid] to the target, and halves the search space until found or exhausted in O(log N) time."),
            ("BM-050", "verbose_correct", "Binary search is a divide-and-conquer search algorithm with a strict precondition: the underlying elements must be sorted in monotonic order (or possess a monotonic predicate). We define search boundaries low = 0 and high = n - 1. In each iteration of a while loop (low <= high), we compute mid = low + (high - low) / 2 to prevent 32-bit integer overflow. If array[mid] == target, we return the index. If array[mid] < target, the target must lie in the right half, so we update low = mid + 1. If array[mid] > target, the target must lie in the left half, so we update high = mid - 1. Because each step discards half the remaining candidate elements, time complexity is O(log n) and space complexity is O(1)."),
            ("BM-051", "partial_incomplete", "Binary search splits the array in half each time to find a target value in O(log N) time."),
            ("BM-052", "incorrect", "Binary search starts at index 0 and inspects every second element (0, 2, 4, ...) until finding the target."),
            ("BM-053", "verbose_wrong", "Binary search can operate on completely random unsorted data by first calculating the hash code of every element, inserting them into a binary search tree in O(N^2) time, and performing in-order traversal to locate the element."),
            ("BM-054", "keyword_stuffed", "Binary search sorted array monotonic precondition divide and conquer low high mid halving O(log N) logarithmic time integer overflow."),
            ("BM-055", "misconception", "Binary search works on any array regardless of order because it automatically reorders the elements during the search."),
            ("BM-056", "contradictory", "Binary search halves the search space in O(log N) time, but it only works if the array is completely unordered and unsorted.")
        ]
    },
    {
        "qid": 50, "topic": "OS & Concurrency", "question": "What is a race condition in multithreading and how do you prevent it?",
        "ref": "A race condition occurs when multiple threads concurrently access shared data and at least one writes, making outcome dependent on execution order. Prevent using mutexes, locks, or atomics.",
        "concepts": ["concurrent shared memory access", "at least one write operation", "non-deterministic outcome / timing dependency", "mutex / lock / atomic synchronization"],
        "cases": [
            ("BM-057", "concise_correct", "A race condition occurs when two or more threads concurrently access shared data without synchronization and at least one modifies it, leading to unpredictable outcomes. It is prevented using mutex locks, semaphores, or atomic operations."),
            ("BM-058", "verbose_correct", "A race condition is a concurrency bug that arises when two or more threads execute concurrently, access shared mutable state simultaneously, and at least one thread performs a write operation. Because thread scheduling is non-deterministic and managed by the operating system kernel, the final program state depends on the exact interleaving of instruction execution. This leads to subtle, intermittent bugs like lost updates, dirty reads, or data corruption. Race conditions are prevented by enforcing mutual exclusion around critical sections. Primary mechanisms include mutex locks (pthread_mutex), read-write locks, semaphores, and atomic hardware primitives (e.g. compare-and-swap)."),
            ("BM-059", "partial_incomplete", "A race condition happens when threads run at the same time and overwrite each other. You fix it with locks."),
            ("BM-060", "incorrect", "A race condition is when your computer's CPU clock runs faster than your RAM bus speed, causing memory drops."),
            ("BM-061", "verbose_wrong", "A race condition occurs when threads compete for bandwidth across network interfaces. To prevent it, increase the thread priority to real-time and disable interrupt handling in user space so threads run sequentially without OS interference."),
            ("BM-062", "keyword_stuffed", "Race condition multithreading shared mutable state concurrent write critical section mutual exclusion mutex lock semaphore atomic operations."),
            ("BM-063", "misconception", "Declaring a shared variable as volatile in C/C++ completely eliminates race conditions and makes all operations atomic."),
            ("BM-064", "paraphrase", "When multiple threads concurrently manipulate shared memory with unsynchronized writes, the resulting values depend on execution timing. Mutexes and atomic primitives ensure exclusive access, preventing the race.")
        ]
    }
]

all_records = []
for t in topics_data:
    for case_id, cat, text in t["cases"]:
        all_records.append({
            "case_id": case_id,
            "qid": t["qid"],
            "topic": t["topic"],
            "question": t["question"],
            "reference_answer": t["ref"],
            "rubric_concepts": t["concepts"],
            "candidate_answer": text,
            "expected_quality_category": cat
        })

# Write JSON
json_path = out_dir / "benchmark_cases.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(all_records, f, indent=2)

# Write CSV
csv_path = out_dir / "benchmark_dataset.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(all_records[0].keys()))
    writer.writeheader()
    writer.writerows(all_records)

# Write Blinded Annotation Sheet for 3 Human Raters
annotation_dir = Path("research/annotation")
annotation_dir.mkdir(parents=True, exist_ok=True)
blinded_csv = annotation_dir / "rating_template_64cases.csv"
with open(blinded_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["item_id", "question_id", "topic", "question", "candidate_answer", "score_0_to_1", "rater_comments"])
    for r in all_records:
        writer.writerow([r["case_id"], r["qid"], r["topic"], r["question"], r["candidate_answer"], "", ""])

print(f"Generated {len(all_records)} balanced benchmark cases in {json_path} and {csv_path}.")
print(f"Generated blinded annotation template with {len(all_records)} items in {blinded_csv}.")
