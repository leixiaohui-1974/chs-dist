用户指南
========

欢迎使用 CHS-Core API！本指南将帮助您快速上手并有效使用 CHS-Core 系统的接口定义包。

快速开始
--------

安装
^^^^

首先安装 CHS-Core API 包：

.. code-block:: bash

   # 从本地安装
   pip install ./chs-core-api

   # 或从私有 PyPI 服务器安装
   pip install chs-core-api --index-url http://your-pypi-server.com/simple/

基本使用
^^^^^^^^

导入所需的接口和类型：

.. code-block:: python

   from chs_core_api import (
       WaterSystemComponent,
       ReservoirInterface,
       PumpInterface,
       FlowRate,
       WaterLevel,
       ComponentStatus
   )

实现接口
^^^^^^^^

实现一个简单的水泵组件：

.. code-block:: python

   from chs_core_api import PumpInterface, ComponentStatus, FlowRate
   from datetime import datetime
   from typing import Optional

   class MyPump(PumpInterface):
       def __init__(self, pump_id: str):
           self.pump_id = pump_id
           self._status = ComponentStatus.OFFLINE
           self._flow_rate = FlowRate(0.0, "m³/s", datetime.now())

       def get_id(self) -> str:
           return self.pump_id

       def get_status(self) -> ComponentStatus:
           return self._status

       def start(self) -> bool:
           try:
               # 启动水泵的实际逻辑
               self._status = ComponentStatus.ONLINE
               return True
           except Exception:
               self._status = ComponentStatus.ERROR
               return False

       def stop(self) -> bool:
           try:
               # 停止水泵的实际逻辑
               self._status = ComponentStatus.OFFLINE
               self._flow_rate = FlowRate(0.0, "m³/s", datetime.now())
               return True
           except Exception:
               return False

       def get_flow_rate(self) -> FlowRate:
           return self._flow_rate

       def set_flow_rate(self, flow_rate: FlowRate) -> bool:
           try:
               # 设置流量的实际逻辑
               self._flow_rate = flow_rate
               return True
           except Exception:
               return False

       def get_efficiency(self) -> float:
           # 返回水泵效率
           return 0.85

核心概念
--------

组件系统
^^^^^^^^

CHS-Core 采用基于组件的架构，所有设备和系统都实现相应的接口：

1. **WaterSystemComponent**: 所有水系统组件的基础接口
2. **ReservoirInterface**: 水库组件接口
3. **PumpInterface**: 水泵组件接口

每个组件都有唯一的标识符和状态管理功能。

数据类型
^^^^^^^^

CHS-Core 提供了丰富的数据类型来表示水利系统中的各种数据：

- **FlowRate**: 流量数据，支持多种单位
- **WaterLevel**: 水位数据，支持不同参考基准
- **ControlSignal**: 控制信号，用于设备控制
- **Measurement**: 测量数据，包含质量和不确定度信息

状态管理
^^^^^^^^

组件状态通过 ``ComponentStatus`` 枚举管理：

- ``OFFLINE``: 离线状态
- ``ONLINE``: 在线状态
- ``MAINTENANCE``: 维护状态
- ``ERROR``: 错误状态
- ``UNKNOWN``: 未知状态

常见使用场景
------------

场景1：监控系统集成
^^^^^^^^^^^^^^^^^^^

创建一个监控系统来管理多个组件：

