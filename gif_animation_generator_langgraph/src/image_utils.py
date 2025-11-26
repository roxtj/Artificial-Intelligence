async def get_image_data(session, url: str):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
    return None
