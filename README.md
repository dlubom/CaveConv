
# CaveConv [Work in progress]

CaveConv is a Python tool for converting PocketTopo cave survey files to Survex format. This project includes functionalities for reading PocketTopo files, processing the data, and exporting it to Survex format using Jinja2 templates.

## Project Structure

- `src/`: Source code directory
  - `main.py`: Entry point of the application
  - `models.py`: Data models for the application
  - `parsers/`: Directory containing PocketTopo file parser
  - `exporters/`: Directory containing Survex file exporter
  - `templates/`: Directory containing Jinja2 templates for exporting data

- `tests/`: Directory containing test files
  - `test_pockettopo.py`: Unit tests for PocketTopo parser
  - `data/`: Directory containing sample PocketTopo files for testing

- `pyproject.toml`: Configuration file for Poetry
- `.gitignore`: Git ignore file
- `README.md`: Project documentation (this file)

## Requirements

- Python 3.10+
- Poetry

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/caveconv.git
   cd caveconv
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

## Usage

To convert a PocketTopo file to Survex format, run the following command:

```bash
poetry run python src/main.py <path_to_pockettopo_file> --export-survex <output_survex_file>
```

Example:

```bash
poetry run python src/main.py tests/data/01/example.top --export-survex example.svx
```

This command will read the PocketTopo file `example.top` and export the data to `example.svx`.

## Running Tests

To run the unit tests, use the following command:

```bash
poetry run pytest
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any features, bug fixes, or improvements.

---

**Note:** This project is currently a work in progress and may have incomplete features or bugs. Please report any issues you encounter.