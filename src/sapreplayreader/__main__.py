"""Command-line entry for sapreplayreader."""
import sys


def main(argv=None):
    argv = argv or sys.argv[1:]
    
    # If no arguments, launch GUI
    if not argv:
        try:
            from .gui_main import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Error loading GUI: {e}")
            print("Please ensure PyQt5 and matplotlib are installed.")
            return 1
        return 0
    
    # If arguments provided, run CLI mode
    if argv[0] == "--gui":
        try:
            from .gui_main import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Error loading GUI: {e}")
            print("Please ensure PyQt5 and matplotlib are installed.")
            return 1
        return 0
    
    # Otherwise, process replay file
    path = argv[0]
    try:
        from . import reader
        data = reader.get_replay(path)
        print(f"Read replay from {path}: {len(data)} keys")
    except Exception as e:
        print(f"Error reading replay: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
