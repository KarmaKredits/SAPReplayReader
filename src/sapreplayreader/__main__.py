"""Command-line entry for sapreplayreader."""
import sys
from .reader import read_replay


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: python -m sapreplayreader <replay-file>")
        return 1
    path = argv[0]
    data = read_replay(path)
    print(f"Read replay from {path}: {len(data)} keys (placeholder)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
