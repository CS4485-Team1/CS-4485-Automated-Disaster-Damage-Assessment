import json
import os
from pathlib import Path
from PIL import Image

def get_label_xy(imagePath: str):
    imgPath = Path(imagePath)
    labelPath = imgPath.parent.parent / "labels" / imgPath.name.replace(".png", ".json")
    

    with open(labelPath, 'r') as p:
        data = json.load(p)
        features = data.get("features", {}).get("xy", [])
        
        extracted_data = []
        for obj in features:
            wkt = obj.get("wkt", ",")
            coords = wkt.replace("POLYGON ((", "").replace("))", "")
            subtype = obj.get("properties", {}).get("subtype", "unknown")
            
            extracted_data.append({
                "coords": coords,
                "subtype": subtype
            })
        return extracted_data
    
def create_bounding_box(coords: str):
    padding = 15
    points = coords.split(",")
    xs, ys = [], []
    for p in points:
        parts = p.strip().split(" ")
        if(len(parts) == 2):
            xs.append(float(parts[0]))
            ys.append(float(parts[1]))
    if not xs or not ys:
        return None
    min_x= min(xs) - padding
    min_y = min(ys) - padding
    max_x = max(xs) + padding
    max_y = max(ys) + padding
    return (int(min_x), int(min_y), int(max_x), int(max_y))

def get_pairs(image_directory: str, output_crop_directory: str):
    valid_building_pairs = []
    groupIds = {}
    path = Path(image_directory)
    crop = Path(output_crop_directory)
    crop.mkdir(parents=True, exist_ok=True)

    for imgPath in path.glob("*.png"):
        name = imgPath.name
        if "wildfire" not in name:
            continue
        
        parts = name.split("_")
        cityAndDisaster = parts[0]
        num = parts[1]
        time = parts[2]
        city = cityAndDisaster.replace("-wildfire", "")
        pair = f"{city}-{num}"

        if pair not in groupIds:
            groupIds[pair] = {'city': city}

        if "pre" in time:
            groupIds[pair]['pre'] = str(imgPath)
        elif "post" in time:
            groupIds[pair]["post"] = str(imgPath)
            groupIds[pair]['labels_data'] = get_label_xy(imgPath)

    for pair_id, data in groupIds.items():
        if "pre" not in data or "post" not in data or "labels_data" not in data:
            continue

        with Image.open(data['pre']) as pre, Image.open(data["post"]) as post:
            for idx, item in enumerate(data["labels_data"]):
                points = item["coords"]
                subtype = item["subtype"]
                
                bounding = create_bounding_box(points)
                pre_crop = pre.crop(bounding)
                post_crop = post.crop(bounding)
                
                pre_crop_path = crop / f"{pair_id}_bldg{idx}_pre.png"
                post_crop_path = crop / f"{pair_id}_bldg{idx}_post.png"
                
                pre_crop.save(pre_crop_path)
                post_crop.save(post_crop_path)
                
                valid_building_pairs.append({
                    "building_id": f"{pair_id}_bldg{idx}",
                    "city": data["city"],
                    "subtype": subtype,
                    "pre_crop": str(pre_crop_path),
                    "post_crop": str(post_crop_path),
                })
    return valid_building_pairs

if __name__ == "__main__":
    script_dir = Path(__file__).parent 
    test_image_dir = script_dir.parent / "data" / "images" / "test" / "images"
    output_crop_dir = script_dir.parent / "data" / "images" / "test" / "building_crops"
    
    try:
        results = get_pairs(str(test_image_dir), str(output_crop_dir))
        print(f"Found and extracted {len(results)} individual building pairs.\n")
        
        for sample in results:
            print(f"Building ID: {sample['building_id']} | Subtype: {sample['subtype']}")
            print(f"  Pre: {sample['pre_crop']}")
            print(f"  Post: {sample['post_crop']}")
            
    except Exception as e:
        print(f"Error: {e}")