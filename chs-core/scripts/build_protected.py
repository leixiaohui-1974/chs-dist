#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHS-Core 受保护构建脚本

此脚本自动化整个代码保护和打包流程：
1. 清理旧的构建文件
2. 运行代码质量检查
3. 执行测试套件
4. 应用代码保护
5. 构建分发包
6. 验证构建结果

使用方法:
    python scripts/build_protected.py
    python scripts/build_protected.py --protection-method all
    python scripts/build_protected.py --skip-tests --verbose
"""

import os
import sys
import shutil
import subprocess
import argparse
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import zipfile

# 添加脚本目录到Python路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from protect_code import CodeProtector

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ProtectedBuilder:
    """受保护构建器
    
    负责整个代码保护和构建流程的自动化。
    """
    
    def __init__(self, project_root: str, config_file: Optional[str] = None):
        """
        初始化构建器
        
        Args:
            project_root: 项目根目录
            config_file: 配置文件路径
        """
        self.project_root = Path(project_root)
        self.config_file = config_file or (script_dir / "protection_config.json")
        
        # 加载配置
        self.config = self._load_config()
        
        # 设置目录
        self.source_dir = self.project_root / "src" if (self.project_root / "src").exists() else self.project_root
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.protected_dir = self.project_root / "dist_protected"
        
        # 构建统计
        self.build_stats = {
            "start_time": datetime.now(),
            "end_time": None,
            "duration": None,
            "steps_completed": [],
            "steps_failed": [],
            "files_processed": 0,
            "packages_created": 0,
            "total_size": 0
        }
        
        logger.info(f"受保护构建器初始化完成")
        logger.info(f"项目根目录: {self.project_root}")
        logger.info(f"源代码目录: {self.source_dir}")
        logger.info(f"保护输出目录: {self.protected_dir}")
    
    def build(self, protection_method: str = "bytecode", 
              skip_tests: bool = False, 
              skip_quality_check: bool = False,
              create_packages: bool = True) -> bool:
        """
        执行完整的受保护构建流程
        
        Args:
            protection_method: 保护方法
            skip_tests: 是否跳过测试
            skip_quality_check: 是否跳过质量检查
            create_packages: 是否创建分发包
            
        Returns:
            bool: 构建是否成功
        """
        try:
            logger.info("🚀 开始受保护构建流程...")
            
            # 步骤1: 清理构建目录
            if not self._clean_build_directories():
                return False
            
            # 步骤2: 代码质量检查
            if not skip_quality_check:
                if not self._run_quality_checks():
                    logger.warning("代码质量检查失败，但继续构建...")
            
            # 步骤3: 运行测试
            if not skip_tests:
                if not self._run_tests():
                    logger.error("测试失败，停止构建")
                    return False
            
            # 步骤4: 应用代码保护
            if not self._apply_code_protection(protection_method):
                logger.error("代码保护失败，停止构建")
                return False
            
            # 步骤5: 创建分发包
            if create_packages:
                if not self._create_distribution_packages():
                    logger.error("创建分发包失败，停止构建")
                    return False
            
            # 步骤6: 验证构建结果
            if not self._verify_build_results():
                logger.warning("构建验证失败，但构建已完成")
            
            # 步骤7: 生成构建报告
            self._generate_build_report()
            
            # 完成构建
            self.build_stats["end_time"] = datetime.now()
            self.build_stats["duration"] = (self.build_stats["end_time"] - self.build_stats["start_time"]).total_seconds()
            
            logger.info("🎉 受保护构建完成！")
            logger.info(f"构建耗时: {self.build_stats['duration']:.2f} 秒")
            logger.info(f"受保护代码位置: {self.protected_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"构建过程中发生错误: {e}")
            return False
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        try:
            if self.config_file and Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"已加载配置文件: {self.config_file}")
                    return config
            else:
                logger.warning(f"配置文件不存在: {self.config_file}，使用默认配置")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置
        """
        return {
            "protection_levels": {
                "api": "source",
                "core": "bytecode",
                "engine": "bytecode"
            },
            "build_settings": {
                "clean_before_build": True,
                "verify_after_build": True,
                "create_checksums": True
            }
        }
    
    def _clean_build_directories(self) -> bool:
        """
        清理构建目录
        
        Returns:
            bool: 清理是否成功
        """
        try:
            logger.info("🧹 清理构建目录...")
            
            # 清理目录列表
            dirs_to_clean = [self.build_dir, self.dist_dir, self.protected_dir]
            
            for dir_path in dirs_to_clean:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    logger.debug(f"已清理目录: {dir_path}")
                
                # 重新创建目录
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # 清理Python缓存
            self._clean_python_cache()
            
            self.build_stats["steps_completed"].append("clean_directories")
            logger.info("✓ 构建目录清理完成")
            return True
            
        except Exception as e:
            logger.error(f"清理构建目录失败: {e}")
            self.build_stats["steps_failed"].append("clean_directories")
            return False
    
    def _clean_python_cache(self):
        """
        清理Python缓存文件
        """
        try:
            for root, dirs, files in os.walk(self.project_root):
                # 删除__pycache__目录
                if '__pycache__' in dirs:
                    pycache_dir = Path(root) / '__pycache__'
                    shutil.rmtree(pycache_dir)
                    logger.debug(f"已清理缓存目录: {pycache_dir}")
                
                # 删除.pyc文件
                for file in files:
                    if file.endswith(('.pyc', '.pyo')):
                        pyc_file = Path(root) / file
                        pyc_file.unlink()
                        logger.debug(f"已删除缓存文件: {pyc_file}")
        
        except Exception as e:
            logger.warning(f"清理Python缓存时出现警告: {e}")
    
    def _run_quality_checks(self) -> bool:
        """
        运行代码质量检查
        
        Returns:
            bool: 质量检查是否通过
        """
        try:
            logger.info("🔍 运行代码质量检查...")
            
            checks_passed = 0
            total_checks = 0
            
            # 检查1: flake8代码风格检查
            total_checks += 1
            if self._run_flake8():
                checks_passed += 1
                logger.info("✓ flake8检查通过")
            else:
                logger.warning("⚠ flake8检查未通过")
            
            # 检查2: mypy类型检查
            total_checks += 1
            if self._run_mypy():
                checks_passed += 1
                logger.info("✓ mypy检查通过")
            else:
                logger.warning("⚠ mypy检查未通过")
            
            # 检查3: 安全检查
            total_checks += 1
            if self._run_security_check():
                checks_passed += 1
                logger.info("✓ 安全检查通过")
            else:
                logger.warning("⚠ 安全检查未通过")
            
            success_rate = checks_passed / total_checks
            logger.info(f"代码质量检查完成，通过率: {success_rate:.1%} ({checks_passed}/{total_checks})")
            
            # 如果通过率低于50%，认为失败
            if success_rate >= 0.5:
                self.build_stats["steps_completed"].append("quality_checks")
                return True
            else:
                self.build_stats["steps_failed"].append("quality_checks")
                return False
            
        except Exception as e:
            logger.error(f"代码质量检查失败: {e}")
            self.build_stats["steps_failed"].append("quality_checks")
            return False
    
    def _run_flake8(self) -> bool:
        """
        运行flake8检查
        
        Returns:
            bool: 检查是否通过
        """
        try:
            cmd = ["flake8", str(self.source_dir), "--max-line-length=88", "--extend-ignore=E203,W503"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                return True
            else:
                logger.debug(f"flake8输出: {result.stdout}")
                logger.debug(f"flake8错误: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.warning("flake8未安装，跳过检查")
            return True
        except Exception as e:
            logger.warning(f"flake8检查失败: {e}")
            return False
    
    def _run_mypy(self) -> bool:
        """
        运行mypy类型检查
        
        Returns:
            bool: 检查是否通过
        """
        try:
            cmd = ["mypy", str(self.source_dir), "--ignore-missing-imports"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                return True
            else:
                logger.debug(f"mypy输出: {result.stdout}")
                logger.debug(f"mypy错误: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.warning("mypy未安装，跳过检查")
            return True
        except Exception as e:
            logger.warning(f"mypy检查失败: {e}")
            return False
    
    def _run_security_check(self) -> bool:
        """
        运行安全检查
        
        Returns:
            bool: 检查是否通过
        """
        try:
            # 检查是否有明显的安全问题
            security_issues = []
            
            # 检查硬编码密码
            for py_file in self.source_dir.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        
                    # 简单的安全检查
                    if 'password' in content and '=' in content:
                        if any(word in content for word in ['"password"', "'password'", 'pwd=']):
                            security_issues.append(f"可能的硬编码密码: {py_file}")
                    
                    if 'secret' in content and '=' in content:
                        if any(word in content for word in ['"secret"', "'secret'", 'secret_key=']):
                            security_issues.append(f"可能的硬编码密钥: {py_file}")
                            
                except Exception:
                    continue
            
            if security_issues:
                logger.warning("发现潜在安全问题:")
                for issue in security_issues:
                    logger.warning(f"  - {issue}")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"安全检查失败: {e}")
            return False
    
    def _run_tests(self) -> bool:
        """
        运行测试套件
        
        Returns:
            bool: 测试是否通过
        """
        try:
            logger.info("🧪 运行测试套件...")
            
            # 检查是否存在测试目录
            test_dirs = [self.project_root / "tests", self.project_root / "test"]
            test_dir = None
            
            for td in test_dirs:
                if td.exists():
                    test_dir = td
                    break
            
            if not test_dir:
                logger.warning("未找到测试目录，跳过测试")
                self.build_stats["steps_completed"].append("tests")
                return True
            
            # 运行pytest
            cmd = ["python", "-m", "pytest", str(test_dir), "-v", "--tb=short"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info("✓ 所有测试通过")
                self.build_stats["steps_completed"].append("tests")
                return True
            else:
                logger.error("❌ 测试失败")
                logger.debug(f"测试输出: {result.stdout}")
                logger.debug(f"测试错误: {result.stderr}")
                self.build_stats["steps_failed"].append("tests")
                return False
                
        except FileNotFoundError:
            logger.warning("pytest未安装，跳过测试")
            self.build_stats["steps_completed"].append("tests")
            return True
        except Exception as e:
            logger.error(f"运行测试失败: {e}")
            self.build_stats["steps_failed"].append("tests")
            return False
    
    def _apply_code_protection(self, method: str) -> bool:
        """
        应用代码保护
        
        Args:
            method: 保护方法
            
        Returns:
            bool: 保护是否成功
        """
        try:
            logger.info(f"🔒 应用代码保护 ({method})...")
            
            # 创建代码保护器
            protector = CodeProtector(str(self.source_dir), str(self.protected_dir))
            
            # 应用自定义配置
            if hasattr(self, 'config') and self.config:
                protector.config.update(self.config)
            
            # 执行保护
            success = False
            
            if method == "bytecode":
                success = protector.protect_bytecode()
            elif method == "obfuscate":
                success = protector.protect_obfuscate()
            elif method == "layered":
                success = protector.protect_layered()
            elif method == "all":
                success = protector.protect_all()
            else:
                logger.error(f"未知的保护方法: {method}")
                return False
            
            if success:
                logger.info(f"✓ 代码保护 ({method}) 完成")
                self.build_stats["steps_completed"].append(f"protection_{method}")
                
                # 统计处理的文件数
                self.build_stats["files_processed"] = len(list(self.protected_dir.rglob("*")))
                
                return True
            else:
                logger.error(f"❌ 代码保护 ({method}) 失败")
                self.build_stats["steps_failed"].append(f"protection_{method}")
                return False
                
        except Exception as e:
            logger.error(f"应用代码保护失败: {e}")
            self.build_stats["steps_failed"].append(f"protection_{method}")
            return False
    
    def _create_distribution_packages(self) -> bool:
        """
        创建分发包
        
        Returns:
            bool: 创建是否成功
        """
        try:
            logger.info("📦 创建分发包...")
            
            packages_created = 0
            
            # 创建API包
            api_dir = self.protected_dir / "chs_core_api"
            if api_dir.exists():
                if self._build_package(api_dir, "chs-core-api"):
                    packages_created += 1
                    logger.info("✓ API包创建成功")
                else:
                    logger.warning("⚠ API包创建失败")
            
            # 创建实现包
            impl_dirs = [
                self.protected_dir / "bytecode",
                self.protected_dir / "obfuscated",
                self.protected_dir / "layered" / "chs_core_impl"
            ]
            
            for impl_dir in impl_dirs:
                if impl_dir.exists():
                    package_name = f"chs-core-impl-{impl_dir.name}"
                    if self._build_package(impl_dir, package_name):
                        packages_created += 1
                        logger.info(f"✓ 实现包 ({impl_dir.name}) 创建成功")
                    else:
                        logger.warning(f"⚠ 实现包 ({impl_dir.name}) 创建失败")
            
            # 创建完整分发包
            if self._create_complete_distribution():
                packages_created += 1
                logger.info("✓ 完整分发包创建成功")
            
            self.build_stats["packages_created"] = packages_created
            
            if packages_created > 0:
                logger.info(f"✓ 分发包创建完成，共创建 {packages_created} 个包")
                self.build_stats["steps_completed"].append("create_packages")
                return True
            else:
                logger.error("❌ 未能创建任何分发包")
                self.build_stats["steps_failed"].append("create_packages")
                return False
                
        except Exception as e:
            logger.error(f"创建分发包失败: {e}")
            self.build_stats["steps_failed"].append("create_packages")
            return False
    
    def _build_package(self, package_dir: Path, package_name: str) -> bool:
        """
        构建单个包
        
        Args:
            package_dir: 包目录
            package_name: 包名称
            
        Returns:
            bool: 构建是否成功
        """
        try:
            # 检查setup.py是否存在
            setup_file = package_dir / "setup.py"
            if not setup_file.exists():
                logger.warning(f"未找到setup.py文件: {setup_file}")
                return False
            
            # 运行构建命令
            cmd = ["python", "setup.py", "sdist", "bdist_wheel"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=package_dir)
            
            if result.returncode == 0:
                # 移动构建结果到主分发目录
                package_dist_dir = package_dir / "dist"
                if package_dist_dir.exists():
                    for file in package_dist_dir.iterdir():
                        dest_file = self.dist_dir / f"{package_name}_{file.name}"
                        shutil.copy2(file, dest_file)
                        logger.debug(f"包文件已复制: {dest_file}")
                
                return True
            else:
                logger.error(f"包构建失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"构建包失败 {package_name}: {e}")
            return False
    
    def _create_complete_distribution(self) -> bool:
        """
        创建完整的分发包
        
        Returns:
            bool: 创建是否成功
        """
        try:
            # 创建完整分发包的ZIP文件
            zip_file = self.dist_dir / f"chs-core-protected-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 添加受保护的代码
                for file_path in self.protected_dir.rglob("*"):
                    if file_path.is_file():
                        arc_name = file_path.relative_to(self.protected_dir)
                        zf.write(file_path, arc_name)
                
                # 添加文档
                docs_dir = self.project_root / "docs"
                if docs_dir.exists():
                    for file_path in docs_dir.rglob("*"):
                        if file_path.is_file() and not file_path.name.startswith('.'):
                            arc_name = Path("docs") / file_path.relative_to(docs_dir)
                            zf.write(file_path, arc_name)
                
                # 添加README和LICENSE
                for file_name in ["README.md", "LICENSE", "requirements.txt"]:
                    file_path = self.project_root / file_name
                    if file_path.exists():
                        zf.write(file_path, file_name)
            
            # 计算文件大小
            file_size = zip_file.stat().st_size
            self.build_stats["total_size"] = file_size
            
            logger.info(f"完整分发包已创建: {zip_file} ({file_size / 1024 / 1024:.2f} MB)")
            return True
            
        except Exception as e:
            logger.error(f"创建完整分发包失败: {e}")
            return False
    
    def _verify_build_results(self) -> bool:
        """
        验证构建结果
        
        Returns:
            bool: 验证是否通过
        """
        try:
            logger.info("🔍 验证构建结果...")
            
            verification_passed = 0
            total_verifications = 0
            
            # 验证1: 检查受保护目录是否存在
            total_verifications += 1
            if self.protected_dir.exists() and any(self.protected_dir.iterdir()):
                verification_passed += 1
                logger.debug("✓ 受保护目录验证通过")
            else:
                logger.warning("⚠ 受保护目录为空或不存在")
            
            # 验证2: 检查分发包是否创建
            total_verifications += 1
            if self.dist_dir.exists() and any(self.dist_dir.iterdir()):
                verification_passed += 1
                logger.debug("✓ 分发包验证通过")
            else:
                logger.warning("⚠ 分发包目录为空或不存在")
            
            # 验证3: 检查关键文件是否存在
            total_verifications += 1
            if self._verify_critical_files():
                verification_passed += 1
                logger.debug("✓ 关键文件验证通过")
            else:
                logger.warning("⚠ 关键文件验证失败")
            
            # 验证4: 检查文件完整性
            total_verifications += 1
            if self._verify_file_integrity():
                verification_passed += 1
                logger.debug("✓ 文件完整性验证通过")
            else:
                logger.warning("⚠ 文件完整性验证失败")
            
            success_rate = verification_passed / total_verifications
            logger.info(f"构建验证完成，通过率: {success_rate:.1%} ({verification_passed}/{total_verifications})")
            
            if success_rate >= 0.75:
                self.build_stats["steps_completed"].append("verification")
                return True
            else:
                self.build_stats["steps_failed"].append("verification")
                return False
                
        except Exception as e:
            logger.error(f"验证构建结果失败: {e}")
            self.build_stats["steps_failed"].append("verification")
            return False
    
    def _verify_critical_files(self) -> bool:
        """
        验证关键文件是否存在
        
        Returns:
            bool: 验证是否通过
        """
        try:
            critical_files = [
                "__init__.py",
                "setup.py"
            ]
            
            missing_files = []
            
            for file_name in critical_files:
                found = False
                for file_path in self.protected_dir.rglob(file_name):
                    if file_path.is_file():
                        found = True
                        break
                
                if not found:
                    missing_files.append(file_name)
            
            if missing_files:
                logger.warning(f"缺少关键文件: {missing_files}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证关键文件失败: {e}")
            return False
    
    def _verify_file_integrity(self) -> bool:
        """
        验证文件完整性
        
        Returns:
            bool: 验证是否通过
        """
        try:
            # 简单的完整性检查：确保文件不为空
            empty_files = []
            
            for file_path in self.protected_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.pyc']:
                    if file_path.stat().st_size == 0:
                        empty_files.append(file_path)
            
            if empty_files:
                logger.warning(f"发现空文件: {[str(f) for f in empty_files]}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证文件完整性失败: {e}")
            return False
    
    def _generate_build_report(self):
        """
        生成构建报告
        """
        try:
            report = {
                "build_info": {
                    "timestamp": datetime.now().isoformat(),
                    "project_root": str(self.project_root),
                    "source_directory": str(self.source_dir),
                    "protected_directory": str(self.protected_dir),
                    "distribution_directory": str(self.dist_dir)
                },
                "build_statistics": self.build_stats,
                "configuration": self.config,
                "file_manifest": self._generate_file_manifest()
            }
            
            report_file = self.dist_dir / "build_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"构建报告已生成: {report_file}")
            
        except Exception as e:
            logger.error(f"生成构建报告失败: {e}")
    
    def _generate_file_manifest(self) -> Dict[str, Any]:
        """
        生成文件清单
        
        Returns:
            Dict[str, Any]: 文件清单
        """
        try:
            manifest = {
                "protected_files": [],
                "distribution_files": [],
                "checksums": {}
            }
            
            # 受保护文件清单
            if self.protected_dir.exists():
                for file_path in self.protected_dir.rglob("*"):
                    if file_path.is_file():
                        rel_path = str(file_path.relative_to(self.protected_dir))
                        file_info = {
                            "path": rel_path,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        }
                        manifest["protected_files"].append(file_info)
                        
                        # 计算文件哈希
                        if file_path.suffix in ['.py', '.pyc']:
                            with open(file_path, 'rb') as f:
                                file_hash = hashlib.sha256(f.read()).hexdigest()
                                manifest["checksums"][rel_path] = file_hash
            
            # 分发文件清单
            if self.dist_dir.exists():
                for file_path in self.dist_dir.iterdir():
                    if file_path.is_file():
                        file_info = {
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        }
                        manifest["distribution_files"].append(file_info)
            
            return manifest
            
        except Exception as e:
            logger.error(f"生成文件清单失败: {e}")
            return {}


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="CHS-Core 受保护构建工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s
  %(prog)s --protection-method all
  %(prog)s --skip-tests --verbose
  %(prog)s --config custom_config.json
        """
    )
    
    parser.add_argument(
        "--protection-method",
        choices=["bytecode", "obfuscate", "layered", "all"],
        default="bytecode",
        help="代码保护方法 (默认: bytecode)"
    )
    
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="跳过测试"
    )
    
    parser.add_argument(
        "--skip-quality-check",
        action="store_true",
        help="跳过代码质量检查"
    )
    
    parser.add_argument(
        "--no-packages",
        action="store_true",
        help="不创建分发包"
    )
    
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--project-root",
        default=".",
        help="项目根目录 (默认: 当前目录)"
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
    
    # 验证项目根目录
    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        logger.error(f"项目根目录不存在: {project_root}")
        sys.exit(1)
    
    try:
        # 创建受保护构建器
        builder = ProtectedBuilder(
            project_root=str(project_root),
            config_file=args.config
        )
        
        # 执行构建
        success = builder.build(
            protection_method=args.protection_method,
            skip_tests=args.skip_tests,
            skip_quality_check=args.skip_quality_check,
            create_packages=not args.no_packages
        )
        
        if success:
            logger.info("🎉 受保护构建成功完成！")
            sys.exit(0)
        else:
            logger.error("❌ 受保护构建失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("用户中断构建")
        sys.exit(1)
    except Exception as e:
        logger.error(f"构建过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()