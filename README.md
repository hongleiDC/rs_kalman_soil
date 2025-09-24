# GNSS-R 土壤湿度数据同化与集合卡尔曼滤波器

本项目演示了一个使用集合卡尔曼滤波器（EnKF）从模拟的GNSS-R（全球导航卫星系统反射计）观测中估算土壤湿度的数据同化框架。

## 描述

该项目以面向对象的方式构建，包括以下关键组件：

*   **过程模型**：一个简单的先期降水指数（API）模型，根据降水量描述土壤湿度的时间演变。
*   **观测模型**：一个基于物理的前向模型，将土壤湿度映射到GNSS-R反射率。该模型考虑了：
    *   土壤介电特性（Wang & Schmugge模型）
    *   菲涅尔反射率
    *   植被衰减
    *   地表粗糙度
*   **集合卡尔曼滤波器（EnKF）**：数据同化算法，结合过程模型预测和观测，提供改进的土壤湿度估算。
*   **模拟**：一个Jupyter Notebook（`Main.ipynb`），运行一个完整的模拟实验。它生成一个综合的“真实”数据集和模拟观测，然后应用EnKF估算土壤湿度。结果被可视化，以比较真实的土壤湿度、开环模型（无同化）和EnKF同化状态。

## 项目结构

```
.
├── README.md
├── src
│   ├── EnsembleKalmanFilter.py
│   ├── Main.ipynb
│   ├── ObservationModel.py
│   └── ProcessModel.py
```

*   `src/ProcessModel.py`: 实现土壤湿度过程模型（API模型）。
*   `src/ObservationModel.py`: 实现前向观测模型（土壤湿度到GNSS-R反射率）。
*   `src/EnsembleKalmanFilter.py`: 实现集合卡尔曼滤波器算法。
*   `src/Main.ipynb`: 运行模拟和可视化结果的主脚本。

## 如何运行

模拟从`Main.ipynb` Jupyter Notebook中运行。

1.  **安装依赖**：
    确保您已安装所需的Python库。主要依赖项是：
    *   `numpy`
    *   `matplotlib`

    您可以使用conda安装它们：
    ```bash
    conda install -c conda-forge numpy matplotlib
    ```

2.  **运行模拟**：
    *   在Jupyter环境中打开并运行`src/Main.ipynb`笔记本。
    *   该笔记本将执行模拟，执行数据同化，并生成显示结果的图表。

## 依赖

*   Python 3.x
*   NumPy
*   Matplotlib
