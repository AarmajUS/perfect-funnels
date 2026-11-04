import json, sys
FINISHES = {
 "white": "classic white shaker cabinets, white quartz countertops, white subway tile backsplash, brushed nickel hardware",
 "navy":  "modern navy blue cabinets, light butcher block wood countertops, brass hardware",
 "wood":  "warm natural oak wood cabinets, grey marble countertops, matte black hardware",
}
POS = ("photorealistic interior photograph of a real kitchen, elevated corner view, "
       "L-shaped kitchen layout, {fin}, stainless steel four-burner range, undermount sink in the countertop, "
       "tall stainless steel refrigerator, light hardwood floor, plain white walls, soft natural daylight, "
       "architectural photography, sharp detail")
NEG = ("cartoon, illustration, 3d render, cgi, video game, blueprint, sketch, drawing, painting, "
       "deformed, distorted perspective, kitchen island, window, curtains, people, animals, "
       "extra refrigerator, extra oven, text, watermark, logo, blurry, low quality")
# args: tier cnmode finish seed mapimg outprefix [img2img denoise srcimg]
tier, cnmode, finish, seed, mapimg, outprefix = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6]
img2img = len(sys.argv) > 7 and sys.argv[7] == "img2img"
denoise = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0
srcimg = sys.argv[9] if len(sys.argv) > 9 else None
ckpt = "sd_xl_base_1.0.safetensors" if tier == "sdxl" else "v1-5-pruned-emaonly-fp16.safetensors"
import os
W, H = (1024, 960) if tier == "sdxl" else (int(os.environ.get("WF_W", 512)), int(os.environ.get("WF_H", 480)))
if img2img: W, H = 512, 341
steps = 25 if tier == "sdxl" else int(os.environ.get("WF_STEPS", 20))
n = {}
n["1"] = {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}}
n["2"] = {"class_type": "CLIPTextEncode", "inputs": {"text": POS.format(fin=FINISHES[finish]), "clip": ["1", 1]}}
n["3"] = {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}}
n["4"] = {"class_type": "LoadImage", "inputs": {"image": mapimg}}
if tier == "sdxl":
    n["7"] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "controlnet-union-sdxl-promax.safetensors"}}
    n["8"] = {"class_type": "SetUnionControlNetType", "inputs": {"control_net": ["7", 0], "type": cnmode}}
    cn = ["8", 0]
else:
    cnfile = "control_v11f1p_sd15_depth_fp16.safetensors" if cnmode == "depth" else "control_v11p_sd15_canny_fp16.safetensors"
    n["7"] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": cnfile}}
    cn = ["7", 0]
n["11"] = {"class_type": "ControlNetApplyAdvanced", "inputs": {
    "positive": ["2", 0], "negative": ["3", 0], "control_net": cn, "image": ["4", 0],
    "strength": 0.85, "start_percent": 0.0, "end_percent": 1.0}}
if img2img:
    n["20"] = {"class_type": "LoadImage", "inputs": {"image": srcimg}}
    n["13"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["20", 0], "vae": ["1", 2]}}
else:
    n["13"] = {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}}
n["14"] = {"class_type": "KSampler", "inputs": {
    "model": ["1", 0], "positive": ["11", 0], "negative": ["11", 1], "latent_image": ["13", 0],
    "seed": seed, "steps": steps, "cfg": 7.0, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": denoise}}
n["15"] = {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["1", 2]}}
n["16"] = {"class_type": "SaveImage", "inputs": {"images": ["15", 0], "filename_prefix": outprefix}}
print(json.dumps(n))
