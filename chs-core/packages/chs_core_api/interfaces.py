"""CHS-Core 核心接口定义

本模块定义了 CHS-Core 系统的核心接口，包括：
- 水力系统组件接口
- 数据处理器接口
- 仿真引擎接口
- 配置管理接口

这些接口为跨团队协作提供了稳定的契约。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from .types import FlowRate, WaterLevel, ControlSignal, ComponentState, SimulationResult


class WaterSystemComponent(ABC):
    """水力系统组件基础接口
    
    所有水力系统组件（水库、泵站、阀门等）都应实现此接口。
    提供统一的组件操作和状态管理方法。
    """
    
    @abstractmethod
    def get_component_id(self) -> str:
        """获取组件唯一标识符
        
        Returns:
            str: 组件ID
        """
        pass
    
    @abstractmethod
    def get_flow_rate(self) -> FlowRate:
        """获取当前流量
        
        Returns:
            FlowRate: 当前流量值
        """
        pass
    
    @abstractmethod
    def set_control_signal(self, signal: ControlSignal) -> None:
        """设置控制信号
        
        Args:
            signal: 控制信号值
        """
        pass
    
    @abstractmethod
    def get_state(self) -> ComponentState:
        """获取组件当前状态
        
        Returns:
            ComponentState: 组件状态信息
        """
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """更新组件状态
        
        Args:
            dt: 时间步长（秒）
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """重置组件到初始状态"""
        pass


class ReservoirInterface(WaterSystemComponent):
    """水库组件接口
    
    定义水库特有的操作方法。
    """
    
    @abstractmethod
    def get_water_level(self) -> WaterLevel:
        """获取当前水位
        
        Returns:
            WaterLevel: 当前水位值
        """
        pass
    
    @abstractmethod
    def get_capacity(self) -> float:
        """获取水库容量
        
        Returns:
            float: 水库总容量（立方米）
        """
        pass
    
    @abstractmethod
    def set_inflow(self, rate: FlowRate) -> None:
        """设置入流量
        
        Args:
            rate: 入流量值
        """
        pass
    
    @abstractmethod
    def calculate_outflow(self) -> FlowRate:
        """计算出流量
        
        Returns:
            FlowRate: 计算得出的出流量
        """
        pass


class PumpInterface(WaterSystemComponent):
    """泵站组件接口
    
    定义泵站特有的操作方法。
    """
    
    @abstractmethod
    def get_pump_efficiency(self) -> float:
        """获取泵站效率
        
        Returns:
            float: 泵站效率（0-1之间）
        """
        pass
    
    @abstractmethod
    def set_pump_speed(self, speed: float) -> None:
        """设置泵站转速
        
        Args:
            speed: 转速（转/分钟）
        """
        pass
    
    @abstractmethod
    def get_power_consumption(self) -> float:
        """获取功耗
        
        Returns:
            float: 当前功耗（千瓦）
        """
        pass


class DataProcessor(ABC):
    """数据处理器接口
    
    定义数据处理的标准方法，包括清洗、分析、异常检测等。
    """
    
    @abstractmethod
    def process_data(self, data: Any) -> Any:
        """处理数据
        
        Args:
            data: 输入数据
            
        Returns:
            Any: 处理后的数据
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Any) -> bool:
        """验证数据有效性
        
        Args:
            data: 待验证的数据
            
        Returns:
            bool: 数据是否有效
        """
        pass
    
    @abstractmethod
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        pass


class AnomalyDetectorInterface(DataProcessor):
    """异常检测器接口
    
    专门用于检测数据中的异常模式。
    """
    
    @abstractmethod
    def detect_anomalies(self, data: Any) -> List[Dict[str, Any]]:
        """检测异常
        
        Args:
            data: 待检测的数据
            
        Returns:
            List[Dict[str, Any]]: 异常信息列表
        """
        pass
    
    @abstractmethod
    def set_threshold(self, threshold: float) -> None:
        """设置异常检测阈值
        
        Args:
            threshold: 阈值
        """
        pass


class SimulationEngine(ABC):
    """仿真引擎接口
    
    定义仿真执行的核心方法。
    """
    
    @abstractmethod
    def initialize_simulation(self, config: Dict[str, Any]) -> None:
        """初始化仿真
        
        Args:
            config: 仿真配置参数
        """
        pass
    
    @abstractmethod
    def add_component(self, component: WaterSystemComponent) -> None:
        """添加组件到仿真
        
        Args:
            component: 水力系统组件
        """
        pass
    
    @abstractmethod
    def run_simulation(self, duration: float, time_step: float) -> SimulationResult:
        """运行仿真
        
        Args:
            duration: 仿真时长（秒）
            time_step: 时间步长（秒）
            
        Returns:
            SimulationResult: 仿真结果
        """
        pass
    
    @abstractmethod
    def pause_simulation(self) -> None:
        """暂停仿真"""
        pass
    
    @abstractmethod
    def resume_simulation(self) -> None:
        """恢复仿真"""
        pass
    
    @abstractmethod
    def stop_simulation(self) -> None:
        """停止仿真"""
        pass
    
    @abstractmethod
    def get_simulation_status(self) -> str:
        """获取仿真状态
        
        Returns:
            str: 仿真状态（'running', 'paused', 'stopped', 'completed'）
        """
        pass


class ConfigurationManager(ABC):
    """配置管理器接口
    
    定义配置文件的加载、保存和管理方法。
    """
    
    @abstractmethod
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict[str, Any]: 配置数据
        """
        pass
    
    @abstractmethod
    def save_config(self, config: Dict[str, Any], config_path: str) -> None:
        """保存配置文件
        
        Args:
            config: 配置数据
            config_path: 保存路径
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置有效性
        
        Args:
            config: 配置数据
            
        Returns:
            bool: 配置是否有效
        """
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置数据
        """
        pass