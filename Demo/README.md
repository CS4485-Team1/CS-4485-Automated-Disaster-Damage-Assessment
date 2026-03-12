Demo flow for house-crop preprocessing.

Files:
- `preprocessing.py`: creates one pre/post crop pair per labeled building
- `adapter.py`: normalizes preprocessing output into one simple schema
- `service.py`: sends crop pairs to the VLM
- `runner.py`: runs preprocessing and can run VLM on a limited number of crop pairs

Expected output record:

```json
{
  "id": "santa-rosa-00000375_bldg51",
  "city": "santa-rosa",
  "pre_image_path": "path/to/pre_crop.png",
  "post_image_path": "path/to/post_crop.png"
}
```

Run from repo root:

```powershell
cd Demo
python runner.py
```

Run preprocessing for one scene:

```powershell
cd Demo
python runner.py scene santa-rosa-00000002
```

Run VLM on the first 10 crop pairs:

```powershell
cd Demo
python runner.py vlm 10
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
