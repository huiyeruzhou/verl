from operator import length_hint
import time
import asyncio
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletion
import os
clients = [
    AsyncOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-",
)
]
def _before_sleep_print(retry_state):
    exc = retry_state.outcome.exception() if retry_state.outcome else None
    if exc:
        # 打印异常字符串
        import datetime
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 重试 {retry_state.attempt_number} 次: {str(exc)}")

calling = 0
import tenacity
@tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=5, min=5, max=90), 
        stop=tenacity.stop_after_attempt(20), 
        retry=tenacity.retry_if_exception_type(OpenAIError),
        reraise=True, 
        before_sleep=_before_sleep_print
)
async def call_llm(model, prompt: str, n: int = 1, enable_thinking: bool = True) -> ChatCompletion:
    global calling
    client = clients[calling]
    calling = (calling + 1) % len(clients)
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=40960-1024,
        temperature=1.0,
        n=n,
        # extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
    )
    return response

async def async_main(tasks, max_workers=2048):
    start = time.time()
    import tqdm
    sem = asyncio.Semaphore(max_workers)
    with tqdm.tqdm(total=length_hint(tasks)) as pbar:
        async def _tsk(coro):
            async with sem:
                ret = await coro
                pbar.update(1)
            return ret
        tasks = [_tsk(t) for t in tasks]
        responses = await asyncio.gather(*tasks)
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    return responses