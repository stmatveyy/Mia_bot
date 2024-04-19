from redis import Redis

data = {"settings" : "fuck y",
        "id" : 1}

r = Redis(host='localhost', port=6379)
r.hmset("a", data)
sp = r.hmget("a",["settings", "id"])[0]

