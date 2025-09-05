API 参考
========

CHS-Core API 提供了一套完整的接口定义，用于构建水利系统应用。本节包含所有接口、类型和异常的详细文档。

概述
----

CHS-Core API 采用分层架构设计，主要包含以下几个部分：

- **核心接口** - 定义系统组件的基本行为
- **数据类型** - 提供统一的数据结构
- **异常处理** - 建立完整的错误处理机制

架构原则
--------

1. **接口分离** - 将接口定义与具体实现分离
2. **类型安全** - 使用强类型定义确保数据一致性
3. **可扩展性** - 支持系统功能的灵活扩展
4. **标准化** - 提供统一的编程接口

API 组织结构
------------

.. toctree::
   :maxdepth: 2
   :caption: 核心组件

   interfaces
   types
   exceptions

快速导航
--------

核心接口
^^^^^^^^

- :class:`~chs_core_api.WaterSystemComponent` - 水系统组件基类
- :class:`~chs_core_api.ReservoirInterface` - 水库接口
- :class:`~chs_core_api.PumpInterface` - 水泵接口
- :class:`~chs_core_api.DataProcessor` - 数据处理器接口
- :class:`~chs_core_api.AnomalyDetectorInterface` - 异常检测接口
- :class:`~chs_core_api.SimulationEngine` - 仿真引擎接口
- :class:`~chs_core_api.ConfigurationManager` - 配置管理接口

数据类型
^^^^^^^^

**基础类型**

- :class:`~chs_core_api.FlowRate` - 流量数据
- :class:`~chs_core_api.WaterLevel` - 水位数据
- :class:`~chs_core_api.ControlSignal` - 控制信号

**状态枚举**

- :class:`~chs_core_api.ComponentStatus` - 组件状态
- :class:`~chs_core_api.AlarmLevel` - 报警级别

**复合类型**

- :class:`~chs_core_api.ComponentState` - 组件状态信息
- :class:`~chs_core_api.Measurement` - 测量数据
- :class:`~chs_core_api.TimeSeriesData` - 时间序列数据
- :class:`~chs_core_api.SimulationResult` - 仿真结果
- :class:`~chs_core_api.ConfigurationSchema` - 配置模式
- :class:`~chs_core_api.APIResponse` - API响应

异常类型
^^^^^^^^

**基础异常**

- :class:`~chs_core_api.CHSCoreException` - 基础异常类

**组件异常**

- :class:`~chs_core_api.ComponentException` - 组件异常
- :class:`~chs_core_api.ComponentNotFoundError` - 组件未找到
- :class:`~chs_core_api.ComponentStateError` - 组件状态错误
- :class:`~chs_core_api.ComponentConfigurationError` - 组件配置错误

**数据处理异常**

- :class:`~chs_core_api.DataException` - 数据异常
- :class:`~chs_core_api.DataValidationError` - 数据验证错误
- :class:`~chs_core_api.DataProcessingException` - 数据处理异常
- :class:`~chs_core_api.DataFormatError` - 数据格式错误

**仿真异常**

- :class:`~chs_core_api.SimulationException` - 仿真异常
- :class:`~chs_core_api.SimulationConfigurationError` - 仿真配置错误
- :class:`~chs_core_api.SimulationExecutionError` - 仿真执行错误
- :class:`~chs_core_api.SimulationConvergenceError` - 仿真收敛错误

**配置异常**

- :class:`~chs_core_api.ConfigurationException` - 配置异常
- :class:`~chs_core_api.ConfigurationValidationError` - 配置验证错误
- :class:`~chs_core_api.ConfigurationLoadError` - 配置加载错误
- :class:`~chs_core_api.ConfigurationSaveError` - 配置保存错误

**网络和API异常**

- :class:`~chs_core_api.NetworkException` - 网络异常
- :class:`~chs_core_api.APIException` - API异常
- :class:`~chs_core_api.AuthenticationError` - 认证错误
- :class:`~chs_core_api.AuthorizationError` - 授权错误
- :class:`~chs_core_api.RateLimitError` - 速率限制错误

使用示例
--------

基本用法
^^^^^^^^

.. code-block:: python

   from chs_core_api import (
       ReservoirInterface,
       ComponentStatus,
       WaterLevel,
       FlowRate
   )
   from datetime import datetime

   # 实现水库接口
   class MyReservoir(ReservoirInterface):
       def __init__(self, reservoir_id: str):
           self.reservoir_id = reservoir_id
           self._status = ComponentStatus.OFFLINE
           
       def get_id(self) -> str:
           return self.reservoir_id
           
       def get_status(self) -> ComponentStatus:
           return self._status
           
       # 实现其他必需方法...

   # 使用水库
   reservoir = MyReservoir("RESERVOIR_001")
   print(f"水库ID: {reservoir.get_id()}")
   print(f"状态: {reservoir.get_status()}")

