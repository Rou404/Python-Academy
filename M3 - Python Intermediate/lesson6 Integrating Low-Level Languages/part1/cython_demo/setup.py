from setuptools import setup
from Cython.Build import cythonize

setup(
    name="mymod",
    ext_modules=cythonize("mymod.pyx"),
    zip_safe=False,
)



"""
To build this external library, run this in the cwd

python setup.py build_ext --inplace

"""