import ast
import operator
from datetime import datetime
from pathlib import Path
from omen.config import WORKSPACE_DIR

_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
        ast.Pow: operator.pow}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}

def _safe_math(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
        left, right = _safe_math(node.left), _safe_math(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 8:
            raise ValueError("Exponent too large.")
        return _BIN[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_safe_math(node.operand))
    raise ValueError("Only basic arithmetic is allowed.")

def calculate(expression):
    if len(expression) > 120:
        raise ValueError("Expression too long.")
    result = _safe_math(ast.parse(expression, mode="eval").body)
    if isinstance(result, complex) or abs(result) > 10**15:
        raise ValueError("Result outside supported range.")
    return str(result)

def current_time():
    return datetime.now().astimezone().strftime("%A, %d %B %Y, %I:%M:%S %p %Z")

def _workspace():
    path = Path(WORKSPACE_DIR).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path

def list_workspace_files():
    files = [p.name for p in _workspace().iterdir() if p.is_file()]
    return "\\n".join(files) if files else "Workspace is empty."

def read_workspace_file(filename):
    base = _workspace()
    target = (base / filename).resolve()
    if base not in target.parents:
        raise ValueError("Access outside workspace is blocked.")
    if not target.is_file():
        raise FileNotFoundError(f"{filename} not found.")
    if target.stat().st_size > 200_000:
        raise ValueError("File exceeds 200 KB.")
    return target.read_text(encoding="utf-8", errors="replace")

def tool_definitions():
    specs = [
        ("calculate", "Evaluate basic arithmetic safely.", {"expression": {"type": "string"}}, ["expression"]),
        ("current_time", "Get local date and time.", {}, []),
        ("save_memory", "Save a note only when the user explicitly asks you to remember it.", {"content": {"type": "string"}}, ["content"]),
        ("search_memory", "Search saved user notes.", {"query": {"type": "string"}}, ["query"]),
        ("list_workspace_files", "List files in the restricted workspace.", {}, []),
        ("read_workspace_file", "Read a text file from the restricted workspace only.", {"filename": {"type": "string"}}, ["filename"]),
    ]
    return [{"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": {"type": "object", "properties": props, "required": required}
    }} for name, desc, props, required in specs]
