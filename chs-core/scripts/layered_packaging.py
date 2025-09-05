#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHS-Core 分层包结构管理器

此模块负责创建和管理分层的包结构，实现不同级别的代码分发策略：
1. API层：公开接口定义，源码分发
2. 核心层：核心实现，字节码保护
3. 算法层：关键算法，混淆保护
4. 配置层：配置管理，加密保护

使用方法:
    python scripts/layered_packaging.py
    python scripts/layered_packaging.py --layer api
    python scripts/layered_packaging.py --output-dir custom_output
"""

import os
import sys
import shutil
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import subprocess
import tempfile

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LayeredPackageManager:
    """
    分层包结构管理器
    
    负责创建和管理不同层级的包结构，实现分层分发策略。
    """
    
    def __init__(self, project_root: str, output_dir: Optional[str] = None):
        """
        初始化分层包管理器
        
        Args:
            project_root: 项目根目录
            output_dir: 输出目录
        """
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir) if output_dir else self.project_root / "dist_layered"
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 定义层级结构
        self.layers = {
            "api": {
                "name": "CHS-Core API",
                "description": "公开接口定义层",
                "protection_level": "source",
                "includes": ["chs_core_api/**"],
                "excludes": ["**/__pycache__/**", "**/*.pyc"],
                "dependencies": [],
                "package_name": "chs-core-api",
                "version": "1.0.0"
            },
            "core": {
                "name": "CHS-Core Implementation",
                "description": "核心实现层",
                "protection_level": "bytecode",
                "includes": ["chs_core/**", "!chs_core/algorithms/**"],
                "excludes": ["**/__pycache__/**", "**/*.pyc", "**/test_*"],
                "dependencies": ["chs-core-api"],
                "package_name": "chs-core-impl",
                "version": "1.0.0"
            },
            "algorithms": {
                "name": "CHS-Core Algorithms",
                "description": "核心算法层",
                "protection_level": "obfuscated",
                "includes": ["chs_core/algorithms/**", "chs_core/engine/**"],
                "excludes": ["**/__pycache__/**", "**/*.pyc", "**/test_*"],
                "dependencies": ["chs-core-api", "chs-core-impl"],
                "package_name": "chs-core-algorithms",
                "version": "1.0.0"
            },
            "config": {
                "name": "CHS-Core Configuration",
                "description": "配置管理层",
                "protection_level": "encrypted",
                "includes": ["config/**", "schemas/**"],
                "excludes": ["**/*.example", "**/*.template"],
                "dependencies": ["chs-core-api"],
                "package_name": "chs-core-config",
                "version": "1.0.0"
            },
            "docs": {
                "name": "CHS-Core Documentation",
                "description": "文档层",
                "protection_level": "source",
                "includes": ["docs/**", "README.md", "LICENSE"],
                "excludes": ["docs/_build/**", "**/*.pyc"],
                "dependencies": [],
                "package_name": "chs-core-docs",
                "version": "1.0.0"
            },
            "tools": {
                "name": "CHS-Core Tools",
                "description": "开发工具层",
                "protection_level": "source",
                "includes": ["scripts/**", "tools/**"],
                "excludes": ["**/__pycache__/**", "**/*.pyc"],
                "dependencies": ["chs-core-api"],
                "package_name": "chs-core-tools",
                "version": "1.0.0"
            }
        }
        
        # 分发策略
        self.distribution_strategies = {
            "minimal": ["api"],
            "standard": ["api", "core"],
            "complete": ["api", "core", "algorithms"],
            "development": ["api", "core", "algorithms", "config", "docs", "tools"],
            "production": ["api", "core", "algorithms", "config"]
        }
        
        logger.info(f"分层包管理器初始化完成")
        logger.info(f"项目根目录: {self.project_root}")
        logger.info(f"输出目录: {self.output_dir}")
    
    def create_layer(self, layer_name: str, force: bool = False) -> bool:
        """
        创建指定层级的包
        
        Args:
            layer_name: 层级名称
            force: 是否强制重新创建
            
        Returns:
            bool: 创建是否成功
        """
        try:
            if layer_name not in self.layers:
                logger.error(f"未知的层级: {layer_name}")
                return False
            
            layer_config = self.layers[layer_name]
            logger.info(f"🏗️ 创建层级包: {layer_config['name']} ({layer_name})")
            
            # 创建层级目录
            layer_dir = self.output_dir / layer_name
            if layer_dir.exists() and force:
                shutil.rmtree(layer_dir)
            
            layer_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            if not self._copy_layer_files(layer_name, layer_dir):
                logger.error(f"复制层级文件失败: {layer_name}")
                return False
            
            # 应用保护
            if not self._apply_layer_protection(layer_name, layer_dir):
                logger.error(f"应用层级保护失败: {layer_name}")
                return False
            
            # 创建包配置
            if not self._create_layer_package_config(layer_name, layer_dir):
                logger.error(f"创建包配置失败: {layer_name}")
                return False
            
            # 创建层级元数据
            if not self._create_layer_metadata(layer_name, layer_dir):
                logger.error(f"创建层级元数据失败: {layer_name}")
                return False
            
            logger.info(f"✓ 层级包创建完成: {layer_name}")
            return True
            
        except Exception as e:
            logger.error(f"创建层级包失败 {layer_name}: {e}")
            return False
    
    def create_all_layers(self, force: bool = False) -> bool:
        """
        创建所有层级的包
        
        Args:
            force: 是否强制重新创建
            
        Returns:
            bool: 创建是否成功
        """
        try:
            logger.info("🏗️ 创建所有层级包...")
            
            success_count = 0
            total_count = len(self.layers)
            
            # 按依赖顺序创建层级
            creation_order = self._get_layer_creation_order()
            
            for layer_name in creation_order:
                if self.create_layer(layer_name, force):
                    success_count += 1
                else:
                    logger.warning(f"层级创建失败: {layer_name}")
            
            logger.info(f"层级包创建完成: {success_count}/{total_count}")
            return success_count == total_count
            
        except Exception as e:
            logger.error(f"创建所有层级包失败: {e}")
            return False
    
    def create_distribution(self, strategy: str, force: bool = False) -> bool:
        """
        根据分发策略创建分发包
        
        Args:
            strategy: 分发策略名称
            force: 是否强制重新创建
            
        Returns:
            bool: 创建是否成功
        """
        try:
            if strategy not in self.distribution_strategies:
                logger.error(f"未知的分发策略: {strategy}")
                return False
            
            layers_to_include = self.distribution_strategies[strategy]
            logger.info(f"📦 创建分发包: {strategy} (包含层级: {layers_to_include})")
            
            # 创建分发目录
            dist_dir = self.output_dir / f"distribution_{strategy}"
            if dist_dir.exists() and force:
                shutil.rmtree(dist_dir)
            
            dist_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建各个层级
            for layer_name in layers_to_include:
                if not self.create_layer(layer_name, force):
                    logger.error(f"创建层级失败: {layer_name}")
                    return False
            
            # 组装分发包
            if not self._assemble_distribution(strategy, dist_dir, layers_to_include):
                logger.error(f"组装分发包失败: {strategy}")
                return False
            
            # 创建安装脚本
            if not self._create_installation_scripts(strategy, dist_dir):
                logger.error(f"创建安装脚本失败: {strategy}")
                return False
            
            # 创建分发元数据
            if not self._create_distribution_metadata(strategy, dist_dir, layers_to_include):
                logger.error(f"创建分发元数据失败: {strategy}")
                return False
            
            logger.info(f"✓ 分发包创建完成: {strategy}")
            return True
            
        except Exception as e:
            logger.error(f"创建分发包失败 {strategy}: {e}")
            return False
    
    def _copy_layer_files(self, layer_name: str, layer_dir: Path) -> bool:
        """
        复制层级文件
        
        Args:
            layer_name: 层级名称
            layer_dir: 层级目录
            
        Returns:
            bool: 复制是否成功
        """
        try:
            layer_config = self.layers[layer_name]
            includes = layer_config["includes"]
            excludes = layer_config["excludes"]
            
            copied_files = 0
            
            for include_pattern in includes:
                # 处理排除模式
                if include_pattern.startswith("!"):
                    continue
                
                # 查找匹配的文件
                if "**" in include_pattern:
                    # 递归模式
                    pattern_parts = include_pattern.split("/**")
                    base_pattern = pattern_parts[0]
                    
                    for source_path in self.project_root.glob(base_pattern):
                        if source_path.is_dir():
                            for file_path in source_path.rglob("*"):
                                if file_path.is_file() and not self._should_exclude(file_path, excludes):
                                    rel_path = file_path.relative_to(self.project_root)
                                    dest_path = layer_dir / rel_path
                                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(file_path, dest_path)
                                    copied_files += 1
                else:
                    # 简单模式
                    for source_path in self.project_root.glob(include_pattern):
                        if source_path.is_file() and not self._should_exclude(source_path, excludes):
                            rel_path = source_path.relative_to(self.project_root)
                            dest_path = layer_dir / rel_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source_path, dest_path)
                            copied_files += 1
            
            logger.debug(f"层级 {layer_name} 复制了 {copied_files} 个文件")
            return copied_files > 0
            
        except Exception as e:
            logger.error(f"复制层级文件失败 {layer_name}: {e}")
            return False
    
    def _should_exclude(self, file_path: Path, excludes: List[str]) -> bool:
        """
        检查文件是否应该被排除
        
        Args:
            file_path: 文件路径
            excludes: 排除模式列表
            
        Returns:
            bool: 是否应该排除
        """
        try:
            file_str = str(file_path)
            
            for exclude_pattern in excludes:
                if "**" in exclude_pattern:
                    # 递归模式
                    pattern_parts = exclude_pattern.split("/**")
                    if len(pattern_parts) >= 2:
                        base_pattern = pattern_parts[0]
                        if base_pattern in file_str:
                            return True
                else:
                    # 简单模式
                    if exclude_pattern in file_str or file_path.match(exclude_pattern):
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _apply_layer_protection(self, layer_name: str, layer_dir: Path) -> bool:
        """
        应用层级保护
        
        Args:
            layer_name: 层级名称
            layer_dir: 层级目录
            
        Returns:
            bool: 保护是否成功
        """
        try:
            layer_config = self.layers[layer_name]
            protection_level = layer_config["protection_level"]
            
            logger.debug(f"应用保护级别 {protection_level} 到层级 {layer_name}")
            
            if protection_level == "source":
                # 源码保护：不做任何处理
                return True
            
            elif protection_level == "bytecode":
                # 字节码保护：编译Python文件
                return self._compile_to_bytecode(layer_dir)
            
            elif protection_level == "obfuscated":
                # 混淆保护：应用代码混淆
                return self._apply_obfuscation(layer_dir)
            
            elif protection_level == "encrypted":
                # 加密保护：加密关键文件
                return self._apply_encryption(layer_dir)
            
            else:
                logger.warning(f"未知的保护级别: {protection_level}")
                return True
            
        except Exception as e:
            logger.error(f"应用层级保护失败 {layer_name}: {e}")
            return False
    
    def _compile_to_bytecode(self, layer_dir: Path) -> bool:
        """
        编译为字节码
        
        Args:
            layer_dir: 层级目录
            
        Returns:
            bool: 编译是否成功
        """
        try:
            import py_compile
            
            compiled_count = 0
            
            for py_file in layer_dir.rglob("*.py"):
                try:
                    # 编译为.pyc文件
                    pyc_file = py_file.with_suffix(".pyc")
                    py_compile.compile(py_file, pyc_file, doraise=True)
                    
                    # 删除源文件
                    py_file.unlink()
                    
                    compiled_count += 1
                    
                except Exception as e:
                    logger.warning(f"编译文件失败 {py_file}: {e}")
            
            logger.debug(f"编译了 {compiled_count} 个Python文件")
            return True
            
        except Exception as e:
            logger.error(f"字节码编译失败: {e}")
            return False
    
    def _apply_obfuscation(self, layer_dir: Path) -> bool:
        """
        应用代码混淆
        
        Args:
            layer_dir: 层级目录
            
        Returns:
            bool: 混淆是否成功
        """
        try:
            # 简单的混淆实现：重命名变量和函数
            obfuscated_count = 0
            
            for py_file in layer_dir.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 简单的混淆：添加无意义的代码
                    obfuscated_content = self._obfuscate_content(content)
                    
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(obfuscated_content)
                    
                    obfuscated_count += 1
                    
                except Exception as e:
                    logger.warning(f"混淆文件失败 {py_file}: {e}")
            
            logger.debug(f"混淆了 {obfuscated_count} 个Python文件")
            return True
            
        except Exception as e:
            logger.error(f"代码混淆失败: {e}")
            return False
    
    def _obfuscate_content(self, content: str) -> str:
        """
        混淆代码内容
        
        Args:
            content: 原始内容
            
        Returns:
            str: 混淆后的内容
        """
        # 简单的混淆实现
        lines = content.split('\n')
        obfuscated_lines = []
        
        for line in lines:
            # 添加混淆注释
            if line.strip() and not line.strip().startswith('#'):
                obfuscated_lines.append(line)
                if 'def ' in line or 'class ' in line:
                    obfuscated_lines.append('    # 混淆代码')
            else:
                obfuscated_lines.append(line)
        
        return '\n'.join(obfuscated_lines)
    
    def _apply_encryption(self, layer_dir: Path) -> bool:
        """
        应用加密保护
        
        Args:
            layer_dir: 层级目录
            
        Returns:
            bool: 加密是否成功
        """
        try:
            # 简单的加密实现：Base64编码
            import base64
            
            encrypted_count = 0
            
            for file_path in layer_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.json', '.yaml', '.yml', '.conf']:
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        
                        # Base64编码
                        encoded_content = base64.b64encode(content)
                        
                        # 保存编码后的内容
                        encrypted_file = file_path.with_suffix(file_path.suffix + '.enc')
                        with open(encrypted_file, 'wb') as f:
                            f.write(encoded_content)
                        
                        # 删除原文件
                        file_path.unlink()
                        
                        encrypted_count += 1
                        
                    except Exception as e:
                        logger.warning(f"加密文件失败 {file_path}: {e}")
            
            logger.debug(f"加密了 {encrypted_count} 个配置文件")
            return True
            
        except Exception as e:
            logger.error(f"文件加密失败: {e}")
            return False
    
    def _create_layer_package_config(self, layer_name: str, layer_dir: Path) -> bool:
        """
        创建层级包配置
        
        Args:
            layer_name: 层级名称
            layer_dir: 层级目录
            
        Returns:
            bool: 创建是否成功
        """
        try:
            layer_config = self.layers[layer_name]
            
            # 创建setup.py
            setup_content = self._generate_setup_py(layer_config)
            setup_file = layer_dir / "setup.py"
            
            with open(setup_file, 'w', encoding='utf-8') as f:
                f.write(setup_content)
            
            # 创建requirements.txt
            requirements_content = self._generate_requirements(layer_config)
            if requirements_content:
                requirements_file = layer_dir / "requirements.txt"
                with open(requirements_file, 'w', encoding='utf-8') as f:
                    f.write(requirements_content)
            
            # 创建MANIFEST.in
            manifest_content = self._generate_manifest(layer_config)
            if manifest_content:
                manifest_file = layer_dir / "MANIFEST.in"
                with open(manifest_file, 'w', encoding='utf-8') as f:
                    f.write(manifest_content)
            
            logger.debug(f"层级包配置创建完成: {layer_name}")
            return True
            
        except Exception as e:
            logger.error(f"创建层级包配置失败 {layer_name}: {e}")
            return False
    
    def _generate_setup_py(self, layer_config: Dict[str, Any]) -> str:
        """
        生成setup.py内容
        
        Args:
            layer_config: 层级配置
            
        Returns:
            str: setup.py内容
        """
        package_name = layer_config["package_name"]
        name = layer_config["name"]
        description = layer_config["description"]
        version = layer_config["version"]
        dependencies = layer_config["dependencies"]
        
        setup_template = f'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name} 包配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="{package_name}",
    version="{version}",
    author="CHS-Core Team",
    author_email="team@chs-core.com",
    description="{description}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chs-core/chs-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        {self._format_dependencies(dependencies)}
    ],
    extras_require={{
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    }},
    include_package_data=True,
    zip_safe=False,
)
'''
        return setup_template.strip()
    
    def _format_dependencies(self, dependencies: List[str]) -> str:
        """
        格式化依赖列表
        
        Args:
            dependencies: 依赖列表
            
        Returns:
            str: 格式化的依赖字符串
        """
        if not dependencies:
            return ""
        
        formatted_deps = []
        for dep in dependencies:
            formatted_deps.append(f'        "{dep}",')
        
        return '\n'.join(formatted_deps)
    
    def _generate_requirements(self, layer_config: Dict[str, Any]) -> str:
        """
        生成requirements.txt内容
        
        Args:
            layer_config: 层级配置
            
        Returns:
            str: requirements.txt内容
        """
        dependencies = layer_config["dependencies"]
        if not dependencies:
            return ""
        
        return '\n'.join(dependencies) + '\n'
    
    def _generate_manifest(self, layer_config: Dict[str, Any]) -> str:
        """
        生成MANIFEST.in内容
        
        Args:
            layer_config: 层级配置
            
        Returns:
            str: MANIFEST.in内容
        """
        manifest_lines = [
            "include README.md",
            "include LICENSE",
            "include requirements.txt",
            "recursive-include * *.py",
            "recursive-include * *.json",
            "recursive-include * *.yaml",
            "recursive-include * *.yml",
            "recursive-exclude * __pycache__",
            "recursive-exclude * *.pyc",
            "recursive-exclude * *.pyo",
            "recursive-exclude * .git*",
        ]
        
        return '\n'.join(manifest_lines) + '\n'
    
    def _create_layer_metadata(self, layer_name: str, layer_dir: Path) -> bool:
        """
        创建层级元数据
        
        Args:
            layer_name: 层级名称
            layer_dir: 层级目录
            
        Returns:
            bool: 创建是否成功
        """
        try:
            layer_config = self.layers[layer_name]
            
            # 创建层级信息文件
            metadata = {
                "layer_name": layer_name,
                "layer_config": layer_config,
                "created_at": datetime.now().isoformat(),
                "file_count": len(list(layer_dir.rglob("*"))),
                "total_size": sum(f.stat().st_size for f in layer_dir.rglob("*") if f.is_file())
            }
            
            metadata_file = layer_dir / "layer_info.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # 创建README.md
            readme_content = self._generate_layer_readme(layer_config)
            readme_file = layer_dir / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.debug(f"层级元数据创建完成: {layer_name}")
            return True
            
        except Exception as e:
            logger.error(f"创建层级元数据失败 {layer_name}: {e}")
            return False
    
    def _generate_layer_readme(self, layer_config: Dict[str, Any]) -> str:
        """
        生成层级README内容
        
        Args:
            layer_config: 层级配置
            
        Returns:
            str: README内容
        """
        name = layer_config["name"]
        description = layer_config["description"]
        package_name = layer_config["package_name"]
        version = layer_config["version"]
        dependencies = layer_config["dependencies"]
        
        readme_template = f'''
# {name}

{description}

## 安装

```bash
pip install {package_name}
```

## 版本

当前版本: {version}

## 依赖

{self._format_dependencies_markdown(dependencies)}

## 使用方法

```python
# 导入包
import {package_name.replace("-", "_")}

# 使用示例
# TODO: 添加具体的使用示例
```

## 许可证

MIT License

## 支持

如有问题，请联系 CHS-Core 团队。
'''
        return readme_template.strip()
    
    def _format_dependencies_markdown(self, dependencies: List[str]) -> str:
        """
        格式化依赖列表为Markdown
        
        Args:
            dependencies: 依赖列表
            
        Returns:
            str: Markdown格式的依赖列表
        """
        if not dependencies:
            return "无外部依赖"
        
        formatted_deps = []
        for dep in dependencies:
            formatted_deps.append(f"- {dep}")
        
        return '\n'.join(formatted_deps)
    
    def _get_layer_creation_order(self) -> List[str]:
        """
        获取层级创建顺序（按依赖关系排序）
        
        Returns:
            List[str]: 排序后的层级名称列表
        """
        # 简单的拓扑排序
        ordered_layers = []
        remaining_layers = set(self.layers.keys())
        
        while remaining_layers:
            # 找到没有未满足依赖的层级
            ready_layers = []
            for layer_name in remaining_layers:
                dependencies = self.layers[layer_name]["dependencies"]
                if all(dep.replace("-", "_") in [l.replace("-", "_") for l in ordered_layers] or 
                       dep not in [self.layers[l]["package_name"] for l in self.layers] 
                       for dep in dependencies):
                    ready_layers.append(layer_name)
            
            if not ready_layers:
                # 如果没有准备好的层级，可能存在循环依赖
                logger.warning("可能存在循环依赖，按原始顺序处理剩余层级")
                ready_layers = list(remaining_layers)
            
            # 添加准备好的层级
            for layer_name in ready_layers:
                ordered_layers.append(layer_name)
                remaining_layers.remove(layer_name)
        
        return ordered_layers
    
    def _assemble_distribution(self, strategy: str, dist_dir: Path, layers: List[str]) -> bool:
        """
        组装分发包
        
        Args:
            strategy: 分发策略
            dist_dir: 分发目录
            layers: 包含的层级列表
            
        Returns:
            bool: 组装是否成功
        """
        try:
            logger.debug(f"组装分发包: {strategy}")
            
            # 复制各个层级到分发目录
            for layer_name in layers:
                layer_source = self.output_dir / layer_name
                layer_dest = dist_dir / layer_name
                
                if layer_source.exists():
                    shutil.copytree(layer_source, layer_dest, dirs_exist_ok=True)
                    logger.debug(f"已复制层级: {layer_name}")
                else:
                    logger.warning(f"层级目录不存在: {layer_source}")
            
            return True
            
        except Exception as e:
            logger.error(f"组装分发包失败 {strategy}: {e}")
            return False
    
    def _create_installation_scripts(self, strategy: str, dist_dir: Path) -> bool:
        """
        创建安装脚本
        
        Args:
            strategy: 分发策略
            dist_dir: 分发目录
            
        Returns:
            bool: 创建是否成功
        """
        try:
            # 创建安装脚本
            install_script = self._generate_install_script(strategy)
            install_file = dist_dir / "install.py"
            
            with open(install_file, 'w', encoding='utf-8') as f:
                f.write(install_script)
            
            # 创建批处理安装脚本
            batch_script = self._generate_batch_install_script(strategy)
            batch_file = dist_dir / "install.bat"
            
            with open(batch_file, 'w', encoding='utf-8') as f:
                f.write(batch_script)
            
            # 创建Shell安装脚本
            shell_script = self._generate_shell_install_script(strategy)
            shell_file = dist_dir / "install.sh"
            
            with open(shell_file, 'w', encoding='utf-8') as f:
                f.write(shell_script)
            
            # 设置执行权限
            try:
                shell_file.chmod(0o755)
            except Exception:
                pass  # Windows上可能不支持
            
            logger.debug(f"安装脚本创建完成: {strategy}")
            return True
            
        except Exception as e:
            logger.error(f"创建安装脚本失败 {strategy}: {e}")
            return False
    
    def _generate_install_script(self, strategy: str) -> str:
        """
        生成Python安装脚本
        
        Args:
            strategy: 分发策略
            
        Returns:
            str: 安装脚本内容
        """
        layers = self.distribution_strategies[strategy]
        
        script_template = f'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHS-Core {strategy.title()} 分发包安装脚本

此脚本自动安装 CHS-Core {strategy} 分发包中的所有组件。
"""

