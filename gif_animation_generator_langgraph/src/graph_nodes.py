import asyncio
import aiohttp
import io
import os
import json
import base64
import time
from typing import Optional
from PIL import Image

from dotenv import load_dotenv
load_dotenv()

from langchain_ollama import OllamaLLM as Ollama
from .graph_state import GraphState
from .image_utils import get_image_data

# ============================================================
# CONFIG
# ============================================================
WORKFLOW_FILE = "ComfyUI/workflows/workflow_api.json"
COMFYUI_URL = "http://127.0.0.1:8188"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
USE_OPENROUTER = OPENROUTER_KEY is not None and OPENROUTER_KEY.strip() != ""

# ============================================================
# OPENROUTER (primary) and OLLAMA (fallback)
# ============================================================
def openrouter_generate(prompt: str) -> str:
    import requests

    if not OPENROUTER_KEY:
        raise RuntimeError("OPENROUTER_API_KEY missing")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",   # OpenRouter requires these
        "X-Title": "GifGenerator",
        "User-Agent": "GifGenerator/1.0",
    }

    payload = {
        "model": "anthropic/claude-3.5-sonnet",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": 800,
    }

    # Note: many corporate networks use TLS interception -> you previously used verify=False.
    # Keep verify=False if your environment requires it (e.g. Zscaler), otherwise set True.
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60, verify=False)
    except Exception as e:
        raise RuntimeError(f"OpenRouter request failed: {e}")

    # If endpoint returns HTML or a block page, surface it for debugging
    text = resp.text or ""
    if not text.strip().startswith("{"):
        # print raw response for debugging
        print("RAW RESPONSE:", text[:2000])
        raise RuntimeError("Invalid OpenRouter response (non-json)")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Invalid OpenRouter structure: {e} - {data}")

ollama_llm = Ollama(model="llama3")

def llm_generate(prompt: str) -> str:
    global USE_OPENROUTER
    if USE_OPENROUTER:
        try:
            return openrouter_generate(prompt)
        except Exception as e:
            print("OpenRouter failed → switching to Ollama:", e)
            USE_OPENROUTER = False
    # Ollama fallback (synchronous)
    return ollama_llm.invoke(prompt)

# ============================================================
# SDXL (ComfyUI) helper - robust node detection & prompt printing
# ============================================================
async def generate_sdxl_image(prompt: str, timeout_seconds: int = 120) -> Optional[str]:
    """
    Sends a workflow to local ComfyUI, injects the prompt into the correct node,
    polls history and returns the saved filename path relative to ComfyUI folder.
    """

    if not os.path.exists(WORKFLOW_FILE):
        raise FileNotFoundError(
            f"Workflow file missing: {WORKFLOW_FILE}\n"
            "Place the SDXL workflow JSON (ComfyUI) at this path."
        )

    # load workflow and identify nodes
    with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # Try to detect the correct CLIPTextEncode node to set the positive prompt.
    # Heuristics:
    # 1) find key where class_type == "CLIPTextEncode" and inputs.text == "PROMPT_REPLACE"
    # 2) fall back to first CLIPTextEncode node
    clip_nodes = [k for k, v in workflow.items() if v.get("class_type") == "CLIPTextEncode"]
    positive_node_key = None
    negative_node_key = None

    # normalize keys as strings
    clip_nodes = [str(k) for k in clip_nodes]

    # First preference: node where text == "PROMPT_REPLACE"
    for k in clip_nodes:
        txt = workflow[k].get("inputs", {}).get("text", "")
        if isinstance(txt, str) and "PROMPT_REPLACE" in txt:
            positive_node_key = k
            break

    # If none found, choose the first CLIPTextEncode as positive
    if positive_node_key is None and clip_nodes:
        positive_node_key = clip_nodes[0]

    # Choose a different CLIPTextEncode as negative (if exists)
    if clip_nodes:
        for k in clip_nodes:
            if k != positive_node_key:
                negative_node_key = k
                break

    # Safety: if no CLIPTextEncode nodes found, raise error
    if positive_node_key is None:
        raise RuntimeError("No CLIPTextEncode node found in workflow. Edit workflow file.")

    # Inject prompts
    workflow_before = json.dumps(workflow, indent=2)  # keep a copy if needed

    # Set positive prompt
    workflow[positive_node_key].setdefault("inputs", {})["text"] = prompt
    # Ensure negative prompt exists and is empty (so prompt isn't mis-used as negative)
    if negative_node_key:
        workflow[negative_node_key].setdefault("inputs", {})["text"] = ""

    # Find SaveImage node key dynamically (search for class_type == SaveImage)
    save_nodes = [k for k, v in workflow.items() if v.get("class_type") == "SaveImage"]
    save_node_key = None
    if save_nodes:
        save_node_key = str(save_nodes[0])
    else:
        # if no SaveImage node, attempt common fallback index "7" or "13"
        for candidate in ("7", "13"):
            if candidate in workflow and workflow[candidate].get("class_type") == "SaveImage":
                save_node_key = candidate
                break

    if save_node_key is None:
        raise RuntimeError("No SaveImage node found in workflow. Edit workflow file to include a SaveImage node.")

    # # Print debug information (what gets sent to ComfyUI)
    # print("\n================ COMFYUI PROMPT (injected) ================\n")
    print(f"Positive prompt node: {positive_node_key}")
    # if negative_node_key:
    #     print(f"Negative prompt node: {negative_node_key}")
    # print(f"SaveImage node: {save_node_key}\n")
    # print(">>> Positive prompt (first 1000 chars):\n")
    # print(workflow[positive_node_key]["inputs"]["text"][:1000])
    # print("\n>>> Full workflow JSON being sent (truncated to 2000 chars):\n")
    # print(json.dumps(workflow, indent=2)[:2000])
    # print("\n=========================================================\n")

    # POST the prompt to ComfyUI
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{COMFYUI_URL}/api/prompt", json={"prompt": workflow}, timeout=60) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"ComfyUI /api/prompt returned status {resp.status}: {text[:2000]}")
                data = await resp.json()
        except Exception as e:
            raise RuntimeError(f"Failed to send prompt to ComfyUI: {e}")

    prompt_id = data.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI returned no prompt_id: {data}")

    history_url = f"{COMFYUI_URL}/api/history/{prompt_id}"
    start_time = time.time()

    # Poll loop
    while time.time() - start_time < timeout_seconds:
        await asyncio.sleep(1)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(history_url, timeout=10) as resp:
                    if resp.status != 200:
                        continue
                    hist = await resp.json()
        except Exception:
            continue

        if prompt_id not in hist:
            continue

        outputs = hist[prompt_id].get("outputs", {})
        # Check for SaveImage outputs
        if save_node_key in outputs and isinstance(outputs[save_node_key], dict):
            node_out = outputs[save_node_key]
            images = node_out.get("images") or node_out.get("files") or []
            if images:
                # images entries usually have 'filename' key
                img0 = images[0]
                filename = img0.get("filename") or img0.get("name") or None
                if filename:
                    # ComfyUI typically stores them in ComfyUI/output/<filename>
                    filepath = os.path.join("ComfyUI", "output", filename)
                    # Ensure file exists (ComfyUI might still be moving it)
                    wait_until = time.time() + 5
                    while not os.path.exists(filepath) and time.time() < wait_until:
                        await asyncio.sleep(0.5)
                    if os.path.exists(filepath):
                        return filepath
                    else:
                        # still return the expected path even if file not yet present
                        return filepath
        # If outputs contain 'error' messages, surface them for debugging
        if "error" in hist[prompt_id]:
            raise RuntimeError(f"ComfyUI returned error for prompt_id {prompt_id}: {hist[prompt_id]['error']}")

    # timeout
    return None

