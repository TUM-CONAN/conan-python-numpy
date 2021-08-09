import os

from conans import ConanFile, tools


class PythonNumpyConan(ConanFile):
    name = "python-numpy"
    version = tools.get_env("GIT_TAG", "1.18.4")
    license = "MIT"
    description = "Numpy extension for Python Interpreter"
    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        tools.get("https://github.com/numpy/numpy/releases/download/v%s/numpy-%s.tar.gz" % (self.version, self.version))

    def build_requirements(self):
        self.build_requires("generators/1.0.0@camposs/stable")
        self.build_requires("python-setuptools/[>=41.2.0]@camposs/stable")
        self.build_requires("python-pip/[>=19.2.3]@camposs/stable")
        self.build_requires("cython/0.29.16@camposs/stable")

    def requirements(self):
        self.requires("python/[>=3.8.2]@camposs/stable")
        self.requires("clapack/3.2.1@camposs/stable")

    def build(self):
        with tools.chdir("numpy-" + self.version):
            self.run('pip install --no-use-pep517 --install-option="--prefix=\"%s\"" .' % self.package_folder, run_environment=True)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.8", "site-packages"))
