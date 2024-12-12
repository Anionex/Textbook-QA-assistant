from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import subprocess

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the extension")
        
        for ext in self.extensions:
            self.build_extension(ext)
            
        # 把当前目录下的Release目录下的文件移动到当前目录下
        release_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Release')
        if os.path.exists(release_dir):
            for file in os.listdir(release_dir):
                if file.endswith('.pyd'):
                    src = os.path.join(release_dir, file)
                    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
                    os.rename(src, dst)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={os.path.dirname(os.path.abspath(__file__))}',
            f'-DPYTHON_EXECUTABLE={sys.executable}'
        ]

        if sys.platform.startswith('win'):
            cmake_args += ['-A', 'x64']
            build_args = ['--config', 'Release', '--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=Release']
            build_args = ['--', '-j2']

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        subprocess.check_call(['cmake', os.path.join(ext.sourcedir, 'NNS')] + cmake_args, cwd=self.build_temp)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)

setup(
    name="nns",
    version="0.1.0",
    description="NNS算法实现",
    ext_modules=[CMakeExtension("NNS")],
    cmdclass={"build_ext": CMakeBuild},
    install_requires=["numpy>=1.19.0"]
)
