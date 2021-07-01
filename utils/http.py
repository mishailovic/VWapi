from aiohttp import ClientSession

session = None


async def get_session():
    global session  # Because why not
    if not session:
        session = ClientSession()
    return session


async def fetch(url: str, *args, **kwargs):
    session = await get_session()
    response = await session.get(url, *args, **kwargs)
    if response.status == 200:
        return await response.json()
