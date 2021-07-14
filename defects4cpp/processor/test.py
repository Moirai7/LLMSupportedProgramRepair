import argparse
from os import getcwd
from typing import Callable, Iterable, List, Optional, Set

import message
import taxonomy
from processor.core.argparser import create_taxonomy_parser
from processor.core.command import DockerCommand, DockerCommandLine, DockerExecInfo


class ValidateCase(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        """
        case == INCLUDE[:EXCLUDE]
          INCLUDE | EXCLUDE
          * select: ','
          * range:  '-'
        e.g.
          1-100:3,6,7 (to 100 from 1 except 3, 6 and 7)
          20-30,40-88:47-52 (to 30 from 20 and to 88 from 40 except to 62 from 47)
        """

        def select_cases(expr: str) -> Set[int]:
            if not expr:
                return set()
            cases: Set[int] = set()
            partitions = expr.split(",")
            for partition in partitions:
                tokens = partition.split("-")
                if len(tokens) == 1:
                    cases.add(int(tokens[0]))
                else:
                    cases.update(range(int(tokens[0]), int(tokens[1]) + 1))
            return cases

        values = values.split(":")
        included_cases = select_cases(values[0])
        excluded_cases = select_cases(values[1]) if len(values) > 1 else set()
        # TODO: the range must be validated by taxonomy lookup.
        setattr(namespace, self.dest, (included_cases, excluded_cases))


class TestCommandLine(DockerCommandLine):
    def __init__(self, commands: Iterable[str], case: int):
        self.commands = commands
        self.case = case

    def before(self, info: DockerExecInfo):
        message.info2(f"case #{self.case}")

    def after(self, info: DockerExecInfo):
        pass


class CoverageCommandLine(DockerCommandLine):
    def __init__(self, commands: Iterable[str], case: int):
        self.commands = commands
        self.case = case

    def before(self, info: DockerExecInfo):
        message.info2(f"case #{self.case}")

    def after(self, info: DockerExecInfo):
        coverage = info.worktree.host / TestCommand.coverage_output
        name = f"{coverage.parent.name}-{self.case:04}.json"
        if not coverage.exists():
            message.warning(f"Failed to generate coverage data. {name} is not created")
            return
        # TODO: add option to control where to place json files.
        coverage = coverage.rename(f"{getcwd()}/{name}")
        message.info2(f"{name} is created at {str(coverage)}")


class TestCommand(DockerCommand):
    """
    Run test.
    """

    coverage_output = "coverage.json"
    default_options = ["--print-summary", "--delete", "--json", coverage_output]

    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.add_argument(
            "--coverage",
            dest="coverage",
            help="build with gcov flags",
            action="store_true",
        )
        self.parser.add_argument(
            "-c",
            "--case",
            help="Index of test cases to run",
            type=str,
            dest="case",
            action=ValidateCase,
        )
        self.parser.usage = "d++ test --project=[project_name] --no=[number] --case=[number] [checkout directory]"
        self._coverage = False

    def run(self, argv: List[str]) -> DockerExecInfo:
        args = self.parser.parse_args(argv)
        self._coverage = True if args.coverage else False
        metadata: taxonomy.MetaData = args.metadata
        test_command = (
            metadata.common.test_cov_command
            if self._coverage
            else metadata.common.test_command
        )
        index = args.index

        # Default value is to run all cases.
        selected_defect = metadata.defects[index - 1]
        if not args.case:
            cases = set(range(1, selected_defect.cases + 1))
        else:
            included_cases, excluded_cases = args.case
            if not included_cases:
                included_cases = set(range(1, selected_defect.cases + 1))
            cases = included_cases.difference(excluded_cases)

        filter_command = self._make_filter_command(selected_defect)
        if self._coverage:
            coverage_command = self._make_coverage_command(metadata)
            generator = (
                CoverageCommandLine(
                    coverage_command(
                        [
                            filter_command(case),
                            *test_command,
                        ]
                    ),
                    case,
                )
                for case in cases
            )
        else:
            generator = (
                TestCommandLine(
                    [
                        filter_command(case),
                        *test_command,
                    ],
                    case,
                )
                for case in cases
            )
        stream = False if args.quiet else True

        return DockerExecInfo(metadata, args.worktree, generator, stream)

    def setup(self, info: DockerExecInfo):
        if not self._coverage:
            message.info(f"Start running {info.metadata.name}")
        else:
            message.info(f"Generating coverage data for {info.metadata.name}")

    def teardown(self, info: DockerExecInfo):
        if not self._coverage:
            message.info(f"Finished {info.metadata.name}")

    def _make_coverage_command(
        self, metadata: taxonomy.MetaData
    ) -> Callable[[List[str]], List[str]]:
        def coverage_command(commands: List[str]) -> List[str]:
            commands.append(command)
            return commands

        exclude = " ".join([f"--gcov-exclude {dir}" for dir in metadata.common.exclude])
        command = f"gcovr {' '.join(self.default_options)} {exclude} --root {metadata.common.root}"

        return coverage_command

    def _make_filter_command(self, defect: taxonomy.Defect) -> Callable[[int], str]:
        """
        Returns command to run inside docker that modifies lua script return value which will be used to select which test case to run.

        Assume that "split.patch" newly creates "defects4cpp.lua" file.
        Read "split.patch" and get line containing "create mode ... defects4cpp.lua"
        This should retrieve the path to "defects4cpp.lua" relative to the project directory.
        """

        def filter_command(case: int) -> str:
            return f"bash -c 'echo return {case} > {lua_path}'"

        with open(defect.split_patch) as fp:
            lines = [line for line in fp if "create mode" in line]

        lua_path: Optional[str] = None
        for line in lines:
            if "defects4cpp.lua" in line:
                # "create mode number filename"[-1] == filename
                lua_path = line.split()[-1]
                break
        if not lua_path:
            raise AssertionError(f"could not get lua_path in {defect.split_patch}")

        return filter_command

    @property
    def help(self) -> str:
        return "Run test"
