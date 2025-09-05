#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的CHS-Core发布脚本
直接复制构建好的文件到发布目录
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def create_release_structure(target_dir):
    """创建发布目录结构"""
    target_path = Path(target_dir)
    
    # 创建目录结构
    dirs = {
        'packages': target_path / 'packages',
        'docs': target_path / 'docs',
        'scripts': target_path / 'scripts',
        'examples': target_path / 'examples'
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"创建目录: {dir_path}")
    
    return dirs

def copy_packages(project_root, release_dirs):
    """复制包文件"""
    dist_dir = project_root / 'dist'
    packages_dir = release_dirs['packages']
    
    if dist_dir.exists():
        for file in dist_dir.glob('*'):
            if file.is_file():
                target_file = packages_dir / file.name
                shutil.copy2(file, target_file)
                print(f"复制包: {file.name}")
    
    # 复制API包
    api_dir = project_root / 'chs_core_api'
    if api_dir.exists():
        api_target = packages_dir / 'chs_core_api'
        if api_target.exists():
            shutil.rmtree(api_target)
        shutil.copytree(api_dir, api_target)
        print(f"复制API包: chs_core_api")

def copy_docs(project_root, release_dirs):
    """复制文档"""
    docs_source = project_root / 'docs'
    docs_target = release_dirs['docs']
    
    if docs_source.exists():
        for item in docs_source.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                rel_path = item.relative_to(docs_source)
                target_path = docs_target / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_path)
        print(f"复制文档目录")

def copy_scripts(project_root, release_dirs):
    """复制脚本"""
    scripts_source = project_root / 'scripts'
    scripts_target = release_dirs['scripts']
    
    if scripts_source.exists():
        for item in scripts_source.glob('*.py'):
            shutil.copy2(item, scripts_target)
            print(f"复制脚本: {item.name}")
        
        for item in scripts_source.glob('*.json'):
            shutil.copy2(item, scripts_target)
            print(f"复制配置: {item.name}")

def copy_root_files(project_root, target_dir):
    """复制根目录重要文件"""
    important_files = ['README.md', 'requirements.txt', 'setup.py']
    
    for file_name in important_files:
        source_file = project_root / file_name
        if source_file.exists():
            target_file = target_dir / file_name
            shutil.copy2(source_file, target_file)
            print(f"复制文件: {file_name}")

def create_release_info(target_dir):
    """创建发布信息文件"""
    release_info = {
        'project': 'CHS-Core',
        'version': '0.1.0',
        'build_time': datetime.now().isoformat(),
        'description': 'Core simulation engine for complex hydraulic systems',
        'components': {
            'main_package': 'chs_core-0.1.0-py3-none-any.whl',
            'api_package': 'chs_core_api/',
            'documentation': 'docs/',
            'scripts': 'scripts/'
        },
        'installation': {
            'pip_install': 'pip install packages/chs_core-0.1.0-py3-none-any.whl',
            'api_install': 'pip install packages/chs_core_api/',
            'requirements': 'pip install -r requirements.txt'
        }
    }
    
    info_file = target_dir / 'release_info.json'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(release_info, f, indent=2, ensure_ascii=False)
    
    print(f"创建发布信息: {info_file}")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) != 2:
        print("使用方法: python simple_publish.py <目标目录>")
        print("示例: python simple_publish.py E:\\OneDrive\\Documents\\GitHub\\CHS-SDK\\chs-dist\\chs-core")
        sys.exit(1)
    
    target_dir = Path(sys.argv[1])
    project_root = Path(__file__).parent.parent
    
    print(f"开始发布CHS-Core到: {target_dir}")
    print(f"项目根目录: {project_root}")
    
    try:
        # 1. 创建发布目录结构
        release_dirs = create_release_structure(target_dir)
        
        # 2. 复制包文件
        copy_packages(project_root, release_dirs)
        
        # 3. 复制文档
        copy_docs(project_root, release_dirs)
        
        # 4. 复制脚本
        copy_scripts(project_root, release_dirs)
        
        # 5. 复制根目录文件
        copy_root_files(project_root, target_dir)
        
        # 6. 创建发布信息
        create_release_info(target_dir)
        
        print(f"\n✅ CHS-Core发布成功！")
        print(f"📁 发布目录: {target_dir}")
        print(f"📦 主包: {target_dir}/packages/chs_core-0.1.0-py3-none-any.whl")
        print(f"📚 文档: {target_dir}/docs/")
        print(f"🔧 脚本: {target_dir}/scripts/")
        
    except Exception as e:
        print(f"❌ 发布失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()