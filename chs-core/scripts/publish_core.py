#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHS-Core 发布脚本

该脚本用于自动化CHS-Core项目的发布流程，包括：
1. 代码质量检查
2. 测试执行
3. 代码保护
4. 打包构建
5. 发布到指定目录

使用方法:
    python publish_core.py --target-dir E:\OneDrive\Documents\GitHub\CHS-SDK\chs-dist\chs-core
    python publish_core.py --protection-level all --target-dir /path/to/release
    python publish_core.py --skip-tests --target-dir /path/to/release
"""

import os
import sys
import shutil
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.protect_code import CodeProtector
    from scripts.build_protected import ProtectedBuilder
    from scripts.layered_packaging import LayeredPackager
except ImportError as e:
    print(f"警告: 无法导入保护模块: {e}")
    print("将使用基础发布模式")
    CodeProtector = None
    ProtectedBuilder = None
    LayeredPackager = None


class CorePublisher:
    """CHS-Core 发布管理器"""
    
    def __init__(self, project_root: Path, target_dir: Path):
        self.project_root = project_root
        self.target_dir = target_dir
        self.build_dir = project_root / "build" / "release"
        self.dist_dir = project_root / "dist"
        self.log_file = project_root / "publish.log"
        
        # 确保目标目录存在
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
        # 发布配置
        self.config = {
            "version": "0.1.0",
            "build_timestamp": datetime.now().isoformat(),
            "protection_enabled": CodeProtector is not None,
            "packages": [
                "chs-core-api",
                "chs-core-implementation", 
                "chs-core-complete"
            ]
        }
    
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> bool:
        """执行命令"""
        if cwd is None:
            cwd = self.project_root
            
        self.log(f"执行命令: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            if result.returncode == 0:
                self.log(f"命令执行成功: {' '.join(command)}")
                if result.stdout:
                    self.log(f"输出: {result.stdout.strip()}")
                return True
            else:
                self.log(f"命令执行失败: {' '.join(command)}", "ERROR")
                if result.stderr:
                    self.log(f"错误: {result.stderr.strip()}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"命令执行异常: {e}", "ERROR")
            return False
    
    def check_dependencies(self) -> bool:
        """检查依赖项"""
        self.log("检查项目依赖...")
        
        # 检查Python版本
        if sys.version_info < (3, 8):
            self.log("Python版本过低，需要3.8+", "ERROR")
            return False
        
        # 检查必要的包
        required_packages = ["setuptools", "wheel", "build"]
        for package in required_packages:
            if not self.run_command([sys.executable, "-c", f"import {package}"]):
                self.log(f"安装缺失的包: {package}")
                if not self.run_command([sys.executable, "-m", "pip", "install", package]):
                    return False
        
        return True
    
    def run_quality_checks(self) -> bool:
        """运行代码质量检查"""
        self.log("运行代码质量检查...")
        
        # 检查是否有flake8
        try:
            import flake8
            if not self.run_command([sys.executable, "-m", "flake8", ".", "--max-line-length=88", "--extend-ignore=E203,W503"]):
                self.log("代码风格检查发现问题，但继续构建", "WARNING")
        except ImportError:
            self.log("flake8未安装，跳过代码风格检查", "WARNING")
        
        # 检查是否有mypy
        try:
            import mypy
            if not self.run_command([sys.executable, "-m", "mypy", ".", "--ignore-missing-imports"]):
                self.log("类型检查发现问题，但继续构建", "WARNING")
        except ImportError:
            self.log("mypy未安装，跳过类型检查", "WARNING")
        
        return True
    
    def run_tests(self) -> bool:
        """运行测试"""
        self.log("运行项目测试...")
        
        # 检查是否有pytest
        try:
            import pytest
            if not self.run_command([sys.executable, "-m", "pytest", "tests/", "-v"]):
                self.log("测试失败，但继续构建", "WARNING")
                return True  # 允许测试失败时继续构建
        except ImportError:
            self.log("pytest未安装，跳过测试", "WARNING")
        
        return True
    
    def build_basic_packages(self) -> bool:
        """构建基础包"""
        self.log("构建基础Python包...")
        
        # 清理之前的构建
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        # 构建主包
        if not self.run_command([sys.executable, "-m", "build"]):
            return False
        
        # 构建API包
        api_dir = self.project_root / "chs_core_api"
        if api_dir.exists() and (api_dir / "setup.py").exists():
            if not self.run_command([sys.executable, "setup.py", "sdist", "bdist_wheel"], cwd=api_dir):
                self.log("API包构建失败，但继续", "WARNING")
        
        return True
    
    def build_protected_packages(self, protection_level: str = "bytecode") -> bool:
        """构建受保护的包"""
        if not self.config["protection_enabled"]:
            self.log("代码保护模块未可用，使用基础构建", "WARNING")
            return self.build_basic_packages()
        
        self.log(f"构建受保护的包 (保护级别: {protection_level})...")
        
        try:
            # 使用保护构建器
            builder = ProtectedBuilder(self.project_root)
            
            # 设置保护级别
            protection_config = {
                "bytecode": {"api": "source", "core": "bytecode", "algorithms": "bytecode"},
                "obfuscated": {"api": "source", "core": "obfuscated", "algorithms": "obfuscated"},
                "all": {"api": "source", "core": "obfuscated", "algorithms": "encrypted"}
            }
            
            config = protection_config.get(protection_level, protection_config["bytecode"])
            
            # 执行保护构建
            if not builder.build_all(config):
                self.log("保护构建失败，回退到基础构建", "WARNING")
                return self.build_basic_packages()
            
            return True
            
        except Exception as e:
            self.log(f"保护构建异常: {e}", "ERROR")
            return self.build_basic_packages()
    
    def create_layered_packages(self) -> bool:
        """创建分层包"""
        if not self.config["protection_enabled"] or LayeredPackager is None:
            self.log("分层打包模块未可用，跳过", "WARNING")
            return True
        
        self.log("创建分层包结构...")
        
        try:
            packager = LayeredPackager(self.project_root)
            
            # 创建不同的分发包
            packages = [
                ("api", "source"),
                ("implementation", "bytecode"),
                ("complete", "obfuscated")
            ]
            
            for package_type, protection in packages:
                output_dir = self.build_dir / f"chs-core-{package_type}"
                if packager.create_distribution_package(package_type, output_dir, protection):
                    self.log(f"成功创建 {package_type} 包")
                else:
                    self.log(f"创建 {package_type} 包失败", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"分层打包异常: {e}", "ERROR")
            return True  # 非关键错误，继续
    
    def copy_to_release_dir(self) -> bool:
        """复制到发布目录"""
        self.log(f"复制构建结果到发布目录: {self.target_dir}...")
        
        try:
            # 创建发布目录结构
            release_structure = {
                "packages": self.target_dir / "packages",
                "docs": self.target_dir / "docs", 
                "scripts": self.target_dir / "scripts",
                "examples": self.target_dir / "examples"
            }
            
            for dir_path in release_structure.values():
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # 复制包文件
            if self.dist_dir.exists():
                for file in self.dist_dir.glob("*"):
                    if file.is_file():
                        shutil.copy2(file, release_structure["packages"])
                        self.log(f"复制包文件: {file.name}")
            
            # 复制分层包
            if self.build_dir.exists():
                for package_dir in self.build_dir.glob("chs-core-*"):
                    if package_dir.is_dir():
                        target_package_dir = release_structure["packages"] / package_dir.name
                        if target_package_dir.exists():
                            shutil.rmtree(target_package_dir)
                        shutil.copytree(package_dir, target_package_dir)
                        self.log(f"复制分层包: {package_dir.name}")
            
            # 复制文档
            docs_source = self.project_root / "docs"
            if docs_source.exists():
                for item in docs_source.rglob("*"):
                    if item.is_file() and not item.name.startswith("."):
                        rel_path = item.relative_to(docs_source)
                        target_path = release_structure["docs"] / rel_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_path)
            
            # 复制脚本
            scripts_source = self.project_root / "scripts"
            if scripts_source.exists():
                for item in scripts_source.glob("*.py"):
                    shutil.copy2(item, release_structure["scripts"])
            
            # 复制重要文件
            important_files = ["README.md", "requirements.txt", "setup.py"]
            for file_name in important_files:
                source_file = self.project_root / file_name
                if source_file.exists():
                    shutil.copy2(source_file, self.target_dir)
            
            # 生成发布信息
            release_info = {
                "project": "CHS-Core",
                "version": self.config["version"],
                "build_time": self.config["build_timestamp"],
                "protection_enabled": self.config["protection_enabled"],
                "packages": list(release_structure["packages"].glob("*")),
                "build_log": str(self.log_file)
            }
            
            with open(self.target_dir / "release_info.json", "w", encoding="utf-8") as f:
                json.dump(release_info, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            self.log(f"复制到发布目录失败: {e}", "ERROR")
            return False
    
    def cleanup(self):
        """清理临时文件"""
        self.log("清理临时文件...")
        
        cleanup_dirs = [
            self.project_root / "build",
            self.project_root / "*.egg-info"
        ]
        
        for pattern in cleanup_dirs:
            if "*" in str(pattern):
                for path in self.project_root.glob(pattern.name):
                    if path.is_dir():
                        shutil.rmtree(path)
            elif pattern.exists():
                shutil.rmtree(pattern)
    
    def publish(self, protection_level: str = "bytecode", skip_tests: bool = False, 
                skip_quality: bool = False) -> bool:
        """执行完整的发布流程"""
        self.log("开始CHS-Core发布流程...")
        self.log(f"项目根目录: {self.project_root}")
        self.log(f"发布目标目录: {self.target_dir}")
        self.log(f"保护级别: {protection_level}")
        
        try:
            # 1. 检查依赖
            if not self.check_dependencies():
                self.log("依赖检查失败", "ERROR")
                return False
            
            # 2. 代码质量检查
            if not skip_quality and not self.run_quality_checks():
                self.log("质量检查失败，但继续构建", "WARNING")
            
            # 3. 运行测试
            if not skip_tests and not self.run_tests():
                self.log("测试失败，但继续构建", "WARNING")
            
            # 4. 构建包
            if protection_level == "none":
                if not self.build_basic_packages():
                    self.log("基础包构建失败", "ERROR")
                    return False
            else:
                if not self.build_protected_packages(protection_level):
                    self.log("保护包构建失败", "ERROR")
                    return False
            
            # 5. 创建分层包
            if not self.create_layered_packages():
                self.log("分层包创建失败，但继续", "WARNING")
            
            # 6. 复制到发布目录
            if not self.copy_to_release_dir():
                self.log("复制到发布目录失败", "ERROR")
                return False
            
            # 7. 清理
            self.cleanup()
            
            self.log("CHS-Core发布完成！")
            self.log(f"发布文件位于: {self.target_dir}")
            return True
            
        except Exception as e:
            self.log(f"发布过程异常: {e}", "ERROR")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CHS-Core 发布脚本")
    parser.add_argument(
        "--target-dir", 
        type=str, 
        required=True,
        help="发布目标目录"
    )
    parser.add_argument(
        "--protection-level",
        choices=["none", "bytecode", "obfuscated", "all"],
        default="bytecode",
        help="代码保护级别 (默认: bytecode)"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="跳过测试"
    )
    parser.add_argument(
        "--skip-quality",
        action="store_true", 
        help="跳过代码质量检查"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 设置项目路径
    project_root = Path(__file__).parent.parent
    target_dir = Path(args.target_dir)
    
    # 创建发布器
    publisher = CorePublisher(project_root, target_dir)
    
    # 执行发布
    success = publisher.publish(
        protection_level=args.protection_level,
        skip_tests=args.skip_tests,
        skip_quality=args.skip_quality
    )
    
    if success:
        print(f"\n✅ CHS-Core发布成功！")
        print(f"📁 发布目录: {target_dir}")
        print(f"📋 构建日志: {publisher.log_file}")
        sys.exit(0)
    else:
        print(f"\n❌ CHS-Core发布失败！")
        print(f"📋 查看日志: {publisher.log_file}")
        sys.exit(1)


if __name__ == "__main__":
    main()