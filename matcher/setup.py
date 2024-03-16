from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

extensions = [
    Extension("regex_matcher", ["regex_matcher.pyx", "RegexMatcher.cpp"],
              language="c++")
]

setup(
    ext_modules=cythonize(extensions)
)
