"""
Package the Psycode image set into a self-contained subfolder with:
  raw/          - copies of all raw original image files
  processed/    - individual processed images as PNG
  code/         - the generation script
  *.pkl         - the final pkl file
"""

import os
import sys
import shutil
import pickle
import glob
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# Paths
# ============================================================================

WORKING_DIR = (
    r'Z:\braintv\workgroups\ophysdev\OPhysCore'
    r'\Data driven decision - Do not DELETE'
    r'\2019-05-28 - Create new image set CD'
)

PSYCODE_DIR = os.path.join(WORKING_DIR, 'Psycode imaging set')

VHC_TEMP_DIR = (
    r'\\allen\programs\braintv\workgroups\cortexmodels\michaelbu'
    r'\mat_backup\michaelbu\Natural_Image_Processing'
    r'\Original_Images\vhc_temp'
)

PKL_NAME = 'Natural_Images_Lum_Matched_set_Psycode_2026.04.08.pkl'
PKL_PATH = os.path.join(PSYCODE_DIR, PKL_NAME)

SCRIPT_NAME = 'generate_psycode_pkl_v3.py'
SCRIPT_PATH = os.path.join(PSYCODE_DIR, SCRIPT_NAME)

# Output folder
OUTPUT_DIR = os.path.join(PSYCODE_DIR, 'Psycode_CD_set')

# Image specs: pkl_name, raw filename, source, subfolder hint for glob
IMAGE_SPECS = [
    {'pkl_name': 'im000', 'filename': '100075.jpg',            'source': 'BSDS'},
    {'pkl_name': 'im018', 'filename': '135037.jpg',            'source': 'BSDS'},
    {'pkl_name': 'im025', 'filename': '173036.jpg',            'source': 'BSDS'},
    {'pkl_name': 'im038', 'filename': '309004.jpg',            'source': 'BSDS'},
    {'pkl_name': 'im039', 'filename': '326038.jpg',            'source': 'BSDS'},
    {'pkl_name': 'im070', 'filename': 'imk01251.imc',          'source': 'VHC'},
    {'pkl_name': 'im088', 'filename': 'imk01733.imc',          'source': 'VHC'},
    {'pkl_name': 'im117', 'filename': 'pippin_Mex07_030.tif',  'source': 'McGill'},
]


def main():
    # --- Create folder structure ---
    raw_dir = os.path.join(OUTPUT_DIR, 'raw')
    processed_dir = os.path.join(OUTPUT_DIR, 'processed')
    code_dir = os.path.join(OUTPUT_DIR, 'code')

    for d in [raw_dir, processed_dir, code_dir]:
        os.makedirs(d, exist_ok=True)
        print(f"Created: {d}")

    # --- 1. Copy raw originals ---
    print("\n--- Copying raw originals ---")
    for spec in IMAGE_SPECS:
        name = spec['pkl_name']
        fname = spec['filename']

        if spec['source'] == 'VHC':
            src = os.path.join(VHC_TEMP_DIR, fname)
        else:
            pattern = os.path.join(WORKING_DIR, 'Original_Images', '**', fname)
            matches = glob.glob(pattern, recursive=True)
            if not matches:
                print(f"  WARNING: Could not find {fname}")
                continue
            src = matches[0]

        # Name the copy with the pkl name prefix for clarity
        ext = os.path.splitext(fname)[1]
        dst_name = f"{name}_{fname}"
        dst = os.path.join(raw_dir, dst_name)

        shutil.copy2(src, dst)
        size_kb = os.path.getsize(dst) / 1024
        print(f"  {name} -> {dst_name}  ({size_kb:.0f} KB)")

    # --- 2. Copy pkl ---
    print("\n--- Copying pkl ---")
    dst_pkl = os.path.join(OUTPUT_DIR, PKL_NAME)
    shutil.copy2(PKL_PATH, dst_pkl)
    size_mb = os.path.getsize(dst_pkl) / (1024 * 1024)
    print(f"  {PKL_NAME}  ({size_mb:.1f} MB)")

    # --- 3. Save processed images as individual PNGs ---
    print("\n--- Saving processed images as PNG ---")
    with open(PKL_PATH, 'rb') as f:
        dict_image = pickle.load(f)

    for name in sorted(dict_image.keys()):
        arr = dict_image[name][name]
        png_path = os.path.join(processed_dir, f"{name}.png")
        Image.fromarray(arr, mode='L').save(png_path)
        print(f"  {name}.png  shape={arr.shape}  range=[{arr.min()}, {arr.max()}]")

    # --- 4. Save tiled overview ---
    print("\n--- Saving tiled overview ---")
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    sorted_names = sorted(dict_image.keys())
    for idx, name in enumerate(sorted_names):
        row, col = idx // 4, idx % 4
        ax = axes[row, col]
        ax.imshow(dict_image[name][name], cmap='gray', vmin=0, vmax=255)
        ax.set_title(name, fontsize=14)
        ax.axis('off')
    plt.suptitle('Psycode CD Set - Reprocessed from Raw Originals', fontsize=16)
    plt.tight_layout()
    overview_path = os.path.join(processed_dir, 'overview_tile.png')
    plt.savefig(overview_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  overview_tile.png")

    # --- 5. Copy code ---
    print("\n--- Copying code ---")
    shutil.copy2(SCRIPT_PATH, os.path.join(code_dir, SCRIPT_NAME))
    print(f"  {SCRIPT_NAME}")

    # Also copy this packaging script
    this_script = os.path.abspath(__file__)
    shutil.copy2(this_script, os.path.join(code_dir, os.path.basename(this_script)))
    print(f"  {os.path.basename(this_script)}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print(f"Packaged folder: {OUTPUT_DIR}")
    print("Structure:")
    for root, dirs, files in os.walk(OUTPUT_DIR):
        level = root.replace(OUTPUT_DIR, '').count(os.sep)
        indent = '  ' * level
        folder_name = os.path.basename(root)
        print(f"  {indent}{folder_name}/")
        sub_indent = '  ' * (level + 1)
        for f in sorted(files):
            size = os.path.getsize(os.path.join(root, f))
            if size > 1024 * 1024:
                print(f"  {sub_indent}{f}  ({size / (1024*1024):.1f} MB)")
            else:
                print(f"  {sub_indent}{f}  ({size / 1024:.0f} KB)")
    print("=" * 60)
    print("Done!")


if __name__ == '__main__':
    main()
