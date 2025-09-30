import os
from setuptools import setup, find_packages

# Read version from package
def get_version():
    with open("docugen/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split('"')[1]
    return "0.0.0"

setup(
    name="docugen",
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.1.0",
        "anthropic>=0.18.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "autopep8>=2.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "docugen=docugen.cli:main",
        ],
    },
    python_requires=">=3.11",
    author="Your Name",
    author_email="your.email@example.com",
    description="CLI tool for automated code documentation",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/docugen",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)