from langgraph.graph import StateGraph, END
from .graph_state import GraphState   # <-- ADD THIS

from .graph_nodes import (
    generate_character_description,
    generate_plot,
    generate_image_prompts,
    create_images,
    create_gif,
)

def create_workflow():
    # LangGraph now requires the state schema
    workflow = StateGraph(GraphState)

    workflow.add_node("generate_character_description", generate_character_description)
    workflow.add_node("generate_plot", generate_plot)
    workflow.add_node("generate_image_prompts", generate_image_prompts)
    workflow.add_node("create_images", create_images)
    workflow.add_node("create_gif", create_gif)

    workflow.add_edge("generate_character_description", "generate_plot")
    workflow.add_edge("generate_plot", "generate_image_prompts")
    workflow.add_edge("generate_image_prompts", "create_images")
    workflow.add_edge("create_images", "create_gif")
    workflow.add_edge("create_gif", END)

    workflow.set_entry_point("generate_character_description")

    return workflow.compile()