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
from iliasqc.convert import txt_to_qti, txt_to_quiz_zip, txt_to_zip
from iliasqc.ilias import (
    create_ilias_archive,
    export_target_point_combinations_csv,
    update_pool_overview_csv,
)
from iliasqc.parser import (
    Answer,
    Question,
    extract_metadata,
    extract_point_values,
    parse_question_file,
)
from iliasqc.qti import convert_to_qti, create_question
from iliasqc.quiz import (
    create_integrated_quiz_archive,
    create_quiz_archive,
)
from iliasqc.template import generate_template

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
    "create_question",
    "create_ilias_archive",
    "create_quiz_archive",
    "create_integrated_quiz_archive",
    "export_combinations_csv",
    "export_target_point_combinations_csv",
    "extract_metadata",
    "extract_point_values",
    "find_combinations",
    "format_combinations_table",
    "generate_pools_by_points",
    "generate_quiz_combinations",
    "generate_quiz_from_combination",
    "generate_template",
    "parse_question_file",
    "txt_to_qti",
    "txt_to_zip",
    "txt_to_quiz_zip",
    "update_pool_overview_csv",
]
