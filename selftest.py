import importlib
m = importlib.import_module("dupescan")
assert hasattr(m, "main") and callable(m.main), "main() missing in dupescan"
print("selftest OK: dupescan importable, main() callable")
