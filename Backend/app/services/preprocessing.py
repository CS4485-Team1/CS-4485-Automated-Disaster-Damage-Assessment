import os
from pathlib import Path

def get_pairs(image_directory: str):
    groupIds = {}
    path = Path(image_directory)
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
    
    validPairs = []
    for pairs, data in groupIds.items():
        if "pre" in data and "post" in data:
            validPairs.append({
                "id": pairs,
                "city": data["city"],
                "pre": data["pre"],
                "post": data["post"]
            })
    return validPairs


if __name__ == "__main__":
    
    script_dir = Path(__file__).parent 
    test_image_dir = script_dir.parent / "data" / "images" / "test" / "images"
    
    print(f"Scanning directory: {test_image_dir}...")
    
    try:
        results = get_pairs(test_image_dir)
        
        print(f"Found {len(results)} valid pairs:")
        for pair in results:
            print(f"  [{pair['city']}] ID: {pair['id']}")
            print(f"     Pre:  {pair['pre']}")
            print(f"     Post: {pair['post']}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error: {e}")
        print("Tip: Check if the 'test_image_dir' path is correct for where you are currently standing in the terminal.")