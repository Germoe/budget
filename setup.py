from setuptools import find_packages, setup

setup(
    name='budget',
    packages=find_packages(include=['budget']),
    version='0.0.1',
    description='A Budget Helper Library',
    author='Sebastian Engels',
    install_requires=['numpy==1.21.4','forex-python==1.8','pandas==1.3.4'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
    license='MIT',
)