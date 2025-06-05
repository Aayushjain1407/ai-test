from setuptools import setup, find_packages

setup(
    name="ai-test",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        'fastapi',
        'uvicorn',
        'openfabric-pysdk',
    ],
    python_requires='>=3.7',
)
