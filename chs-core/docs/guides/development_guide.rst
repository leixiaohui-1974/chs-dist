开发指南
========

本指南面向希望基于 CHS-Core API 开发水利系统组件和应用的开发者。它提供了详细的开发规范、最佳实践和实现指导。

开发环境设置
------------

环境要求
^^^^^^^^

- Python 3.8 或更高版本
- pip 包管理器
- Git 版本控制
- IDE 或文本编辑器（推荐 PyCharm、VS Code）

安装开发依赖
^^^^^^^^^^^^

.. code-block:: bash

   # 克隆项目
   git clone <your-project-repository>
   cd your-project

   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate

   # 安装 CHS-Core API
   pip install chs-core-api

   # 安装开发依赖
   pip install pytest pytest-cov black flake8 mypy sphinx

项目结构
^^^^^^^^

推荐的项目结构：

.. code-block:: text

   your-project/
   ├── src/
   │   └── your_package/
   │       ├── __init__.py
   │       ├── components/
   │       │   ├── __init__.py
   │       │   ├── pumps.py
   │       │   ├── reservoirs.py
   │       │   └── sensors.py
   │       ├── processors/
   │       │   ├── __init__.py
   │       │   └── data_processor.py
   │       ├── engines/
   │       │   ├── __init__.py
   │       │   └── simulation_engine.py
   │       └── utils/
   │           ├── __init__.py
   │           └── helpers.py
   ├── tests/
   │   ├── __init__.py
   │   ├── test_components.py
   │   ├── test_processors.py
   │   └── test_engines.py
   ├── docs/
   │   ├── conf.py
   │   └── index.rst
   ├── requirements.txt
   ├── setup.py
   └── README.md

接口实现指南
------------

组件接口实现
^^^^^^^^^^^^

实现水系统组件时，需要继承相应的接口并实现所有抽象方法：

