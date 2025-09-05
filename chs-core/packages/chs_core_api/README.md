# CHS-Core API 接口定义包

## 项目简介

`chs-core-api` 是 CHS-Core 水力系统仿真平台的 API 接口定义包。本包提供了标准化的接口定义、类型规范和异常处理机制，使不同团队能够基于统一的接口契约进行协作开发，而无需访问具体的实现代码。

## 主要特性

### 🔌 标准化接口
- **水力系统组件接口**：水库、泵站、阀门等组件的统一接口
- **数据处理器接口**：数据清洗、验证、异常检测的标准接口
- **仿真引擎接口**：仿真执行和控制的核心接口
- **配置管理接口**：配置加载、验证、保存的统一接口

### 📊 完整类型系统
- **基础数据类型**：流量、水位、控制信号等专业类型
- **复合数据类型**：组件状态、测量数据、时间序列等
- **枚举类型**：组件状态、报警级别等标准化枚举
- **类型别名**：常用类型的简化别名

### ⚠️ 统一异常处理
- **分层异常体系**：组件、数据处理、仿真、配置等分类异常
- **详细错误信息**：包含错误代码、详细信息和上下文
- **标准化错误格式**：便于错误处理和日志记录

## 安装方法

### 从 PyPI 安装（推荐）
```bash
pip install chs-core-api
```

### 从源码安装
```bash
git clone https://github.com/chs-core/chs-core-api.git
cd chs-core-api
pip install -e .
```

### 开发环境安装
```bash
pip install chs-core-api[dev]
```

## 快速开始

### 基础使用示例

```python
from chs_core_api import (
    WaterSystemComponent, 
    ReservoirInterface,
    FlowRate, 
    WaterLevel, 
    ComponentState,
    ComponentStatus
)
from chs_core_api.exceptions import ComponentStateError
from datetime import datetime

# 实现水库组件
class MyReservoir(ReservoirInterface):
    def __init__(self, reservoir_id: str, capacity: float):
        self.reservoir_id = reservoir_id
        self.capacity = capacity
        self.current_level = WaterLevel(50.0, "m", "reservoir_bottom")
        self.status = ComponentStatus.ONLINE
    
    def get_component_id(self) -> str:
        return self.reservoir_id
    
    def get_flow_rate(self) -> FlowRate:
        # 根据水位计算流量
        flow_value = max(0, self.current_level.value - 30) * 0.1
        return FlowRate(flow_value, "m³/s", datetime.now())
    
    def get_water_level(self) -> WaterLevel:
        return self.current_level
    
    def get_capacity(self) -> float:
        return self.capacity
    
    def set_inflow(self, rate: FlowRate) -> None:
        # 更新水位
        inflow_rate = rate.to_cubic_meters_per_second()
        # 简化的水位计算
        self.current_level.value += inflow_rate * 0.01
    
    def calculate_outflow(self) -> FlowRate:
        return self.get_flow_rate()
    
    # 实现基类的抽象方法
    def set_control_signal(self, signal):
        pass
    
    def get_state(self) -> ComponentState:
        return ComponentState(
            component_id=self.reservoir_id,
            status=self.status,
            health_score=95.0,
            last_update=datetime.now(),
            parameters={
                "water_level": self.current_level.value,
                "capacity": self.capacity
            },
            alarms=[]
        )
    
    def update(self, dt: float) -> None:
        # 更新组件状态
        pass
    
    def reset(self) -> None:
        self.current_level = WaterLevel(50.0, "m", "reservoir_bottom")
        self.status = ComponentStatus.ONLINE

# 使用示例
reservoir = MyReservoir("RES001", 1000000.0)

# 获取组件信息
print(f"组件ID: {reservoir.get_component_id()}")
print(f"当前水位: {reservoir.get_water_level().value} {reservoir.get_water_level().unit}")
print(f"当前流量: {reservoir.get_flow_rate().value} {reservoir.get_flow_rate().unit}")

# 设置入流
inflow = FlowRate(5.0, "m³/s")
reservoir.set_inflow(inflow)

# 获取组件状态
state = reservoir.get_state()
print(f"组件状态: {state.status.value}")
print(f"健康度: {state.health_score}%")
```

### 数据处理示例

