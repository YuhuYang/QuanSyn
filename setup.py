import setuptools
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="quansyn", 
    version="0.0.1",   
    author="Mu Yang",    
    author_email="yuhuyang@163.com",   
    description="A package for quantitative syntax analysis",
    long_description=long_description,    
    long_description_content_type="text/markdown",
    url="https://github.com/YuhuYang/QuanSyn",   
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6', 
)