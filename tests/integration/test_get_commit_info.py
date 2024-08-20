from dpm.install import get_commit_info
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

def test_get_commit_info():
    source_branch = {"path": "https://raw.githubusercontent.com/splor-mg/dados-sisor-2023/main/datapackage.yaml"}
    source_sha = {
        "path": "https://raw.githubusercontent.com/splor-mg/sisor-dados-2024/2a9a8280c6deda1b47e1cf708995b374125d4edd/datapackage.json"}

    expected_branch = {
        "host": "raw.githubusercontent.com",
        "user": "splor-mg",
        "repo": "dados-sisor-2023",
        "ref": "main",
        "sha": "8fe577af619ae7ec7fec821b60fed96d46561858"
    }

    expected_sha = {
        "host": "raw.githubusercontent.com",
        "user": "splor-mg",
        "repo": "sisor-dados-2024",
        "ref": "2a9a8280c6deda1b47e1cf708995b374125d4edd",
        "sha": "2a9a8280c6deda1b47e1cf708995b374125d4edd"
    }

    assert expected_branch == get_commit_info(source_branch)
    assert expected_sha == get_commit_info(source_sha)
