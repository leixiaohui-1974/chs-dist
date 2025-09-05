接口定义
========

CHS-Core API 提供了一套完整的接口定义，用于标准化水力系统组件的行为和交互方式。

核心接口概览
------------

.. currentmodule:: chs_core_api.interfaces

.. autosummary::
   :toctree: generated/
   :nosignatures:

   WaterSystemComponent
   ReservoirInterface
   PumpInterface
   DataProcessor
   AnomalyDetectorInterface
   SimulationEngine
   ConfigurationManager

水力系统组件接口
----------------

WaterSystemComponent
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: WaterSystemComponent
   :members:
   :undoc-members:
   :show-inheritance:

   这是所有水力系统组件的基础接口。所有具体的组件（如水库、泵站、阀门等）都应该实现此接口。

   **核心功能：**

   - 组件标识和状态管理
   - 流量获取和控制信号处理
   - 组件更新和重置机制

   **使用示例：**

   .. code-block:: python

      from chs_core_api import WaterSystemComponent, FlowRate, ComponentState
      from datetime import datetime

      class CustomComponent(WaterSystemComponent):
          def __init__(self, component_id: str):
              self.component_id = component_id
              self.flow_rate = FlowRate(0.0)
              
          def get_component_id(self) -> str:
              return self.component_id
              
          def get_flow_rate(self) -> FlowRate:
              return self.flow_rate
              
          # ... 实现其他抽象方法

ReservoirInterface
^^^^^^^^^^^^^^^^^^

.. autoclass:: ReservoirInterface
   :members:
   :undoc-members:
   :show-inheritance:

   水库组件专用接口，继承自 :class:`WaterSystemComponent`。

   **专有功能：**

   - 水位监测和管理
   - 库容计算
   - 入流和出流控制

   **使用示例：**

   .. code-block:: python

      from chs_core_api import ReservoirInterface, WaterLevel, FlowRate

      class Reservoir(ReservoirInterface):
          def __init__(self, reservoir_id: str, capacity: float):
              self.reservoir_id = reservoir_id
              self.capacity = capacity
              self.water_level = WaterLevel(50.0, "m", "reservoir_bottom")
              
          def get_water_level(self) -> WaterLevel:
              return self.water_level
              
          def get_capacity(self) -> float:
              return self.capacity
              
          def set_inflow(self, rate: FlowRate) -> None:
              # 根据入流更新水位
              inflow_rate = rate.to_cubic_meters_per_second()
              # 简化的水位计算逻辑
              self.water_level.value += inflow_rate * 0.01
              
          def calculate_outflow(self) -> FlowRate:
              # 根据水位计算出流
              outflow_value = max(0, self.water_level.value - 30) * 0.1
              return FlowRate(outflow_value)

PumpInterface
^^^^^^^^^^^^^

.. autoclass:: PumpInterface
   :members:
   :undoc-members:
   :show-inheritance:

   泵站组件专用接口，继承自 :class:`WaterSystemComponent`。

   **专有功能：**

   - 泵站效率监测
   - 转速控制
   - 功耗计算

   **使用示例：**

   .. code-block:: python

      from chs_core_api import PumpInterface, FlowRate

      class Pump(PumpInterface):
          def __init__(self, pump_id: str):
              self.pump_id = pump_id
              self.efficiency = 0.85
              self.speed = 1500.0  # RPM
              self.power = 0.0
              
          def get_pump_efficiency(self) -> float:
              return self.efficiency
              
          def set_pump_speed(self, speed: float) -> None:
              self.speed = speed
              # 根据转速更新功耗
              self.power = (speed / 1500.0) ** 3 * 100.0
              
          def get_power_consumption(self) -> float:
              return self.power

数据处理接口
------------

DataProcessor
^^^^^^^^^^^^^

