#!/usr/bin/env python3

import ast
import py_compile
import sys
from pathlib import Path

def find_loop_leaks(tree):
    warnings = []

    for parent in ast.walk(tree):
        body = getattr(parent, "body", None)

        if not isinstance(body, list):
            continue

        for index, node in enumerate(body):
            if not isinstance(node, ast.For):
                continue

            assigned_before = set()

            for statement in body[:index]:
                for child in ast.walk(statement):
                    if (
                        isinstance(child, ast.Name)
                        and isinstance(child.ctx, ast.Store)
                    ):
                        assigned_before.add(child.id)

            assigned_inside = {
                child.id
                for child in ast.walk(node)
                if (
                    isinstance(child, ast.Name)
                    and isinstance(child.ctx, ast.Store)
                )
            }

            loop_only = assigned_inside - assigned_before

            for statement in body[index + 1:]:
                assigned_here = {
                    child.id
                    for child in ast.walk(statement)
                    if (
                        isinstance(child, ast.Name)
                        and isinstance(child.ctx, ast.Store)
                    )
                }

                used_after = {
                    child.id
                    for child in ast.walk(statement)
                    if (
                        isinstance(child, ast.Name)
                        and isinstance(child.ctx, ast.Load)
                    )
                }

                leaked = loop_only & used_after - assigned_here

                if leaked:
                    warnings.append(
                        (
                            node.lineno,
                            sorted(leaked),
                            statement.lineno,
                        )
                    )
                    break

    return warnings
    
def check_file(path: Path) -> int:
    print(f"Checking: {path}")

    try:
        py_compile.compile(str(path), doraise=True)
        print("Syntax  : PASS")
    except py_compile.PyCompileError as exc:
        print("Syntax  : FAIL")
        print(exc)
        return 1

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    functions = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    print(f"Functions: {len(functions)}")

    for node in functions:
        print(
            f"  {node.name:<25} "
            f"lines {node.lineno}-{node.end_lineno}"
        )

    print("AST     : PASS")
    loop_warnings = find_loop_leaks(tree)

    if loop_warnings:
        print("Loops   : WARN")

        for loop_line, names, use_line in loop_warnings:
            print(
                f"  line {loop_line}: variables {', '.join(names)} "
                f"used after loop at line {use_line}"
            )
    else:
        print("Loops   : PASS")
    return 0


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_python.py <python-file>")
        sys.exit(2)

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(2)

    if path.suffix != ".py":
        print(f"Not a Python file: {path}")
        sys.exit(2)

    sys.exit(check_file(path))


if __name__ == "__main__":
    main()