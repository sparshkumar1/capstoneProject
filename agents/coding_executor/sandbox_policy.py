import ast


BLOCKED_MODULES = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "pathlib",
    "shutil",
    "ctypes",
    "threading",
    "multiprocessing",
    "signal",
    "resource",
}

BLOCKED_NAMES = {
    "open",
    "exec",
    "eval",
    "compile",
    "__import__",
    "input",
}


def validate_source_safety(source_code: str) -> tuple[bool, list[str]]:
    reasons = []

    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        return False, [f"Syntax error: {exc}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split(".")[0]
                if root_name in BLOCKED_MODULES:
                    reasons.append(f"Blocked import: {root_name}")

        if isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if mod in BLOCKED_MODULES:
                reasons.append(f"Blocked import-from: {mod}")

        if isinstance(node, ast.Name) and node.id in BLOCKED_NAMES:
            reasons.append(f"Blocked symbol usage: {node.id}")

    return len(reasons) == 0, reasons
