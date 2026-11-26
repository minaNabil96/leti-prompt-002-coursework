import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
META = ROOT / "logs" / "model_metadata"

for mid in ("M1", "M2", "M3", "M4", "M5", "M6"):
    d = json.loads((META / f"{mid}.json").read_text(encoding="utf-8"))
    print("=" * 70)
    print(mid, d.get("id"))
    print(" pipeline:", d.get("pipeline_tag"), "| library:", d.get("library_name"),
          "| downloads:", d.get("downloads"), "| likes:", d.get("likes"))
    print(" tags:", d.get("tags"))
    print(" safetensors:", d.get("safetensors"))
    print(" config:", {k: v for k, v in (d.get("config") or {}).items()
                        if k in ("model_type", "architectures", "hidden_size", "num_hidden_layers")})
    print(" cardData:", json.dumps(d.get("cardData") or {}, ensure_ascii=False)[:700])
    print(" siblings:", len(d.get("siblings") or []))
    print(" lastModified:", d.get("lastModified"), "created:", d.get("createdAt"))