```python
from chs_core_api import DataProcessor, Measurement
from chs_core_api.exceptions import DataValidationError
from datetime import datetime
from typing import Any, Dict, List

class WaterQualityProcessor(DataProcessor):
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
    
    def process_data(self, data: Any) -> Any:
        """处理水质数据"""
        if isinstance(data, Measurement):
            # 处理单个测量值
            processed_value = self._process_measurement(data)
            self.processed_count += 1
            return processed_value
        elif isinstance(data, list):
            # 处理测量值列表
            return [self._process_measurement(m) for m in data if isinstance(m, Measurement)]
        else:
            raise DataValidationError("data", data, "必须是 Measurement 或 Measurement 列表")
    
    def _process_measurement(self, measurement: Measurement) -> Measurement:
        """处理单个测量值"""
        # 数据清洗和校正
        corrected_value = measurement.value
        
        # 异常值检测
        if measurement.parameter == "pH" and not (0 <= measurement.value <= 14):
            corrected_value = max(0, min(14, measurement.value))
        elif measurement.parameter == "temperature" and not (-10 <= measurement.value <= 50):
            corrected_value = max(-10, min(50, measurement.value))
        
        return Measurement(
            sensor_id=measurement.sensor_id,
            parameter=measurement.parameter,
            value=corrected_value,
            unit=measurement.unit,
            timestamp=measurement.timestamp,
            quality=0.9 if corrected_value != measurement.value else measurement.quality
        )
    
    def validate_data(self, data: Any) -> bool:
        """验证数据有效性"""
        try:
            if isinstance(data, Measurement):
                return self._validate_measurement(data)
            elif isinstance(data, list):
                return all(self._validate_measurement(m) for m in data if isinstance(m, Measurement))
            return False
        except Exception:
            return False
    
    def _validate_measurement(self, measurement: Measurement) -> bool:
        """验证单个测量值"""
        # 检查必要字段
        if not measurement.sensor_id or not measurement.parameter:
            return False
        
        # 检查数值范围
        if measurement.parameter == "pH":
            return 0 <= measurement.value <= 14
        elif measurement.parameter == "temperature":
            return -10 <= measurement.value <= 50
        elif measurement.parameter == "dissolved_oxygen":
            return 0 <= measurement.value <= 20
        
        return True
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "success_rate": (self.processed_count - self.error_count) / max(1, self.processed_count)
        }

# 使用示例
processor = WaterQualityProcessor()

# 创建测量数据
measurements = [
    Measurement("SENSOR001", "pH", 7.2, "pH", datetime.now()),
    Measurement("SENSOR002", "temperature", 25.5, "°C", datetime.now()),
    Measurement("SENSOR003", "dissolved_oxygen", 8.5, "mg/L", datetime.now()),
]

# 验证数据
for measurement in measurements:
    is_valid = processor.validate_data(measurement)
    print(f"测量值 {measurement.parameter}: {measurement.value} - 有效性: {is_valid}")

# 处理数据
processed_data = processor.process_data(measurements)
print(f"处理了 {len(processed_data)} 个测量值")

# 获取统计信息
stats = processor.get_processing_stats()
print(f"处理统计: {stats}")
```

### 异常处理示例

```python
from chs_core_api.exceptions import (
    ComponentNotFoundError,
    ComponentStateError,
    DataValidationError,
    SimulationConvergenceError
)

def handle_component_operations():
    """演示组件操作的异常处理"""
    try:
        # 模拟组件操作
        component_id = "PUMP001"
        current_state = "maintenance"
        expected_state = "online"
        
        if current_state != expected_state:
            raise ComponentStateError(
                component_id=component_id,
                current_state=current_state,
                expected_state=expected_state
            )
    
    except ComponentStateError as e:
        print(f"组件状态错误: {e}")
        print(f"错误详情: {e.to_dict()}")
        
        # 根据错误信息进行处理
        if e.current_state == "maintenance":
            print("组件正在维护中，等待维护完成...")
    
    except ComponentNotFoundError as e:
        print(f"组件未找到: {e.component_id}")
        print("请检查组件配置")

def handle_data_validation():
    """演示数据验证的异常处理"""
    try:
        # 模拟数据验证
        field_name = "flow_rate"
        value = -5.0
        validation_rule = "必须大于等于0"
        
        if value < 0:
            raise DataValidationError(
                field_name=field_name,
                value=value,
                validation_rule=validation_rule
            )
    
    except DataValidationError as e:
        print(f"数据验证失败: {e}")
        print(f"字段: {e.field_name}, 值: {e.value}")
        print(f"验证规则: {e.validation_rule}")
        
        # 数据修正
        corrected_value = max(0, float(e.value))
        print(f"已修正为: {corrected_value}")

def handle_simulation_errors():
    """演示仿真错误的异常处理"""
    try:
        # 模拟仿真收敛错误
        raise SimulationConvergenceError(
            iteration_count=1000,
            tolerance=1e-6,
            current_error=1e-3
        )
    
    except SimulationConvergenceError as e:
        print(f"仿真收敛失败: {e}")
        print(f"迭代次数: {e.iteration_count}")
        print(f"当前误差: {e.current_error}, 容差: {e.tolerance}")
        
        # 调整仿真参数
        if e.current_error > e.tolerance * 100:
            print("误差过大，建议检查模型参数")
        else:
            print("可以尝试增加迭代次数或放宽容差")

# 运行异常处理示例
if __name__ == "__main__":
    print("=== 组件操作异常处理 ===")
    handle_component_operations()
    
    print("\n=== 数据验证异常处理 ===")
    handle_data_validation()
    
    print("\n=== 仿真错误异常处理 ===")
    handle_simulation_errors()
```

