CHS-Core API 文档
=================

欢迎使用 CHS-Core API 文档！

CHS-Core API 是一个专为水力系统仿真平台设计的接口定义包，提供了标准化的接口定义、类型规范和异常处理机制，使不同团队能够基于统一的接口契约进行协作开发。

主要特性
--------

🔌 **标准化接口**
   - 水力系统组件接口：水库、泵站、阀门等组件的统一接口
   - 数据处理器接口：数据清洗、验证、异常检测的标准接口
   - 仿真引擎接口：仿真执行和控制的核心接口
   - 配置管理接口：配置加载、验证、保存的统一接口

📊 **完整类型系统**
   - 基础数据类型：流量、水位、控制信号等专业类型
   - 复合数据类型：组件状态、测量数据、时间序列等
   - 枚举类型：组件状态、报警级别等标准化枚举
   - 类型别名：常用类型的简化别名

⚠️ **统一异常处理**
   - 分层异常体系：组件、数据处理、仿真、配置等分类异常
   - 详细错误信息：包含错误代码、详细信息和上下文
   - 标准化错误格式：便于错误处理和日志记录

快速开始
--------

安装
^^^^

.. code-block:: bash

   pip install chs-core-api

基础使用
^^^^^^^^

.. code-block:: python

   from chs_core_api import (
       WaterSystemComponent, 
       ReservoirInterface,
       FlowRate, 
       WaterLevel
   )
   
   # 实现水库组件
   class MyReservoir(ReservoirInterface):
       def __init__(self, reservoir_id: str, capacity: float):
           self.reservoir_id = reservoir_id
           self.capacity = capacity
           # ... 其他初始化代码
       
       def get_component_id(self) -> str:
           return self.reservoir_id
       
       # ... 实现其他接口方法

文档目录
--------

.. toctree::
   :maxdepth: 2
   :caption: 用户指南

   installation
   quickstart
   examples
   best_practices

.. toctree::
   :maxdepth: 2
   :caption: API 参考

   api/interfaces
   api/types
   api/exceptions
   api/modules

.. toctree::
   :maxdepth: 2
   :caption: 开发指南

   development/contributing
   development/testing
   development/documentation
   development/release

.. toctree::
   :maxdepth: 1
   :caption: 其他

   changelog
   license
   support

索引和表格
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

版本信息
--------

:版本: 0.1.0
:发布日期: 2024年1月
:Python版本: 3.8+
:许可证: MIT License

联系我们
--------

- **GitHub**: https://github.com/chs-core/chs-core-api
- **文档**: https://chs-core-api.readthedocs.io/
- **问题反馈**: https://github.com/chs-core/chs-core-api/issues
- **邮箱**: dev@chs-core.com