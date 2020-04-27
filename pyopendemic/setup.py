from setuptools import setup

setup(
    name='pyopendemic',
    version='0.0a1',
    packages=['opendemic', 'opendemic.data'],
    url='https://www.opendemic.org/',
    license='MIT',
    author='Opendemic.org',
    author_email='teamopendemic@gmail.com',
    description='A Python package that provides a data science toolkit for the '
                'covid19 epidemic.',
    install_requires=['numpy', 'scipy', 'pandas']
)
