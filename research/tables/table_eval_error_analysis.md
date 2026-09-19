# Qualitative Error Analysis & Confusion Matrix (EXP-EVAL-4)

**Exact Agreement Rate**: 8/20 (40.0%)

## Confusion Matrix (Human Tier vs System Tier)

| True \ Predicted | Poor | Average | Good | Excellent |
| :--- | :---: | :---: | :---: | :---: |
| **Poor** | 8 | 1 | 0 | 0 |
| **Average** | 2 | 0 | 0 | 0 |
| **Good** | 0 | 3 | 0 | 0 |
| **Excellent** | 2 | 2 | 2 | 0 |

## Discrepancy Breakdown ($|\text{System} - \text{Human}| \ge 0.20$)

### Q1: Explain your logic to find the two indices in an array that sum up to a target value.
- **Answer**: "*(Empty / Non-response)*"
- **Human Score**: 0.4000 | **System Score**: 0.0634 ($\Delta = -0.3366$)
- **Error Classification**: False Negative (Underestimated)
- **Diagnostic**: $S_1 = 0.000, S_2 = 0.000, R = 0.127$
- **Weakest Identified Gap**: Omitted mandatory requirement specified in rubric

### Q1: Explain your logic to find the two indices in an array that sum up to a target value.
- **Answer**: "I usually start by sorting arrays because sorted data is clean to read, and then I print all values ..."
- **Human Score**: 0.5000 | **System Score**: 0.0000 ($\Delta = -0.5000$)
- **Error Classification**: False Negative (Underestimated)
- **Diagnostic**: $S_1 = 0.151, S_2 = 0.000, R = 0.189$
- **Weakest Identified Gap**: single pass iteration through the array with constant-time hash map lookup at each step

### Q1: Explain your logic to find the two indices in an array that sum up to a target value.
- **Answer**: "One way is to check each pair and stop when the sum matches the target. That is correct but it is O(..."
- **Human Score**: 0.8000 | **System Score**: 0.2324 ($\Delta = -0.5676$)
- **Error Classification**: False Negative (Underestimated)
- **Diagnostic**: $S_1 = 0.321, S_2 = 0.000, R = 0.309$
- **Weakest Identified Gap**: single pass iteration through the array with constant-time hash map lookup at each step

### Q1: Explain your logic to find the two indices in an array that sum up to a target value.
- **Answer**: "I keep a dictionary of seen numbers and their positions while scanning left to right. For each value..."
- **Human Score**: 0.9000 | **System Score**: 0.1151 ($\Delta = -0.7849$)
- **Error Classification**: False Negative (Underestimated)
- **Diagnostic**: $S_1 = 0.211, S_2 = 0.000, R = 0.267$
- **Weakest Identified Gap**: single pass iteration through the array with constant-time hash map lookup at each step

### Q1: Explain your logic to find the two indices in an array that sum up to a target value.
- **Answer**: "Use one pass with a hash table from number to index. At index i with value x, compute need = target ..."
- **Human Score**: 0.9000 | **System Score**: 0.4692 ($\Delta = -0.4308$)
- **Error Classification**: False Negative (Underestimated)
- **Diagnostic**: $S_1 = 0.372, S_2 = 0.750, R = 0.442$
- **Weakest Identified Gap**: Arrays core principle

### Q3: Describe the approach to reverse a singly linked list in-place.
- **Answer**: "Maintain three references: previous, current, and next_node. While current is not null, first save n..."
- **Human Score**: 0.7000 | **System Score**: 0.4040 ($\Delta = -0.2960$)
- **Error Classification**: False Negative (Underestimated)
- **Diagnostic**: $S_1 = 0.235, S_2 = 0.500, R = 0.527$
- **Weakest Identified Gap**: LinkedLists core principle

### Q41: What is a pointer in C and how do you declare one?
- **Answer**: "A pointer is a variable that holds a memory location of another object. For example, int *p declares..."
- **Human Score**: 0.8000 | **System Score**: 0.5146 ($\Delta = -0.2854$)
- **Error Classification**: False Negative (Underestimated)
- **Diagnostic**: $S_1 = 0.582, S_2 = 0.750, R = 0.429$
- **Weakest Identified Gap**: C_Programming core principle

