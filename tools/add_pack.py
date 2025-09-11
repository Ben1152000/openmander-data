#!/usr/bin/env python3
"""
Zip a state pack and update packs/manifest.json.

Usage:
  python tools/add_pack.py /path/to/IL_2020_pack

It will create:
  packs/IL/IL_2020_pack.zip
and update packs/manifest.json:

{
  "IL": {
    "IL_2020": {
      "path": "IL/IL_2020_pack.zip",
      "sha256": "...",
      "size": 123456789
    }
  }
}
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

CHUNK = 1 << 20  # 1 MiB


def parse_pack_name(pack_dir: Path):
    """
    Expect directory names like 'IL_2020_pack' (2–3 letter state codes OK).
    Returns (state, version_key, base_name).
    """
    base = pack_dir.name
    m = re.match(r"^([A-Z]+)_(\d+)_pack$", base)
    if not m:
        raise SystemExit(
            f"Error: '{base}' does not match expected pattern 'XX_YYYY_pack' (e.g., IL_2020_pack)"
        )
    state, year = m.group(1), m.group(2)
    version_key = f"{state}_{year}"
    return state, version_key, base


def zip_dir(src: Path, dst_zip: Path):
    dst_zip.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(dst_zip, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        # Include files recursively; store paths under top-level folder 'src.name'
        for p in src.rglob("*"):
            if p.is_file():
                arcname = Path(src.name) / p.relative_to(src)
                zf.write(p, arcname)
    return dst_zip


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(manifest_path: Path) -> dict:
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())
    return {}


def save_manifest(manifest: dict, manifest_path: Path):
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Zip a state pack and update packs/manifest.json")
    ap.add_argument("pack_path", type=Path, help="Path to pack directory (e.g., /path/to/IL_2020_pack)")
    ap.add_argument("--packs-dir", type=Path, default=Path("packs"), help="Output packs dir (default: packs)")
    ap.add_argument("--manifest", type=Path, default=None, help="Manifest path (default: packs/manifest.json)")
    args = ap.parse_args()

    pack_dir = args.pack_path.resolve()
    if not pack_dir.is_dir():
        raise SystemExit(f"Error: {pack_dir} is not a directory")

    state, version_key, base = parse_pack_name(pack_dir)

    packs_dir = args.packs_dir.resolve()
    state_dir = packs_dir / state
    out_zip = state_dir / f"{base}.zip"  # e.g., packs/IL/IL_2020_pack.zip

    # Create zip (-r9 equivalent)
    out_zip = zip_dir(pack_dir, out_zip)

    # Compute size and sha256
    size = out_zip.stat().st_size
    digest = sha256_file(out_zip)

    # Update manifest
    manifest_path = args.manifest or (packs_dir / "manifest.json")
    manifest = load_manifest(manifest_path)
    manifest.setdefault(state, {})
    manifest[state][version_key] = {
        "path": f"{state}/{out_zip.name}",
        "sha256": digest,
        "size": size,
    }
    save_manifest(manifest, manifest_path)

    print(f"Created: {out_zip}")
    print(f"Size:    {size} bytes")
    print(f"SHA256:  {digest}")
    print(f"Manifest updated: {manifest_path}")


if __name__ == "__main__":
    main()
