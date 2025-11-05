#!/usr/bin/env python3
"""
Setup script for SuperClaude Multi-Agents.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

# Read dev requirements
dev_requirements_file = Path(__file__).parent / "requirements-dev.txt"
dev_requirements = []
if dev_requirements_file.exists():
    dev_requirements = [
        line.strip()
        for line in dev_requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#") and not line.startswith("-r")
    ]

setup(
    name="super-claude-multi-agents",
    version="0.1.0",
    description="Multi-Agent Orchestration System for AI Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SuperClaude Team",
    author_email="",
    url="https://github.com/mlik-sudo/SuperClaude-Multi-Agents",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai agents orchestration multi-agent claude gemini openai",
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.2",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "super-claude=core.super_claude:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md"],
    },
    zip_safe=False,
)
