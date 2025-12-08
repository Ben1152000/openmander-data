import concurrent.futures
import traceback

import openmander

BASE_PATH = "/Users/benjamin/Programming/projects/openmander/packs/"

STATE_CODES = [
    "AL", "AZ", "AR",       "CO", "CT", "DE", "FL", "GA", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA",       "MD", "MA", "MI",
    "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
    "NC", "ND", "OH", "OK",       "PA", "RI", "SC", "SD", "TN",
    "TX", "UT", "VT", "VA", "WA",       "WI", "WY",
]

# STATE_CODES = [ "CA", "ME", "OR", "WV" ]

#   CA: RuntimeError: GET https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/06_CALIFORNIA/06/tl_2020_06_vtd20.zip returned error status
#   OR: RuntimeError: GET https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/41_OREGON/41/tl_2020_41_vtd20.zip returned error status
#   ME: RuntimeError: No parent found for entity with geo_id: GeoId { ty: Block, id: "230039511002023" }
#   WV: RuntimeError: No parent found for entity with geo_id: GeoId { ty: Block, id: "540330306042014" }


# Tune this depending on how much parallel download you want
MAX_WORKERS = 4


def build_and_load_state(code: str) -> tuple[str, bool, str | None]:
    """
    Build the pack for a single state and try to load the map.
    Returns (state_code, success, error_message_or_None).
    """
    try:
        print(f"[{code}] Starting build_pack")
        pack_path = openmander.build_pack(code, path=BASE_PATH, verbose=1)
        print(f"[{code}] Finished build_pack, loading Map")
        _map = openmander.Map(pack_path)
        print(f"[{code}] Map loaded successfully")
        return code, True, None
    except Exception as e:
        # Capture a short error message + full traceback for debugging
        err_msg = f"{type(e).__name__}: {e}"
        tb = traceback.format_exc()
        print(f"[{code}] ERROR: {err_msg}\n{tb}")
        return code, False, err_msg


def main():
    successes: list[str] = []
    failures: dict[str, str] = {}

    # Use a thread pool because build_pack is likely I/O-bound (lots of downloads)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_state = {
            executor.submit(build_and_load_state, code): code
            for code in STATE_CODES
        }

        for future in concurrent.futures.as_completed(future_to_state):
            code = future_to_state[future]
            try:
                state_code, ok, error = future.result()
            except Exception as e:
                # This should be rare since we already catch inside build_and_load_state,
                # but just in case:
                err_msg = f"Unhandled: {type(e).__name__}: {e}"
                print(f"[{code}] FATAL ERROR: {err_msg}")
                failures[code] = err_msg
                continue

            if ok:
                successes.append(state_code)
            else:
                failures[state_code] = error or "Unknown error"

    print("\n=== SUMMARY ===")
    print(f"Total states: {len(STATE_CODES)}")
    print(f"Successful: {len(successes)}")
    print(f"Failed: {len(failures)}")

    if successes:
        print("\nStates built successfully:")
        print(", ".join(sorted(successes)))

    if failures:
        print("\nStates with issues:")
        for code, msg in sorted(failures.items()):
            print(f"  {code}: {msg}")


if __name__ == "__main__":
    main()