.. code-block:: python

   from chs_core_api import (
       WaterSystemComponent,
       ComponentStatus,
       ComponentState,
       AlarmLevel
   )
   from typing import List, Dict
   from datetime import datetime

   class MonitoringSystem:
       def __init__(self):
           self.components: Dict[str, WaterSystemComponent] = {}
           self.alarms: List[Dict] = []

       def register_component(self, component: WaterSystemComponent):
           """注册组件到监控系统"""
           self.components[component.get_id()] = component

       def get_system_status(self) -> Dict[str, ComponentState]:
           """获取所有组件的状态"""
           status = {}
           for comp_id, component in self.components.items():
               status[comp_id] = ComponentState(
                   component_id=comp_id,
                   status=component.get_status(),
                   health_score=self._calculate_health_score(component),
                   last_update=datetime.now(),
                   parameters=self._get_component_parameters(component),
                   alarms=self._get_component_alarms(comp_id)
               )
           return status

       def check_alarms(self):
           """检查系统报警"""
           for comp_id, component in self.components.items():
               if component.get_status() == ComponentStatus.ERROR:
                   self._create_alarm(
                       comp_id,
                       AlarmLevel.CRITICAL,
                       "组件处于错误状态"
                   )
               elif component.get_status() == ComponentStatus.OFFLINE:
                   self._create_alarm(
                       comp_id,
                       AlarmLevel.WARNING,
                       "组件离线"
                   )

       def _calculate_health_score(self, component: WaterSystemComponent) -> float:
           """计算组件健康度评分"""
           if component.get_status() == ComponentStatus.ONLINE:
               return 100.0
           elif component.get_status() == ComponentStatus.MAINTENANCE:
               return 80.0
           elif component.get_status() == ComponentStatus.OFFLINE:
               return 50.0
           else:
               return 0.0

       def _get_component_parameters(self, component: WaterSystemComponent) -> Dict:
           """获取组件参数"""
           # 根据组件类型获取相应参数
           return {"status": component.get_status().value}

       def _get_component_alarms(self, comp_id: str) -> List[Dict]:
           """获取组件相关报警"""
           return [alarm for alarm in self.alarms if alarm["component_id"] == comp_id]

       def _create_alarm(self, comp_id: str, level: AlarmLevel, message: str):
           """创建报警"""
           alarm = {
               "component_id": comp_id,
               "level": level.value,
               "message": message,
               "timestamp": datetime.now()
           }
           self.alarms.append(alarm)

场景2：数据处理管道
^^^^^^^^^^^^^^^^^^^

实现一个数据处理管道来处理传感器数据：

