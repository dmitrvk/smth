import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='smth',
    version='0.1.1',
    keywords='scan sane cli',
    description='Scan in batch mode from console',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dmitrvk/smth',
    packages=('smth', 'smth.db', 'smth.models'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux'
    ],
    python_requires='>=3.8',
    install_requires=[
        'fpdf>=1.7',
        'inquirer>=2.6',
        'Pillow>=4.0',
        'python-sane>=2.8',
    ],
    entry_points={
        'console_scripts': [
            'smth=smth.main:main',
        ],
    },
)

