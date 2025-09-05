类型定义
========

CHS-Core API 提供了一套完整的类型系统，用于标准化数据表示和交换格式。这些类型定义确保了不同组件之间的数据一致性和类型安全。

类型概览
--------

.. currentmodule:: chs_core_api.types

.. autosummary::
   :toctree: generated/
   :nosignatures:

   FlowRate
   WaterLevel
   ControlSignal
   ComponentState
   ComponentStatus
   AlarmLevel
   Measurement
   TimeSeriesData
   SimulationResult
   ConfigurationSchema
   APIResponse

基础数据类型
------------

FlowRate
^^^^^^^^

.. autoclass:: FlowRate
   :members:
   :undoc-members:
   :show-inheritance:

   流量数据类型，用于表示水流的流量信息。

   **特性：**

   - 支持多种流量单位（m³/s, L/s, m³/h, L/min）
   - 包含时间戳信息
   - 提供单位转换方法
   - 自动验证数值有效性

   **使用示例：**

   .. code-block:: python

      from chs_core_api import FlowRate
      from datetime import datetime

      # 创建流量对象
      flow = FlowRate(value=5.0, unit="m³/s", timestamp=datetime.now())
      print(f"流量: {flow.value} {flow.unit}")

      # 单位转换
      flow_cms = flow.to_cubic_meters_per_second()
      print(f"转换为立方米每秒: {flow_cms}")

      # 不同单位的流量
      flow_lps = FlowRate(1000.0, "L/s")
      flow_cms_converted = flow_lps.to_cubic_meters_per_second()
      print(f"1000 L/s = {flow_cms_converted} m³/s")

WaterLevel
^^^^^^^^^^

.. autoclass:: WaterLevel
   :members:
   :undoc-members:
   :show-inheritance:

   水位数据类型，用于表示水位高度信息。

   **特性：**

   - 支持多种长度单位（m, cm, mm, ft）
   - 支持不同参考基准（海平面、库底、地面）
   - 包含时间戳信息
   - 提供单位转换方法

   **使用示例：**

   .. code-block:: python

      from chs_core_api import WaterLevel
      from datetime import datetime

      # 创建水位对象
      level = WaterLevel(
          value=125.5, 
          unit="m", 
          reference="sea_level",
          timestamp=datetime.now()
      )
      print(f"水位: {level.value} {level.unit} (参考: {level.reference})")

      # 单位转换
      level_meters = level.to_meters()
      print(f"转换为米: {level_meters}")

      # 不同参考基准的水位
      reservoir_level = WaterLevel(45.0, "m", "reservoir_bottom")
      print(f"库底以上水位: {reservoir_level.value} {reservoir_level.unit}")

ControlSignal
^^^^^^^^^^^^^

.. autoclass:: ControlSignal
   :members:
   :undoc-members:
   :show-inheritance:

   控制信号数据类型，用于表示发送给设备的控制指令。

   **特性：**

   - 支持多种信号类型（开关、模拟、数字、命令）
   - 灵活的信号值类型（数值、布尔、字符串）
   - 优先级管理
   - 时间戳记录

   **使用示例：**

   .. code-block:: python

      from chs_core_api import ControlSignal
      from datetime import datetime

      # 开关信号
      switch_signal = ControlSignal(
          signal_type="switch",
          value=True,
          timestamp=datetime.now(),
          priority=5
      )

      # 模拟信号
      analog_signal = ControlSignal(
          signal_type="analog",
          value=75.5,
          unit="%",
          timestamp=datetime.now(),
          priority=3
      )

      # 命令信号
      command_signal = ControlSignal(
          signal_type="command",
          value="start_pump",
          timestamp=datetime.now(),
          priority=8
      )

状态和枚举类型
--------------

ComponentStatus
^^^^^^^^^^^^^^^

.. autoclass:: ComponentStatus
   :members:
   :undoc-members:
   :show-inheritance:

   组件状态枚举，定义了组件的标准运行状态。

   **状态值：**

   - ``OFFLINE``: 离线状态
   - ``ONLINE``: 在线状态
   - ``MAINTENANCE``: 维护状态
   - ``ERROR``: 错误状态
   - ``UNKNOWN``: 未知状态

   **使用示例：**

   .. code-block:: python

      from chs_core_api import ComponentStatus

      # 设置组件状态
      status = ComponentStatus.ONLINE
      print(f"组件状态: {status.value}")

      # 状态判断
      if status == ComponentStatus.ONLINE:
          print("组件正常运行")
      elif status == ComponentStatus.MAINTENANCE:
          print("组件正在维护")