.. code-block:: python

   from chs_core_api import (
       DataProcessor,
       Measurement,
       TimeSeriesData,
       DataValidationError
   )
   from typing import List
   from datetime import datetime, timedelta

   class SensorDataProcessor(DataProcessor):
       def __init__(self, processor_id: str):
           self.processor_id = processor_id
           self.quality_threshold = 0.8

       def get_id(self) -> str:
           return self.processor_id

       def process_data(self, data: List[Measurement]) -> TimeSeriesData:
           """处理传感器测量数据"""
           # 数据验证
           validated_data = self._validate_measurements(data)
           
           # 数据清洗
           cleaned_data = self._clean_data(validated_data)
           
           # 数据插值
           interpolated_data = self._interpolate_missing_values(cleaned_data)
           
           # 转换为时间序列格式
           return self._convert_to_time_series(interpolated_data)

       def _validate_measurements(self, data: List[Measurement]) -> List[Measurement]:
           """验证测量数据"""
           valid_data = []
           for measurement in data:
               if measurement.quality >= self.quality_threshold:
                   valid_data.append(measurement)
               else:
                   print(f"警告: 测量数据质量低于阈值 {measurement.sensor_id}")
           
           if not valid_data:
               raise DataValidationError(
                   "没有有效的测量数据",
                   data_source=self.processor_id,
                   error_code="NO_VALID_DATA"
               )
           
           return valid_data

       def _clean_data(self, data: List[Measurement]) -> List[Measurement]:
           """数据清洗：移除异常值"""
           if len(data) < 3:
               return data
           
           values = [m.value for m in data]
           mean_val = sum(values) / len(values)
           std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5
           
           # 移除超过3个标准差的异常值
           cleaned_data = []
           for measurement in data:
               if abs(measurement.value - mean_val) <= 3 * std_val:
                   cleaned_data.append(measurement)
           
           return cleaned_data

       def _interpolate_missing_values(self, data: List[Measurement]) -> List[Measurement]:
           """插值处理缺失值"""
           # 简单的线性插值实现
           if len(data) < 2:
               return data
           
           # 按时间排序
           sorted_data = sorted(data, key=lambda x: x.timestamp)
           
           # 检查时间间隔，插值缺失的数据点
           interpolated_data = []
           for i in range(len(sorted_data) - 1):
               current = sorted_data[i]
               next_measurement = sorted_data[i + 1]
               
               interpolated_data.append(current)
               
               # 如果时间间隔过大，进行插值
               time_diff = (next_measurement.timestamp - current.timestamp).total_seconds()
               if time_diff > 120:  # 超过2分钟
                   # 插入中间点
                   mid_time = current.timestamp + timedelta(seconds=time_diff/2)
                   mid_value = (current.value + next_measurement.value) / 2
                   
                   interpolated_measurement = Measurement(
                       sensor_id=current.sensor_id,
                       parameter=current.parameter,
                       value=mid_value,
                       unit=current.unit,
                       timestamp=mid_time,
                       quality=min(current.quality, next_measurement.quality),
                       uncertainty=max(current.uncertainty, next_measurement.uncertainty)
                   )
                   interpolated_data.append(interpolated_measurement)
           
           # 添加最后一个数据点
           interpolated_data.append(sorted_data[-1])
           
           return interpolated_data

       def _convert_to_time_series(self, data: List[Measurement]) -> TimeSeriesData:
           """转换为时间序列数据"""
           if not data:
               raise DataValidationError(
                   "无法转换空数据为时间序列",
                   data_source=self.processor_id,
                   error_code="EMPTY_DATA"
               )
           
           # 假设所有测量都是同一参数
           first_measurement = data[0]
           
           timestamps = [m.timestamp for m in data]
           values = [m.value for m in data]
           
           metadata = {
               "processor_id": self.processor_id,
               "sensor_count": len(set(m.sensor_id for m in data)),
               "quality_range": [min(m.quality for m in data), max(m.quality for m in data)],
               "processing_time": datetime.now()
           }
           
           return TimeSeriesData(
               parameter=first_measurement.parameter,
               unit=first_measurement.unit,
               timestamps=timestamps,
               values=values,
               metadata=metadata
           )

场景3：仿真引擎集成
^^^^^^^^^^^^^^^^^^^

实现一个简单的仿真引擎：

