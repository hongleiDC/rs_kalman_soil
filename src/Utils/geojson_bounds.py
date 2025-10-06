"""从GeoJSON文件中提取地理边界的实用工具函数。

此模块提供了从GeoJSON文件中读取和提取边界框（bounding box）信息的功能。
边界框由四个值组成：最小经度、最小纬度、最大经度、最大纬度。
"""

from pathlib import Path
from typing import Dict, List, Tuple, Union

try:
    import geopandas as gpd
except ImportError as exc:
    raise ImportError(
        "geopandas 是必需的。请通过 'pip install geopandas' 安装。"
    ) from exc


def get_geojson_bounds(geojson_path: Union[str, Path]) -> Dict[str, float]:
    """
    从GeoJSON文件中提取四边边界的经纬度。
    
    参数:
        geojson_path: GeoJSON文件的路径
        
    返回:
        包含边界信息的字典，键为:
        - 'min_lon': 最小经度（西边界）
        - 'min_lat': 最小纬度（南边界）
        - 'max_lon': 最大经度（东边界）
        - 'max_lat': 最大纬度（北边界）
        
    异常:
        FileNotFoundError: 当GeoJSON文件不存在时
        ValueError: 当GeoJSON文件为空或无效时
        
    示例:
        >>> bounds = get_geojson_bounds("zhengzhou.geojson")
        >>> print(f"经度范围: {bounds['min_lon']} 到 {bounds['max_lon']}")
        >>> print(f"纬度范围: {bounds['min_lat']} 到 {bounds['max_lat']}")
    """
    geojson_path = Path(geojson_path)
    
    # 检查文件是否存在
    if not geojson_path.exists():
        raise FileNotFoundError(f"GeoJSON文件未找到: {geojson_path}")
    
    # 读取GeoJSON文件
    try:
        gdf = gpd.read_file(geojson_path)
    except Exception as e:
        raise ValueError(f"无法读取GeoJSON文件 {geojson_path}: {e}") from e
    
    # 检查是否为空
    if gdf.empty:
        raise ValueError(f"GeoJSON文件为空: {geojson_path}")
    
    # 获取所有几何体的总边界
    # bounds返回 (minx, miny, maxx, maxy)
    total_bounds = gdf.total_bounds
    
    return {
        'min_lon': float(total_bounds[0]),  # 西边界
        'min_lat': float(total_bounds[1]),  # 南边界
        'max_lon': float(total_bounds[2]),  # 东边界
        'max_lat': float(total_bounds[3])   # 北边界
    }


def get_geojson_bounds_tuple(geojson_path: Union[str, Path]) -> Tuple[float, float, float, float]:
    """
    从GeoJSON文件中提取边界，返回元组格式。
    
    参数:
        geojson_path: GeoJSON文件的路径
        
    返回:
        (min_lon, min_lat, max_lon, max_lat) 元组
        
    示例:
        >>> min_lon, min_lat, max_lon, max_lat = get_geojson_bounds_tuple("zhengzhou.geojson")
        >>> print(f"边界框: ({min_lon}, {min_lat}, {max_lon}, {max_lat})")
    """
    bounds = get_geojson_bounds(geojson_path)
    return (
        bounds['min_lon'],
        bounds['min_lat'],
        bounds['max_lon'],
        bounds['max_lat']
    )


def print_geojson_bounds(geojson_path: Union[str, Path]) -> None:
    """
    打印GeoJSON文件的边界信息，便于快速查看。
    
    参数:
        geojson_path: GeoJSON文件的路径
        
    示例:
        >>> print_geojson_bounds("zhengzhou.geojson")
        边界信息 (zhengzhou.geojson):
        ==========================================
        最小经度（西边界）: 112.72
        最大经度（东边界）: 114.21
        最小纬度（南边界）: 34.16
        最大纬度（北边界）: 34.98
        ==========================================
        经度跨度: 1.48 度
        纬度跨度: 0.82 度
    """
    try:
        bounds = get_geojson_bounds(geojson_path)
        
        print(f"\n边界信息 ({Path(geojson_path).name}):")
        print("=" * 42)
        print(f"最小经度（西边界）: {bounds['min_lon']:.2f}")
        print(f"最大经度（东边界）: {bounds['max_lon']:.2f}")
        print(f"最小纬度（南边界）: {bounds['min_lat']:.2f}")
        print(f"最大纬度（北边界）: {bounds['max_lat']:.2f}")
        print("=" * 42)
        
        lon_span = bounds['max_lon'] - bounds['min_lon']
        lat_span = bounds['max_lat'] - bounds['min_lat']
        print(f"经度跨度: {lon_span:.2f} 度")
        print(f"纬度跨度: {lat_span:.2f} 度")
        print()
        
    except Exception as e:
        print(f"错误: {e}")


def get_bounding_box_corners(geojson_path: Union[str, Path]) -> List[Tuple[float, float]]:
    """
    获取边界框的四个角点坐标（顺时针，从左下角开始）。
    
    参数:
        geojson_path: GeoJSON文件的路径
        
    返回:
        包含四个角点坐标的列表: [(lon, lat), ...]
        顺序为: 左下、左上、右上、右下
        
    示例:
        >>> corners = get_bounding_box_corners("zhengzhou.geojson")
        >>> for i, (lon, lat) in enumerate(corners, 1):
        ...     print(f"角点{i}: ({lon:.2f}, {lat:.2f})")
    """
    bounds = get_geojson_bounds(geojson_path)
    
    return [
        (bounds['min_lon'], bounds['min_lat']),  # 左下角
        (bounds['min_lon'], bounds['max_lat']),  # 左上角
        (bounds['max_lon'], bounds['max_lat']),  # 右上角
        (bounds['max_lon'], bounds['min_lat'])   # 右下角
    ]


if __name__ == "__main__":
    # 示例用法
    import sys
    
    if len(sys.argv) > 1:
        geojson_file = sys.argv[1]
    else:
        # 默认使用郑州市的GeoJSON文件
        geojson_file = "../../boundary/zhengzhou.geojson"
    
    print(f"读取GeoJSON文件: {geojson_file}\n")
    
    # 方法1: 获取字典格式的边界
    bounds_dict = get_geojson_bounds(geojson_file)
    print("方法1 - 字典格式:")
    print(bounds_dict)
    print()
    
    # 方法2: 获取元组格式的边界
    bounds_tuple = get_geojson_bounds_tuple(geojson_file)
    print("方法2 - 元组格式:")
    print(f"(min_lon, min_lat, max_lon, max_lat) = {bounds_tuple}")
    print()
    
    # 方法3: 打印格式化的边界信息
    print("方法3 - 格式化输出:")
    print_geojson_bounds(geojson_file)
    
    # 方法4: 获取四个角点
    corners = get_bounding_box_corners(geojson_file)
    print("方法4 - 边界框角点:")
    corner_names = ["左下角", "左上角", "右上角", "右下角"]
    for name, (lon, lat) in zip(corner_names, corners):
        print(f"  {name}: 经度={lon:.4f}, 纬度={lat:.4f}")