## API 参考

### 核心接口

#### WaterSystemComponent
水力系统组件的基础接口，所有组件都应实现此接口。

**主要方法：**
- `get_component_id() -> str`：获取组件ID
- `get_flow_rate() -> FlowRate`：获取流量
- `set_control_signal(signal: ControlSignal)`：设置控制信号
- `get_state() -> ComponentState`：获取组件状态
- `update(dt: float)`：更新组件
- `reset()`：重置组件

#### ReservoirInterface
水库组件专用接口，继承自 WaterSystemComponent。

**额外方法：**
- `get_water_level() -> WaterLevel`：获取水位
- `get_capacity() -> float`：获取容量
- `set_inflow(rate: FlowRate)`：设置入流
- `calculate_outflow() -> FlowRate`：计算出流

#### PumpInterface
泵站组件专用接口，继承自 WaterSystemComponent。

**额外方法：**
- `get_pump_efficiency() -> float`：获取效率
- `set_pump_speed(speed: float)`：设置转速
- `get_power_consumption() -> float`：获取功耗

#### DataProcessor
数据处理器接口，定义数据处理的标准方法。

**主要方法：**
- `process_data(data: Any) -> Any`：处理数据
- `validate_data(data: Any) -> bool`：验证数据
- `get_processing_stats() -> Dict[str, Any]`：获取统计信息

#### SimulationEngine
仿真引擎接口，定义仿真执行的核心方法。

**主要方法：**
- `initialize_simulation(config: Dict[str, Any])`：初始化仿真
- `add_component(component: WaterSystemComponent)`：添加组件
- `run_simulation(duration: float, time_step: float) -> SimulationResult`：运行仿真
- `pause_simulation()`、`resume_simulation()`、`stop_simulation()`：控制仿真
- `get_simulation_status() -> str`：获取仿真状态

### 数据类型

#### FlowRate
流量数据类型，包含数值、单位和时间戳。

```python
@dataclass
class FlowRate:
    value: float
    unit: str = "m³/s"
    timestamp: Optional[datetime] = None
```

#### WaterLevel
水位数据类型，包含数值、单位和参考基准。

```python
@dataclass
class WaterLevel:
    value: float
    unit: str = "m"
    reference: str = "sea_level"
    timestamp: Optional[datetime] = None
```

#### ComponentState
组件状态信息，包含完整的状态数据。

```python
@dataclass
class ComponentState:
    component_id: str
    status: ComponentStatus
    health_score: float
    last_update: datetime
    parameters: Dict[str, Any]
    alarms: List[Dict[str, Any]]
```

### 异常类型

#### CHSCoreException
所有 CHS-Core 异常的基类，提供统一的异常信息格式。

#### ComponentException
组件相关异常的基类，包括：
- `ComponentNotFoundError`：组件未找到
- `ComponentStateError`：组件状态错误
- `ComponentConfigurationError`：组件配置错误

#### DataProcessingException
数据处理异常的基类，包括：
- `DataValidationError`：数据验证错误
- `DataFormatError`：数据格式错误
- `AnomalyDetectionError`：异常检测错误

#### SimulationException
仿真异常的基类，包括：
- `SimulationInitializationError`：仿真初始化错误
- `SimulationConvergenceError`：仿真收敛错误
- `SimulationTimeoutError`：仿真超时错误

## 开发指南

### 实现自定义组件

1. **继承相应的接口**：根据组件类型选择合适的基础接口
2. **实现所有抽象方法**：确保实现接口定义的所有方法
3. **遵循类型约定**：使用定义的数据类型和异常类型
4. **添加适当的错误处理**：使用统一的异常体系

### 类型检查

本包支持静态类型检查，推荐使用 mypy：

```bash
pip install mypy
mypy your_code.py
```

### 测试

```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=chs_core_api
```

### 代码格式化

```bash
# 格式化代码
black your_code.py

# 检查代码风格
flake8 your_code.py
```

## 版本兼容性

- **Python**: 3.8+
- **类型检查**: 支持 mypy
- **向后兼容**: 遵循语义化版本控制

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 支持

- **文档**: [https://chs-core-api.readthedocs.io/](https://chs-core-api.readthedocs.io/)
- **问题反馈**: [GitHub Issues](https://github.com/chs-core/chs-core-api/issues)
- **讨论**: [GitHub Discussions](https://github.com/chs-core/chs-core-api/discussions)

## 更新日志

### v0.1.0 (2024-01-XX)
- 初始版本发布
- 基础接口定义
- 完整类型系统
- 统一异常处理
- 完整文档和示例