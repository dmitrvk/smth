import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='smth',
    version='0.7.0',
    keywords='scan sane cli',
    description='Scan books and handwriting in batch mode from console',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dmitrvk/smth',
    packages=(
        'smth', 'smth.commands', 'smth.models',
    ),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Multimedia :: Graphics :: Capture :: Scanners',
    ],
    python_requires='>=3.8',
    install_requires=[
        'fpdf>=1.7',
        'PyInquirer>=1.0',
        'Pillow>=7.2',
        'python-sane>=2.8',
    ],
    entry_points={
        'console_scripts': [
            'smth=smth.main:main',
        ],
    },
)
