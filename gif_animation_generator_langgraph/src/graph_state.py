from typing import TypedDict, Annotated, Sequence, List
from langchain_core.messages import HumanMessage, AIMessage

class GraphState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], "Conversation messages"]
    query: Annotated[str, "User query describing the animation"]
    plot: Annotated[str, "Generated 5-step plot"]
    character_description: Annotated[str, "Character/scene description"]
    image_prompts: Annotated[List[str], "Image prompts list"]
    image_urls: Annotated[List[str], "DALL-E image URLs"]
    gif_data: Annotated[bytes, "GIF bytes"]
