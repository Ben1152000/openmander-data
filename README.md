# OpenMander State Data Packs

Prebuilt **state pack** archives used internally by the OpenMander toolkit. Artifacts are stored via **Git LFS**.

- Layout: `packs/{STATE}/{STATE}_2020_pack.zip` (e.g., `packs/IL/IL_2020_pack.zip`)
- Metadata: `packs/manifest.json` with `{ path, sha256, size }` per pack
- Contents (may vary): demographics, elections, topology/adjacency, geometries, and metadata

## Data Sources (Provenance)

- Dave’s Redistricting App (DRA). 2020. *Block-Level Demographic Data & Election Results (v06).*  
  Available at: `https://data.dra2020.net/file/dra-block-data/`.  
  Accessed September 12, 2025.

- U.S. Census Bureau. 2020. *TIGER/Line Shapefiles: 2020 Census PL 94-171 (Redistricting), State.*  
  Available at: `https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/`.  
  Accessed September 12, 2025.

- U.S. Census Bureau. 2020. *2020 Census Block Assignment Files (BAF), State.*  
  Available at: `https://www2.census.gov/geo/docs/maps-data/data/baf2020/`.  
  Accessed September 12, 2025.
