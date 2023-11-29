import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
name='name_matcher',
version='0.0.1',
author='Tereza Martinkova',
author_email='tm1450@georgetown.edu',
description='homework4',
long_description=long_description,
long_description_content_type='text/markdown',
packages=setuptools.find_packages(),
python_requires='>=3.6',
extras_requres={"dev": ["pytest", "flake8", "autopep8"]},
)