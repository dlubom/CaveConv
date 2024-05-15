"""
Main module for CaveConv.
This module reads a PocketTopo file and can export it to Survex format.
"""

import argparse
from parsers.pockettopo import PocketTopo
from exporters.survex import SurvexExporter


def main():
    """
    Main function to parse arguments and execute the file conversion.
    """
    parser = argparse.ArgumentParser(description="Read a PocketTopo file and print its contents.")
    parser.add_argument("filename", type=str, help="The PocketTopo file to read")
    parser.add_argument("--export-survex", type=str, help="Export to Survex file")

    args = parser.parse_args()
    filename = args.filename

    caveconv = PocketTopo(filename)
    cave_data = caveconv.read_pockettopo_file()

    if args.export_survex:
        exporter = SurvexExporter()
        cave_name = args.export_survex.split(".")[0]
        exporter.export(cave_data, args.export_survex, cave_name)
        print(f"Data exported to {args.export_survex}")


if __name__ == "__main__":
    main()
