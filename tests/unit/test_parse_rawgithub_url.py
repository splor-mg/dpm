from dpm.install import parse_rawgithub_url

def test_parse_rawgithub_url():

    expected = {
        "host": "raw.githubusercontent.com",
        "user": "splor-mg",
        "repo": "sisor-dados-2024",
        "ref": "main",
    }
    assert parse_rawgithub_url("https://raw.githubusercontent.com/splor-mg/sisor-dados-2024/main/datapackage.json") == expected