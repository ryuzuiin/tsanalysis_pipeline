from setuptools import setup, find_packages

setup(
    name="tsanalysis_pipeline",
    version="0.1.0",
    package_dir={"": "src"},  
    packages=find_packages(where="src"),  
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "statsmodels",
        "scikit-learn",
        "pyyaml",
    ],
    author="LIU RUIYUN",
    author_email="ryuuzuiih@yahoo.co.jp",
    description="A comprehensive time series analysis pipeline",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ryuzuiin/tsanalysis_pipeline",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
