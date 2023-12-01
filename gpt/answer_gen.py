import g4f
import asyncio
g4f.debug.logging = True  # Enable logging
g4f.check_version = False

_providers = [
    g4f.Provider.Aichat,
    g4f.Provider.ChatBase,
    g4f.Provider.Bing,
    g4f.Provider.GptGo,
    g4f.Provider.You,
    g4f.Provider.Yqcloud,
]


async def run_provider(provider: g4f.Provider.BaseProvider, prompt: str):
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}],
            provider=provider,
        )
        print(response)

    except Exception as e:
        return e


async def ask_gpt(prompt: str):
    calls = [
        run_provider(provider, prompt) for provider in _providers
    ]
    await asyncio.gather(*calls)
