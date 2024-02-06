from setuptools import setup, find_packages

setup(
    name='raft',
    version='0.1.0',
    description='A key value store using the Raft consensus algorithm',
    author='Ioannis {Kalopisis, Notaris}',
    author_email='notarisj@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pymongo~=4.3.3',
        'uvicorn~=0.21.0',
        'fastapi~=0.109.1',
        'requests~=2.31.0',
        'prompt_toolkit~=3.0.38',
        'starlette~=0.36.2',
        'setuptools~=65.5.1',
        'tabulate~=0.9.0',
    ],
)
