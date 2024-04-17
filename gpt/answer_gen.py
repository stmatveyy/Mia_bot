import g4f
import asyncio
g4f.debug.logging = True  # Enable logging
g4f.check_version = False

_providers = [
    g4f.Provider.ChatBase,
    g4f.Provider.Bing,
    g4f.Provider.GptGo,
    g4f.Provider.Yqcloud,
    g4f.Provider.OpenaiChat,
    g4f.Provider.ChatgptAi,
    g4f.Provider.FreeGpt,
    g4f.Provider.Hashnode
]


async def run_provider(provider: g4f.Provider.BaseProvider,
                       prompt: str) -> None | str:

    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}],
            provider=provider,
        )
        return response if response else None

    except Exception as e:
        print(e)
        return None


async def ask_gpt(prompt: str):
    for provider in _providers:
        task = asyncio.create_task(run_provider(provider, prompt))
        while not task.done():
            await asyncio.sleep(0.1)
        if task.done():
            res = task.result()
            if res:
                return res
            else:
                continue
    return "Упс! Что-то не так.. Попробуй спросить меня еще раз, или измени текст запроса."