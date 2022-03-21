import os
import re
import sys
import pathlib
import platform
import subprocess

from distutils.version import LooseVersion
from setuptools import Extension
from setuptools.command.build_ext import build_ext
from setuptools import setup, find_packages

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir='', target_name='', cmake_args=(), debug=False):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        if not target_name:
            target_name = os.path.basename(self.name) + "Python"  # for vtk
        self.target_name = target_name
        self.cmake_args = list(cmake_args)
        self.debug = debug


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: " +
                ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)',
                                                   out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            print(ext.name)
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))
        # required for auto-detection of auxiliary "native" libs
        #if not extdir.endswith(os.path.sep):
        #    extdir += os.path.sep
        #extdir += ext.target_pkg
        cmake_args = ext.cmake_args
        from distutils import sysconfig
        lib_dir = str(pathlib.Path(sysconfig.get_python_lib()).parent)
        include_dir = sysconfig.get_python_inc()
        cmake_args += [#'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
            '-DCMAKE_INSTALL_PREFIX=' + extdir,
            '-DPython3_EXECUTABLE=' + sys.executable,
            '-DPython3_LIBRARY=' + lib_dir,
            '-DPython3_INCLUDE_DIR=' + include_dir]

        # Pile all .so in one place and use $ORIGIN as RPATH
        #cmake_args += ["-DCMAKE_BUILD_WITH_INSTALL_RPATH=TRUE"]

        try:
            # if running in da conda environment
            pref = os.environ['CONDA_PREFIX']
            cmake_args += ["-DCMAKE_INSTALL_RPATH={}".format(";".join((".","$ORIGIN", "{}/lib".format(pref))))]
        except KeyError:
            cmake_args += ["-DCMAKE_INSTALL_RPATH={}".format(";".join((".","$ORIGIN")))]

        cfg = 'Debug' if ext.debug else 'Release'
        build_args = ['--config', cfg]

        cmake_args += ['-DCMAKE_CXX_FLAGS_DEBUG="-g"',
                       '-DCMAKE_CXX_FLAGS_RELEASE="-O3"']

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(
                cfg.upper(),
                ext.outputdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j4']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''),
            self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args,
                              cwd=self.build_temp, env=env)

        subprocess.check_call(['cmake', '--build', '.', '--target', ext.target_name] + build_args,
                              cwd=self.build_temp)
        subprocess.check_call(['cmake', '--install', '.'],
                              cwd=self.build_temp)
        print()  # Add an empty line for cleaner output


setup(
    name="vtk-openvr",
    version="0.1.0",
    author="Felix Igelbrink",
    author_email="felix.igelbrink@uni-osnabrueck.de",
    description="VTK's openVR module built as a separate python package",
    license="MIT",
    classifiers=[
        'Private :: Do Not Upload to pypi server',
    ],
    packages=find_packages(include=['vtk_openvr']),
    ext_modules=[CMakeExtension('vtk_openvr', target_name="all",
                                cmake_args=["-DBUILD_PYTHON=ON"], debug=False)],
    cmdclass=dict(build_ext=CMakeBuild),
    install_requires=['numpy'],
    extras_require={
        'examples': ['pyvista'],
    },
    zip_safe=False,
)