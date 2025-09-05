"""CHS-Core 类型定义

本模块定义了 CHS-Core 系统中使用的所有数据类型，
包括基础数据类型、复合类型和枚举类型。

这些类型定义为跨团队协作提供了统一的数据契约。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


# 基础数值类型
@dataclass
class FlowRate:
    """流量类型
    
    表示水流的流量，包含数值和单位信息。
    """
    value: float  # 流量数值
    unit: str = "m³/s"  # 单位，默认为立方米每秒
    timestamp: Optional[datetime] = None  # 测量时间戳
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("流量值不能为负数")
        if self.unit not in ["m³/s", "L/s", "m³/h", "L/min"]:
            raise ValueError(f"不支持的流量单位: {self.unit}")
    
    def to_cubic_meters_per_second(self) -> float:
        """转换为立方米每秒
        
        Returns:
            float: 以立方米每秒为单位的流量值
        """
        conversion_factors = {
            "m³/s": 1.0,
            "L/s": 0.001,
            "m³/h": 1/3600,
            "L/min": 0.001/60
        }
        return self.value * conversion_factors[self.unit]


@dataclass
class WaterLevel:
    """水位类型
    
    表示水位高度，包含数值和参考基准信息。
    """
    value: float  # 水位数值
    unit: str = "m"  # 单位，默认为米
    reference: str = "sea_level"  # 参考基准（海平面、库底等）
    timestamp: Optional[datetime] = None  # 测量时间戳
    
    def __post_init__(self):
        if self.unit not in ["m", "cm", "mm", "ft"]:
            raise ValueError(f"不支持的水位单位: {self.unit}")
        if self.reference not in ["sea_level", "reservoir_bottom", "ground_level"]:
            raise ValueError(f"不支持的参考基准: {self.reference}")
    
    def to_meters(self) -> float:
        """转换为米
        
        Returns:
            float: 以米为单位的水位值
        """
        conversion_factors = {
            "m": 1.0,
            "cm": 0.01,
            "mm": 0.001,
            "ft": 0.3048
        }
        return self.value * conversion_factors[self.unit]


@dataclass
class ControlSignal:
    """控制信号类型
    
    表示发送给设备的控制指令。
    """
    signal_type: str  # 信号类型（开关、调节等）
    value: Union[float, bool, str]  # 信号值
    unit: Optional[str] = None  # 单位（如果适用）
    timestamp: Optional[datetime] = None  # 发送时间戳
    priority: int = 1  # 优先级（1-10，10最高）
    
    def __post_init__(self):
        if self.signal_type not in ["switch", "analog", "digital", "command"]:
            raise ValueError(f"不支持的信号类型: {self.signal_type}")
        if not 1 <= self.priority <= 10:
            raise ValueError("优先级必须在1-10之间")


class ComponentStatus(Enum):
    """组件状态枚举"""
    OFFLINE = "offline"  # 离线
    ONLINE = "online"  # 在线
    MAINTENANCE = "maintenance"  # 维护中
    ERROR = "error"  # 错误状态
    UNKNOWN = "unknown"  # 未知状态


class AlarmLevel(Enum):
    """报警级别枚举"""
    INFO = "info"  # 信息
    WARNING = "warning"  # 警告
    CRITICAL = "critical"  # 严重
    EMERGENCY = "emergency"  # 紧急


@dataclass
class ComponentState:
    """组件状态信息
    
    包含组件的完整状态信息。
    """
    component_id: str  # 组件ID
    status: ComponentStatus  # 运行状态
    health_score: float  # 健康度评分（0-100）
    last_update: datetime  # 最后更新时间
    parameters: Dict[str, Any]  # 状态参数
    alarms: List[Dict[str, Any]]  # 报警信息
    
    def __post_init__(self):
        if not 0 <= self.health_score <= 100:
            raise ValueError("健康度评分必须在0-100之间")


@dataclass
class Measurement:
    """测量数据类型
    
    表示传感器或设备的测量值。
    """
    sensor_id: str  # 传感器ID
    parameter: str  # 测量参数名称
    value: float  # 测量值
    unit: str  # 单位
    timestamp: datetime  # 测量时间
    quality: float = 1.0  # 数据质量（0-1）
    uncertainty: Optional[float] = None  # 测量不确定度
    
    def __post_init__(self):
        if not 0 <= self.quality <= 1:
            raise ValueError("数据质量必须在0-1之间")
        if self.uncertainty is not None and self.uncertainty < 0:
            raise ValueError("测量不确定度不能为负数")


@dataclass
class TimeSeriesData:
    """时间序列数据类型
    
    表示一组按时间排序的测量数据。
    """
    parameter: str  # 参数名称
    unit: str  # 单位
    timestamps: List[datetime]  # 时间戳列表
    values: List[float]  # 数值列表
    metadata: Dict[str, Any]  # 元数据
    
    def __post_init__(self):
        if len(self.timestamps) != len(self.values):
            raise ValueError("时间戳和数值列表长度必须相等")
        if len(self.timestamps) == 0:
            raise ValueError("时间序列数据不能为空")


@dataclass
class SimulationResult:
    """仿真结果类型
    
    包含仿真运行的完整结果。
    """
    simulation_id: str  # 仿真ID
    start_time: datetime  # 开始时间
    end_time: datetime  # 结束时间
    duration: float  # 仿真时长（秒）
    time_step: float  # 时间步长（秒）
    components_data: Dict[str, TimeSeriesData]  # 各组件的时间序列数据
    summary_statistics: Dict[str, Any]  # 汇总统计信息
    convergence_info: Dict[str, Any]  # 收敛信息
    warnings: List[str]  # 警告信息
    errors: List[str]  # 错误信息
    
    @property
    def is_successful(self) -> bool:
        """判断仿真是否成功
        
        Returns:
            bool: 仿真是否成功完成
        """
        return len(self.errors) == 0
    
    @property
    def execution_time(self) -> float:
        """获取实际执行时间
        
        Returns:
            float: 执行时间（秒）
        """
        return (self.end_time - self.start_time).total_seconds()


@dataclass
class ConfigurationSchema:
    """配置模式定义
    
    定义配置文件的结构和验证规则。
    """
    name: str  # 配置名称
    version: str  # 版本号
    schema: Dict[str, Any]  # JSON Schema定义
    default_values: Dict[str, Any]  # 默认值
    required_fields: List[str]  # 必填字段
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否符合模式
        
        Args:
            config: 待验证的配置
            
        Returns:
            bool: 配置是否有效
        """
        # 检查必填字段
        for field in self.required_fields:
            if field not in config:
                return False
        
        # 这里可以添加更复杂的验证逻辑
        return True


@dataclass
class APIResponse:
    """API响应类型
    
    标准化的API响应格式。
    """
    success: bool  # 是否成功
    data: Any  # 响应数据
    message: str  # 响应消息
    error_code: Optional[str] = None  # 错误代码
    timestamp: datetime = None  # 响应时间戳
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# 常用的类型别名
ComponentID = str
ParameterName = str
Timestamp = datetime
NumericValue = Union[int, float]
ConfigDict = Dict[str, Any]
MetadataDict = Dict[str, Any]