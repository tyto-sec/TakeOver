from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="TakeOver",
    version="2.0.0",
    author="Victor Silva",
    description="Automated subdomain takeover and permissive email configurations detection tool",
    long_description="TakeOver Scanner: Automated tool for discovering subdomain takeover vulnerabilities and permissive SPF records through comprehensive DNS enumeration and analysis.",
    packages=find_packages(include=["src", "src.*"]),
    package_dir={"": "."},
    py_modules=["main"],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "TakeOver=main:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)