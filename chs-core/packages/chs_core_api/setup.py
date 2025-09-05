"""CHS-Core API 包安装配置

本文件用于独立打包和分发 CHS-Core API 接口定义包。
其他团队可以通过安装此包来获得接口定义，而无需安装完整的实现。
"""

from setuptools import setup, find_packages
import os

# 读取版本信息
def get_version():
    """从 __init__.py 文件中读取版本号"""
    version_file = os.path.join(os.path.dirname(__file__), '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

# 读取长描述
def get_long_description():
    """读取详细描述"""
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "CHS-Core API 接口定义包"

setup(
    name="chs-core-api",
    version=get_version(),
    author="CHS Development Team",
    author_email="dev@chs-core.com",
    description="CHS-Core 系统的 API 接口定义包",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/chs-core/chs-core-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Hydrology",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 最小依赖，只包含类型定义所需的包
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "sphinx-autodoc-typehints>=1.12",
            "myst-parser>=0.15",
        ],
    },
    keywords=[
        "chs-core", "api", "interface", "hydrology", 
        "water-system", "simulation", "data-processing"
    ],
    project_urls={
        "Bug Reports": "https://github.com/chs-core/chs-core-api/issues",
        "Source": "https://github.com/chs-core/chs-core-api",
        "Documentation": "https://chs-core-api.readthedocs.io/",
    },
    include_package_data=True,
    package_data={
        "chs_core_api": ["py.typed"],  # 标记为类型化包
    },
    zip_safe=False,
)