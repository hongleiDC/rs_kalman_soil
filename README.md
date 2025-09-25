# GNSS-R 土壤湿度数据同化与集合卡尔曼滤波器

本项目演示了一个使用集合卡尔曼滤波器（EnKF）从GNSS-R（全球导航卫星系统反射计）观测中估算土壤湿度的数据同化框架，既支持合成数据，也可接入真实数据（以 2021 年 7 月郑州为例）。

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
│   ├── EnsembleKalmanFilter.py   # EnKF 核心实现
│   ├── ObservationModel.py       # GNSS-R 观测算子
│   ├── ProcessModel.py           # 土壤-植被过程模型
│   ├── Main.ipynb                # 交互式合成实验
│   ├── run_simulation.py         # 合成数据命令行演示
│   └── run_real_data.py          # 真实数据同化模板（郑州 2021/07）
```

*   `src/ProcessModel.py`: 土壤湿度与植被含水量的耦合过程模型。
*   `src/ObservationModel.py`: Mironov 介电 + 菲涅尔 + 植被衰减的 GNSS-R 前向模型。
*   `src/EnsembleKalmanFilter.py`: 集合卡尔曼滤波器算法。
*   `src/Main.ipynb`: 交互式笔记本演示合成实验全过程。
*   `src/run_simulation.py`: 命令行运行的合成数据示例。
*   `src/run_real_data.py`: 真实数据同化脚本，需要用户填入数据路径。

## 环境准备

推荐使用 Conda 创建隔离环境：

```bash
conda create -n gnssr_enkf python=3.10
conda activate gnssr_enkf

# 合成实验所需依赖
conda install -c conda-forge numpy matplotlib

# 真实数据工作流额外依赖
conda install -c conda-forge pandas xarray netcdf4 h5netcdf

# 如需运行 Jupyter 笔记本
conda install -c conda-forge jupyterlab
```

## 快速开始

### 合成数据演示

* 命令行运行：
  ```bash
  python src/run_simulation.py
  ```
  终端会打印合成实验的最终状态与误差统计。

* 交互式查看：打开 `src/Main.ipynb`，按顺序执行各单元，可获得曲线与图形。

### 真实数据示例（郑州 2021/07）

1. 准备以下数据并将文件路径填入 `src/run_real_data.py` 的 `DataCatalog`：
   - **GPM IMERG**：2021-07-01 至 2021-07-31 的降水数据（NetCDF/HDF）。
   - **ERA5-Land**：包含变量 `t2m`、`pev` 的再分析数据。
   - **CYGNSS Level 1/2**：含反射率与入射角的 GNSS-R 观测。
   - **土壤质地**：如 SoilGrids sand/clay 分数的静态网格文件。

2. 执行脚本：
   ```bash
   python src/run_real_data.py
   ```
   输出将保存为 `enkf_results_zhengzhou_202107.csv`。
