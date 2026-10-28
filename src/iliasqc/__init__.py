"""iliasqc – convert txt files into ILIAS-compatible question-pool zip archives."""

from importlib.metadata import PackageNotFoundError, version

from iliasqc.combine import (
    PoolCombination,
    PoolInfo,
    export_combinations_csv,
    find_combinations,
    format_combinations_table,
    generate_pools_by_points,
    generate_quiz_combinations,
    generate_quiz_from_combination,
)
from iliasqc.convert import txt_to_zip
from iliasqc.ilias import create_ilias_archive, create_manifest
from iliasqc.parser import (
    Answer,
    Question,
    extract_metadata,
    extract_point_values,
    parse_question_file,
)
from iliasqc.qti import convert_to_qti, create_question

try:
    __version__ = version("iliasqc")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "__version__",
    "Answer",
    "Question",
    "PoolCombination",
    "PoolInfo",
    "convert_to_qti",
    "create_ilias_archive",
    "create_manifest",
    "create_question",
    "export_combinations_csv",
    "extract_metadata",
    "extract_point_values",
    "find_combinations",
    "format_combinations_table",
    "generate_pools_by_points",
    "generate_quiz_combinations",
    "parse_question_file",
    "txt_to_zip",
]
