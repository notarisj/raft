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
        'fastapi~=0.94.0',
        'requests~=2.30.0',
    ],
)
