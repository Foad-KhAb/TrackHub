import ast
import sys
from pathlib import Path

# Methods that return a new QuerySet and are usually expected to be used
QS_METHODS = {
    "filter",
    "exclude",
    "annotate",
    "order_by",
    "distinct",
    "values",
    "values_list",
    "select_related",
    "prefetch_related",
    "only",
    "defer",
    "alias",
}


def is_qs_chaining_call(node: ast.AST) -> bool:
    # Look for an expression statement like:  combined.filter(...)
    # node is ast.Expr; node.value should be ast.Call whose func is ast.Attribute
    if not isinstance(node, ast.Expr):
        return False
    call = node.value
    if not isinstance(call, ast.Call):
        return False
    func = call.func
    if not isinstance(func, ast.Attribute):
        return False
    return func.attr in QS_METHODS


def main(paths: list[str]) -> int:
    failed = 0
    for p in paths:
        path = Path(p)
        if not path.suffix == ".py":
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            # Let other hooks catch syntax errors
            continue

        for node in ast.walk(tree):
            if is_qs_chaining_call(node):
                # Allow `return combined.filter(...)`
                # Our node is ast.Expr; return statements are ast.Return, so they won't match
                # If you want to allow a trailing ';' assignment etc., ast removes that anyway.

                # Report the location
                failed = 1
                lineno = getattr(node, "lineno", "?")
                print(
                    f"{p}:{lineno}: "
                    f"ignored QuerySet call result (did you forget to assign or return?). "
                    f"Use `qs = qs.filter(...)` or `return qs.filter(...)`."
                )
    return failed


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
