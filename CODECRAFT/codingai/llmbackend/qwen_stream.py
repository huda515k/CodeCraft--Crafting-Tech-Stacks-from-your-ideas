import requests
import json
import sys

def stream_from_llm(prompt_text: str):
    """
    Stream text responses from Ollama line-by-line.
    Keeps all indentation and spacing intact.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5-coder:7b",
        "prompt": prompt_text,
        "stream": True
    }

    with requests.post(url, json=payload, stream=True) as r:
        buffer = ""

        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            # 🧠 When model sends text
            if "response" in data:
                text = data["response"]
                buffer += text

                # ✅ Yield each full line without stripping spaces/tabs
                while "\n" in buffer:
                    part, buffer = buffer.split("\n", 1)
                    yield part + "\n"                     # ← no .strip()
                    sys.stdout.write(part + "\n")         # ← no .strip()
                    sys.stdout.flush()

            # 🏁 When model signals completion
            if data.get("done"):
                if buffer:
                    yield buffer                          # ← keep raw remainder
                    sys.stdout.write(buffer)
                    sys.stdout.flush()
                break
