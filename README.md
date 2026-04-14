# iliasqc

[![PyPI version](https://img.shields.io/pypi/v/iliasqc.svg)](https://pypi.org/project/iliasqc/)
[![conda-forge version](https://img.shields.io/conda/vn/conda-forge/iliasqc.svg)](https://anaconda.org/conda-forge/iliasqc)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Python package to convert txt files into zip folder that can be uploaded to Ilias to create question pools.

## Installation

### pip

```bash
pip install iliasqc
```

### conda / mamba (conda-forge)

```bash
conda install -c conda-forge iliasqc
# or
mamba install -c conda-forge iliasqc
```

## Usage

### Command line

```bash
iliasqc questions.txt
```

An optional `-o` / `--output` flag lets you specify a custom output path:

```bash
iliasqc questions.txt -o my_pool.zip
```

### Python API

```python
from iliasqc.convert import txt_to_zip

output_path = txt_to_zip("questions.txt")
print(f"Created: {output_path}")
```

## Development

```bash
git clone https://github.com/famosab/iliasqc.git
cd iliasqc
pip install -e ".[dev]"
pytest
```

## Contributing

Contributions are welcome! Please open an issue or pull request on [GitHub](https://github.com/famosab/iliasqc).

## License

MIT – see [LICENSE](LICENSE).
