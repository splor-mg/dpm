from frictionless import Package
from dpm.extract import extract_sources

def main():
    dp_spreadmart = Package('datapackage.json')
    extract_sources(dp_spreadmart)
