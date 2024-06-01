from setuptools import setup, find_packages

setup(name='ctui',
      version='0.2.0',
      packages=find_packages(),
      zip_safe=False,
      entry_points={
          'console_scripts': ['ctui=ctui.__main__:main'],
      }
      )
