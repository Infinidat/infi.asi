from setuptools import setup, find_packages

setup(
    name="infi.asi",
    version="0.4.17.post3",
    description="Python ASI (SCSI) interface",
    author="ielbazis",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