.. code-block:: python

   from chs_core_api import (
       SimulationEngine,
       SimulationResult,
       TimeSeriesData,
       SimulationParameterError
   )
   from typing import Dict, Any
   from datetime import datetime, timedelta

   class HydraulicSimulationEngine(SimulationEngine):
       def __init__(self, engine_id: str):
           self.engine_id = engine_id
           self.is_running = False

       def get_id(self) -> str:
           return self.engine_id

       def run_simulation(self, parameters: Dict[str, Any]) -> SimulationResult:
           """运行水力仿真"""
           # 验证参数
           self._validate_parameters(parameters)
           
           simulation_id = f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
           start_time = datetime.now()
           
           try:
               self.is_running = True
               
               # 执行仿真计算
               components_data = self._execute_simulation(parameters)
               
               end_time = datetime.now()
               duration = (end_time - start_time).total_seconds()
               
               # 计算统计信息
               summary_stats = self._calculate_summary_statistics(components_data)
               
               return SimulationResult(
                   simulation_id=simulation_id,
                   start_time=start_time,
                   end_time=end_time,
                   duration=duration,
                   time_step=parameters.get("time_step", 1.0),
                   components_data=components_data,
                   summary_statistics=summary_stats,
                   convergence_info={
                       "converged": True,
                       "iterations": 100,
                       "final_error": 1e-8
                   },
                   warnings=[],
                   errors=[]
               )
           
           finally:
               self.is_running = False

       def stop_simulation(self) -> bool:
           """停止仿真"""
           self.is_running = False
           return True

       def get_simulation_status(self) -> Dict[str, Any]:
           """获取仿真状态"""
           return {
               "engine_id": self.engine_id,
               "is_running": self.is_running,
               "last_run": datetime.now()
           }

       def _validate_parameters(self, parameters: Dict[str, Any]):
           """验证仿真参数"""
           required_params = ["duration", "time_step", "initial_conditions"]
           
           for param in required_params:
               if param not in parameters:
                   raise SimulationParameterError(
                       f"缺少必需参数: {param}",
                       simulation_id=self.engine_id,
                       error_code="MISSING_PARAMETER",
                       context={"missing_parameter": param}
                   )
           
           # 验证数值范围
           if parameters["duration"] <= 0:
               raise SimulationParameterError(
                   "仿真持续时间必须大于0",
                   simulation_id=self.engine_id,
                   error_code="INVALID_DURATION"
               )
           
           if parameters["time_step"] <= 0:
               raise SimulationParameterError(
                   "时间步长必须大于0",
                   simulation_id=self.engine_id,
                   error_code="INVALID_TIME_STEP"
               )

       def _execute_simulation(self, parameters: Dict[str, Any]) -> Dict[str, TimeSeriesData]:
           """执行仿真计算"""
           duration = parameters["duration"]
           time_step = parameters["time_step"]
           
           # 生成时间序列
           num_steps = int(duration / time_step) + 1
           timestamps = [datetime.now() + timedelta(seconds=i * time_step) for i in range(num_steps)]
           
           # 模拟水库水位变化
           initial_level = parameters["initial_conditions"].get("water_level", 125.0)
           water_levels = []
           
           for i in range(num_steps):
               # 简单的水位变化模型
               level = initial_level + 0.01 * i - 0.001 * i * i
               water_levels.append(max(level, 120.0))  # 最低水位限制
           
           # 创建组件数据
           components_data = {
               "RESERVOIR001": TimeSeriesData(
                   parameter="water_level",
                   unit="m",
                   timestamps=timestamps,
                   values=water_levels,
                   metadata={
                       "component_type": "reservoir",
                       "simulation_engine": self.engine_id
                   }
               )
           }
           
           return components_data

       def _calculate_summary_statistics(self, components_data: Dict[str, TimeSeriesData]) -> Dict[str, Any]:
           """计算汇总统计信息"""
           stats = {}
           
           for component_id, data in components_data.items():
               if data.parameter == "water_level":
                   stats["max_water_level"] = max(data.values)
                   stats["min_water_level"] = min(data.values)
                   stats["avg_water_level"] = sum(data.values) / len(data.values)
           
           return stats

错误处理
--------

异常处理策略
^^^^^^^^^^^^

CHS-Core API 提供了完整的异常体系，建议采用分层异常处理：

.. code-block:: python

   from chs_core_api.exceptions import (
       ComponentNotFoundError,
       ComponentConnectionError,
       DataValidationError,
       CHSCoreException
   )
   import logging

   logger = logging.getLogger(__name__)

   def safe_component_operation(component_id: str):
       try:
           # 获取组件
           component = get_component(component_id)
           
           # 连接组件
           if not component.connect():
               raise ComponentConnectionError(
                   f"无法连接到组件 {component_id}",
                   component_id=component_id
               )
           
           # 执行操作
           result = component.perform_operation()
           return result
           
       except ComponentNotFoundError as e:
           logger.error(f"组件未找到: {e.component_id}")
           return {"error": "组件不存在", "component_id": e.component_id}
           
       except ComponentConnectionError as e:
           logger.warning(f"组件连接失败: {e.component_id}")
           # 尝试重新连接
           return retry_connection(e.component_id)
           
       except DataValidationError as e:
           logger.error(f"数据验证失败: {e.message}")
           return {"error": "数据无效", "details": e.context}
           
       except CHSCoreException as e:
           logger.critical(f"系统异常: {e.error_code} - {e.message}")
           return {"error": "系统错误", "code": e.error_code}
           
       except Exception as e:
           logger.exception("未预期的错误")
           return {"error": "内部错误"}

重试机制
^^^^^^^^

对于网络相关的操作，建议实现重试机制：