数据处理示例
^^^^^^^^^^^^

.. code-block:: python

   from chs_core_api import (
       DataProcessor,
       Measurement,
       TimeSeriesData,
       DataValidationError
   )
   from typing import List
   from datetime import datetime

   # 实现数据处理器
   class MyDataProcessor(DataProcessor):
       def get_id(self) -> str:
           return "PROCESSOR_001"
           
       def process_data(self, data: List[Measurement]) -> TimeSeriesData:
           if not data:
               raise DataValidationError("输入数据为空")
           
           # 处理数据逻辑
           timestamps = [m.timestamp for m in data]
           values = [m.value for m in data]
           
           return TimeSeriesData(
               parameter=data[0].parameter,
               unit=data[0].unit,
               timestamps=timestamps,
               values=values,
               metadata={"processor_id": self.get_id()}
           )

   # 使用数据处理器
   processor = MyDataProcessor()
   
   # 创建测试数据
   measurements = [
       Measurement(
           sensor_id="SENSOR_001",
           parameter="water_level",
           value=125.5,
           unit="m",
           timestamp=datetime.now(),
           quality=0.95,
           uncertainty=0.1
       )
   ]
   
   # 处理数据
   result = processor.process_data(measurements)
   print(f"处理结果: {len(result.values)} 个数据点")

异常处理示例
^^^^^^^^^^^^

.. code-block:: python

   from chs_core_api import (
       ComponentException,
       DataValidationError,
       SimulationException
   )

   try:
       # 执行可能出错的操作
       reservoir.start()
   except ComponentException as e:
       print(f"组件错误: {e.message}")
       print(f"组件ID: {e.component_id}")
       print(f"错误代码: {e.error_code}")
   except Exception as e:
       print(f"未知错误: {e}")

   try:
       # 数据验证
       processor.process_data(invalid_data)
   except DataValidationError as e:
       print(f"数据验证失败: {e.message}")
       print(f"数据源: {e.data_source}")
       print(f"错误代码: {e.error_code}")

版本兼容性
----------

CHS-Core API 遵循语义化版本控制（Semantic Versioning）：

- **主版本号** - 不兼容的API变更
- **次版本号** - 向后兼容的功能新增
- **修订版本号** - 向后兼容的问题修正

当前版本: |version|

兼容性保证
^^^^^^^^^^

- 在同一主版本内，API保持向后兼容
- 新增功能通过次版本号发布
- 废弃功能会在下一主版本移除前提供充分的迁移时间
- 所有破坏性变更都会在发布说明中详细说明

迁移指南
^^^^^^^^

当需要升级到新的主版本时，请参考相应的迁移指南：

- `从 v0.x 迁移到 v1.x <migration_v1.html>`_
- `从 v1.x 迁移到 v2.x <migration_v2.html>`_

扩展开发
--------

自定义接口
^^^^^^^^^^

您可以基于现有接口创建自定义接口：

.. code-block:: python

   from chs_core_api import WaterSystemComponent
   from abc import abstractmethod
   from typing import Dict, Any

   class CustomSensorInterface(WaterSystemComponent):
       """自定义传感器接口"""
       
       @abstractmethod
       def calibrate(self, calibration_data: Dict[str, Any]) -> bool:
           """校准传感器"""
           pass
           
       @abstractmethod
       def get_calibration_status(self) -> Dict[str, Any]:
           """获取校准状态"""
           pass

自定义数据类型
^^^^^^^^^^^^^^

创建符合您需求的数据类型：

.. code-block:: python

   from dataclasses import dataclass
   from datetime import datetime
   from typing import Optional

   @dataclass
   class CustomMeasurement:
       """自定义测量数据类型"""
       sensor_id: str
       parameter: str
       value: float
       unit: str
       timestamp: datetime
       location: Optional[str] = None
       elevation: Optional[float] = None
       
       def __post_init__(self):
           """数据验证"""
           if self.value < 0:
               raise ValueError("测量值不能为负数")

贡献指南
--------

如果您希望为 CHS-Core API 贡献代码或文档，请参考 `贡献指南 <../guides/contributing.html>`_。

主要贡献方式：

1. **报告问题** - 在 GitHub 上提交 Issue
2. **功能建议** - 提出新功能的需求和设计
3. **代码贡献** - 提交 Pull Request
4. **文档改进** - 完善文档和示例
5. **测试用例** - 增加测试覆盖率

支持和反馈
----------

如果您在使用 CHS-Core API 时遇到问题或有任何建议，请通过以下方式联系我们：

- **GitHub Issues**: https://github.com/your-org/chs-core-api/issues
- **邮件支持**: support@your-org.com
- **技术论坛**: https://forum.your-org.com/chs-core
- **文档反馈**: docs@your-org.com

我们致力于为开发者提供最好的API体验，您的反馈对我们非常重要。