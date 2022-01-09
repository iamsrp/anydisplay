import os
from setuptools import setup, find_packages

setup(
    name             = "anydisplay",
    version          = "1.0.0",
    author           = "Steve Payne",
    author_email     = "anydisplay@iamsrp.com",
    description      = ("Wrapper classes to write to various displays"),
    license          = "BSD",
    keywords         = "raspberry pi display",
    url              = "http://github.com/iamsrp/anydisplay/",
    packages         = find_packages(),
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    classifiers      = [ "Development Status :: 4 - Beta",
                         "Environment :: Console",
                         "License :: OSI Approved :: MIT License",
                         "Natural Language :: English",
                         "Operating System :: Unix",
                         "Programming Language :: Python :: 3",
                         "Topic :: Multimedia :: Graphics",
                         "Topic :: Software Development :: Libraries", ],
)
