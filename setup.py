"""setuptools packaging."""

import setuptools

setuptools.setup(
    name="dataworks_ingestion_metadata_interface",
    version="0.0.1",
    author="DWP DataWorks",
    author_email="dataworks@digital.uc.dwp.gov.uk",
    description="Lambdas that provision and query the metadata table",
    long_description="Lambdas that provision and query the metadata table",
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "query=query:main",
            "provisioner=provisioner:main",
            "unreconciled=unreconciled:main",
        ]
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    install_requires=["argparse", "boto3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
