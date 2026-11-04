import subprocess, json, sys, os
SC="/tmp/solidcraft-test/app/solidcraft-0.28.0-linux-x86_64/bin/solidcraft-cli"
OUT=os.path.expanduser("~/workspace/goals/aoma-ai-agency-site-and-ghl-offer-redesign/files/kitchen-funnel-demo/solidcraft-prototype")
p = subprocess.Popen([SC,"mcp","--headless","--in",f"{OUT}/kitchen.sc","--allow-path",OUT],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
def send(obj):
    p.stdin.write(json.dumps(obj)+"\n"); p.stdin.flush()
def read_until(id_):
    while True:
        line = p.stdout.readline()
        if not line: raise RuntimeError("EOF from MCP server")
        try: msg=json.loads(line)
        except: continue
        if msg.get("id")==id_: return msg
send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"prototype-test","version":"0.1"}}})
init = read_until(1)
print("INIT server:", json.dumps(init.get("result",{}).get("serverInfo",{})), "protocol:", init.get("result",{}).get("protocolVersion"))
send({"jsonrpc":"2.0","method":"notifications/initialized"})
send({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"measure","arguments":{}}})
m = read_until(2)
txt = m["result"]["content"][0]["text"]
meas = json.loads(txt)
print("MEASURE via MCP keys:", list(meas.keys())[:10]); print("MEASURE total:", json.dumps(meas.get("total", meas.get("totals",{})))[:300])
names = [b.get("name") for b in meas.get("bodies",[])]
print("bodies:", ", ".join(names))
send({"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"screenshot","arguments":{"view":"top","width":900,"height":760,"path":f"{OUT}/kitchen-top-mcp.png","grid":False}}})
s = read_until(3)
print("SCREENSHOT via MCP result keys:", list(s.get("result",{}).keys()), "| isError:", s.get("result",{}).get("isError"))
p.stdin.close(); p.terminate()
