"""CHS-Core 异常定义

本模块定义了 CHS-Core 系统中使用的所有自定义异常类，
为错误处理提供了统一的异常体系。

异常层次结构：
- CHSCoreException (基础异常)
  - ComponentException (组件相关异常)
    - ComponentNotFoundError
    - ComponentStateError
    - ComponentConfigurationError
  - DataProcessingException (数据处理异常)
    - DataValidationError
    - DataFormatError
    - AnomalyDetectionError
  - SimulationException (仿真异常)
    - SimulationInitializationError
    - SimulationConvergenceError
    - SimulationTimeoutError
  - ConfigurationException (配置异常)
    - ConfigurationLoadError
    - ConfigurationValidationError
    - ConfigurationSaveError
"""

from typing import Any, Dict, Optional


class CHSCoreException(Exception):
    """CHS-Core 基础异常类
    
    所有 CHS-Core 相关异常的基类。
    提供统一的异常信息格式和错误代码机制。
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 详细信息字典
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """将异常信息转换为字典格式
        
        Returns:
            Dict[str, Any]: 异常信息字典
        """
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }
    
    def __str__(self) -> str:
        base_msg = f"[{self.error_code}] {self.message}"
        if self.details:
            details_str = ", ".join([f"{k}={v}" for k, v in self.details.items()])
            return f"{base_msg} (详细信息: {details_str})"
        return base_msg


# 组件相关异常
class ComponentException(CHSCoreException):
    """组件相关异常基类"""
    pass


class ComponentNotFoundError(ComponentException):
    """组件未找到异常
    
    当尝试访问不存在的组件时抛出。
    """
    
    def __init__(self, component_id: str, message: Optional[str] = None):
        default_message = f"未找到组件: {component_id}"
        super().__init__(
            message or default_message,
            error_code="COMPONENT_NOT_FOUND",
            details={"component_id": component_id}
        )
        self.component_id = component_id


class ComponentStateError(ComponentException):
    """组件状态异常
    
    当组件处于不正确的状态时抛出。
    """
    
    def __init__(self, component_id: str, current_state: str, 
                 expected_state: str, message: Optional[str] = None):
        default_message = f"组件 {component_id} 状态错误: 当前状态为 {current_state}，期望状态为 {expected_state}"
        super().__init__(
            message or default_message,
            error_code="COMPONENT_STATE_ERROR",
            details={
                "component_id": component_id,
                "current_state": current_state,
                "expected_state": expected_state
            }
        )
        self.component_id = component_id
        self.current_state = current_state
        self.expected_state = expected_state


class ComponentConfigurationError(ComponentException):
    """组件配置异常
    
    当组件配置无效或缺失时抛出。
    """
    
    def __init__(self, component_id: str, config_issue: str, 
                 message: Optional[str] = None):
        default_message = f"组件 {component_id} 配置错误: {config_issue}"
        super().__init__(
            message or default_message,
            error_code="COMPONENT_CONFIG_ERROR",
            details={
                "component_id": component_id,
                "config_issue": config_issue
            }
        )
        self.component_id = component_id
        self.config_issue = config_issue


# 数据处理相关异常
class DataProcessingException(CHSCoreException):
    """数据处理异常基类"""
    pass


class DataValidationError(DataProcessingException):
    """数据验证异常
    
    当数据验证失败时抛出。
    """
    
    def __init__(self, field_name: str, value: Any, 
                 validation_rule: str, message: Optional[str] = None):
        default_message = f"数据验证失败: 字段 '{field_name}' 的值 '{value}' 不符合规则 '{validation_rule}'"
        super().__init__(
            message or default_message,
            error_code="DATA_VALIDATION_ERROR",
            details={
                "field_name": field_name,
                "value": str(value),
                "validation_rule": validation_rule
            }
        )
        self.field_name = field_name
        self.value = value
        self.validation_rule = validation_rule


class DataFormatError(DataProcessingException):
    """数据格式异常
    
    当数据格式不正确时抛出。
    """
    
    def __init__(self, expected_format: str, actual_format: str, 
                 message: Optional[str] = None):
        default_message = f"数据格式错误: 期望格式为 '{expected_format}'，实际格式为 '{actual_format}'"
        super().__init__(
            message or default_message,
            error_code="DATA_FORMAT_ERROR",
            details={
                "expected_format": expected_format,
                "actual_format": actual_format
            }
        )
        self.expected_format = expected_format
        self.actual_format = actual_format


class AnomalyDetectionError(DataProcessingException):
    """异常检测异常
    
    当异常检测过程中发生错误时抛出。
    """
    
    def __init__(self, detector_type: str, error_details: str, 
                 message: Optional[str] = None):
        default_message = f"异常检测器 '{detector_type}' 执行失败: {error_details}"
        super().__init__(
            message or default_message,
            error_code="ANOMALY_DETECTION_ERROR",
            details={
                "detector_type": detector_type,
                "error_details": error_details
            }
        )
        self.detector_type = detector_type
        self.error_details = error_details


# 仿真相关异常
class SimulationException(CHSCoreException):
    """仿真异常基类"""
    pass


class SimulationInitializationError(SimulationException):
    """仿真初始化异常
    
    当仿真初始化失败时抛出。
    """
    
    def __init__(self, initialization_step: str, error_details: str, 
                 message: Optional[str] = None):
        default_message = f"仿真初始化失败，步骤: {initialization_step}，错误: {error_details}"
        super().__init__(
            message or default_message,
            error_code="SIMULATION_INIT_ERROR",
            details={
                "initialization_step": initialization_step,
                "error_details": error_details
            }
        )
        self.initialization_step = initialization_step
        self.error_details = error_details


class SimulationConvergenceError(SimulationException):
    """仿真收敛异常
    
    当仿真无法收敛时抛出。
    """
    
    def __init__(self, iteration_count: int, tolerance: float, 
                 current_error: float, message: Optional[str] = None):
        default_message = f"仿真收敛失败: 迭代 {iteration_count} 次后，当前误差 {current_error} 仍大于容差 {tolerance}"
        super().__init__(
            message or default_message,
            error_code="SIMULATION_CONVERGENCE_ERROR",
            details={
                "iteration_count": iteration_count,
                "tolerance": tolerance,
                "current_error": current_error
            }
        )
        self.iteration_count = iteration_count
        self.tolerance = tolerance
        self.current_error = current_error


class SimulationTimeoutError(SimulationException):
    """仿真超时异常
    
    当仿真执行超时时抛出。
    """
    
    def __init__(self, timeout_seconds: float, elapsed_seconds: float, 
                 message: Optional[str] = None):
        default_message = f"仿真执行超时: 设定超时时间 {timeout_seconds} 秒，已执行 {elapsed_seconds} 秒"
        super().__init__(
            message or default_message,
            error_code="SIMULATION_TIMEOUT_ERROR",
            details={
                "timeout_seconds": timeout_seconds,
                "elapsed_seconds": elapsed_seconds
            }
        )
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds


# 配置相关异常
class ConfigurationException(CHSCoreException):
    """配置异常基类"""
    pass


class ConfigurationLoadError(ConfigurationException):
    """配置加载异常
    
    当配置文件加载失败时抛出。
    """
    
    def __init__(self, config_path: str, load_error: str, 
                 message: Optional[str] = None):
        default_message = f"配置文件加载失败: {config_path}，错误: {load_error}"
        super().__init__(
            message or default_message,
            error_code="CONFIG_LOAD_ERROR",
            details={
                "config_path": config_path,
                "load_error": load_error
            }
        )
        self.config_path = config_path
        self.load_error = load_error


class ConfigurationValidationError(ConfigurationException):
    """配置验证异常
    
    当配置验证失败时抛出。
    """
    
    def __init__(self, validation_errors: Dict[str, str], 
                 message: Optional[str] = None):
        error_summary = ", ".join([f"{k}: {v}" for k, v in validation_errors.items()])
        default_message = f"配置验证失败: {error_summary}"
        super().__init__(
            message or default_message,
            error_code="CONFIG_VALIDATION_ERROR",
            details={"validation_errors": validation_errors}
        )
        self.validation_errors = validation_errors


class ConfigurationSaveError(ConfigurationException):
    """配置保存异常
    
    当配置文件保存失败时抛出。
    """
    
    def __init__(self, config_path: str, save_error: str, 
                 message: Optional[str] = None):
        default_message = f"配置文件保存失败: {config_path}，错误: {save_error}"
        super().__init__(
            message or default_message,
            error_code="CONFIG_SAVE_ERROR",
            details={
                "config_path": config_path,
                "save_error": save_error
            }
        )
        self.config_path = config_path
        self.save_error = save_error


# 网络和通信相关异常
class NetworkException(CHSCoreException):
    """网络异常基类"""
    pass


class ConnectionError(NetworkException):
    """连接异常
    
    当网络连接失败时抛出。
    """
    
    def __init__(self, endpoint: str, connection_error: str, 
                 message: Optional[str] = None):
        default_message = f"连接失败: {endpoint}，错误: {connection_error}"
        super().__init__(
            message or default_message,
            error_code="CONNECTION_ERROR",
            details={
                "endpoint": endpoint,
                "connection_error": connection_error
            }
        )
        self.endpoint = endpoint
        self.connection_error = connection_error


class APIError(NetworkException):
    """API异常
    
    当API调用失败时抛出。
    """
    
    def __init__(self, api_endpoint: str, status_code: int, 
                 response_body: str, message: Optional[str] = None):
        default_message = f"API调用失败: {api_endpoint}，状态码: {status_code}"
        super().__init__(
            message or default_message,
            error_code="API_ERROR",
            details={
                "api_endpoint": api_endpoint,
                "status_code": status_code,
                "response_body": response_body
            }
        )
        self.api_endpoint = api_endpoint
        self.status_code = status_code
        self.response_body = response_body