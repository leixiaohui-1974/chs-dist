"""CHS-Core API 接口包

本包包含 CHS-Core 的公共 API 接口定义，
允许其他团队基于稳定的接口进行开发，
而无需访问具体的实现细节。

主要功能：
- 水力系统组件接口定义
- 数据处理器接口规范
- 仿真引擎接口标准
- 配置管理接口协议
- 统一的类型定义和异常处理

使用方式：
    from chs_core_api import WaterSystemComponent, DataProcessor
    from chs_core_api.types import FlowRate, WaterLevel
    
    class MyComponent(WaterSystemComponent):
        def get_flow_rate(self) -> FlowRate:
            # 实现接口方法
            pass
"""

__version__ = "0.1.0"
__author__ = "CHS Development Team"

# 导入接口定义
from .interfaces import (
    WaterSystemComponent,
    ReservoirInterface,
    PumpInterface,
    DataProcessor,
    AnomalyDetectorInterface,
    SimulationEngine,
    ConfigurationManager,
)

# 导入类型定义
from .types import (
    FlowRate,
    WaterLevel,
    ControlSignal,
    ComponentState,
    ComponentStatus,
    AlarmLevel,
    Measurement,
    TimeSeriesData,
    SimulationResult,
    ConfigurationSchema,
    APIResponse,
    ComponentID,
    ParameterName,
    Timestamp,
    NumericValue,
    ConfigDict,
    MetadataDict,
)

# 导入异常定义
from .exceptions import (
    CHSCoreException,
    ComponentException,
    ComponentNotFoundError,
    ComponentStateError,
    ComponentConfigurationError,
    DataProcessingException,
    DataValidationError,
    DataFormatError,
    AnomalyDetectionError,
    SimulationException,
    SimulationInitializationError,
    SimulationConvergenceError,
    SimulationTimeoutError,
    ConfigurationException,
    ConfigurationLoadError,
    ConfigurationValidationError,
    ConfigurationSaveError,
    NetworkException,
    ConnectionError,
    APIError,
)

# 导出公共API
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    
    # 接口定义
    "WaterSystemComponent",
    "ReservoirInterface",
    "PumpInterface",
    "DataProcessor",
    "AnomalyDetectorInterface",
    "SimulationEngine",
    "ConfigurationManager",
    
    # 类型定义
    "FlowRate",
    "WaterLevel",
    "ControlSignal",
    "ComponentState",
    "ComponentStatus",
    "AlarmLevel",
    "Measurement",
    "TimeSeriesData",
    "SimulationResult",
    "ConfigurationSchema",
    "APIResponse",
    "ComponentID",
    "ParameterName",
    "Timestamp",
    "NumericValue",
    "ConfigDict",
    "MetadataDict",
    
    # 异常定义
    "CHSCoreException",
    "ComponentException",
    "ComponentNotFoundError",
    "ComponentStateError",
    "ComponentConfigurationError",
    "DataProcessingException",
    "DataValidationError",
    "DataFormatError",
    "AnomalyDetectionError",
    "SimulationException",
    "SimulationInitializationError",
    "SimulationConvergenceError",
    "SimulationTimeoutError",
    "ConfigurationException",
    "ConfigurationLoadError",
    "ConfigurationValidationError",
    "ConfigurationSaveError",
    "NetworkException",
    "ConnectionError",
    "APIError",
]