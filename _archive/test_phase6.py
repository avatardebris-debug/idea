import sys
mods = ["hypothesis_store", "reflection", "experimenter", "validation_runner"]
for m in mods:
    try:
        __import__(m)
        print(f"OK: {m}")
    except Exception as e:
        print(f"FAIL: {m} — {e}")
        sys.exit(1)

print("\nRunning hypothesis_store smoke test...")
import hypothesis_store as hs
import pathlib
store = hs.HypothesisStore(pathlib.Path(".agent/__test_hyp.jsonl"))
r1 = store.add_if_novel("Fewer tool calls leads to higher scores", "strategy")
r2 = store.add_if_novel("Using fewer tools results in better task performance", "strategy")
r3 = store.add_if_novel("The curiosity drive weight should not exceed 0.2", "metric")
print(f"  Novel: {r1}, Duplicate rejected: {not r2}, Different domain: {r3}")
store.save()
pathlib.Path(".agent/__test_hyp.jsonl").unlink(missing_ok=True)
print("All OK")
