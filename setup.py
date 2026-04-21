from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()]

setup(
    name="llm-agent",
    version="0.1.0",
    author="Jogo2002",
    author_email="goldhaberjosh@gmail.com",
    description="A command-line chat tool with file utilities and LLM integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jogo2002/LLM-Agent",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "llm-agent=chat:main",
        ],
    },
)
