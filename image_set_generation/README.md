# Image Set P — Generation & Provenance

This folder contains everything needed to reproduce **image set P** for the
Psycode behavior task (OpenScope).

## Image Selection

8 images selected from the Allen Brain Observatory 118 natural scenes based on
Contour Complexity Index (CCI) spread. Indices into the 118 set:
**[18, 0, 25, 70, 39, 117, 88, 38]**

## Raw Originals

| Image | Database | Original File | Correlation |
|-------|----------|---------------|-------------|
| im000 | BSDS Test | 100075.jpg | 0.929 |
| im018 | BSDS Test | 135037.jpg | 0.920 |
| im025 | BSDS Test | 173036.jpg | 0.953 |
| im038 | BSDS Test | 309004.jpg | 0.861 |
| im039 | BSDS Test | 326038.jpg | 0.902 |
| im070 | VHC | imk01251.imc | 0.987 |
| im088 | VHC | imk01733.imc | 0.929 |
| im117 | McGill | pippin_Mex07_030.tif | 0.888 |

Correlations are Pearson r between the reprocessed image and the reference image
from the Allen Brain Observatory NWB file (experiment 663488086).

## Processing Pipeline

Identical to the Allen Visual Coding luminance-matching pipeline
(see `2019_05_29_create_E_F_reproc_set` notebook):

1. **Load** raw image (BSDS `.jpg`, VHC `.imc` uint16 binary, McGill `.tif`)
2. **Gamma decode** — power 2.2 for BSDS/McGill, no-op for VHC
3. **Crop & resize** — force 16:10 aspect ratio, resize to 1920×1200, crop to
   prewarp size (918 × 1174)
4. **Compute target luminance** — `uint8(255 × median(mean_to_max_ratio))` across
   all 8 images → **target_luminance = 70**
5. **Luminance match** — `fit_scale_to_saturation(target_luminance=70,
   target_saturation=2, apply_screen_mask=True)`
6. **Convert to uint8** — clip [0, 255]
7. **Apply screen mask** — pixels outside the warped screen region set to 127

## Folder Structure

```
image_set_generation/
├── Natural_Images_Lum_Matched_set_ophys_P_2026.04.09.pkl   # Final pkl
├── README.md
├── raw/                  # Original source images
│   ├── im000_100075.jpg
│   ├── im018_135037.jpg
│   ├── im025_173036.jpg
│   ├── im038_309004.jpg
│   ├── im039_326038.jpg
│   ├── im070_imk01251.imc
│   ├── im088_imk01733.imc
│   └── im117_pippin_Mex07_030.tif
├── processed/            # Pipeline output as viewable PNGs
│   ├── im000.png … im117.png
│   └── overview_tile.png
└── code/                 # Scripts to reproduce
    ├── generate_psycode_pkl_v3.py   # Full reprocessing pipeline
    └── package_psycode_set.py       # Packaging utility
```

## pkl Format

```python
import pickle
with open('Natural_Images_Lum_Matched_set_ophys_P_2026.04.09.pkl', 'rb') as f:
    image_set = pickle.load(f)

# image_set['im000']['im000'] -> numpy uint8 array, shape (918, 1174)
```

## Dependencies

- Python 3.11+
- numpy, Pillow, matplotlib
- allensdk (for `make_display_mask` screen mask)

Install: `pip install allensdk numpy Pillow matplotlib`
