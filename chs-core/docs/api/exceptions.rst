异常处理
========

CHS-Core API 提供了一套完整的异常处理体系，用于标准化错误处理和异常管理。这些异常类确保了不同组件之间的错误处理一致性和可预测性。

异常概览
--------

.. currentmodule:: chs_core_api.exceptions

.. autosummary::
   :toctree: generated/
   :nosignatures:

   CHSCoreException
   ComponentException
   ComponentNotFoundError
   ComponentConnectionError
   ComponentConfigurationError
   DataProcessingException
   DataValidationError
   DataFormatError
   DataSourceError
   SimulationException
   SimulationConvergenceError
   SimulationTimeoutError
   SimulationParameterError
   ConfigurationException
   ConfigurationValidationError
   ConfigurationFileError
   NetworkException
   APIException
   AuthenticationError
   AuthorizationError

基础异常类
----------

CHSCoreException
^^^^^^^^^^^^^^^^

.. autoclass:: CHSCoreException
   :members:
   :undoc-members:
   :show-inheritance:

   CHS-Core 系统的基础异常类，所有其他异常都继承自此类。

   **特性：**

   - 提供统一的错误代码机制
   - 支持详细的错误信息
   - 包含时间戳记录
   - 支持错误上下文信息

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import CHSCoreException

      try:
          # 某些可能出错的操作
          pass
      except CHSCoreException as e:
          print(f"CHS-Core 错误: {e.message}")
          print(f"错误代码: {e.error_code}")
          print(f"发生时间: {e.timestamp}")
          if e.context:
              print(f"上下文: {e.context}")

组件相关异常
------------

ComponentException
^^^^^^^^^^^^^^^^^^

.. autoclass:: ComponentException
   :members:
   :undoc-members:
   :show-inheritance:

   组件相关异常的基类，用于处理组件操作中的各种错误。

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import ComponentException

      def operate_component(component_id: str):
          try:
              # 组件操作代码
              pass
          except ComponentException as e:
              print(f"组件 {e.component_id} 操作失败: {e.message}")
              # 记录错误日志
              logger.error(f"组件异常: {e}")

ComponentNotFoundError
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ComponentNotFoundError
   :members:
   :undoc-members:
   :show-inheritance:

   当请求的组件不存在时抛出的异常。

   **使用场景：**

   - 通过ID查找组件时组件不存在
   - 尝试访问已删除的组件
   - 组件配置中引用了不存在的组件

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import ComponentNotFoundError

      def get_component(component_id: str):
          if component_id not in components_registry:
              raise ComponentNotFoundError(
                  f"组件 {component_id} 未找到",
                  component_id=component_id,
                  error_code="COMPONENT_NOT_FOUND"
              )
          return components_registry[component_id]

      try:
          component = get_component("PUMP999")
      except ComponentNotFoundError as e:
          print(f"错误: {e.message}")
          print(f"组件ID: {e.component_id}")

ComponentConnectionError
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ComponentConnectionError
   :members:
   :undoc-members:
   :show-inheritance:

   当组件连接失败时抛出的异常。

   **使用场景：**

   - 网络连接中断
   - 设备通信失败
   - 协议不匹配

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import ComponentConnectionError
      import socket

      def connect_to_component(component_id: str, host: str, port: int):
          try:
              sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              sock.connect((host, port))
              return sock
          except socket.error as e:
              raise ComponentConnectionError(
                  f"无法连接到组件 {component_id}",
                  component_id=component_id,
                  error_code="CONNECTION_FAILED",
                  context={"host": host, "port": port, "original_error": str(e)}
              )

ComponentConfigurationError
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ComponentConfigurationError
   :members:
   :undoc-members:
   :show-inheritance:

   当组件配置错误时抛出的异常。

   **使用场景：**

   - 配置参数无效
   - 必需参数缺失
   - 配置值超出范围

数据处理异常
------------

