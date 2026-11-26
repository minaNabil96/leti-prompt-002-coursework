import pathlib

base = pathlib.Path(__file__).resolve().parents[2]
a = base / "deliverable" / "Задание5_logs"
b = base / "labeling" / "deliverable" / "logs"
na = sorted(p.name for p in a.iterdir() if p.is_file())
nb = sorted(p.name for p in b.iterdir() if p.is_file())
print("same log set:", na == nb, len(na))
for p in (a, b):
    t = (p / "worklog.md").read_text(encoding="utf-8")
    print(p.name, p, "16:37:", "16:37" in t, "16:19-16:25:", "16:19-16:25" in t)
    print("  stress:", (p / "stress_agreement.json").exists(), (p / "labels_blind_stress.json").exists())
print(na)
