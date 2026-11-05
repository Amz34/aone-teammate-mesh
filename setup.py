import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aone-teammate-mesh",
    version="0.1.0",
    author="Aamir Zameer",
    author_email="aamir@amz34.com",
    description="Autonomous persistent AI coworker runtime & orchestration mesh",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Amz34/aone-teammate-mesh",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "aone-teammate=aone_teammate_mesh.cli:main",
        ],
    },
)
