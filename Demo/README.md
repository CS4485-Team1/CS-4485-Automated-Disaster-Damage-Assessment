Demo folder for the house crop test.

Files:
- `preprocessing.py` makes the building crops
- `adapter.py` cleans the output format
- `service.py` sends crop pairs to the VLM
- `runner.py` runs the steps

Output format:

```json
{
  "id": "santa-rosa-00000375_bldg51",
  "city": "santa-rosa",
  "pre_image_path": "path/to/pre_crop.png",
  "post_image_path": "path/to/post_crop.png",
  "ground_truth": "no-damage"
}
```

Run all preprocessing:

```powershell
cd Demo
python runner.py
```

Run one scene only:

```powershell
cd Demo
python runner.py scene santa-rosa-00000002
```

Run VLM on one scene:

```powershell
cd Demo
python runner.py scene-vlm santa-rosa-00000002 10
```

If Pillow is missing:

```powershell
pip install Pillow
```
