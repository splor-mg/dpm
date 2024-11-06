# macros/main.py
import toml

def define_env(env):
    # Load pyproject.toml
    pyproject = toml.load("pyproject.toml")

    # Access specific fields of pyproject to use in index.md
    project_info = pyproject.get("project", {})
    env.variables["project_version"] = project_info.get("version", "unknown")
    env.variables["project_description"] = project_info.get("description", "No description provided.")
    env.variables["project_name"] = project_info.get("name", "No name provided.")
    env.variables["dependencies"] = project_info.get("dependencies", "No name provided.")
    env.filters['format_dependency'] = format_dependency

import re

def format_dependency(dep):
    # Match the dependency and version specifiers
    match = re.match(r'(\S+)\s*(>=|<=|>|<|==|!=)\s*([\S]+)(.*)', dep)
    if match:
        package, operator, version, condition = match.groups()
        # Create a readable string
        readable = f"{package} (version {operator} {version})"
        if condition:
            condition = condition.strip().replace(';', ' if')
            readable += f" {condition.replace('python_version', 'Python version')}"
        return readable
    return dep  # Return as is if not matched
