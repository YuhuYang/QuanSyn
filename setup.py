import setuptools
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="quantling", 
    version="0.1.0",   
    author="Mu Yang",    
    author_email="yuhuyang@163.com",   
    description="A package for quantiative linguistics",
    long_description=long_description,    
    long_description_content_type="text/markdown",
    url="https://github.com/YuhuYang/QuantLing",   
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6', 
)