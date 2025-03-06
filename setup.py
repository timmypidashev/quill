from setuptools import setup, find_packages

setup(
    name="soliloquy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "colorama>=0.4.4",
        "transformers>=4.20.0",  # Optional, for neural parsing
        "torch>=1.10.0",         # Optional, for neural parsing
    ],
    entry_points={
        "console_scripts": [
            "soliloquy=soliloquy.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A text-based adventure game engine with natural language processing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/soliloquy",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Games/Entertainment :: Role-Playing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
