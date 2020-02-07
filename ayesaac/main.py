"""
main.py
Usage:
     python3 main.py 'services.YOUR_MODULE.main'

Start a service as a module
"""

import sys
import importlib


def main():
    arg = sys.argv

    if len(arg) != 2:
        print("Error: Only one argument type string needed:  main.py 'services.YOUR_MODULE.main'")
    else:
        my_module = importlib.import_module(arg[1])
        my_module.main()


if __name__ == "__main__":
    main()
