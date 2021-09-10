from typing import List

import errors
import processor
import taxonomy
from errors import DppInvalidCaseExpressionError


def out_of_index_error(cmd: processor.TestCommand, default_cmds: List[str], expr: str):
    try:
        cmd.parser.parse_args([*default_cmds, expr])
    except DppInvalidCaseExpressionError:
        return True
    else:
        return False


def test_validate_case(dummy_config):
    d = dummy_config("test_validate_case")
    cmd = processor.TestCommand()
    default_cmds = f"{str(d)} --case".split()

    args = cmd.parser.parse_args([*default_cmds, "1,2,5,9"])
    assert args.case == ({1, 2, 5, 9}, set())

    args = cmd.parser.parse_args([*default_cmds, "1-5,5-9"])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, set())

    args = cmd.parser.parse_args([*default_cmds, "1-5,5-9:"])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, set())

    args = cmd.parser.parse_args([*default_cmds, "1-5,5-9:1"])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, {1})

    args = cmd.parser.parse_args([*default_cmds, "1-5,5-9:1,2"])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, {1, 2})

    args = cmd.parser.parse_args([*default_cmds, "1-5,5-9:1-3"])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, {1, 2, 3})

    args = cmd.parser.parse_args([*default_cmds, "4-8:1-3,9"])
    assert args.case == ({4, 5, 6, 7, 8}, {1, 2, 3, 9})

    args = cmd.parser.parse_args([*default_cmds, ":1-3,9"])
    assert args.case == (set(), {1, 2, 3, 9})

    lower_bound = 1
    assert out_of_index_error(cmd, default_cmds, f"{lower_bound-1}")
    assert not out_of_index_error(cmd, default_cmds, f"{lower_bound}")
    assert out_of_index_error(cmd, default_cmds, f":{lower_bound-1}")
    assert not out_of_index_error(cmd, default_cmds, f":{lower_bound}")
    assert out_of_index_error(cmd, default_cmds, f"{lower_bound-1},{lower_bound}")
    assert out_of_index_error(
        cmd, default_cmds, f"{lower_bound}-{lower_bound+10}:{lower_bound-1}"
    )

    upper_bound = 201
    assert out_of_index_error(cmd, default_cmds, f"{upper_bound+1}")
    assert not out_of_index_error(cmd, default_cmds, f"{upper_bound}")
    assert out_of_index_error(cmd, default_cmds, f":{upper_bound+1}")
    assert not out_of_index_error(cmd, default_cmds, f":{upper_bound}")
    assert out_of_index_error(cmd, default_cmds, f"{upper_bound},{upper_bound+1}")
    assert out_of_index_error(
        cmd, default_cmds, f"{upper_bound-10}-{upper_bound}:{upper_bound+1}"
    )


def test_invalid_case_expression(dummy_config):
    d = dummy_config("test_validate_case")
    cmd = processor.TestCommand()
    project_name = "yara"
    index = 1
    default_cmds = f"{str(d)} --case".split()

    t = taxonomy.Taxonomy()
    project = t[project_name]
    cases = project.defects[index].num_cases

    expr = f"{cases+1}"
    try:
        cmd.parser.parse_args([*default_cmds, expr])
    except errors.DppInvalidCaseExpressionError:
        assert True
    else:
        assert False


def test_no_case_is_provided(dummy_config):
    d = dummy_config("test_validate_case")
    cmd = processor.TestCommand()
    default_cmds = f"{str(d)}".split()

    args = cmd.parser.parse_args(default_cmds)
    metadata = args.metadata
    index = args.worktree.index
    selected_defect: taxonomy.Defect = metadata.defects[index - 1]

    docker_cmd = cmd.run(default_cmds)
    assert len(list(docker_cmd.scripts)) == selected_defect.num_cases


def test_exclude_only(dummy_config):
    d = dummy_config("test_validate_case")
    cmd = processor.TestCommand()
    default_cmds = f"{str(d)} --case :1-100".split()

    args = cmd.parser.parse_args(default_cmds)
    metadata = args.metadata
    index = args.worktree.index
    selected_defect: taxonomy.Defect = metadata.defects[index - 1]

    docker_cmd = cmd.run(default_cmds)
    assert len(list(docker_cmd.scripts)) == (selected_defect.num_cases - 100)
