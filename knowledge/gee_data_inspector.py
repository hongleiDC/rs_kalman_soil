"""
GEE 数据集详细信息获取脚本
用于获取项目中使用的 GEE 数据集的完整数据字典和元数据
"""

import ee
import json
from typing import Dict, Any, List
from pathlib import Path

# 初始化 GEE
try:
    ee.Initialize(project="solid-terra-465503-p1")
except Exception:
    ee.Authenticate()
    ee.Initialize(project="solid-terra-465503-p1")

# 项目中使用的数据集
DATASETS = {
    "imerg": [
        "NASA/GPM_L3/IMERG_V07",
        "NASA/GPM_L3/IMERG_V06"
    ],
    "era5_land": [
        "ECMWF/ERA5_LAND/DAILY_AGGR",
        "ECMWF/ERA5_LAND/HOURLY"
    ],
    "modis_ndvi": [
        "MODIS/061/MOD13Q1",
        "MODIS/006/MOD13Q1",
        "MODIS/061/MYD13Q1"
    ]
}


def get_image_collection_info(ic_id: str) -> Dict[str, Any]:
    """获取 ImageCollection 的详细信息"""
    try:
        ic = ee.ImageCollection(ic_id)
        
        # 获取第一张图像用于分析波段信息
        first_image = ic.first()
        
        # 基本信息
        info = {
            "dataset_id": ic_id,
            "status": "available",
            "total_images": None,
            "date_range": None,
            "bands": [],
            "properties": {},
            "description": None,
            "error": None
        }
        
        try:
            # 获取图像数量（限制查询以避免超时）
            size = ic.limit(10000).size().getInfo()
            info["total_images"] = size
        except Exception as e:
            info["total_images"] = f"查询失败: {str(e)}"
        
        try:
            # 获取时间范围
            date_range = ic.reduceColumns(ee.Reducer.minMax(), ["system:time_start"]).getInfo()
            if date_range and "min" in date_range and "max" in date_range:
                from datetime import datetime
                min_date = datetime.fromtimestamp(date_range["min"] / 1000).strftime("%Y-%m-%d")
                max_date = datetime.fromtimestamp(date_range["max"] / 1000).strftime("%Y-%m-%d")
                info["date_range"] = {"start": min_date, "end": max_date}
        except Exception as e:
            info["date_range"] = f"查询失败: {str(e)}"
        
        try:
            # 获取波段信息
            band_names = first_image.bandNames().getInfo()
            bands_info = []
            
            for band_name in band_names:
                band = first_image.select([band_name])
                band_info = band.getInfo()
                
                band_detail = {
                    "name": band_name,
                    "data_type": None,
                    "dimensions": None,
                    "crs": None,
                    "crs_transform": None,
                    "description": None,
                    "units": None,
                    "scale": None,
                    "offset": None,
                    "min": None,
                    "max": None,
                    "no_data": None
                }
                
                # 从 band_info 中提取信息
                if "bands" in band_info and len(band_info["bands"]) > 0:
                    b = band_info["bands"][0]
                    band_detail["data_type"] = b.get("data_type", {}).get("precision")
                    band_detail["dimensions"] = b.get("dimensions")
                    band_detail["crs"] = b.get("crs")
                    band_detail["crs_transform"] = b.get("crs_transform")
                    
                # 尝试获取属性信息
                props = band_info.get("properties", {})
                for key in ["description", "units", "scale", "offset", "min", "max", "no_data"]:
                    if f"{band_name}_{key}" in props:
                        band_detail[key] = props[f"{band_name}_{key}"]
                    elif key in props:
                        band_detail[key] = props[key]
                
                bands_info.append(band_detail)
            
            info["bands"] = bands_info
            
        except Exception as e:
            info["bands"] = f"查询失败: {str(e)}"
        
        try:
            # 获取图像属性（元数据）
            image_info = first_image.getInfo()
            if "properties" in image_info:
                info["properties"] = image_info["properties"]
        except Exception as e:
            info["properties"] = f"查询失败: {str(e)}"
        
        return info
        
    except Exception as e:
        return {
            "dataset_id": ic_id,
            "status": "unavailable",
            "error": str(e)
        }


def format_band_table(bands: List[Dict]) -> str:
    """将波段信息格式化为 Markdown 表格"""
    if isinstance(bands, str):
        return f"\n{bands}\n"
    
    table = "| 波段名称 | 数据类型 | 单位 | 描述 | 取值范围 |\n"
    table += "|---------|---------|------|------|----------|\n"
    
    for band in bands:
        name = band.get("name", "N/A")
        dtype = band.get("data_type", "N/A")
        units = band.get("units", "N/A")
        desc = band.get("description", "N/A")
        
        min_val = band.get("min", "N/A")
        max_val = band.get("max", "N/A")
        value_range = f"{min_val} ~ {max_val}"
        
        table += f"| {name} | {dtype} | {units} | {desc} | {value_range} |\n"
    
    return table