.. code-block:: python

   import time
   from functools import wraps
   from chs_core_api.exceptions import NetworkException, ComponentConnectionError

   def retry_on_network_error(max_retries=3, delay=1.0):
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               last_exception = None
               
               for attempt in range(max_retries):
                   try:
                       return func(*args, **kwargs)
                   except (NetworkException, ComponentConnectionError) as e:
                       last_exception = e
                       if attempt < max_retries - 1:
                           wait_time = delay * (2 ** attempt)  # 指数退避
                           logger.warning(
                               f"操作失败，{wait_time:.1f}秒后重试 "
                               f"(尝试 {attempt + 1}/{max_retries}): {e.message}"
                           )
                           time.sleep(wait_time)
                       else:
                           logger.error(f"操作最终失败: {e.message}")
               
               raise last_exception
           return wrapper
       return decorator

   @retry_on_network_error(max_retries=3, delay=2.0)
   def connect_to_remote_component(component_id: str):
       # 连接到远程组件的代码
       pass

配置管理
--------

配置文件结构
^^^^^^^^^^^^

推荐使用 JSON 或 YAML 格式的配置文件：

.. code-block:: json

   {
     "system": {
       "name": "CHS水利监控系统",
       "version": "1.0.0",
       "log_level": "INFO"
     },
     "components": {
       "RESERVOIR001": {
         "type": "reservoir",
         "capacity": 1000000,
         "min_level": 120.0,
         "max_level": 150.0
       },
       "PUMP001": {
         "type": "pump",
         "max_flow_rate": 50.0,
         "efficiency": 0.85
       }
     },
     "monitoring": {
       "sampling_interval": 60,
       "alarm_thresholds": {
         "water_level_low": 125.0,
         "water_level_high": 145.0
       }
     }
   }

配置验证
^^^^^^^^

使用配置模式验证配置文件：

.. code-block:: python

   from chs_core_api import ConfigurationSchema, ConfigurationValidationError
   import json

   def load_and_validate_config(config_path: str) -> dict:
       # 定义配置模式
       schema = ConfigurationSchema(
           name="system_config",
           version="1.0",
           schema={
               "type": "object",
               "properties": {
                   "system": {
                       "type": "object",
                       "properties": {
                           "name": {"type": "string"},
                           "version": {"type": "string"},
                           "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]}
                       },
                       "required": ["name", "version"]
                   },
                   "components": {"type": "object"},
                   "monitoring": {"type": "object"}
               },
               "required": ["system", "components"]
           },
           required_fields=["system", "components"]
       )
       
       # 加载配置文件
       try:
           with open(config_path, 'r', encoding='utf-8') as f:
               config = json.load(f)
       except FileNotFoundError:
           raise ConfigurationFileError(
               f"配置文件不存在: {config_path}",
               config_path=config_path,
               error_code="FILE_NOT_FOUND"
           )
       except json.JSONDecodeError as e:
           raise ConfigurationValidationError(
               f"配置文件格式错误: {e}",
               config_path=config_path,
               error_code="INVALID_JSON"
           )
       
       # 验证配置
       if not schema.validate_config(config):
           raise ConfigurationValidationError(
               "配置文件验证失败",
               config_path=config_path,
               error_code="SCHEMA_VALIDATION_FAILED"
           )
       
       return config

性能优化
--------

数据缓存
^^^^^^^^

对于频繁访问的数据，建议使用缓存机制：

