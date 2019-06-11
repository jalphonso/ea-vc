from setuptools import setup, find_packages

import juniper_datacenter_fabric.about as about


def requirements(filename='requirements.txt'):
  return open(filename.strip()).readlines()


with open("README.md", "r") as fh:
  long_description = fh.read()

with open("LICENSE.md", "r") as fh:
  license_file = fh.read()


setup(
    name=about.package_name,
    version=about.package_version,
    description='Juniper Datacenter Fabric Tools',
    license=license_file,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Juniper Networks',
    packages=find_packages(),
    install_requires=requirements(),
    include_package_data=True,
    entry_points='''
        [console_scripts]
        fabric_mgr=juniper_datacenter_fabric.manage_vc:main
        fabric_init=juniper_datacenter_fabric.initialize_fabric:main
    '''
)
