from pathlib import Path
import re
import json

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
OUT_PATH = ROOT / "security_audit" / "reports" / ".env.sanitized"

SUSPECT_KEYS = (
    "SECRET", "TOKEN", "PASSWORD", "PRIVATE", "WEBHOOK", "API_KEY", "CLIENT_SECRET", "JWT_SECRET"
)

PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"),             # OpenAI
    re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),            # Hugging Face
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),               # AWS AK
    re.compile(r"\b[0-9a-f]{64}\b", re.I),             # 64-hex
    re.compile(r"\b[0-9a-f]{32}\b", re.I),             # 32-hex
    re.compile(r"organizations/.+/apiKeys/.+"),          # Coinbase style
    re.compile(r"-----BEGIN .* PRIVATE KEY-----"),       # PEM keys
]

def redact_value(val: str) -> str:
    if not val.strip():
        return val
    return "REDACTED"

def main():
    findings = []
    out_lines = []
    if not ENV_PATH.exists():
        print(json.dumps({"error": ".env not found"}))
        return
    for i, line in enumerate(ENV_PATH.read_text(errors="ignore").splitlines(), 1):
        if line.strip().startswith('#') or '=' not in line:
            out_lines.append(line)
            continue
        key, val = line.split('=', 1)
        key_u = key.strip().upper()
        needs_redact = any(k in key_u for k in SUSPECT_KEYS)
        if not needs_redact:
            # pattern-based detection
            for rx in PATTERNS:
                if rx.search(val):
                    needs_redact = True
                    break
        if needs_redact:
            findings.append({"line": i, "key": key.strip()})
            out_lines.append(f"{key}REDACTED")
        else:
            out_lines.append(line)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(out_lines) + "\n")
    print(json.dumps({"sanitized_written": str(OUT_PATH), "redacted_count": len(findings)}, indent=2))

if __name__ == "__main__":
    main()