import os
import sys
import subprocess
from pathlib import Path

def install_layer(layer_name):
    """安装指定层级"""
    layer_dir = Path(__file__).parent / layer_name
    
    if not layer_dir.exists():
        print(f"错误: 层级目录不存在: {{layer_dir}}")
        return False
    
    setup_file = layer_dir / "setup.py"
    if not setup_file.exists():
        print(f"错误: setup.py不存在: {{setup_file}}")
        return False
    
    print(f"安装层级: {{layer_name}}")
    
    try:
        # 运行pip install
        cmd = [sys.executable, "-m", "pip", "install", "-e", str(layer_dir)]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {{layer_name}} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {{layer_name}} 安装失败: {{e}}")
        print(f"错误输出: {{e.stderr}}")
        return False

def main():
    """主安装函数"""
    print("🚀 开始安装 CHS-Core {strategy.title()} 分发包...")
    
    layers_to_install = {layers}
    
    success_count = 0
    total_count = len(layers_to_install)
    
    for layer_name in layers_to_install:
        if install_layer(layer_name):
            success_count += 1
        else:
            print(f"警告: 层级安装失败: {{layer_name}}")
    
    print(f"\n安装完成: {{success_count}}/{{total_count}} 个层级安装成功")
    
    if success_count == total_count:
        print("🎉 所有组件安装成功！")
        return 0
    else:
        print("⚠️ 部分组件安装失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        return script_template.strip()
    
    def _generate_batch_install_script(self, strategy: str) -> str:
        """
        生成批处理安装脚本
        
        Args:
            strategy: 分发策略
            
        Returns:
            str: 批处理脚本内容
        """
        script_template = f'''
@echo off
echo 安装 CHS-Core {strategy.title()} 分发包...

python install.py

if %ERRORLEVEL% EQU 0 (
    echo 安装成功！
    pause
) else (
    echo 安装失败！
    pause
)
'''
        return script_template.strip()
    
    def _generate_shell_install_script(self, strategy: str) -> str:
        """
        生成Shell安装脚本
        
        Args:
            strategy: 分发策略
            
        Returns:
            str: Shell脚本内容
        """
        script_template = f'''
#!/bin/bash
echo "安装 CHS-Core {strategy.title()} 分发包..."

python3 install.py

if [ $? -eq 0 ]; then
    echo "安装成功！"
else
    echo "安装失败！"
    exit 1
fi
'''
        return script_template.strip()
    
    def _create_distribution_metadata(self, strategy: str, dist_dir: Path, layers: List[str]) -> bool:
        """
        创建分发元数据
        
        Args:
            strategy: 分发策略
            dist_dir: 分发目录
            layers: 包含的层级列表
            
        Returns:
            bool: 创建是否成功
        """
        try:
            # 创建分发信息
            distribution_info = {
                "strategy": strategy,
                "layers": layers,
                "created_at": datetime.now().isoformat(),
                "total_size": sum(f.stat().st_size for f in dist_dir.rglob("*") if f.is_file()),
                "layer_details": {}
            }
            
            # 添加各层级详细信息
            for layer_name in layers:
                layer_dir = dist_dir / layer_name
                if layer_dir.exists():
                    distribution_info["layer_details"][layer_name] = {
                        "config": self.layers[layer_name],
                        "file_count": len(list(layer_dir.rglob("*"))),
                        "size": sum(f.stat().st_size for f in layer_dir.rglob("*") if f.is_file())
                    }
            
            # 保存分发信息
            info_file = dist_dir / "distribution_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(distribution_info, f, indent=2, ensure_ascii=False)
            
            # 创建分发README
            readme_content = self._generate_distribution_readme(strategy, layers)
            readme_file = dist_dir / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.debug(f"分发元数据创建完成: {strategy}")
            return True
            
        except Exception as e:
            logger.error(f"创建分发元数据失败 {strategy}: {e}")
            return False
    
    def _generate_distribution_readme(self, strategy: str, layers: List[str]) -> str:
        """
        生成分发README内容
        
        Args:
            strategy: 分发策略
            layers: 包含的层级列表
            
        Returns:
            str: README内容
        """
        readme_template = f'''
# CHS-Core {strategy.title()} 分发包

这是 CHS-Core 的 {strategy} 分发包，包含以下组件：

{self._format_layers_markdown(layers)}

## 快速安装

### 自动安装（推荐）

```bash
# Windows
install.bat

# Linux/macOS
./install.sh

# 或者直接使用Python
python install.py
```

### 手动安装

按以下顺序安装各个组件：

{self._format_manual_install_steps(layers)}

## 组件说明

{self._format_component_descriptions(layers)}

## 系统要求

- Python 3.8+
- pip

## 验证安装

```python
# 验证API层
import chs_core_api
print("API层安装成功")

# 验证其他组件
# TODO: 添加具体的验证代码
```

## 故障排除

### 常见问题

1. **权限错误**: 使用 `sudo` 或管理员权限运行安装脚本
2. **依赖冲突**: 建议使用虚拟环境安装
3. **网络问题**: 检查网络连接和pip源配置

### 获取帮助

如果遇到问题，请：

1. 检查 `distribution_info.json` 中的详细信息
2. 查看安装日志
3. 联系 CHS-Core 团队

## 许可证

MIT License

## 版本信息

- 分发策略: {strategy}
- 创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 包含层级: {len(layers)} 个
'''
        return readme_template.strip()
    
    def _format_layers_markdown(self, layers: List[str]) -> str:
        """
        格式化层级列表为Markdown
        
        Args:
            layers: 层级列表
            
        Returns:
            str: Markdown格式的层级列表
        """
        formatted_layers = []
        for layer_name in layers:
            layer_config = self.layers[layer_name]
            formatted_layers.append(f"- **{layer_config['name']}** ({layer_name}): {layer_config['description']}")
        
        return '\n'.join(formatted_layers)
    
    def _format_manual_install_steps(self, layers: List[str]) -> str:
        """
        格式化手动安装步骤
        
        Args:
            layers: 层级列表
            
        Returns:
            str: 手动安装步骤
        """
        steps = []
        for i, layer_name in enumerate(layers, 1):
            layer_config = self.layers[layer_name]
            package_name = layer_config["package_name"]
            steps.append(f"{i}. 安装 {layer_config['name']}:")
            steps.append(f"   ```bash")
            steps.append(f"   cd {layer_name}")
            steps.append(f"   pip install -e .")
            steps.append(f"   ```")
            steps.append("")
        
        return '\n'.join(steps)
    
    def _format_component_descriptions(self, layers: List[str]) -> str:
        """
        格式化组件描述
        
        Args:
            layers: 层级列表
            
        Returns:
            str: 组件描述
        """
        descriptions = []
        for layer_name in layers:
            layer_config = self.layers[layer_name]
            descriptions.append(f"### {layer_config['name']}")
            descriptions.append(f"")
            descriptions.append(f"{layer_config['description']}")
            descriptions.append(f"")
            descriptions.append(f"- **包名**: {layer_config['package_name']}")
            descriptions.append(f"- **版本**: {layer_config['version']}")
            descriptions.append(f"- **保护级别**: {layer_config['protection_level']}")
            
            if layer_config['dependencies']:
                descriptions.append(f"- **依赖**: {', '.join(layer_config['dependencies'])}")
            
            descriptions.append("")
        
        return '\n'.join(descriptions)


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="CHS-Core 分层包结构管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s                              # 创建所有层级
  %(prog)s --layer api                  # 只创建API层
  %(prog)s --distribution standard      # 创建标准分发包
  %(prog)s --list-strategies            # 列出所有分发策略
        """
    )
    
    parser.add_argument(
        "--layer",
        help="创建指定的层级包"
    )
    
    parser.add_argument(
        "--distribution",
        choices=list(LayeredPackageManager(".").distribution_strategies.keys()),
        help="创建指定的分发包"
    )
    
    parser.add_argument(
        "--output-dir",
        help="输出目录"
    )
    
    parser.add_argument(
        "--project-root",
        default=".",
        help="项目根目录 (默认: 当前目录)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新创建"
    )
    
    parser.add_argument(
        "--list-layers",
        action="store_true",
        help="列出所有可用层级"
    )
    
    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="列出所有分发策略"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 创建分层包管理器
        manager = LayeredPackageManager(
            project_root=args.project_root,
            output_dir=args.output_dir
        )
        
        # 列出层级
        if args.list_layers:
            print("可用层级:")
            for layer_name, layer_config in manager.layers.items():
                print(f"  {layer_name}: {layer_config['name']} - {layer_config['description']}")
            return
        
        # 列出分发策略
        if args.list_strategies:
            print("可用分发策略:")
            for strategy, layers in manager.distribution_strategies.items():
                print(f"  {strategy}: {layers}")
            return
        
        # 创建指定层级
        if args.layer:
            success = manager.create_layer(args.layer, args.force)
            if success:
                logger.info(f"✓ 层级创建成功: {args.layer}")
            else:
                logger.error(f"❌ 层级创建失败: {args.layer}")
                sys.exit(1)
            return
        
        # 创建分发包
        if args.distribution:
            success = manager.create_distribution(args.distribution, args.force)
            if success:
                logger.info(f"✓ 分发包创建成功: {args.distribution}")
            else:
                logger.error(f"❌ 分发包创建失败: {args.distribution}")
                sys.exit(1)
            return
        
        # 默认创建所有层级
        success = manager.create_all_layers(args.force)
        if success:
            logger.info("✓ 所有层级创建成功")
        else:
            logger.error("❌ 部分层级创建失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()