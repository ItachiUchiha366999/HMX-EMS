from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="university_erp",
    version="0.0.1",
    author="University",
    author_email="support@university.edu",
    description="Comprehensive University Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/university/university_erp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Frappe",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "frappe>=15.0.0",
        "erpnext>=15.0.0",
        "hrms>=15.0.0",
        "education>=15.0.0",
    ],
    include_package_data=True,
    zip_safe=False,
)
