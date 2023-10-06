from setuptools import setup, find_packages

setup(name='invest',
      version='0.0.35',
      description='A collection of utilities for investors and traders',
      url='https://github.com/AlessandroGianfelici/pyInvest.git',
      author='Alessandro Gianfelici',
      author_email='alessandro.gianfelici@hotmail.com',
      license='MIT License',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['numpy',
                        'pandas',
                        #'yfinance',
                        'plotly',
                        'datetime'],
      zip_safe=False)