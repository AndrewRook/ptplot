import re

from dataclasses import dataclass
from typing import Union


@dataclass
class Package:
    name: str
    dependency_kind: Union[str, None] = None
    dependency_version: Union[str, None] = None


def parse_conda_envs(min_env_name, max_env_name, optional_packages=None, package_modifiers=None):
    if optional_packages is None:
        optional_packages = {}
    if package_modifiers is None:
        package_modifiers = {}

    # Parse out the min and max envs
    min_env_dependencies = _parse_conda_env_file(min_env_name)
    max_env_dependencies = _parse_conda_env_file(max_env_name)

    # Check that all the minimum env specifications are '=='
    num_not_equal = sum([
        min_dep.dependency_kind != "=="
        for min_dep in min_env_dependencies
    ])
    if num_not_equal != 0:
        raise ValueError("All minimum environments should be explicitly pinned with '=='")

    # Check that envs have same number of packages
    if len(min_env_dependencies) != len(max_env_dependencies):
        return IndexError("Environments have different number of dependencies")

    # Generate the initial dependency strings for pip
    required_dependencies = []
    optional_dependencies = {
        package: [] for package in optional_packages
    }
    for min_dependency, max_dependency in zip(min_env_dependencies, max_env_dependencies):
        # Check that envs have same packages
        if min_dependency.name != max_dependency.name:
            raise ValueError("Environments have different dependencies")
        # Determine if an optional dependency
        extra_requires_names = [
            key for key, package_names in optional_packages.items()
            if min_dependency.name in package_names
        ]
        # Apply any modifiers (e.g. [dev])
        dependency_name = min_dependency.name + (
            "" if min_dependency.name not in package_modifiers
            else f"[{package_modifiers[min_dependency.name]}]"
        )

        # Figure out what the allowed versions are:
        dependency_version = f">={min_dependency.dependency_version}"
        if max_dependency.dependency_kind is not None:
            max_dependency_kind = "<" if max_dependency.dependency_kind == "<" else "<="
            dependency_version +=f",{max_dependency_kind}{max_dependency.dependency_version}"
        full_dependency_string = dependency_name + dependency_version
        if len(extra_requires_names) == 0:
            # Required dependency
            required_dependencies.append(full_dependency_string)
        else:
            # Optional dependency
            for name in extra_requires_names:
                optional_dependencies[name].append(full_dependency_string)

    # TODO: ensure that the optional dependencies are actually in the conda files

    return required_dependencies, optional_dependencies


def _parse_conda_env_file(env_filename):
    with open(env_filename) as env_file:
        file_lines = env_file.readlines()
    # strip all spaces and carriage return, assume no tabs:
    file_lines = [line.strip().replace(" ", "") for line in file_lines]
    raw_dependencies = []
    for i, line in enumerate(file_lines):
        if line == "dependencies:":
            # every line from here on that starts with '-' is a valid dependency
            for dependency_line in file_lines[i + 1:]:
                if dependency_line[0] != "-":
                    break
                if dependency_line == "-pip:":
                    continue
                split_dependency = re.match(
                    r"-([^=><]+)(([=><]{1,2})([.\w]+$)|$)",
                    # (package_name, _, dependency_kind|None, dependency_version|None)
                    dependency_line
                ).groups()
                raw_dependencies.append(
                    Package(split_dependency[0], split_dependency[2], split_dependency[3])
                )
            break
    return sorted(raw_dependencies, key=lambda x: x.name)
