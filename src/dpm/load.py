from frictionless import Package
from dpm.extract import extract_sources

# TODO Create main
# TODO use logging
# TODO transform in a python package

def main():
    dp_spreadmart = Package('datapackage.json')
    extract_sources(dp_spreadmart)