DataProcessingException
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: DataProcessingException
   :members:
   :undoc-members:
   :show-inheritance:

   数据处理相关异常的基类。

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import DataProcessingException

      def process_sensor_data(data):
          try:
              # 数据处理逻辑
              processed_data = complex_processing(data)
              return processed_data
          except DataProcessingException as e:
              print(f"数据处理失败: {e.message}")
              print(f"数据源: {e.data_source}")
              # 返回默认值或重新处理
              return handle_processing_error(e)

DataValidationError
^^^^^^^^^^^^^^^^^^^

.. autoclass:: DataValidationError
   :members:
   :undoc-members:
   :show-inheritance:

   当数据验证失败时抛出的异常。

   **使用场景：**

   - 数据格式不正确
   - 数值超出有效范围
   - 必填字段缺失
   - 数据类型不匹配

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import DataValidationError
      from chs_core_api.types import FlowRate

      def validate_flow_rate(value: float, unit: str) -> FlowRate:
          if value < 0:
              raise DataValidationError(
                  "流量值不能为负数",
                  data_source="flow_sensor",
                  error_code="INVALID_FLOW_VALUE",
                  context={"value": value, "unit": unit}
              )
          
          if unit not in ["m³/s", "L/s", "m³/h", "L/min"]:
              raise DataValidationError(
                  f"不支持的流量单位: {unit}",
                  data_source="flow_sensor",
                  error_code="INVALID_UNIT",
                  context={"unit": unit, "supported_units": ["m³/s", "L/s", "m³/h", "L/min"]}
              )
          
          return FlowRate(value=value, unit=unit)

DataFormatError
^^^^^^^^^^^^^^^

.. autoclass:: DataFormatError
   :members:
   :undoc-members:
   :show-inheritance:

   当数据格式错误时抛出的异常。

   **使用场景：**

   - JSON 解析失败
   - CSV 格式错误
   - 时间戳格式不正确
   - 编码问题

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import DataFormatError
      import json

      def parse_sensor_data(json_string: str):
          try:
              data = json.loads(json_string)
              return data
          except json.JSONDecodeError as e:
              raise DataFormatError(
                  "JSON 数据格式错误",
                  data_source="sensor_api",
                  error_code="JSON_PARSE_ERROR",
                  context={"original_error": str(e), "position": e.pos}
              )

DataSourceError
^^^^^^^^^^^^^^^

.. autoclass:: DataSourceError
   :members:
   :undoc-members:
   :show-inheritance:

   当数据源访问失败时抛出的异常。

   **使用场景：**

   - 数据库连接失败
   - 文件读取错误
   - API 调用失败
   - 网络超时

仿真异常
--------

SimulationException
^^^^^^^^^^^^^^^^^^^

.. autoclass:: SimulationException
   :members:
   :undoc-members:
   :show-inheritance:

   仿真相关异常的基类。

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import SimulationException

      def run_simulation(simulation_id: str, parameters: dict):
          try:
              # 仿真执行逻辑
              result = execute_simulation(parameters)
              return result
          except SimulationException as e:
              print(f"仿真 {e.simulation_id} 执行失败: {e.message}")
              # 清理资源
              cleanup_simulation_resources(e.simulation_id)
              raise

SimulationConvergenceError
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: SimulationConvergenceError
   :members:
   :undoc-members:
   :show-inheritance:

   当仿真无法收敛时抛出的异常。

   **使用场景：**

   - 数值求解不收敛
   - 迭代次数超过限制
   - 误差超出容忍范围

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import SimulationConvergenceError

      def solve_hydraulic_equations(equations, max_iterations=1000, tolerance=1e-6):
          for iteration in range(max_iterations):
              solution = iterate_solution(equations)
              error = calculate_error(solution)
              
              if error < tolerance:
                  return solution
          
          raise SimulationConvergenceError(
              "水力方程求解未收敛",
              simulation_id="hydraulic_solver",
              error_code="CONVERGENCE_FAILED",
              context={
                  "iterations": max_iterations,
                  "final_error": error,
                  "tolerance": tolerance
              }
          )

