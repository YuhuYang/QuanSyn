import setuptools
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="quansyn", 
    version="0.0.6",   
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
    install_requires=[
        'numpy==1.21.5',
        'pandas==1.4.4',
	'conllu==4.5.3',
	'scikit_learn==1.0.2',
	'scipy==1.9.1',
    ],
)