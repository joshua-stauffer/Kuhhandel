import asyncio

def run_async(func, *args, **kwargs):
    """accepts an awaitable and any arguments or keyword arguments and runs it to completion."""
    
    coro = func(*args, **kwargs)
    return asyncio.get_event_loop().run_until_complete(coro)

def run_batch_async(func_tuples: list, test_timeout: int=1):
    """Runs a series of asynchronous calls, including test cases.
    param func_tuples: [(async function, args, kwargs)]"""

    loop = asyncio.get_event_loop()
    tasks = []
    for func, args, kwargs in func_tuples:
        coro = func(*args, **kwargs)
        tasks.append(asyncio.wait_for(coro, test_timeout))
    fut = asyncio.gather(*tasks)
    loop.run_until_complete(fut)
