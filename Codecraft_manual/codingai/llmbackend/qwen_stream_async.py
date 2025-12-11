import aiohttp
import json
import sys
import asyncio

async def stream_from_llm_async(prompt_text: str):
    """
    Async version: Stream text responses from Ollama line-by-line.
    Keeps all indentation and spacing intact.
    Non-blocking for better performance in async contexts.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5-coder:latest",
        "prompt": prompt_text,
        "stream": True
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            buffer = ""

            async for line in response.content:
                if not line:
                    continue

                try:
                    decoded_line = line.decode('utf-8').strip()
                    if not decoded_line:
                        continue
                    data = json.loads(decoded_line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

                # 🧠 When model sends text
                if "response" in data:
                    text = data["response"]
                    buffer += text

                    # ✅ Yield each full line without stripping spaces/tabs
                    while "\n" in buffer:
                        part, buffer = buffer.split("\n", 1)
                        yield part + "\n"  # ← no .strip()
                        sys.stdout.write(part + "\n")  # ← no .strip()
                        sys.stdout.flush()

                # 🏁 When model signals completion
                if data.get("done"):
                    if buffer:
                        yield buffer  # ← keep raw remainder
                        sys.stdout.write(buffer)
                        sys.stdout.flush()
                    break
                
                # Small yield to allow other async tasks
                await asyncio.sleep(0)
