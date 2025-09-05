# -*- coding: utf-8 -*-
"""
CHS-Core API 文档配置文件

本文件配置 Sphinx 文档生成器，用于生成 CHS-Core API 的详细文档。
"""

import os
import sys
from datetime import datetime

# 添加项目路径到 Python 路径
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../chs_core_api'))

# -- 项目信息 --
project = 'CHS-Core API'
copyright = f'{datetime.now().year}, CHS Development Team'
author = 'CHS Development Team'

# 版本信息
release = '0.1.0'
version = '0.1.0'

# -- 通用配置 --

# 需要的扩展
extensions = [
    'sphinx.ext.autodoc',        # 自动生成API文档
    'sphinx.ext.autosummary',    # 自动生成摘要
    'sphinx.ext.viewcode',       # 添加源码链接
    'sphinx.ext.napoleon',       # 支持Google和NumPy风格的docstring
    'sphinx.ext.intersphinx',    # 交叉引用其他文档
    'sphinx.ext.todo',           # TODO支持
    'sphinx.ext.coverage',       # 文档覆盖率
    'sphinx_autodoc_typehints',  # 类型提示支持
    'myst_parser',               # Markdown支持
]

# 添加任何包含模板的路径，相对于此目录
templates_path = ['_templates']

# 源文件后缀
source_suffix = {
    '.rst': None,
    '.md': None,
}

# 主文档（包含目录树的根文档）
master_doc = 'index'

# 国际化
language = 'zh_CN'

# 要排除的模式列表，相对于源目录
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# 默认角色（用于 `text` 标记）
default_role = 'py:obj'

# Pygments（语法高亮）样式
pygments_style = 'sphinx'

# -- HTML 输出选项 --

# HTML主题
html_theme = 'sphinx_rtd_theme'

# 主题选项
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc选项
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# 添加任何包含自定义静态文件的路径（如样式表），相对于此目录
html_static_path = ['_static']

# 自定义侧边栏模板，必须是将文档名称映射到模板名称的字典
html_sidebars = {
    '**': [
        'relations.html',  # 需要 'show_related': True 主题选项来显示
        'searchbox.html',
    ]
}

# HTML页面标题
html_title = f'{project} v{version} 文档'

# 短标题（用于导航栏）
html_short_title = 'CHS-Core API'

# 网站图标
# html_favicon = '_static/favicon.ico'

# 页面底部的版权声明
html_show_copyright = True

# 显示"由Sphinx创建"的链接
html_show_sphinx = True

# -- autodoc 配置 --

# autodoc 默认选项
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# 自动生成存根文件
autodoc_generate_stubs = True

# 类型提示配置
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# -- autosummary 配置 --

# 自动生成存根文件
autosummary_generate = True

# -- napoleon 配置 --

# Google风格docstring
napoleon_google_docstring = True
# NumPy风格docstring
napoleon_numpy_docstring = True
# 包含私有成员
napoleon_include_private_with_doc = False
# 包含特殊成员
napoleon_include_special_with_doc = True
# 使用admonition进行参数
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
# 使用ivar
napoleon_use_ivar = False
# 使用param
napoleon_use_param = True
# 使用rtype
napoleon_use_rtype = True
# 使用keyword
napoleon_use_keyword = True
# 预处理类型
napoleon_preprocess_types = False
# 类型别名
napoleon_type_aliases = None
# 自定义部分
napoleon_custom_sections = None

# -- intersphinx 配置 --

# 交叉引用映射
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

# -- todo 配置 --

# 显示todo
todo_include_todos = True

# -- 自定义配置 --

# 添加模块路径
def setup(app):
    """Sphinx应用设置"""
    app.add_css_file('custom.css')
    
# 文档字符串处理
def process_docstring(app, what, name, obj, options, lines):
    """处理文档字符串"""
    # 这里可以添加自定义的文档字符串处理逻辑
    pass

def setup(app):
    app.connect('autodoc-process-docstring', process_docstring)