AlarmLevel
^^^^^^^^^^

.. autoclass:: AlarmLevel
   :members:
   :undoc-members:
   :show-inheritance:

   报警级别枚举，定义了系统报警的严重程度。

   **级别值：**

   - ``INFO``: 信息级别
   - ``WARNING``: 警告级别
   - ``CRITICAL``: 严重级别
   - ``EMERGENCY``: 紧急级别

复合数据类型
------------

ComponentState
^^^^^^^^^^^^^^

.. autoclass:: ComponentState
   :members:
   :undoc-members:
   :show-inheritance:

   组件状态信息，包含组件的完整状态数据。

   **使用示例：**

   .. code-block:: python

      from chs_core_api import ComponentState, ComponentStatus
      from datetime import datetime

      # 创建组件状态
      state = ComponentState(
          component_id="PUMP001",
          status=ComponentStatus.ONLINE,
          health_score=95.5,
          last_update=datetime.now(),
          parameters={
              "flow_rate": 150.0,
              "pressure": 2.5,
              "temperature": 45.0
          },
          alarms=[
              {
                  "level": "warning",
                  "message": "温度偏高",
                  "timestamp": datetime.now()
              }
          ]
      )

      print(f"组件 {state.component_id} 健康度: {state.health_score}%")
      print(f"报警数量: {len(state.alarms)}")

Measurement
^^^^^^^^^^^

.. autoclass:: Measurement
   :members:
   :undoc-members:
   :show-inheritance:

   测量数据类型，表示传感器或设备的测量值。

   **使用示例：**

   .. code-block:: python

      from chs_core_api import Measurement
      from datetime import datetime

      # 创建测量数据
      measurement = Measurement(
          sensor_id="TEMP001",
          parameter="temperature",
          value=25.5,
          unit="°C",
          timestamp=datetime.now(),
          quality=0.95,
          uncertainty=0.1
      )

      print(f"传感器 {measurement.sensor_id}:")
      print(f"  参数: {measurement.parameter}")
      print(f"  值: {measurement.value} {measurement.unit}")
      print(f"  质量: {measurement.quality * 100}%")
      print(f"  不确定度: ±{measurement.uncertainty}")

TimeSeriesData
^^^^^^^^^^^^^^

.. autoclass:: TimeSeriesData
   :members:
   :undoc-members:
   :show-inheritance:

   时间序列数据类型，表示一组按时间排序的测量数据。

   **使用示例：**

   .. code-block:: python

      from chs_core_api import TimeSeriesData
      from datetime import datetime, timedelta

      # 生成时间序列
      base_time = datetime.now()
      timestamps = [base_time + timedelta(minutes=i) for i in range(10)]
      values = [20.0 + i * 0.5 for i in range(10)]

      # 创建时间序列数据
      ts_data = TimeSeriesData(
          parameter="temperature",
          unit="°C",
          timestamps=timestamps,
          values=values,
          metadata={
              "sensor_id": "TEMP001",
              "location": "入水口",
              "sampling_rate": "1分钟"
          }
      )

      print(f"参数: {ts_data.parameter}")
      print(f"数据点数: {len(ts_data.values)}")
      print(f"时间范围: {ts_data.timestamps[0]} 到 {ts_data.timestamps[-1]}")

SimulationResult
^^^^^^^^^^^^^^^^

.. autoclass:: SimulationResult
   :members:
   :undoc-members:
   :show-inheritance:

   仿真结果类型，包含仿真运行的完整结果。

   **使用示例：**

   .. code-block:: python

      from chs_core_api import SimulationResult, TimeSeriesData
      from datetime import datetime, timedelta

      # 创建仿真结果
      start_time = datetime.now()
      end_time = start_time + timedelta(hours=1)

      result = SimulationResult(
          simulation_id="SIM_20240101_001",
          start_time=start_time,
          end_time=end_time,
          duration=3600.0,
          time_step=1.0,
          components_data={
              "RESERVOIR001": TimeSeriesData(
                  parameter="water_level",
                  unit="m",
                  timestamps=[start_time + timedelta(seconds=i) for i in range(0, 3601, 60)],
                  values=[125.0 + 0.01 * i for i in range(61)],
                  metadata={"component_type": "reservoir"}
              )
          },
          summary_statistics={
              "max_water_level": 125.6,
              "min_water_level": 125.0,
              "avg_flow_rate": 15.5
          },
          convergence_info={
              "converged": True,
              "iterations": 150,
              "final_error": 1e-8
          },
          warnings=[],
          errors=[]
      )

      print(f"仿真 {result.simulation_id}:")
      print(f"  成功: {result.is_successful}")
      print(f"  执行时间: {result.execution_time:.2f} 秒")
      print(f"  组件数据: {len(result.components_data)} 个组件")