def generate_dataset_markdown(category: str, datasets: List[str]) -> str:
    """为每个数据集类别生成 Markdown 文档"""
    
    md_content = f"# {category.upper()} 数据集详细信息\n\n"
    md_content += f"**生成时间**: 2025-10-06\n\n"
    md_content += f"**数据集类别**: {category}\n\n"
    md_content += "---\n\n"
    
    for i, dataset_id in enumerate(datasets, 1):
        print(f"正在获取数据集 {i}/{len(datasets)}: {dataset_id}")
        
        info = get_image_collection_info(dataset_id)
        
        md_content += f"## {i}. {dataset_id}\n\n"
        
        if info["status"] == "unavailable":
            md_content += f"**状态**: ❌ 不可用\n\n"
            md_content += f"**错误信息**: {info['error']}\n\n"
            md_content += "---\n\n"
            continue
        
        md_content += f"**状态**: ✅ 可用\n\n"
        
        # 基本信息
        md_content += "### 基本信息\n\n"
        md_content += f"- **数据集 ID**: `{dataset_id}`\n"
        
        if info.get("total_images"):
            md_content += f"- **图像总数**: {info['total_images']}\n"
        
        if isinstance(info.get("date_range"), dict):
            md_content += f"- **时间范围**: {info['date_range']['start']} 至 {info['date_range']['end']}\n"
        
        md_content += "\n"
        
        # 波段信息
        md_content += "### 波段信息\n\n"
        md_content += format_band_table(info["bands"])
        md_content += "\n"
        
        # 波段详细信息
        if isinstance(info["bands"], list):
            md_content += "### 波段详细信息\n\n"
            for band in info["bands"]:
                md_content += f"#### {band['name']}\n\n"
                md_content += f"- **数据类型**: {band.get('data_type', 'N/A')}\n"
                md_content += f"- **维度**: {band.get('dimensions', 'N/A')}\n"
                md_content += f"- **坐标系**: {band.get('crs', 'N/A')}\n"
                if band.get('units'):
                    md_content += f"- **单位**: {band['units']}\n"
                if band.get('scale'):
                    md_content += f"- **比例因子**: {band['scale']}\n"
                if band.get('offset'):
                    md_content += f"- **偏移量**: {band['offset']}\n"
                if band.get('no_data'):
                    md_content += f"- **无效值**: {band['no_data']}\n"
                md_content += "\n"
        
        # 属性信息
        if info.get("properties") and isinstance(info["properties"], dict):
            md_content += "### 元数据属性\n\n"
            md_content += "```json\n"
            md_content += json.dumps(info["properties"], indent=2, ensure_ascii=False)
            md_content += "\n```\n\n"
        
        # GEE 代码示例
        md_content += "### 使用示例 (GEE Python API)\n\n"
        md_content += "```python\n"
        md_content += "import ee\n\n"
        md_content += "# 初始化\n"
        md_content += "ee.Initialize()\n\n"
        md_content += f"# 加载数据集\n"
        md_content += f"dataset = ee.ImageCollection('{dataset_id}')\n\n"
        md_content += "# 过滤时间和空间范围\n"
        md_content += "filtered = dataset \\\n"
        md_content += "    .filterDate('2021-01-01', '2021-12-31') \\\n"
        md_content += "    .filterBounds(ee.Geometry.Point([113.65, 34.76]))\n\n"
        
        if isinstance(info["bands"], list) and len(info["bands"]) > 0:
            first_band = info["bands"][0]["name"]
            md_content += f"# 选择波段\n"
            md_content += f"image = filtered.first().select('{first_band}')\n\n"
            md_content += "# 获取统计信息\n"
            md_content += "stats = image.reduceRegion(\n"
            md_content += "    reducer=ee.Reducer.mean(),\n"
            md_content += "    geometry=ee.Geometry.Point([113.65, 34.76]),\n"
            md_content += "    scale=1000\n"
            md_content += ").getInfo()\n"
            md_content += "print(stats)\n"
        
        md_content += "```\n\n"
        md_content += "---\n\n"
    
    return md_content


def main():
    """主函数：生成所有数据集的 Markdown 文档"""
    
    output_dir = Path(__file__).parent
    
    print("=" * 60)
    print("GEE 数据集信息提取工具")
    print("=" * 60)
    
    for category, datasets in DATASETS.items():
        print(f"\n处理类别: {category}")
        print("-" * 60)
        
        md_content = generate_dataset_markdown(category, datasets)
        
        # 保存 Markdown 文件
        output_file = output_dir / f"GEE_{category.upper()}_数据字典.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        print(f"✅ 已保存: {output_file}")
    
    print("\n" + "=" * 60)
    print("所有数据集信息提取完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