# ============================================================
# Workflow node functions (unchanged interface)
# ============================================================
def generate_character_description(state: GraphState) -> GraphState:
    query = state["query"]
    prompt = (
        f"Write a highly detailed, consistent scene description.\n"
        f"Query: {query}"
    )
    state["character_description"] = llm_generate(prompt)
    return state

def generate_plot(state: GraphState) -> GraphState:
    desc = state["character_description"]
    prompt = (
        "Create a 5-step GIF plot.\n"
        f"Scene: {desc}\n\n"
        "Format:\n1.\n2.\n3.\n4.\n5."
    )
    state["plot"] = llm_generate(prompt)
    return state

def generate_image_prompts(state: GraphState) -> GraphState:
    plot = state["plot"]
    desc = state["character_description"]

    prompt = (
        f"Generate 5 detailed image prompts based on this plot:\n{plot}\n\n"
        f"Scene consistency:\n{desc}\n\n"
        "Each must start with 1., 2., 3., 4., 5."
    )

    resp = llm_generate(prompt)

    prompts = []
    for line in resp.split("\n"):
        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
            prompts.append(line.split(".", 1)[1].strip())

    # If LLM didn't produce 5 numbered items, try to salvage by taking lines
    if len(prompts) < 5:
        lines = [l.strip() for l in resp.splitlines() if l.strip()]
        for l in lines:
            if len(prompts) >= 5:
                break
            if l not in prompts:
                prompts.append(l)
    state["image_prompts"] = prompts[:5]
    return state

async def create_images(state: GraphState) -> GraphState:
    # Launch SDXL generation tasks concurrently
    tasks = [generate_sdxl_image(p) for p in state.get("image_prompts", [])]
    results = await asyncio.gather(*tasks)
    state["image_urls"] = results
    return state

async def create_gif(state: GraphState) -> GraphState:
    images = []
    for path in state.get("image_urls", []):
        if path and os.path.exists(path):
            try:
                images.append(Image.open(path).convert("RGBA"))
            except Exception:
                # try opening anyway without conversion
                try:
                    images.append(Image.open(path))
                except Exception:
                    continue

    if not images:
        state["gif_data"] = None
        return state

    buf = io.BytesIO()
    # convert to palette-based GIF automatically
    images[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=images[1:],
        duration=800,
        loop=0,
    )
    state["gif_data"] = buf.getvalue()
    return state
