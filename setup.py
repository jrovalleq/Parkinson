import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
   README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='funtions_package',
    version='0.1',
    packages=['funtions_package'],

    author='Jarok Ovalle',
    author_email='jrovalleqg@gmail.com',
    maintainer='Jarok Ovalle',
    maintainer_email='jrovalleq@gmail.com',

    download_url='',
   
    install_requires=['numpy',
                      'scipy',
                      'itk',
                      'SimpleITK',
                      'pyfreesurfer',
                       ],

    include_package_data=True,

    classifiers=[
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'Intended Audience :: Education',
       'Intended Audience :: Healthcare Industry',
       'Intended Audience :: Science/Research',
       'Programming Language :: Python :: 3.7',
       'Programming Language :: Python :: 3.8',
       'Topic :: Scientific/Engineering',
       'Topic :: Scientific/Engineering :: Artificial Intelligence',
       'Topic :: Software Development :: Libraries',
       'Topic :: Software Development :: Libraries :: Application Frameworks',
       'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