SimulationTimeoutError
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: SimulationTimeoutError
   :members:
   :undoc-members:
   :show-inheritance:

   当仿真执行超时时抛出的异常。

   **使用场景：**

   - 仿真执行时间过长
   - 系统资源不足
   - 计算复杂度过高

SimulationParameterError
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: SimulationParameterError
   :members:
   :undoc-members:
   :show-inheritance:

   当仿真参数错误时抛出的异常。

   **使用场景：**

   - 参数值超出有效范围
   - 必需参数缺失
   - 参数组合无效

配置异常
--------

ConfigurationException
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ConfigurationException
   :members:
   :undoc-members:
   :show-inheritance:

   配置相关异常的基类。

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import ConfigurationException

      def load_system_configuration(config_path: str):
          try:
              config = parse_configuration_file(config_path)
              validate_configuration(config)
              return config
          except ConfigurationException as e:
              print(f"配置加载失败: {e.message}")
              print(f"配置文件: {e.config_path}")
              # 使用默认配置
              return get_default_configuration()

ConfigurationValidationError
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ConfigurationValidationError
   :members:
   :undoc-members:
   :show-inheritance:

   当配置验证失败时抛出的异常。

   **使用场景：**

   - 配置格式不正确
   - 必需配置项缺失
   - 配置值类型错误
   - 配置值超出范围

ConfigurationFileError
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ConfigurationFileError
   :members:
   :undoc-members:
   :show-inheritance:

   当配置文件操作失败时抛出的异常。

   **使用场景：**

   - 配置文件不存在
   - 文件权限不足
   - 文件格式错误
   - 文件损坏

网络和API异常
-------------

NetworkException
^^^^^^^^^^^^^^^^

.. autoclass:: NetworkException
   :members:
   :undoc-members:
   :show-inheritance:

   网络相关异常的基类。

   **使用示例：**

   .. code-block:: python

      from chs_core_api.exceptions import NetworkException
      import requests

      def call_external_api(url: str, data: dict):
          try:
              response = requests.post(url, json=data, timeout=30)
              response.raise_for_status()
              return response.json()
          except requests.RequestException as e:
              raise NetworkException(
                  f"API 调用失败: {url}",
                  error_code="API_CALL_FAILED",
                  context={"url": url, "original_error": str(e)}
              )

APIException
^^^^^^^^^^^^

.. autoclass:: APIException
   :members:
   :undoc-members:
   :show-inheritance:

   API 相关异常的基类。

   **使用场景：**

   - API 调用失败
   - 响应格式错误
   - 服务不可用
   - 请求限制

AuthenticationError
^^^^^^^^^^^^^^^^^^^

.. autoclass:: AuthenticationError
   :members:
   :undoc-members:
   :show-inheritance:

   当身份验证失败时抛出的异常。

   **使用场景：**

   - 用户名或密码错误
   - 令牌过期
   - 证书无效

AuthorizationError
^^^^^^^^^^^^^^^^^^

.. autoclass:: AuthorizationError
   :members:
   :undoc-members:
   :show-inheritance:

   当权限验证失败时抛出的异常。

   **使用场景：**

   - 用户权限不足
   - 资源访问被拒绝
   - 操作未授权

异常处理最佳实践
----------------

