"""
sandbox_policy.py — Static Safety & Pre-flight Validation for C Code Submissions.

Provides pre-compilation inspection of untrusted C source code.
Note: Static scanning is an auxiliary pre-flight filter; Docker containment
remains the authoritative security and isolation boundary.
"""

import re

# Direct kernel/network/system headers restricted in basic interview sandboxes
RESTRICTED_C_HEADERS = {
    "sys/socket.h",
    "netinet/in.h",
    "arpa/inet.h",
    "netdb.h",
    "sys/ptrace.h",
    "sys/syscall.h",
    "linux/futex.h",
}

# Forbidden dangerous patterns (direct ptrace / kernel tampering)
FORBIDDEN_C_PATTERNS = [
    (re.compile(r"\bptrace\s*\(", re.IGNORECASE), "Direct ptrace kernel inspection invocation"),
]


def validate_source_safety(source_code: str) -> tuple[bool, list[str]]:
    """
    Validate C source code safety prior to sandbox compilation.
    Returns: (is_safe: bool, reasons: list[str])
    """
    if not source_code or not source_code.strip():
        return False, ["Source code is empty"]

    reasons: list[str] = []

    # Check for forbidden header patterns
    for pattern, desc in FORBIDDEN_C_PATTERNS:
        if pattern.search(source_code):
            reasons.append(f"Blocked dangerous pattern: {desc}")

    # Check maximum source size (e.g. 64 KB limit to prevent compiler memory denial)
    if len(source_code.encode("utf-8")) > 65536:
        reasons.append("Source code exceeds maximum permitted size (64 KB)")

    return len(reasons) == 0, reasons
