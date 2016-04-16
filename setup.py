from setuptools import setup, find_packages

setup(
    name = "flaskal",
    version = "0.1",
    packages = find_packages(),
    author = "Bart Spaans",
    author_email = "bart.spaans@gmail.com",
    description = "Generating flask/alchemy micro services from simple yaml definitions",
    entry_points={
        'console_scripts': [
            'flaskal = flaskal.flaskal:main',
        ]
    }
)
