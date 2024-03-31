'''installer'''
from os import getenv

from setuptools import find_packages, setup

setup(
    name="s3-md5",
    description="Get fast md5 hash from an s3 file",
    version=getenv('VERSION', '1.0.0'),
    url="https://github.com/sakibstark11/s3-md5-python",
    author="Sakib Alam",
    author_email="16sakib@gmail.com",
    license="MIT",
    install_requires=[
        "boto3==1.26.41",
        "boto3-stubs[s3]",
        "setproctitle==1.3.3"
    ],
    extras_require={
        "develop": [
            "autopep8==2.0.1",
            "moto==4.0.12",
            "pytest==7.2.0",
            "pylint==3.1.0",
        ],
        "release": ["wheel==0.43.0"]
    },
    packages=find_packages(exclude=["test", "venv"]),
    python_requires=">=3.10.12",
    entry_points={
        'console_scripts': ['s3-md5=s3_md5.cmd:run'],
    }
)
