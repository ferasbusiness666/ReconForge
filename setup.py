"""Packaging configuration for ReconForge."""

from setuptools import find_packages, setup


setup(
    name="reconforge",
    version="0.1.0",
    description="AI-assisted recon toolkit for bug bounty hunters",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click>=8.1", "rich>=13.0", "requests>=2.31"],
    python_requires=">=3.9",
    entry_points={"console_scripts": ["reconforge=reconforge.cli:cli"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
)