.. code-block:: python

   from chs_core_api import (
       ReservoirInterface,
       ComponentStatus,
       WaterLevel,
       FlowRate
   )
   from typing import Optional, Dict, Any
   from datetime import datetime
   import logging

   logger = logging.getLogger(__name__)

   class SmartReservoir(ReservoirInterface):
       """智能水库实现
       
       这是一个完整的水库组件实现示例，展示了如何正确实现
       ReservoirInterface 接口。
       """
       
       def __init__(self, reservoir_id: str, capacity: float, 
                    min_level: float = 0.0, max_level: float = 100.0):
           """
           初始化智能水库
           
           Args:
               reservoir_id: 水库唯一标识符
               capacity: 水库容量（立方米）
               min_level: 最低水位（米）
               max_level: 最高水位（米）
           """
           self.reservoir_id = reservoir_id
           self.capacity = capacity
           self.min_level = min_level
           self.max_level = max_level
           
           # 内部状态
           self._status = ComponentStatus.OFFLINE
           self._current_level = WaterLevel(
               value=(min_level + max_level) / 2,
               unit="m",
               reference="reservoir_bottom",
               timestamp=datetime.now()
           )
           self._inflow_rate = FlowRate(0.0, "m³/s", datetime.now())
           self._outflow_rate = FlowRate(0.0, "m³/s", datetime.now())
           
           # 配置参数
           self._config = {
               "alarm_low_level": min_level + 5.0,
               "alarm_high_level": max_level - 5.0,
               "auto_control_enabled": True
           }
           
           logger.info(f"智能水库 {reservoir_id} 初始化完成")

       def get_id(self) -> str:
           """获取水库标识符"""
           return self.reservoir_id

       def get_status(self) -> ComponentStatus:
           """获取水库状态"""
           return self._status

       def get_water_level(self) -> WaterLevel:
           """获取当前水位"""
           # 更新时间戳
           self._current_level.timestamp = datetime.now()
           return self._current_level

       def set_water_level(self, level: WaterLevel) -> bool:
           """设置水位（通常用于仿真或校准）"""
           try:
               # 验证水位范围
               if not self._validate_water_level(level.value):
                   logger.warning(
                       f"水位 {level.value} 超出有效范围 [{self.min_level}, {self.max_level}]"
                   )
                   return False
               
               self._current_level = level
               logger.info(f"水库 {self.reservoir_id} 水位设置为 {level.value} {level.unit}")
               
               # 检查报警条件
               self._check_level_alarms()
               
               return True
               
           except Exception as e:
               logger.error(f"设置水位失败: {e}")
               return False

       def get_capacity(self) -> float:
           """获取水库容量"""
           return self.capacity

       def get_inflow_rate(self) -> FlowRate:
           """获取入流流量"""
           return self._inflow_rate

       def get_outflow_rate(self) -> FlowRate:
           """获取出流流量"""
           return self._outflow_rate

       def set_outflow_rate(self, flow_rate: FlowRate) -> bool:
           """设置出流流量"""
           try:
               # 验证流量范围
               if flow_rate.value < 0:
                   logger.warning("出流流量不能为负数")
                   return False
               
               # 检查是否会导致水位过低
               if self._config["auto_control_enabled"]:
                   if not self._validate_outflow_safety(flow_rate):
                       logger.warning("出流流量过大，可能导致水位过低")
                       return False
               
               self._outflow_rate = flow_rate
               logger.info(
                   f"水库 {self.reservoir_id} 出流流量设置为 {flow_rate.value} {flow_rate.unit}"
               )
               
               return True
               
           except Exception as e:
               logger.error(f"设置出流流量失败: {e}")
               return False

       def start(self) -> bool:
           """启动水库监控系统"""
           try:
               # 执行启动检查
               if not self._perform_startup_checks():
                   logger.error(f"水库 {self.reservoir_id} 启动检查失败")
                   return False
               
               self._status = ComponentStatus.ONLINE
               logger.info(f"水库 {self.reservoir_id} 启动成功")
               return True
               
           except Exception as e:
               logger.error(f"水库 {self.reservoir_id} 启动失败: {e}")
               self._status = ComponentStatus.ERROR
               return False

       def stop(self) -> bool:
           """停止水库监控系统"""
           try:
               # 执行安全停止程序
               self._perform_safe_shutdown()
               
               self._status = ComponentStatus.OFFLINE
               logger.info(f"水库 {self.reservoir_id} 已停止")
               return True
               
           except Exception as e:
               logger.error(f"水库 {self.reservoir_id} 停止失败: {e}")
               return False

       def get_configuration(self) -> Dict[str, Any]:
           """获取配置参数"""
           return self._config.copy()

       def set_configuration(self, config: Dict[str, Any]) -> bool:
           """设置配置参数"""
           try:
               # 验证配置参数
               if not self._validate_configuration(config):
                   return False
               
               # 更新配置
               self._config.update(config)
               logger.info(f"水库 {self.reservoir_id} 配置已更新")
               return True
               
           except Exception as e:
               logger.error(f"设置配置失败: {e}")
               return False

       # 私有辅助方法
       def _validate_water_level(self, level: float) -> bool:
           """验证水位是否在有效范围内"""
           return self.min_level <= level <= self.max_level

       def _validate_outflow_safety(self, flow_rate: FlowRate) -> bool:
           """验证出流流量是否安全"""
           # 简化的安全检查：确保不会在1小时内降到最低水位以下
           current_volume = self._calculate_volume_from_level(self._current_level.value)
           outflow_volume_per_hour = flow_rate.value * 3600  # m³/h
           
           min_volume = self._calculate_volume_from_level(self.min_level)
           
           return (current_volume - outflow_volume_per_hour) > min_volume

       def _calculate_volume_from_level(self, level: float) -> float:
           """根据水位计算水量"""
           # 简化计算：假设水库为矩形
           if level <= self.min_level:
               return 0.0
           
           level_ratio = (level - self.min_level) / (self.max_level - self.min_level)
           return self.capacity * level_ratio

       def _check_level_alarms(self):
           """检查水位报警"""
           current_level = self._current_level.value
           
           if current_level <= self._config["alarm_low_level"]:
               logger.warning(f"水库 {self.reservoir_id} 水位过低: {current_level}m")
           elif current_level >= self._config["alarm_high_level"]:
               logger.warning(f"水库 {self.reservoir_id} 水位过高: {current_level}m")

       def _perform_startup_checks(self) -> bool:
           """执行启动检查"""
           # 检查传感器连接
           # 检查通信链路
           # 验证配置参数
           return True

       def _perform_safe_shutdown(self):
           """执行安全停止程序"""
           # 保存当前状态
           # 关闭连接
           # 清理资源
           pass

       def _validate_configuration(self, config: Dict[str, Any]) -> bool:
           """验证配置参数"""
           # 验证报警水位设置
           if "alarm_low_level" in config:
               if config["alarm_low_level"] < self.min_level:
                   logger.error("低水位报警值不能低于最低水位")
                   return False
           
           if "alarm_high_level" in config:
               if config["alarm_high_level"] > self.max_level:
                   logger.error("高水位报警值不能高于最高水位")
                   return False
           
           return True

数据处理器实现
^^^^^^^^^^^^^^

实现数据处理器来处理传感器数据：

