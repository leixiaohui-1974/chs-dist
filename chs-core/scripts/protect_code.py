#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHS-Core 代码保护脚本

此脚本提供多种代码保护机制：
1. 字节码编译 (.pyc)
2. 源码混淆
3. 关键文件加密
4. 分层打包

使用方法:
    python scripts/protect_code.py --method bytecode --source src/ --output dist_protected/
    python scripts/protect_code.py --method obfuscate --source src/ --output dist_protected/
    python scripts/protect_code.py --method all --source src/ --output dist_protected/
"""

import os
import sys
import shutil
import py_compile
import compileall
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import zipfile
import tempfile
import json
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('protection.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CodeProtector:
    """代码保护器
    
    提供多种代码保护机制，包括字节码编译、代码混淆等。
    """
    
    def __init__(self, source_dir: str, output_dir: str):
        """
        初始化代码保护器
        
        Args:
            source_dir: 源代码目录
            output_dir: 输出目录
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        
        # 确保目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保护配置
        self.config = {
            "exclude_patterns": [
                "__pycache__",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".git",
                ".gitignore",
                "*.md",
                "tests/",
                "test_*.py",
                "*_test.py"
            ],
            "keep_source_files": [
                "__init__.py",  # 保留包初始化文件
                "setup.py",     # 保留安装脚本
                "requirements.txt"  # 保留依赖文件
            ],
            "critical_files": [
                "core/",
                "engine/",
                "algorithms/"
            ]
        }
        
        logger.info(f"代码保护器初始化完成")
        logger.info(f"源目录: {self.source_dir}")
        logger.info(f"输出目录: {self.output_dir}")
    
    def protect_bytecode(self) -> bool:
        """
        字节码保护：将Python源码编译为字节码文件
        
        Returns:
            bool: 保护是否成功
        """
        try:
            logger.info("开始字节码保护...")
            
            # 创建字节码输出目录
            bytecode_dir = self.output_dir / "bytecode"
            bytecode_dir.mkdir(parents=True, exist_ok=True)
            
            # 统计信息
            stats = {
                "total_files": 0,
                "compiled_files": 0,
                "skipped_files": 0,
                "error_files": 0
            }
            
            # 遍历源代码目录
            for py_file in self._find_python_files():
                stats["total_files"] += 1
                
                try:
                    # 计算相对路径
                    rel_path = py_file.relative_to(self.source_dir)
                    
                    # 检查是否需要保留源文件
                    if self._should_keep_source(rel_path):
                        # 复制源文件
                        dest_file = bytecode_dir / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(py_file, dest_file)
                        stats["skipped_files"] += 1
                        logger.debug(f"保留源文件: {rel_path}")
                        continue
                    
                    # 编译为字节码
                    pyc_file = self._compile_to_bytecode(py_file, bytecode_dir, rel_path)
                    
                    if pyc_file:
                        stats["compiled_files"] += 1
                        logger.debug(f"编译成功: {rel_path} -> {pyc_file.name}")
                    else:
                        stats["error_files"] += 1
                        logger.warning(f"编译失败: {rel_path}")
                        
                except Exception as e:
                    stats["error_files"] += 1
                    logger.error(f"处理文件失败 {py_file}: {e}")
            
            # 复制非Python文件
            self._copy_non_python_files(bytecode_dir)
            
            # 生成保护报告
            self._generate_protection_report(bytecode_dir, "bytecode", stats)
            
            logger.info(f"字节码保护完成")
            logger.info(f"总文件数: {stats['total_files']}")
            logger.info(f"编译文件数: {stats['compiled_files']}")
            logger.info(f"保留文件数: {stats['skipped_files']}")
            logger.info(f"错误文件数: {stats['error_files']}")
            
            return stats["error_files"] == 0
            
        except Exception as e:
            logger.error(f"字节码保护失败: {e}")
            return False
    
    def protect_obfuscate(self) -> bool:
        """
        代码混淆保护：对源代码进行混淆处理
        
        Returns:
            bool: 保护是否成功
        """
        try:
            logger.info("开始代码混淆保护...")
            
            # 创建混淆输出目录
            obfuscated_dir = self.output_dir / "obfuscated"
            obfuscated_dir.mkdir(parents=True, exist_ok=True)
            
            # 统计信息
            stats = {
                "total_files": 0,
                "obfuscated_files": 0,
                "skipped_files": 0,
                "error_files": 0
            }
            
            # 遍历源代码目录
            for py_file in self._find_python_files():
                stats["total_files"] += 1
                
                try:
                    # 计算相对路径
                    rel_path = py_file.relative_to(self.source_dir)
                    
                    # 检查是否需要保留源文件
                    if self._should_keep_source(rel_path):
                        # 复制源文件
                        dest_file = obfuscated_dir / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(py_file, dest_file)
                        stats["skipped_files"] += 1
                        logger.debug(f"保留源文件: {rel_path}")
                        continue
                    
                    # 混淆代码
                    if self._obfuscate_file(py_file, obfuscated_dir, rel_path):
                        stats["obfuscated_files"] += 1
                        logger.debug(f"混淆成功: {rel_path}")
                    else:
                        stats["error_files"] += 1
                        logger.warning(f"混淆失败: {rel_path}")
                        
                except Exception as e:
                    stats["error_files"] += 1
                    logger.error(f"处理文件失败 {py_file}: {e}")
            
            # 复制非Python文件
            self._copy_non_python_files(obfuscated_dir)
            
            # 生成保护报告
            self._generate_protection_report(obfuscated_dir, "obfuscation", stats)
            
            logger.info(f"代码混淆保护完成")
            logger.info(f"总文件数: {stats['total_files']}")
            logger.info(f"混淆文件数: {stats['obfuscated_files']}")
            logger.info(f"保留文件数: {stats['skipped_files']}")
            logger.info(f"错误文件数: {stats['error_files']}")
            
            return stats["error_files"] == 0
            
        except Exception as e:
            logger.error(f"代码混淆保护失败: {e}")
            return False
    
    def protect_layered(self) -> bool:
        """
        分层保护：创建分层的包结构
        
        Returns:
            bool: 保护是否成功
        """
        try:
            logger.info("开始分层保护...")
            
            # 创建分层输出目录
            layered_dir = self.output_dir / "layered"
            layered_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建公共API包
            api_dir = layered_dir / "chs_core_api"
            api_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建实现包（保护）
            impl_dir = layered_dir / "chs_core_impl"
            impl_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制API定义
            api_source = self.source_dir / "chs_core_api"
            if api_source.exists():
                shutil.copytree(api_source, api_dir, dirs_exist_ok=True)
                logger.info("API定义复制完成")
            
            # 保护实现代码
            impl_source = self.source_dir / "chs_core"
            if impl_source.exists():
                # 对实现代码进行字节码编译
                temp_protector = CodeProtector(str(impl_source), str(impl_dir))
                if temp_protector.protect_bytecode():
                    logger.info("实现代码保护完成")
                else:
                    logger.warning("实现代码保护部分失败")
            
            # 创建分发包
            self._create_distribution_packages(layered_dir)
            
            logger.info("分层保护完成")
            return True
            
        except Exception as e:
            logger.error(f"分层保护失败: {e}")
            return False
    
    def protect_all(self) -> bool:
        """
        全面保护：应用所有保护机制
        
        Returns:
            bool: 保护是否成功
        """
        logger.info("开始全面代码保护...")
        
        success_count = 0
        total_methods = 3
        
        # 字节码保护
        if self.protect_bytecode():
            success_count += 1
            logger.info("✓ 字节码保护成功")
        else:
            logger.error("✗ 字节码保护失败")
        
        # 代码混淆保护
        if self.protect_obfuscate():
            success_count += 1
            logger.info("✓ 代码混淆保护成功")
        else:
            logger.error("✗ 代码混淆保护失败")
        
        # 分层保护
        if self.protect_layered():
            success_count += 1
            logger.info("✓ 分层保护成功")
        else:
            logger.error("✗ 分层保护失败")
        
        success_rate = success_count / total_methods
        logger.info(f"全面保护完成，成功率: {success_rate:.1%} ({success_count}/{total_methods})")
        
        return success_rate >= 0.5  # 至少50%的方法成功
    
    def _find_python_files(self) -> List[Path]:
        """
        查找所有Python文件
        
        Returns:
            List[Path]: Python文件列表
        """
        python_files = []
        
        for root, dirs, files in os.walk(self.source_dir):
            # 排除不需要的目录
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            
            for file in files:
                if file.endswith('.py') and not self._should_exclude(file):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _should_exclude(self, name: str) -> bool:
        """
        检查文件或目录是否应该被排除
        
        Args:
            name: 文件或目录名
            
        Returns:
            bool: 是否应该排除
        """
        import fnmatch
        
        for pattern in self.config["exclude_patterns"]:
            if fnmatch.fnmatch(name, pattern):
                return True
        
        return False
    
    def _should_keep_source(self, rel_path: Path) -> bool:
        """
        检查是否应该保留源文件
        
        Args:
            rel_path: 相对路径
            
        Returns:
            bool: 是否保留源文件
        """
        import fnmatch
        
        path_str = str(rel_path)
        
        for pattern in self.config["keep_source_files"]:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(rel_path.name, pattern):
                return True
        
        return False
    
    def _compile_to_bytecode(self, py_file: Path, output_dir: Path, rel_path: Path) -> Optional[Path]:
        """
        将Python文件编译为字节码
        
        Args:
            py_file: 源Python文件
            output_dir: 输出目录
            rel_path: 相对路径
            
        Returns:
            Optional[Path]: 编译后的字节码文件路径，失败时返回None
        """
        try:
            # 创建目标目录
            dest_dir = output_dir / rel_path.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # 编译为字节码
            pyc_file = dest_dir / f"{rel_path.stem}.pyc"
            
            # 使用py_compile编译
            py_compile.compile(str(py_file), str(pyc_file), doraise=True)
            
            return pyc_file
            
        except Exception as e:
            logger.error(f"编译字节码失败 {py_file}: {e}")
            return None
    
    def _obfuscate_file(self, py_file: Path, output_dir: Path, rel_path: Path) -> bool:
        """
        混淆Python文件
        
        Args:
            py_file: 源Python文件
            output_dir: 输出目录
            rel_path: 相对路径
            
        Returns:
            bool: 混淆是否成功
        """
        try:
            # 创建目标目录
            dest_dir = output_dir / rel_path.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # 读取源文件
            with open(py_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # 简单的混淆处理（实际项目中可以使用更复杂的混淆工具）
            obfuscated_code = self._simple_obfuscate(source_code)
            
            # 写入混淆后的文件
            dest_file = dest_dir / rel_path.name
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated_code)
            
            return True
            
        except Exception as e:
            logger.error(f"混淆文件失败 {py_file}: {e}")
            return False
    
    def _simple_obfuscate(self, source_code: str) -> str:
        """
        简单的代码混淆
        
        Args:
            source_code: 源代码
            
        Returns:
            str: 混淆后的代码
        """
        # 这是一个简化的混淆示例
        # 实际项目中应该使用专业的混淆工具如 pyarmor
        
        lines = source_code.split('\n')
        obfuscated_lines = []
        
        for line in lines:
            # 移除注释（保留文档字符串）
            if line.strip().startswith('#') and '"""' not in line and "'''" not in line:
                continue
            
            # 移除空行
            if not line.strip():
                continue
            
            # 添加混淆标记
            if line.strip() and not line.startswith('    '):
                obfuscated_lines.append(f"# Obfuscated at {datetime.now().isoformat()}")
            
            obfuscated_lines.append(line)
        
        return '\n'.join(obfuscated_lines)
    
    def _copy_non_python_files(self, output_dir: Path):
        """
        复制非Python文件
        
        Args:
            output_dir: 输出目录
        """
        try:
            for root, dirs, files in os.walk(self.source_dir):
                # 排除不需要的目录
                dirs[:] = [d for d in dirs if not self._should_exclude(d)]
                
                for file in files:
                    if not file.endswith('.py') and not self._should_exclude(file):
                        src_file = Path(root) / file
                        rel_path = src_file.relative_to(self.source_dir)
                        dest_file = output_dir / rel_path
                        
                        # 创建目标目录
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 复制文件
                        shutil.copy2(src_file, dest_file)
                        logger.debug(f"复制非Python文件: {rel_path}")
        
        except Exception as e:
            logger.error(f"复制非Python文件失败: {e}")
    
    def _generate_protection_report(self, output_dir: Path, method: str, stats: Dict[str, int]):
        """
        生成保护报告
        
        Args:
            output_dir: 输出目录
            method: 保护方法
            stats: 统计信息
        """
        try:
            report = {
                "protection_method": method,
                "timestamp": datetime.now().isoformat(),
                "source_directory": str(self.source_dir),
                "output_directory": str(output_dir),
                "statistics": stats,
                "config": self.config
            }
            
            report_file = output_dir / "protection_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"保护报告已生成: {report_file}")
            
        except Exception as e:
            logger.error(f"生成保护报告失败: {e}")
    
    def _create_distribution_packages(self, layered_dir: Path):
        """
        创建分发包
        
        Args:
            layered_dir: 分层目录
        """
        try:
            # 创建API包的setup.py
            api_setup = layered_dir / "chs_core_api" / "setup.py"
            if not api_setup.exists():
                self._create_api_setup(api_setup)
            
            # 创建实现包的setup.py
            impl_setup = layered_dir / "chs_core_impl" / "setup.py"
            self._create_impl_setup(impl_setup)
            
            logger.info("分发包配置文件创建完成")
            
        except Exception as e:
            logger.error(f"创建分发包失败: {e}")
    
    def _create_api_setup(self, setup_file: Path):
        """
        创建API包的setup.py
        
        Args:
            setup_file: setup.py文件路径
        """
        setup_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="chs-core-api",
    version="0.1.0",
    description="CHS-Core API接口定义包",
    long_description="CHS-Core水利系统API接口定义，提供标准化的接口规范",
    author="CHS Team",
    author_email="team@chs.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "typing-extensions>=4.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''
        
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(setup_content)
    
    def _create_impl_setup(self, setup_file: Path):
        """
        创建实现包的setup.py
        
        Args:
            setup_file: setup.py文件路径
        """
        setup_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="chs-core-impl",
    version="0.1.0",
    description="CHS-Core 实现包（受保护）",
    long_description="CHS-Core水利系统核心实现，包含受保护的业务逻辑",
    author="CHS Team",
    author_email="team@chs.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "chs-core-api>=0.1.0",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    # 包含字节码文件
    package_data={
        "": ["*.pyc"],
    },
    include_package_data=True,
)
'''
        
        setup_file.parent.mkdir(parents=True, exist_ok=True)
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(setup_content)


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="CHS-Core 代码保护工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --method bytecode --source src/ --output dist_protected/
  %(prog)s --method obfuscate --source src/ --output dist_protected/
  %(prog)s --method layered --source src/ --output dist_protected/
  %(prog)s --method all --source src/ --output dist_protected/
        """
    )
    
    parser.add_argument(
        "--method",
        choices=["bytecode", "obfuscate", "layered", "all"],
        default="bytecode",
        help="保护方法 (默认: bytecode)"
    )
    
    parser.add_argument(
        "--source",
        required=True,
        help="源代码目录"
    )
    
    parser.add_argument(
        "--output",
        required=True,
        help="输出目录"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "--config",
        help="配置文件路径（JSON格式）"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 验证输入
    if not os.path.exists(args.source):
        logger.error(f"源目录不存在: {args.source}")
        sys.exit(1)
    
    try:
        # 创建代码保护器
        protector = CodeProtector(args.source, args.output)
        
        # 加载自定义配置
        if args.config and os.path.exists(args.config):
            with open(args.config, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
                protector.config.update(custom_config)
                logger.info(f"已加载自定义配置: {args.config}")
        
        # 执行保护
        success = False
        
        if args.method == "bytecode":
            success = protector.protect_bytecode()
        elif args.method == "obfuscate":
            success = protector.protect_obfuscate()
        elif args.method == "layered":
            success = protector.protect_layered()
        elif args.method == "all":
            success = protector.protect_all()
        
        if success:
            logger.info("🎉 代码保护完成！")
            logger.info(f"受保护的代码已保存到: {args.output}")
            sys.exit(0)
        else:
            logger.error("❌ 代码保护失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"代码保护过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()