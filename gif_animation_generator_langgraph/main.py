import asyncio
from src.runner import run_workflow
import warnings
import urllib3

warnings.filterwarnings("ignore")
urllib3.disable_warnings()

async def main():
    query = input("Enter your animation description: ")
    result = await run_workflow(query)

    print("\nCharacter Description:")
    print(result["character_description"])

    print("\nPlot:")
    print(result["plot"])

    print("\nGenerated Image URLs:")
    for url in result["image_urls"]:
        print(url)

    if result["gif_data"]:
        with open("output.gif", "wb") as f:
            f.write(result["gif_data"])
        print("\nGIF saved as output.gif")
    else:
        print("GIF generation failed.")

if __name__ == "__main__":
    asyncio.run(main())
