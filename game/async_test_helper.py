import asyncio

def run_async(func, *args, **kwargs):
    """accepts an awaitable and any arguments or keyword arguments and runs it to completion."""
    
    coro = func(*args, **kwargs)
    return asyncio.get_event_loop().run_until_complete(coro)