.. code-block:: python

   from functools import lru_cache
   from datetime import datetime, timedelta
   from typing import Optional

   class ComponentCache:
       def __init__(self, cache_duration: int = 300):  # 5分钟缓存
           self.cache_duration = cache_duration
           self._cache = {}
           self._timestamps = {}

       def get(self, key: str) -> Optional[Any]:
           if key in self._cache:
               # 检查缓存是否过期
               if datetime.now() - self._timestamps[key] < timedelta(seconds=self.cache_duration):
                   return self._cache[key]
               else:
                   # 清除过期缓存
                   del self._cache[key]
                   del self._timestamps[key]
           return None

       def set(self, key: str, value: Any):
           self._cache[key] = value
           self._timestamps[key] = datetime.now()

       def clear(self):
           self._cache.clear()
           self._timestamps.clear()

   # 全局缓存实例
   component_cache = ComponentCache()

   @lru_cache(maxsize=128)
   def get_component_config(component_id: str) -> dict:
       """获取组件配置（带缓存）"""
       # 从缓存获取
       cached_config = component_cache.get(f"config_{component_id}")
       if cached_config:
           return cached_config
       
       # 从数据源加载
       config = load_component_config_from_db(component_id)
       
       # 存入缓存
       component_cache.set(f"config_{component_id}", config)
       
       return config

批量操作
^^^^^^^^

对于大量数据处理，使用批量操作提高效率：

.. code-block:: python

   from typing import List, Dict
   from chs_core_api import Measurement, TimeSeriesData

   class BatchDataProcessor:
       def __init__(self, batch_size: int = 1000):
           self.batch_size = batch_size

       def process_measurements_batch(self, measurements: List[Measurement]) -> List[TimeSeriesData]:
           """批量处理测量数据"""
           results = []
           
           # 按传感器ID分组
           grouped_data = self._group_by_sensor(measurements)
           
           # 批量处理每个传感器的数据
           for sensor_id, sensor_measurements in grouped_data.items():
               # 分批处理
               for i in range(0, len(sensor_measurements), self.batch_size):
                   batch = sensor_measurements[i:i + self.batch_size]
                   processed_batch = self._process_batch(sensor_id, batch)
                   results.append(processed_batch)
           
           return results

       def _group_by_sensor(self, measurements: List[Measurement]) -> Dict[str, List[Measurement]]:
           """按传感器ID分组"""
           grouped = {}
           for measurement in measurements:
               if measurement.sensor_id not in grouped:
                   grouped[measurement.sensor_id] = []
               grouped[measurement.sensor_id].append(measurement)
           return grouped

       def _process_batch(self, sensor_id: str, batch: List[Measurement]) -> TimeSeriesData:
           """处理单个批次"""
           # 批量数据处理逻辑
           timestamps = [m.timestamp for m in batch]
           values = [m.value for m in batch]
           
           return TimeSeriesData(
               parameter=batch[0].parameter,
               unit=batch[0].unit,
               timestamps=timestamps,
               values=values,
               metadata={
                   "sensor_id": sensor_id,
                   "batch_size": len(batch),
                   "processing_time": datetime.now()
               }
           )

测试和调试
----------

单元测试
^^^^^^^^

为您的组件实现编写单元测试：

.. code-block:: python

   import unittest
   from unittest.mock import Mock, patch
   from chs_core_api import ComponentStatus, FlowRate
   from datetime import datetime

   class TestMyPump(unittest.TestCase):
       def setUp(self):
           self.pump = MyPump("TEST_PUMP_001")

       def test_pump_initialization(self):
           """测试水泵初始化"""
           self.assertEqual(self.pump.get_id(), "TEST_PUMP_001")
           self.assertEqual(self.pump.get_status(), ComponentStatus.OFFLINE)

       def test_pump_start_stop(self):
           """测试水泵启停"""
           # 测试启动
           result = self.pump.start()
           self.assertTrue(result)
           self.assertEqual(self.pump.get_status(), ComponentStatus.ONLINE)
           
           # 测试停止
           result = self.pump.stop()
           self.assertTrue(result)
           self.assertEqual(self.pump.get_status(), ComponentStatus.OFFLINE)

       def test_flow_rate_setting(self):
           """测试流量设置"""
           flow_rate = FlowRate(25.0, "m³/s", datetime.now())
           
           # 启动水泵
           self.pump.start()
           
           # 设置流量
           result = self.pump.set_flow_rate(flow_rate)
           self.assertTrue(result)
           
           # 验证流量
           current_flow = self.pump.get_flow_rate()
           self.assertEqual(current_flow.value, 25.0)
           self.assertEqual(current_flow.unit, "m³/s")

       @patch('your_module.actual_pump_hardware')
       def test_pump_hardware_failure(self, mock_hardware):
           """测试硬件故障处理"""
           # 模拟硬件故障
           mock_hardware.start.side_effect = Exception("硬件故障")
           
           result = self.pump.start()
           self.assertFalse(result)
           self.assertEqual(self.pump.get_status(), ComponentStatus.ERROR)

   if __name__ == '__main__':
       unittest.main()

