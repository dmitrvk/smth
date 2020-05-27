import setuptools

setuptools.setup(
    name="smth",
    version="0.0.1",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'smth=smth.main:main',
        ],
    },
)
