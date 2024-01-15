from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'big-map-archive-api-client',
    version = '1.2.0',
    author = 'BIG MAP Archive team',
    author_email = 'big-map-archive@materialscloud.org',
    license = 'BIG-MAP Archive License',
    description = 'A CLI app to interact with BIG-MAP Archive data repositories',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/materialscloud-org/big-map-archive-api-client',
    py_modules = ['cli', 'big_map_archive_api_client', 'finales_api_client'],
    packages = find_packages(),
    install_requires = [requirements],
    entry_points = '''
        [console_scripts]
        bma=cli:cmd_root
    '''
)