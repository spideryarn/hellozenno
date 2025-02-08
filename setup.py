from setuptools import setup, find_packages

setup(
    name="spideryarn",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "peewee",
        "psycopg2-binary",
        "google-cloud-storage",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
    ],
)
