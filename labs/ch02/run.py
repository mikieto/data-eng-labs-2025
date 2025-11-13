# labs/ch02/run.py

import json


def main() -> None:
    """Day-0 skeleton for CH02 lab.

    It only prints a tiny JSON manifest so that you can try a very small
    Change Unit and see the output change.
    """
    manifest = {
        "chapter": "CH02",
        "lab": "boundary_change_unit_evidence_rb30",
        "change_unit_example": "original",
    }

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

