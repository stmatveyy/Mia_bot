import g4f
g4f.debug.logging = True 
g4f.check_version = False 

def ask_gpt(query: str):
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}],
        stream=False)
    return response

