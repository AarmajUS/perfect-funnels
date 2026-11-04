import json, subprocess, sys, time, urllib.request, urllib.error
args = sys.argv[1:]
wf_json = subprocess.run(["python3", "/home/hatch/workspace/comfyui-lab/build_wf2.py"] + args, capture_output=True, text=True)
if wf_json.returncode != 0:
    print("BUILDER ERROR", wf_json.stderr); sys.exit(1)
prompt = json.loads(wf_json.stdout)
body = json.dumps({"prompt": prompt}).encode()
t0 = time.time()
resp = None
for attempt in range(30):
    try:
        req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=body, headers={"Content-Type": "application/json"})
        resp = json.load(urllib.request.urlopen(req)); break
    except Exception as e:
        print("waiting for server:", e, flush=True); time.sleep(10)
if resp is None: raise SystemExit("server never accepted prompt")
pid = resp["prompt_id"]
print("queued", pid, flush=True)
while True:
    time.sleep(10)
    try:
        h = json.load(urllib.request.urlopen(f"http://127.0.0.1:8188/history/{pid}"))
    except Exception as e:
        print("POLL ERROR (server died?)", e, "elapsed", round(time.time()-t0,1), flush=True); break
    if pid in h:
        st = h[pid]["status"]
        print("status", st.get("status_str"), "elapsed", round(time.time()-t0,1), flush=True)
        outs = []
        for node in h[pid].get("outputs", {}).values():
            for im in node.get("images", []): outs.append(im["filename"])
        print("outputs", outs, flush=True)
        break
    if time.time() - t0 > 3600:
        print("TIMEOUT_60MIN"); break
print("WALL_SECONDS", round(time.time()-t0,1))
