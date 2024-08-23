from dpm.install import get_commit_info

def test_get_commit_info_from_branch():
    source = {"path": "https://raw.githubusercontent.com/splor-mg/dados-sisor-2023/main/datapackage.yaml"}
    result = get_commit_info(source)

    expected = {
        "host": "raw.githubusercontent.com",
        "user": "splor-mg",
        "repo": "dados-sisor-2023",
        "ref": "main",
        "sha": "8fe577af619ae7ec7fec821b60fed96d46561858"
    }

    assert result == expected

def test_get_commit_info_from_branch_private_repo():
    # em repositórios privados a função get_commit_info usa a variável de ambiente indicada em 'token' para fins de autenticação
    source = {
        "path": "https://raw.githubusercontent.com/splor-mg/obz-dados/metadata-save/datapackage.yaml",
        "token": "GITHUB_TOKEN"
    }
    result = get_commit_info(source)

    expected = {
        "host": "raw.githubusercontent.com",
        "user": "splor-mg",
        "repo": "obz-dados",
        "ref": "metadata-save",
        "sha": "f0e49cd65e4b234ba639d666d360fa0e33ceae95"
    }

    assert result == expected

def test_get_commit_info_from_sha():
    source = {"path": "https://raw.githubusercontent.com/splor-mg/sisor-dados-2024/2a9a8280c6deda1b47e1cf708995b374125d4edd/datapackage.json"}
    result = get_commit_info(source)

    expected = {
        "host": "raw.githubusercontent.com",
        "user": "splor-mg",
        "repo": "sisor-dados-2024",
        "ref": "2a9a8280c6deda1b47e1cf708995b374125d4edd",
        "sha": "2a9a8280c6deda1b47e1cf708995b374125d4edd"
    }

    assert result == expected