集成测试
^^^^^^^^

测试组件之间的集成：

.. code-block:: python

   import unittest
   from chs_core_api import ComponentStatus

   class TestSystemIntegration(unittest.TestCase):
       def setUp(self):
           self.monitoring_system = MonitoringSystem()
           self.pump = MyPump("PUMP001")
           self.reservoir = MyReservoir("RESERVOIR001")
           
           # 注册组件
           self.monitoring_system.register_component(self.pump)
           self.monitoring_system.register_component(self.reservoir)

       def test_system_monitoring(self):
           """测试系统监控功能"""
           # 启动组件
           self.pump.start()
           self.reservoir.set_status(ComponentStatus.ONLINE)
           
           # 获取系统状态
           status = self.monitoring_system.get_system_status()
           
           # 验证状态
           self.assertIn("PUMP001", status)
           self.assertIn("RESERVOIR001", status)
           self.assertEqual(status["PUMP001"].status, ComponentStatus.ONLINE)
           self.assertEqual(status["RESERVOIR001"].status, ComponentStatus.ONLINE)

       def test_alarm_generation(self):
           """测试报警生成"""
           # 设置组件为错误状态
           self.pump.set_status(ComponentStatus.ERROR)
           
           # 检查报警
           self.monitoring_system.check_alarms()
           
           # 验证报警
           alarms = self.monitoring_system.alarms
           self.assertTrue(len(alarms) > 0)
           self.assertEqual(alarms[0]["component_id"], "PUMP001")

调试技巧
^^^^^^^^

使用日志记录进行调试：

.. code-block:: python

   import logging
   from chs_core_api.exceptions import CHSCoreException

   # 配置日志
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('chs_core.log'),
           logging.StreamHandler()
       ]
   )

   logger = logging.getLogger(__name__)

   class DebuggablePump(MyPump):
       def start(self) -> bool:
           logger.debug(f"尝试启动水泵 {self.pump_id}")
           
           try:
               result = super().start()
               if result:
                   logger.info(f"水泵 {self.pump_id} 启动成功")
               else:
                   logger.warning(f"水泵 {self.pump_id} 启动失败")
               return result
           except Exception as e:
               logger.error(f"水泵 {self.pump_id} 启动异常: {e}", exc_info=True)
               raise

       def set_flow_rate(self, flow_rate) -> bool:
           logger.debug(
               f"设置水泵 {self.pump_id} 流量: {flow_rate.value} {flow_rate.unit}"
           )
           
           try:
               result = super().set_flow_rate(flow_rate)
               if result:
                   logger.info(
                       f"水泵 {self.pump_id} 流量设置成功: {flow_rate.value} {flow_rate.unit}"
                   )
               return result
           except CHSCoreException as e:
               logger.error(
                   f"水泵 {self.pump_id} 流量设置失败: {e.message}",
                   extra={"error_code": e.error_code, "context": e.context}
               )
               raise

总结
----

通过本用户指南，您应该能够：

1. **理解 CHS-Core API 的核心概念**：组件系统、数据类型、状态管理
2. **实现自己的组件**：继承接口并实现具体功能
3. **处理常见场景**：监控系统、数据处理、仿真集成
4. **进行错误处理**：使用异常体系和重试机制
5. **管理配置**：验证和加载配置文件
6. **优化性能**：使用缓存和批量操作
7. **测试和调试**：编写测试用例和使用调试技巧

如需更多帮助，请参考 API 参考文档或联系开发团队。