.. code-block:: python

   from chs_core_api import (
       DataProcessor,
       Measurement,
       TimeSeriesData,
       DataValidationError,
       DataProcessingException
   )
   from typing import List, Dict, Any, Optional
   from datetime import datetime, timedelta
   import numpy as np
   import logging

   logger = logging.getLogger(__name__)

   class AdvancedDataProcessor(DataProcessor):
       """高级数据处理器
       
       提供数据清洗、验证、插值、滤波等功能。
       """
       
       def __init__(self, processor_id: str, config: Optional[Dict[str, Any]] = None):
           self.processor_id = processor_id
           self.config = config or self._get_default_config()
           
           # 统计信息
           self.stats = {
               "processed_count": 0,
               "error_count": 0,
               "last_processing_time": None
           }
           
           logger.info(f"高级数据处理器 {processor_id} 初始化完成")

       def get_id(self) -> str:
           return self.processor_id

       def process_data(self, data: List[Measurement]) -> TimeSeriesData:
           """处理测量数据"""
           start_time = datetime.now()
           
           try:
               logger.debug(f"开始处理 {len(data)} 个数据点")
               
               # 1. 数据验证
               validated_data = self._validate_data(data)
               logger.debug(f"验证后剩余 {len(validated_data)} 个数据点")
               
               # 2. 数据排序
               sorted_data = self._sort_by_timestamp(validated_data)
               
               # 3. 异常值检测和处理
               cleaned_data = self._detect_and_handle_outliers(sorted_data)
               logger.debug(f"清洗后剩余 {len(cleaned_data)} 个数据点")
               
               # 4. 数据插值
               interpolated_data = self._interpolate_missing_values(cleaned_data)
               logger.debug(f"插值后共有 {len(interpolated_data)} 个数据点")
               
               # 5. 数据滤波
               filtered_data = self._apply_filter(interpolated_data)
               
               # 6. 转换为时间序列
               time_series = self._convert_to_time_series(filtered_data)
               
               # 更新统计信息
               self.stats["processed_count"] += len(data)
               self.stats["last_processing_time"] = datetime.now()
               
               processing_time = (datetime.now() - start_time).total_seconds()
               logger.info(
                   f"数据处理完成，耗时 {processing_time:.3f} 秒，"
                   f"输入 {len(data)} 点，输出 {len(time_series.values)} 点"
               )
               
               return time_series
               
           except Exception as e:
               self.stats["error_count"] += 1
               logger.error(f"数据处理失败: {e}")
               raise DataProcessingException(
                   f"数据处理失败: {str(e)}",
                   data_source=self.processor_id,
                   error_code="PROCESSING_FAILED",
                   context={"input_count": len(data), "error": str(e)}
               )

       def get_statistics(self) -> Dict[str, Any]:
           """获取处理统计信息"""
           return self.stats.copy()

       def reset_statistics(self):
           """重置统计信息"""
           self.stats = {
               "processed_count": 0,
               "error_count": 0,
               "last_processing_time": None
           }

       def _get_default_config(self) -> Dict[str, Any]:
           """获取默认配置"""
           return {
               "quality_threshold": 0.8,
               "outlier_detection_method": "iqr",  # iqr, zscore, isolation_forest
               "outlier_threshold": 3.0,
               "interpolation_method": "linear",  # linear, cubic, nearest
               "max_gap_duration": 300,  # 最大插值间隔（秒）
               "filter_type": "moving_average",  # moving_average, median, none
               "filter_window": 5
           }

       def _validate_data(self, data: List[Measurement]) -> List[Measurement]:
           """验证数据质量"""
           if not data:
               raise DataValidationError(
                   "输入数据为空",
                   data_source=self.processor_id,
                   error_code="EMPTY_DATA"
               )
           
           valid_data = []
           quality_threshold = self.config["quality_threshold"]
           
           for measurement in data:
               # 检查数据质量
               if measurement.quality < quality_threshold:
                   logger.debug(
                       f"跳过低质量数据: {measurement.sensor_id}, "
                       f"质量 {measurement.quality} < {quality_threshold}"
                   )
                   continue
               
               # 检查数值有效性
               if not self._is_valid_value(measurement.value):
                   logger.debug(f"跳过无效数值: {measurement.value}")
                   continue
               
               # 检查时间戳
               if not self._is_valid_timestamp(measurement.timestamp):
                   logger.debug(f"跳过无效时间戳: {measurement.timestamp}")
                   continue
               
               valid_data.append(measurement)
           
           if not valid_data:
               raise DataValidationError(
                   "没有有效的测量数据",
                   data_source=self.processor_id,
                   error_code="NO_VALID_DATA"
               )
           
           return valid_data

       def _is_valid_value(self, value: float) -> bool:
           """检查数值是否有效"""
           return not (np.isnan(value) or np.isinf(value))

       def _is_valid_timestamp(self, timestamp: datetime) -> bool:
           """检查时间戳是否有效"""
           now = datetime.now()
           # 时间戳不能是未来时间，也不能太久远
           return (now - timedelta(days=365)) <= timestamp <= now

       def _sort_by_timestamp(self, data: List[Measurement]) -> List[Measurement]:
           """按时间戳排序"""
           return sorted(data, key=lambda x: x.timestamp)

       def _detect_and_handle_outliers(self, data: List[Measurement]) -> List[Measurement]:
           """检测和处理异常值"""
           if len(data) < 3:
               return data
           
           method = self.config["outlier_detection_method"]
           
           if method == "iqr":
               return self._detect_outliers_iqr(data)
           elif method == "zscore":
               return self._detect_outliers_zscore(data)
           else:
               return data

       def _detect_outliers_iqr(self, data: List[Measurement]) -> List[Measurement]:
           """使用IQR方法检测异常值"""
           values = np.array([m.value for m in data])
           
           q1 = np.percentile(values, 25)
           q3 = np.percentile(values, 75)
           iqr = q3 - q1
           
           lower_bound = q1 - 1.5 * iqr
           upper_bound = q3 + 1.5 * iqr
           
           cleaned_data = []
           for measurement in data:
               if lower_bound <= measurement.value <= upper_bound:
                   cleaned_data.append(measurement)
               else:
                   logger.debug(
                       f"检测到异常值: {measurement.value}, "
                       f"范围 [{lower_bound:.2f}, {upper_bound:.2f}]"
                   )
           
           return cleaned_data

       def _detect_outliers_zscore(self, data: List[Measurement]) -> List[Measurement]:
           """使用Z-score方法检测异常值"""
           values = np.array([m.value for m in data])
           
           mean_val = np.mean(values)
           std_val = np.std(values)
           
           if std_val == 0:
               return data
           
           threshold = self.config["outlier_threshold"]
           
           cleaned_data = []
           for measurement in data:
               z_score = abs((measurement.value - mean_val) / std_val)
               if z_score <= threshold:
                   cleaned_data.append(measurement)
               else:
                   logger.debug(
                       f"检测到异常值: {measurement.value}, Z-score: {z_score:.2f}"
                   )
           
           return cleaned_data

       def _interpolate_missing_values(self, data: List[Measurement]) -> List[Measurement]:
           """插值缺失值"""
           if len(data) < 2:
               return data
           
           interpolated_data = []
           max_gap = self.config["max_gap_duration"]
           
           for i in range(len(data) - 1):
               current = data[i]
               next_measurement = data[i + 1]
               
               interpolated_data.append(current)
               
               # 检查时间间隔
               time_gap = (next_measurement.timestamp - current.timestamp).total_seconds()
               
               if time_gap > max_gap:
                   # 插值
                   num_points = int(time_gap / 60)  # 每分钟一个点
                   if num_points > 1:
                       interpolated_points = self._create_interpolated_points(
                           current, next_measurement, num_points
                       )
                       interpolated_data.extend(interpolated_points)
           
           # 添加最后一个点
           interpolated_data.append(data[-1])
           
           return interpolated_data

       def _create_interpolated_points(self, start: Measurement, end: Measurement, 
                                     num_points: int) -> List[Measurement]:
           """创建插值点"""
           points = []
           
           for i in range(1, num_points):
               ratio = i / num_points
               
               # 时间插值
               time_diff = end.timestamp - start.timestamp
               interpolated_time = start.timestamp + ratio * time_diff
               
               # 数值插值
               interpolated_value = start.value + ratio * (end.value - start.value)
               
               # 质量取较低值
               interpolated_quality = min(start.quality, end.quality) * 0.8  # 插值数据质量降低
               
               point = Measurement(
                   sensor_id=start.sensor_id,
                   parameter=start.parameter,
                   value=interpolated_value,
                   unit=start.unit,
                   timestamp=interpolated_time,
                   quality=interpolated_quality,
                   uncertainty=max(start.uncertainty, end.uncertainty)
               )
               
               points.append(point)
           
           return points

       def _apply_filter(self, data: List[Measurement]) -> List[Measurement]:
           """应用滤波器"""
           filter_type = self.config["filter_type"]
           
           if filter_type == "none" or len(data) < 3:
               return data
           
           if filter_type == "moving_average":
               return self._apply_moving_average_filter(data)
           elif filter_type == "median":
               return self._apply_median_filter(data)
           else:
               return data

       def _apply_moving_average_filter(self, data: List[Measurement]) -> List[Measurement]:
           """应用移动平均滤波器"""
           window = self.config["filter_window"]
           filtered_data = []
           
           for i in range(len(data)):
               start_idx = max(0, i - window // 2)
               end_idx = min(len(data), i + window // 2 + 1)
               
               window_values = [data[j].value for j in range(start_idx, end_idx)]
               filtered_value = sum(window_values) / len(window_values)
               
               # 创建滤波后的测量值
               filtered_measurement = Measurement(
                   sensor_id=data[i].sensor_id,
                   parameter=data[i].parameter,
                   value=filtered_value,
                   unit=data[i].unit,
                   timestamp=data[i].timestamp,
                   quality=data[i].quality,
                   uncertainty=data[i].uncertainty
               )
               
               filtered_data.append(filtered_measurement)
           
           return filtered_data

       def _apply_median_filter(self, data: List[Measurement]) -> List[Measurement]:
           """应用中值滤波器"""
           window = self.config["filter_window"]
           filtered_data = []
           
           for i in range(len(data)):
               start_idx = max(0, i - window // 2)
               end_idx = min(len(data), i + window // 2 + 1)
               
               window_values = [data[j].value for j in range(start_idx, end_idx)]
               filtered_value = np.median(window_values)
               
               # 创建滤波后的测量值
               filtered_measurement = Measurement(
                   sensor_id=data[i].sensor_id,
                   parameter=data[i].parameter,
                   value=filtered_value,
                   unit=data[i].unit,
                   timestamp=data[i].timestamp,
                   quality=data[i].quality,
                   uncertainty=data[i].uncertainty
               )
               
               filtered_data.append(filtered_measurement)
           
           return filtered_data

       def _convert_to_time_series(self, data: List[Measurement]) -> TimeSeriesData:
           """转换为时间序列数据"""
           if not data:
               raise DataProcessingException(
                   "无法转换空数据为时间序列",
                   data_source=self.processor_id,
                   error_code="EMPTY_PROCESSED_DATA"
               )
           
           first_measurement = data[0]
           
           timestamps = [m.timestamp for m in data]
           values = [m.value for m in data]
           
           # 计算处理统计信息
           metadata = {
               "processor_id": self.processor_id,
               "processing_config": self.config.copy(),
               "data_count": len(data),
               "sensor_ids": list(set(m.sensor_id for m in data)),
               "quality_stats": {
                   "min": min(m.quality for m in data),
                   "max": max(m.quality for m in data),
                   "avg": sum(m.quality for m in data) / len(data)
               },
               "value_stats": {
                   "min": min(values),
                   "max": max(values),
                   "avg": sum(values) / len(values),
                   "std": np.std(values)
               },
               "processing_time": datetime.now()
           }
           
           return TimeSeriesData(
               parameter=first_measurement.parameter,
               unit=first_measurement.unit,
               timestamps=timestamps,
               values=values,
               metadata=metadata
           )

代码质量标准
------------

代码风格
^^^^^^^^

遵循 PEP 8 Python 代码风格指南：

.. code-block:: bash

   # 使用 black 格式化代码
   black src/ tests/

   # 使用 flake8 检查代码风格
   flake8 src/ tests/ --max-line-length=88

类型注解
^^^^^^^^

使用类型注解提高代码可读性和类型安全：

.. code-block:: python

   from typing import List, Dict, Optional, Union, Any
   from chs_core_api import ComponentStatus, FlowRate

   def process_flow_data(
       flow_rates: List[FlowRate],
       config: Dict[str, Any],
       threshold: Optional[float] = None
   ) -> Union[List[FlowRate], None]:
       """处理流量数据
       
       Args:
           flow_rates: 流量数据列表
           config: 处理配置
           threshold: 可选的阈值参数
           
       Returns:
           处理后的流量数据，如果处理失败返回 None
       """
       if not flow_rates:
           return None
       
       # 处理逻辑
       processed_data = []
       for flow_rate in flow_rates:
           if threshold is None or flow_rate.value >= threshold:
               processed_data.append(flow_rate)
       
       return processed_data

使用 mypy 进行类型检查：

.. code-block:: bash

   mypy src/ --strict

文档字符串
^^^^^^^^^^

使用 Google 风格的文档字符串：

.. code-block:: python

   def calculate_reservoir_volume(water_level: float, 
                                 reservoir_area: float,
                                 bottom_elevation: float) -> float:
       """计算水库蓄水量。
       
       根据水位、水库面积和库底高程计算当前蓄水量。
       
       Args:
           water_level: 当前水位（米，海拔高程）
           reservoir_area: 水库面积（平方米）
           bottom_elevation: 库底高程（米，海拔高程）
           
       Returns:
           蓄水量（立方米）
           
       Raises:
           ValueError: 当水位低于库底高程时
           
       Example:
           >>> volume = calculate_reservoir_volume(125.5, 1000000, 120.0)
           >>> print(f"蓄水量: {volume} 立方米")
           蓄水量: 5500000.0 立方米
       """
       if water_level < bottom_elevation:
           raise ValueError("水位不能低于库底高程")
       
       effective_depth = water_level - bottom_elevation
       volume = reservoir_area * effective_depth
       
       return volume

测试开发
--------

单元测试
^^^^^^^^

使用 pytest 编写单元测试：

.. code-block:: python

   import pytest
   from unittest.mock import Mock, patch
   from datetime import datetime
   from chs_core_api import ComponentStatus, WaterLevel, FlowRate
   from your_package.components.reservoirs import SmartReservoir

   class TestSmartReservoir:
       """智能水库测试类"""
       
       @pytest.fixture
       def reservoir(self):
           """创建测试用水库实例"""
           return SmartReservoir(
               reservoir_id="TEST_RESERVOIR",
               capacity=1000000.0,
               min_level=120.0,
               max_level=150.0
           )
       
       def test_initialization(self, reservoir):
           """测试水库初始化"""
           assert reservoir.get_id() == "TEST_RESERVOIR"
           assert reservoir.get_capacity() == 1000000.0
           assert reservoir.get_status() == ComponentStatus.OFFLINE
       
       def test_water_level_operations(self, reservoir):
           """测试水位操作"""
           # 测试设置有效水位
           new_level = WaterLevel(125.0, "m", "reservoir_bottom", datetime.now())
           assert reservoir.set_water_level(new_level) is True
           
           current_level = reservoir.get_water_level()
           assert current_level.value == 125.0
           
           # 测试设置无效水位
           invalid_level = WaterLevel(200.0, "m", "reservoir_bottom", datetime.now())
           assert reservoir.set_water_level(invalid_level) is False
       
       def test_flow_rate_operations(self, reservoir):
           """测试流量操作"""
           # 测试设置有效出流流量
           flow_rate = FlowRate(10.0, "m³/s", datetime.now())
           assert reservoir.set_outflow_rate(flow_rate) is True
           
           current_outflow = reservoir.get_outflow_rate()
           assert current_outflow.value == 10.0
           
           # 测试设置负流量
           negative_flow = FlowRate(-5.0, "m³/s", datetime.now())
           assert reservoir.set_outflow_rate(negative_flow) is False
       
       def test_start_stop_operations(self, reservoir):
           """测试启停操作"""
           # 测试启动
           assert reservoir.start() is True
           assert reservoir.get_status() == ComponentStatus.ONLINE
           
           # 测试停止
           assert reservoir.stop() is True
           assert reservoir.get_status() == ComponentStatus.OFFLINE
       
       def test_configuration_management(self, reservoir):
           """测试配置管理"""
           # 获取默认配置
           config = reservoir.get_configuration()
           assert "alarm_low_level" in config
           assert "alarm_high_level" in config
           
           # 更新配置
           new_config = {"alarm_low_level": 122.0}
           assert reservoir.set_configuration(new_config) is True
           
           updated_config = reservoir.get_configuration()
           assert updated_config["alarm_low_level"] == 122.0
           
           # 测试无效配置
           invalid_config = {"alarm_low_level": 100.0}  # 低于最低水位
           assert reservoir.set_configuration(invalid_config) is False
       
       @patch('your_package.components.reservoirs.logger')
       def test_error_handling(self, mock_logger, reservoir):
           """测试错误处理"""
           # 模拟启动失败
           with patch.object(reservoir, '_perform_startup_checks', return_value=False):
               assert reservoir.start() is False
               assert reservoir.get_status() == ComponentStatus.OFFLINE
               mock_logger.error.assert_called()
       
       def test_edge_cases(self, reservoir):
           """测试边界情况"""
           # 测试边界水位
           min_level = WaterLevel(120.0, "m", "reservoir_bottom", datetime.now())
           assert reservoir.set_water_level(min_level) is True
           
           max_level = WaterLevel(150.0, "m", "reservoir_bottom", datetime.now())
           assert reservoir.set_water_level(max_level) is True
           
           # 测试边界外水位
           below_min = WaterLevel(119.9, "m", "reservoir_bottom", datetime.now())
           assert reservoir.set_water_level(below_min) is False
           
           above_max = WaterLevel(150.1, "m", "reservoir_bottom", datetime.now())
           assert reservoir.set_water_level(above_max) is False

集成测试
^^^^^^^^

测试组件之间的集成：

.. code-block:: python

   import pytest
   from datetime import datetime, timedelta
   from chs_core_api import Measurement, ComponentStatus
   from your_package.components.reservoirs import SmartReservoir
   from your_package.processors.data_processor import AdvancedDataProcessor

   class TestSystemIntegration:
       """系统集成测试"""
       
       @pytest.fixture
       def system_components(self):
           """创建系统组件"""
           reservoir = SmartReservoir("RESERVOIR001", 1000000.0, 120.0, 150.0)
           processor = AdvancedDataProcessor("PROCESSOR001")
           
           return {
               "reservoir": reservoir,
               "processor": processor
           }
       
       def test_data_flow_integration(self, system_components):
           """测试数据流集成"""
           reservoir = system_components["reservoir"]
           processor = system_components["processor"]
           
           # 启动组件
           assert reservoir.start() is True
           
           # 生成测试数据
           measurements = self._generate_test_measurements()
           
           # 处理数据
           time_series = processor.process_data(measurements)
           
           # 验证处理结果
           assert time_series is not None
           assert len(time_series.values) > 0
           assert time_series.parameter == "water_level"
           
           # 应用处理结果到水库
           latest_level = time_series.values[-1]
           water_level = WaterLevel(
               value=latest_level,
               unit="m",
               reference="reservoir_bottom",
               timestamp=time_series.timestamps[-1]
           )
           
           assert reservoir.set_water_level(water_level) is True
       
       def test_error_propagation(self, system_components):
           """测试错误传播"""
           processor = system_components["processor"]
           
           # 测试空数据处理
           with pytest.raises(DataValidationError):
               processor.process_data([])
           
           # 测试低质量数据
           low_quality_data = [
               Measurement(
                   sensor_id="SENSOR001",
                   parameter="water_level",
                   value=125.0,
                   unit="m",
                   timestamp=datetime.now(),
                   quality=0.1,  # 低质量
                   uncertainty=0.5
               )
           ]
           
           with pytest.raises(DataValidationError):
               processor.process_data(low_quality_data)
       
       def _generate_test_measurements(self) -> List[Measurement]:
           """生成测试测量数据"""
           measurements = []
           base_time = datetime.now() - timedelta(hours=1)
           
           for i in range(60):  # 60个数据点
               measurement = Measurement(
                   sensor_id="LEVEL_SENSOR_001",
                   parameter="water_level",
                   value=125.0 + 0.1 * i + 0.05 * (i % 10),  # 模拟水位变化
                   unit="m",
                   timestamp=base_time + timedelta(minutes=i),
                   quality=0.95,
                   uncertainty=0.1
               )
               measurements.append(measurement)
           
           return measurements

性能测试
^^^^^^^^

使用 pytest-benchmark 进行性能测试：

.. code-block:: python

   import pytest
   from datetime import datetime, timedelta
   from chs_core_api import Measurement
   from your_package.processors.data_processor import AdvancedDataProcessor

   class TestPerformance:
       """性能测试"""
       
       @pytest.fixture
       def large_dataset(self):
           """创建大数据集"""
           measurements = []
           base_time = datetime.now() - timedelta(days=1)
           
           # 生成24小时的数据，每分钟一个点
           for i in range(24 * 60):
               measurement = Measurement(
                   sensor_id=f"SENSOR_{i % 10:03d}",
                   parameter="water_level",
                   value=125.0 + 5.0 * (i % 100) / 100,
                   unit="m",
                   timestamp=base_time + timedelta(minutes=i),
                   quality=0.95,
                   uncertainty=0.1
               )
               measurements.append(measurement)
           
           return measurements
       
       def test_data_processing_performance(self, benchmark, large_dataset):
           """测试数据处理性能"""
           processor = AdvancedDataProcessor("PERF_TEST")
           
           # 基准测试
           result = benchmark(processor.process_data, large_dataset)
           
           # 验证结果
           assert result is not None
           assert len(result.values) > 0
       
       def test_memory_usage(self, large_dataset):
           """测试内存使用"""
           import psutil
           import os
           
           process = psutil.Process(os.getpid())
           initial_memory = process.memory_info().rss
           
           processor = AdvancedDataProcessor("MEMORY_TEST")
           result = processor.process_data(large_dataset)
           
           final_memory = process.memory_info().rss
           memory_increase = final_memory - initial_memory
           
           # 内存增长应该在合理范围内（例如小于100MB）
           assert memory_increase < 100 * 1024 * 1024

运行测试：

.. code-block:: bash

   # 运行所有测试
   pytest tests/

   # 运行特定测试文件
   pytest tests/test_components.py

   # 运行性能测试
   pytest tests/test_performance.py --benchmark-only

   # 生成覆盖率报告
   pytest tests/ --cov=src/ --cov-report=html

持续集成
--------

GitHub Actions 配置
^^^^^^^^^^^^^^^^^^^

创建 `.github/workflows/ci.yml`：

.. code-block:: yaml

   name: CI

   on:
     push:
       branches: [ main, develop ]
     pull_request:
       branches: [ main ]

   jobs:
     test:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: [3.8, 3.9, "3.10", "3.11"]

       steps:
       - uses: actions/checkout@v3
       
       - name: Set up Python ${{ matrix.python-version }}
         uses: actions/setup-python@v3
         with:
           python-version: ${{ matrix.python-version }}
       
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -r requirements.txt
           pip install -r requirements-dev.txt
       
       - name: Lint with flake8
         run: |
           flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
           flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
       
       - name: Type check with mypy
         run: |
           mypy src/ --strict
       
       - name: Test with pytest
         run: |
           pytest tests/ --cov=src/ --cov-report=xml
       
       - name: Upload coverage to Codecov
         uses: codecov/codecov-action@v3
         with:
           file: ./coverage.xml
           flags: unittests
           name: codecov-umbrella

代码质量检查
^^^^^^^^^^^^

创建 `pyproject.toml` 配置文件：

.. code-block:: toml

   [tool.black]
   line-length = 88
   target-version = ['py38']
   include = '\.pyi?$'
   extend-exclude = '''
   /(
     # directories
     \.eggs
     | \.git
     | \.hg
     | \.mypy_cache
     | \.tox
     | \.venv
     | build
     | dist
   )/
   '''

   [tool.isort]
   profile = "black"
   multi_line_output = 3
   line_length = 88

   [tool.mypy]
   python_version = "3.8"
   warn_return_any = true
   warn_unused_configs = true
   disallow_untyped_defs = true
   disallow_incomplete_defs = true
   check_untyped_defs = true
   disallow_untyped_decorators = true
   no_implicit_optional = true
   warn_redundant_casts = true
   warn_unused_ignores = true
   warn_no_return = true
   warn_unreachable = true
   strict_equality = true

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = ["test_*.py"]
   python_classes = ["Test*"]
   python_functions = ["test_*"]
   addopts = "-v --strict-markers --disable-warnings"
   markers = [
       "slow: marks tests as slow (deselect with '-m "not slow"')",
       "integration: marks tests as integration tests",
       "unit: marks tests as unit tests",
   ]

   [tool.coverage.run]
   source = ["src"]
   omit = [
       "*/tests/*",
       "*/test_*.py",
       "setup.py",
   ]

   [tool.coverage.report]
   exclude_lines = [
       "pragma: no cover",
       "def __repr__",
       "raise AssertionError",
       "raise NotImplementedError",
       "if __name__ == .__main__.:",
   ]

部署和分发
----------

包构建
^^^^^^

创建 `setup.py`：

.. code-block:: python

   from setuptools import setup, find_packages

   with open("README.md", "r", encoding="utf-8") as fh:
       long_description = fh.read()

   with open("requirements.txt", "r", encoding="utf-8") as fh:
       requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

   setup(
       name="your-chs-implementation",
       version="0.1.0",
       author="Your Name",
       author_email="your.email@example.com",
       description="CHS-Core 水利系统实现",
       long_description=long_description,
       long_description_content_type="text/markdown",
       url="https://github.com/yourusername/your-chs-implementation",
       packages=find_packages(where="src"),
       package_dir={"": "src"},
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
       ],
       python_requires=">=3.8",
       install_requires=requirements,
       extras_require={
           "dev": [
               "pytest>=6.0",
               "pytest-cov>=2.0",
               "black>=21.0",
               "flake8>=3.8",
               "mypy>=0.800",
               "sphinx>=4.0",
           ],
           "test": [
               "pytest>=6.0",
               "pytest-cov>=2.0",
               "pytest-benchmark>=3.4",
           ],
       },
       entry_points={
           "console_scripts": [
               "your-chs-cli=your_package.cli:main",
           ],
       },
   )

构建和分发：

.. code-block:: bash

   # 构建包
   python setup.py sdist bdist_wheel

   # 检查包
   twine check dist/*

   # 上传到私有 PyPI
   twine upload --repository-url http://your-pypi-server.com/simple/ dist/*

文档生成
^^^^^^^^

使用 Sphinx 生成文档：

.. code-block:: bash

   # 生成文档
   cd docs
   make html

   # 查看文档
   open _build/html/index.html

最佳实践总结
------------

1. **接口设计**
   - 保持接口简洁明确
   - 使用类型注解
   - 提供完整的文档字符串
   - 考虑向后兼容性

2. **错误处理**
   - 使用适当的异常类型
   - 提供详细的错误信息
   - 实现重试机制
   - 记录错误日志

3. **性能优化**
   - 使用缓存机制
   - 实现批量操作
   - 避免不必要的计算
   - 监控内存使用

4. **测试策略**
   - 编写全面的单元测试
   - 实现集成测试
   - 进行性能测试
   - 保持高测试覆盖率

5. **代码质量**
   - 遵循代码风格指南
   - 使用静态分析工具
   - 进行代码审查
   - 持续重构改进

6. **文档维护**
   - 保持文档与代码同步
   - 提供使用示例
   - 编写故障排除指南
   - 定期更新文档

通过遵循这些开发指南和最佳实践，您可以构建高质量、可维护的 CHS-Core 系统组件和应用。