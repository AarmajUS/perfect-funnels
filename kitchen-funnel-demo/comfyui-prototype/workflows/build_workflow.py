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

def wf(tier, finish, seed, img, outprefix, denoise=1.0, img2img=False):
    W, H = (1024, 960) if tier == "sdxl" else (512, 480)
    if img2img:  # k-before restyle at its own size
        W, H = (768, 512)
    ckpt = "sd_xl_base_1.0.safetensors" if tier == "sdxl" else "v1-5-pruned-emaonly-fp16.safetensors"
    steps = 25 if tier == "sdxl" else 20
    n = {}
    n["1"] = {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}}
    n["2"] = {"class_type": "CLIPTextEncode", "inputs": {"text": POS.format(fin=FINISHES[finish]), "clip": ["1", 1]}}
    n["3"] = {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}}
    n["4"] = {"class_type": "LoadImage", "inputs": {"image": img}}
    n["5"] = {"class_type": "DepthAnythingV2Preprocessor", "inputs": {"image": ["4", 0], "ckpt_name": "depth_anything_v2_vits.pth", "resolution": 1024 if tier == "sdxl" else 768}}
    n["6"] = {"class_type": "Canny", "inputs": {"image": ["4", 0], "low_threshold": 0.3, "high_threshold": 0.7}}
    if tier == "sdxl":
        n["7"] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "controlnet-union-sdxl-promax.safetensors"}}
        n["8"] = {"class_type": "SetUnionControlNetType", "inputs": {"control_net": ["7", 0], "type": "depth"}}
        n["9"] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "controlnet-union-sdxl-promax.safetensors"}}
        n["10"] = {"class_type": "SetUnionControlNetType", "inputs": {"control_net": ["9", 0], "type": "canny"}}
        depth_cn, canny_cn = ["8", 0], ["10", 0]
    else:
        n["7"] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "control_v11f1p_sd15_depth_fp16.safetensors"}}
        n["9"] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "control_v11p_sd15_canny_fp16.safetensors"}}
        depth_cn, canny_cn = ["7", 0], ["9", 0]
    n["11"] = {"class_type": "ControlNetApplyAdvanced", "inputs": {
        "positive": ["2", 0], "negative": ["3", 0], "control_net": depth_cn, "image": ["5", 0],
        "strength": 0.8, "start_percent": 0.0, "end_percent": 1.0}}
    n["12"] = {"class_type": "ControlNetApplyAdvanced", "inputs": {
        "positive": ["11", 0], "negative": ["11", 1], "control_net": canny_cn, "image": ["6", 0],
        "strength": 0.6, "start_percent": 0.0, "end_percent": 1.0}}
    if img2img:
        n["13"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["1", 2]}}
        latent = ["13", 0]
    else:
        n["13"] = {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}}
        latent = ["13", 0]
    n["14"] = {"class_type": "KSampler", "inputs": {
        "model": ["1", 0], "positive": ["12", 0], "negative": ["12", 1], "latent_image": latent,
        "seed": seed, "steps": steps, "cfg": 7.0, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": denoise}}
    n["15"] = {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["1", 2]}}
    n["16"] = {"class_type": "SaveImage", "inputs": {"images": ["15", 0], "filename_prefix": outprefix}}
    n["17"] = {"class_type": "SaveImage", "inputs": {"images": ["5", 0], "filename_prefix": outprefix + "-depthmap"}}
    n["18"] = {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": outprefix + "-cannymap"}}
    return n

if __name__ == "__main__":
    tier, finish, seed, img, outprefix = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
    img2img = len(sys.argv) > 6 and sys.argv[6] == "img2img"
    denoise = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
    print(json.dumps(wf(tier, finish, seed, img, outprefix, denoise, img2img)))
