from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="esg-analyzer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="ESG & Impact Pre-Investment Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/esg-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "black>=24.1.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "llm": [
            "openai>=1.12.0",
            "anthropic>=0.18.1",
            "litellm>=1.37.19",
            "instructor>=1.3.7",
            "fireworks-ai>=0.16.1",
        ],
        "pdf": [
            "PyPDF2>=3.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "esg-analyzer=app:main",
        ],
    },
) 