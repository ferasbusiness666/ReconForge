"""Packaging configuration for ReconForge."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="reconforge",
    version="1.2.1",
    description="AI-assisted recon toolkit for bug bounty hunters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Feras",
    author_email="",
    url="https://github.com/ferasbusiness666/ReconForge",
    project_urls={
        "Bug Tracker": "https://github.com/ferasbusiness666/ReconForge/issues",
        "Documentation": "https://github.com/ferasbusiness666/ReconForge#readme",
        "Source Code": "https://github.com/ferasbusiness666/ReconForge",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.1",
        "rich>=13.0",
        "requests>=2.31",
        "dnspython>=2.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "pre-commit>=3.0",
        ],
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "reconforge=reconforge.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    keywords="security recon reconnaissance bug-bounty penetration-testing",
)
