"""
AgentSwarm Tools - Setup Configuration
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="agentswarm-tools",
    version="2.0.0",
    description="Complete AgentSwarm Tools Framework - 101 tools in 8 categories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AgentSwarm",
    author_email="bot@agentswarm.ai",
    url="https://github.com/fmogensen/agentswarm-tools",
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    python_requires=">=3.12",
    install_requires=[
        "agency-swarm>=1.0.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "httpx>=0.25.0",
        "redis>=5.0.0",
        "psycopg2-binary>=2.9.9",
        "sqlalchemy>=2.0.0",
        "openai>=1.6.0",
        "click>=8.1.7",
        "rich>=13.7.0",
        "pyyaml>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "pylint>=3.0.0",
            "mypy>=1.7.0",
            "flake8>=6.1.0",
            "bandit>=1.7.5",
            "safety>=2.3.5",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
            "markdown>=3.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentswarm-tools=scripts.tool_generator:main",
            "agentswarm=cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
