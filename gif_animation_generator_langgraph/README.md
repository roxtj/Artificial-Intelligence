# ✨ GIF Animation Generator (LangGraph + SDXL + ComfyUI) 🏗️

This project generates an animated GIF from a single text prompt using **LangGraph** for reasoning, OpenRouter for free LLMs, and ComfyUI + SDXL for local image generation.  

It is designed as a **fully free alternative** to using OpenAI GPT-4o + DALL·E 3.

---

## 📖 What This Project Does

From a single text prompt, the system automatically creates:

1.  **Character Description:** A detailed visual profile of the subject.
2.  **Storyline:** A coherent 5-step animation sequence.
3.  **Image Prompts:** Five optimized SDXL prompts based on the storyline.
4.  **Image Generation:** Five high-quality images generated locally via ComfyUI.
5.  **Final Animation:** Combines the frames into a smooth `output.gif`.

---

## 💡 Why This Project Exists

Traditionally, generating consistent animated frames requires a paid stack:
> OpenAI GPT-4o → DALL·E 3 → GIF export

This project bypasses subscription costs by using a **completely free pipeline**:

* **OpenRouter:** Access to free-tier LLMs (or fallback to Ollama).
* **ComfyUI:** Fully free, local node-based image generation.
* **SDXL:** High-quality open-source stable diffusion model.
* **LangGraph:** Advanced orchestration and state management.

This achieves consistent multi-frame generation with **zero cost** and **full local control**.

---

## 🎨 Example Output

**Prompt used:**
> "A small cute baby dragon sitting by a fireplace reading a book, warm cozy lighting, magical floating sparks."

![Generated GIF](output.gif)

---

## 📂 Project Structure

```text
gif_animation_generator_langgraph/
│
├── src/
│   ├── __init__.py
│   ├── graph_nodes.py    # Logic for individual LangGraph nodes
│   ├── graph_state.py    # State definition (TypedDict)
│   ├── graph_workflow.py # Graph construction and compilation
│   ├── image_utils.py    # Helper functions for handling images
│   └── runner.py         # Main execution logic called by main.py
│
├── ComfyUI/              # Local installation (ignored in Git)
│   ├── models/
│   └── ...
│
├── main.py               # Entry point
├── .env                  # API Keys
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone [https://github.com/roxtj/Artificial-Intelligence.git](https://github.com/roxtj/Artificial-Intelligence.git)
cd gif_animation_generator_langgraph
```

## 2. Create a virtual environment

```bash
# Windows
python -m venv .venv-gifgen
.\.venv-gifgen\Scripts\activate

# Linux/Mac
python3 -m venv .venv-gifgen
source .venv-gifgen/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```ini
OPENROUTER_API_KEY=your_key_here
```
If the key is missing, the system automatically falls back to Ollama (local LLM).


## 🔌ComfyUI Setup
### 1. Download ComfyUI
Download and place it inside the project:

```bash
gif_animation_generator_langgraph/
└── ComfyUI/
```
Repository link:
https://github.com/comfyanonymous/ComfyUI


### 2. Download Required SDXL Models
Download the following models from [Hugging Face](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) and place them in:
`gif_animation_generator_langgraph/ComfyUI/models/checkpoints/`

**Required Files:**
* `sd_xl_base_1.0.safetensors`
* `sd_xl_base_1.0_0.9vae.safetensors`
* `sd_xl_refiner_1.0.safetensors`
* `sd_xl_refiner_1.0_0.9vae.safetensors`

### 3. Add the Workflow File
Ensure your specific workflow JSON is placed at:
`ComfyUI/workflows/workflow_api.json`

### 4. Start ComfyUI
Open a separate terminal window and run:

```bash
cd ComfyUI
python main.py
```

> **Important:** ComfyUI must stay running while generating GIFs.

## 🚀 Running the Generator

1. Run the generator script:
```bash
python main.py
```

2. You will be prompted:
Enter your animation description:

3. The final GIF will be saved as:
output.gif

## 📝 Notes

* **Automatic Fallback:** The system automatically switches between OpenRouter and Ollama based on availability.
* **Local Processing:** All image generation happens entirely locally via ComfyUI (requires a GPU with sufficient VRAM for SDXL).
* **Cost:** No paid services are required.