.. autoclass:: DataProcessor
   :members:
   :undoc-members:
   :show-inheritance:

   数据处理器的基础接口，定义了数据处理的标准方法。

   **核心功能：**

   - 数据处理和转换
   - 数据验证
   - 处理统计信息

   **使用示例：**

   .. code-block:: python

      from chs_core_api import DataProcessor, Measurement
      from typing import Any, Dict

      class WaterQualityProcessor(DataProcessor):
          def __init__(self):
              self.processed_count = 0
              
          def process_data(self, data: Any) -> Any:
              if isinstance(data, Measurement):
                  # 处理测量数据
                  processed_data = self._clean_measurement(data)
                  self.processed_count += 1
                  return processed_data
              return data
              
          def validate_data(self, data: Any) -> bool:
              if isinstance(data, Measurement):
                  return self._validate_measurement(data)
              return False
              
          def get_processing_stats(self) -> Dict[str, Any]:
              return {"processed_count": self.processed_count}

AnomalyDetectorInterface
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: AnomalyDetectorInterface
   :members:
   :undoc-members:
   :show-inheritance:

   异常检测器接口，继承自 :class:`DataProcessor`。

   **专有功能：**

   - 异常模式检测
   - 阈值设置和管理

仿真引擎接口
------------

SimulationEngine
^^^^^^^^^^^^^^^^

.. autoclass:: SimulationEngine
   :members:
   :undoc-members:
   :show-inheritance:

   仿真引擎的核心接口，定义了仿真执行和控制的标准方法。

   **核心功能：**

   - 仿真初始化和配置
   - 组件管理
   - 仿真执行控制
   - 状态监控

   **使用示例：**

   .. code-block:: python

      from chs_core_api import SimulationEngine, WaterSystemComponent, SimulationResult
      from typing import Dict, Any, List

      class HydraulicSimulationEngine(SimulationEngine):
          def __init__(self):
              self.components: List[WaterSystemComponent] = []
              self.config: Dict[str, Any] = {}
              self.status = "stopped"
              
          def initialize_simulation(self, config: Dict[str, Any]) -> None:
              self.config = config
              self.status = "initialized"
              
          def add_component(self, component: WaterSystemComponent) -> None:
              self.components.append(component)
              
          def run_simulation(self, duration: float, time_step: float) -> SimulationResult:
              self.status = "running"
              # 执行仿真逻辑
              # ...
              self.status = "completed"
              return self._generate_result()
              
          def get_simulation_status(self) -> str:
              return self.status

配置管理接口
------------

ConfigurationManager
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ConfigurationManager
   :members:
   :undoc-members:
   :show-inheritance:

   配置管理器接口，定义了配置文件的加载、保存和管理方法。

   **核心功能：**

   - 配置文件加载和保存
   - 配置验证
   - 默认配置管理

   **使用示例：**

   .. code-block:: python

      from chs_core_api import ConfigurationManager
      import json
      from typing import Dict, Any

      class JSONConfigurationManager(ConfigurationManager):
          def load_config(self, config_path: str) -> Dict[str, Any]:
              with open(config_path, 'r', encoding='utf-8') as f:
                  return json.load(f)
                  
          def save_config(self, config: Dict[str, Any], config_path: str) -> None:
              with open(config_path, 'w', encoding='utf-8') as f:
                  json.dump(config, f, ensure_ascii=False, indent=2)
                  
          def validate_config(self, config: Dict[str, Any]) -> bool:
              required_keys = ['simulation', 'components', 'output']
              return all(key in config for key in required_keys)
              
          def get_default_config(self) -> Dict[str, Any]:
              return {
                  'simulation': {'duration': 3600, 'time_step': 1.0},
                  'components': {},
                  'output': {'format': 'json', 'path': './results'}
              }

接口设计原则
------------

1. **单一职责原则**
   每个接口都有明确的职责范围，避免功能重叠。

2. **开闭原则**
   接口对扩展开放，对修改封闭，便于添加新功能。

3. **里氏替换原则**
   所有实现类都可以替换其接口类型，保证行为一致性。

4. **接口隔离原则**
   接口尽可能小而专一，避免强迫实现不需要的方法。

5. **依赖倒置原则**
   依赖抽象接口而不是具体实现，提高系统的灵活性。

最佳实践
--------

1. **完整实现所有抽象方法**
   确保实现接口的所有抽象方法，避免运行时错误。

2. **遵循类型约定**
   使用定义的数据类型，确保类型安全。

3. **适当的错误处理**
   使用统一的异常体系，提供清晰的错误信息。

4. **文档化实现**
   为实现类提供清晰的文档说明。

5. **单元测试**
   为每个实现类编写完整的单元测试。