import json
from datetime import datetime


def export_as_json(messages: list) -> str:
    payload = {
        "app"           : "MathGPT v2",
        "exported_at"   : datetime.now().isoformat(),
        "message_count" : len(messages),
        "messages"      : messages,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def export_as_markdown(messages: list) -> str:
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 🧮 MathGPT Chat Export",
        f"*Exported: {ts}*",
        "",
        "---",
        "",
    ]
    for msg in messages:
        role  = "👤 **You**" if msg["role"] == "user" else "🧮 **MathGPT**"
        lines.append(f"### {role}")
        lines.append(msg["content"])
        lines.append("")
    return "\n".join(lines)