配置和响应类型
--------------

ConfigurationSchema
^^^^^^^^^^^^^^^^^^^

.. autoclass:: ConfigurationSchema
   :members:
   :undoc-members:
   :show-inheritance:

   配置模式定义，用于定义和验证配置文件的结构。

   **使用示例：**

   .. code-block:: python

      from chs_core_api import ConfigurationSchema

      # 定义配置模式
      schema = ConfigurationSchema(
          name="simulation_config",
          version="1.0",
          schema={
              "type": "object",
              "properties": {
                  "duration": {"type": "number", "minimum": 0},
                  "time_step": {"type": "number", "minimum": 0.001},
                  "components": {"type": "array"}
              }
          },
          default_values={
              "duration": 3600,
              "time_step": 1.0,
              "components": []
          },
          required_fields=["duration", "time_step"]
      )

      # 验证配置
      config = {"duration": 7200, "time_step": 0.5}
      is_valid = schema.validate_config(config)
      print(f"配置有效性: {is_valid}")

APIResponse
^^^^^^^^^^^

.. autoclass:: APIResponse
   :members:
   :undoc-members:
   :show-inheritance:

   标准化的API响应格式，用于统一API返回结果。

   **使用示例：**

   .. code-block:: python

      from chs_core_api import APIResponse
      from datetime import datetime

      # 成功响应
      success_response = APIResponse(
          success=True,
          data={"component_id": "PUMP001", "status": "online"},
          message="组件状态获取成功"
      )

      # 错误响应
      error_response = APIResponse(
          success=False,
          data=None,
          message="组件未找到",
          error_code="COMPONENT_NOT_FOUND"
      )

      print(f"成功: {success_response.success}")
      print(f"消息: {success_response.message}")
      print(f"时间戳: {success_response.timestamp}")

类型别名
--------

为了简化代码编写，CHS-Core API 提供了一些常用的类型别名：

.. currentmodule:: chs_core_api.types

.. autodata:: ComponentID
   :annotation: = str

   组件标识符的类型别名。

.. autodata:: ParameterName
   :annotation: = str

   参数名称的类型别名。

.. autodata:: Timestamp
   :annotation: = datetime

   时间戳的类型别名。

.. autodata:: NumericValue
   :annotation: = Union[int, float]

   数值类型的别名，可以是整数或浮点数。

.. autodata:: ConfigDict
   :annotation: = Dict[str, Any]

   配置字典的类型别名。

.. autodata:: MetadataDict
   :annotation: = Dict[str, Any]

   元数据字典的类型别名。

**使用示例：**

.. code-block:: python

   from chs_core_api.types import ComponentID, ParameterName, ConfigDict

   def get_component_parameter(component_id: ComponentID, 
                              parameter: ParameterName) -> float:
       # 获取组件参数的函数
       pass

   def load_configuration(config: ConfigDict) -> bool:
       # 加载配置的函数
       pass

类型验证和转换
--------------

所有数据类型都包含内置的验证机制，确保数据的有效性：

1. **范围验证**
   - 流量值不能为负数
   - 健康度评分必须在0-100之间
   - 优先级必须在1-10之间

2. **单位验证**
   - 检查单位是否在支持的列表中
   - 自动进行单位转换

3. **格式验证**
   - 检查必填字段
   - 验证数据类型
   - 检查数据结构

4. **一致性验证**
   - 时间戳和数值列表长度一致
   - 参考基准的有效性

**最佳实践：**

1. **使用类型提示**
   在函数签名中使用明确的类型提示。

2. **数据验证**
   在处理外部数据时进行适当的验证。

3. **单位一致性**
   在系统内部使用统一的单位系统。

4. **错误处理**
   对类型验证错误进行适当的处理。

5. **文档化**
   为自定义类型提供清晰的文档说明。