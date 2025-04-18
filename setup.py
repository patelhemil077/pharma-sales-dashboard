from setuptools import setup, find_packages

setup(
    name="pharma_dashboard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pandas",
        "plotly",
    ],
    python_requires=">=3.8",
) 