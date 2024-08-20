import re
from dpm.install import is_commit_sha


def test_is_commit_sha():

    assert is_commit_sha("main") == False
    assert is_commit_sha("5551d0c071f78230dca4656d974e3a36ce52f58c") == True