import asyncio
from .graph_workflow import create_workflow

async def run_workflow(query: str):
    app = create_workflow()

    initial_state = {
        "messages": [],
        "query": query,
        "plot": "",
        "character_description": "",
        "image_prompts": [],
        "image_urls": [],
        "gif_data": None,
    }

    result = await app.ainvoke(initial_state)
    return result