1. **异常层次结构**

   使用适当的异常层次结构，从最具体的异常开始捕获：

   .. code-block:: python

      from chs_core_api.exceptions import (
          ComponentNotFoundError,
          ComponentConnectionError,
          ComponentException,
          CHSCoreException
      )

      try:
          component = get_component("PUMP001")
          component.connect()
          component.start()
      except ComponentNotFoundError as e:
          # 处理组件未找到
          logger.error(f"组件未找到: {e.component_id}")
          return create_error_response("COMPONENT_NOT_FOUND", str(e))
      except ComponentConnectionError as e:
          # 处理连接错误
          logger.warning(f"组件连接失败: {e.component_id}")
          return create_error_response("CONNECTION_FAILED", str(e))
      except ComponentException as e:
          # 处理其他组件异常
          logger.error(f"组件异常: {e.component_id} - {e.message}")
          return create_error_response("COMPONENT_ERROR", str(e))
      except CHSCoreException as e:
          # 处理系统级异常
          logger.critical(f"系统异常: {e.error_code} - {e.message}")
          return create_error_response("SYSTEM_ERROR", str(e))

2. **错误上下文信息**

   提供丰富的上下文信息以便调试：

   .. code-block:: python

      from chs_core_api.exceptions import DataValidationError

      def validate_measurement_data(data: dict):
          required_fields = ["sensor_id", "value", "timestamp"]
          missing_fields = [field for field in required_fields if field not in data]
          
          if missing_fields:
              raise DataValidationError(
                  "测量数据缺少必需字段",
                  data_source="sensor_input",
                  error_code="MISSING_REQUIRED_FIELDS",
                  context={
                      "missing_fields": missing_fields,
                      "required_fields": required_fields,
                      "provided_data": data
                  }
              )

3. **异常链和原因**

   保留原始异常信息：

   .. code-block:: python

      from chs_core_api.exceptions import DataSourceError
      import sqlite3

      def query_database(query: str):
          try:
              conn = sqlite3.connect("data.db")
              cursor = conn.cursor()
              cursor.execute(query)
              return cursor.fetchall()
          except sqlite3.Error as e:
              raise DataSourceError(
                  "数据库查询失败",
                  data_source="sqlite_database",
                  error_code="DATABASE_QUERY_ERROR",
                  context={"query": query, "original_error": str(e)}
              ) from e

4. **日志记录**

   结合异常处理进行适当的日志记录：

   .. code-block:: python

      import logging
      from chs_core_api.exceptions import SimulationException

      logger = logging.getLogger(__name__)

      def run_simulation_with_logging(simulation_id: str):
          try:
              logger.info(f"开始仿真: {simulation_id}")
              result = run_simulation(simulation_id)
              logger.info(f"仿真完成: {simulation_id}")
              return result
          except SimulationException as e:
              logger.error(
                  f"仿真失败: {simulation_id}",
                  extra={
                      "simulation_id": e.simulation_id,
                      "error_code": e.error_code,
                      "context": e.context
                  }
              )
              raise

5. **错误恢复策略**

   实现适当的错误恢复机制：

   .. code-block:: python

      from chs_core_api.exceptions import ComponentConnectionError
      import time

      def connect_with_retry(component_id: str, max_retries: int = 3):
          for attempt in range(max_retries):
              try:
                  return connect_to_component(component_id)
              except ComponentConnectionError as e:
                  if attempt == max_retries - 1:
                      # 最后一次尝试失败，重新抛出异常
                      raise
                  
                  logger.warning(
                      f"连接失败，{2**attempt} 秒后重试 (尝试 {attempt + 1}/{max_retries}): {e.message}"
                  )
                  time.sleep(2**attempt)  # 指数退避

6. **异常文档化**

   在函数文档中明确说明可能抛出的异常：

   .. code-block:: python

      def process_sensor_data(sensor_id: str, data: dict) -> ProcessedData:
          """
          处理传感器数据。

          Args:
              sensor_id: 传感器标识符
              data: 原始传感器数据

          Returns:
              ProcessedData: 处理后的数据

          Raises:
              ComponentNotFoundError: 当传感器不存在时
              DataValidationError: 当数据格式无效时
              DataProcessingException: 当数据处理失败时
          """
          pass

通过遵循这些最佳实践，可以构建一个健壮、可维护的异常处理体系，提高系统的可靠性和可调试性。