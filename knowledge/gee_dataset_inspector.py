"""
GEE 数据集详细信息提取工具
自动获取项目中使用的 GEE 数据集的详细信息并生成 Markdown 文档
"""

import ee
from typing import Dict, Any, List
import json
from datetime import datetime


class GEEDatasetInspector:
    """Google Earth Engine 数据集信息检查器"""
    
    def __init__(self, project_id: str = "solid-terra-465503-p1"):
        """初始化 GEE 连接"""
        try:
            ee.Initialize(project=project_id)
            print(f"✅ GEE 初始化成功 (项目: {project_id})")
        except Exception as e:
            print(f"⚠️ 初始化失败，尝试认证...")
            ee.Authenticate()
            ee.Initialize(project=project_id)
            print(f"✅ GEE 认证并初始化成功")
    
    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """获取数据集的详细信息"""
        try:
            # 尝试作为 ImageCollection 获取
            ic = ee.ImageCollection(dataset_id)
            
            # 获取第一张影像以提取元数据
            first_image = ic.limit(1).first()
            
            # 获取数据集信息
            info = {
                "dataset_id": dataset_id,
                "type": "ImageCollection",
                "status": "可访问",
                "total_images": None,  # 总数可能很大，不获取
                "bands": [],
                "properties": {},
                "date_range": {},
                "spatial_info": {},
            }
            
            # 获取波段信息
            try:
                band_names = first_image.bandNames().getInfo()
                info["bands"] = band_names
                
                # 获取每个波段的详细信息
                band_details = []
                for band_name in band_names:
                    try:
                        band = first_image.select(band_name)
                        band_info = band.getInfo()
                        
                        # 提取波段属性
                        band_detail = {
                            "name": band_name,
                            "data_type": band_info.get("bands", [{}])[0].get("data_type", {}).get("precision", "未知"),
                            "dimensions": band_info.get("bands", [{}])[0].get("dimensions", []),
                            "crs": band_info.get("bands", [{}])[0].get("crs", "未知"),
                        }
                        band_details.append(band_detail)
                    except Exception as e:
                        band_details.append({
                            "name": band_name,
                            "error": str(e)
                        })
                
                info["band_details"] = band_details
            except Exception as e:
                info["bands_error"] = str(e)
            
            # 获取属性信息
            try:
                props = first_image.propertyNames().getInfo()
                info["property_names"] = props
                
                # 获取示例属性值
                sample_props = {}
                for prop in props[:10]:  # 只获取前10个属性
                    try:
                        value = first_image.get(prop).getInfo()
                        sample_props[prop] = value
                    except:
                        sample_props[prop] = "无法获取"
                info["sample_properties"] = sample_props
            except Exception as e:
                info["properties_error"] = str(e)
            
            # 获取时间范围信息
            try:
                first_date = first_image.date().format('YYYY-MM-dd').getInfo()
                info["first_image_date"] = first_date
            except Exception as e:
                info["date_error"] = str(e)
            
            # 获取投影和分辨率信息
            try:
                projection = first_image.select(0).projection()
                info["projection"] = projection.getInfo()
            except Exception as e:
                info["projection_error"] = str(e)
            
            return info
            
        except Exception as e:
            return {
                "dataset_id": dataset_id,
                "type": "未知",
                "status": "错误",
                "error": str(e)
            }
    
    def generate_markdown(self, dataset_info: Dict[str, Any]) -> str:
        """根据数据集信息生成 Markdown 文档"""
        md = []
        
        dataset_id = dataset_info.get("dataset_id", "未知数据集")
        dataset_name = dataset_id.split("/")[-1]
        
        # 标题
        md.append(f"# {dataset_id}\n")
        md.append(f"**数据集 ID**: `{dataset_id}`\n")
        md.append(f"**数据类型**: {dataset_info.get('type', '未知')}\n")
        md.append(f"**状态**: {dataset_info.get('status', '未知')}\n")
        md.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.append("\n---\n")
        
        # 数据集描述（需要手动补充）
        md.append("## 📋 数据集描述\n")
        md.append("> TODO: 添加数据集的详细描述\n")
        md.append("\n")
        
        # 时间信息
        if "first_image_date" in dataset_info:
            md.append("## 📅 时间信息\n")
            md.append(f"- **首张影像日期**: {dataset_info['first_image_date']}\n")
            if "date_range" in dataset_info and dataset_info["date_range"]:
                md.append(f"- **时间范围**: {dataset_info['date_range']}\n")
            md.append("\n")
        
        # 波段信息
        if "bands" in dataset_info and dataset_info["bands"]:
            md.append("## 📊 波段信息\n")
            md.append(f"**波段数量**: {len(dataset_info['bands'])}\n\n")
            md.append("| 波段名称 | 数据类型 | 描述 |\n")
            md.append("|---------|---------|------|\n")
            
            if "band_details" in dataset_info:
                for band in dataset_info["band_details"]:
                    name = band.get("name", "未知")
                    dtype = band.get("data_type", "未知")
                    md.append(f"| `{name}` | {dtype} | TODO: 添加描述 |\n")
            else:
                for band in dataset_info["bands"]:
                    md.append(f"| `{band}` | 未知 | TODO: 添加描述 |\n")
            md.append("\n")
            
            # 详细波段信息
            if "band_details" in dataset_info:
                md.append("### 波段详细信息\n\n")
                for band in dataset_info["band_details"]:
                    if "error" not in band:
                        md.append(f"#### `{band['name']}`\n")
                        md.append(f"- **数据类型**: {band.get('data_type', '未知')}\n")
                        if band.get('dimensions'):
                            md.append(f"- **维度**: {band['dimensions']}\n")
                        md.append(f"- **坐标系统**: {band.get('crs', '未知')}\n")
                        md.append("\n")
        
        # 投影和分辨率
        if "projection" in dataset_info:
            md.append("## 🗺️ 空间信息\n")
            proj = dataset_info["projection"]
            if isinstance(proj, dict):
                md.append(f"- **坐标系统**: `{proj.get('crs', '未知')}`\n")
                if 'transform' in proj:
                    transform = proj['transform']
                    if len(transform) >= 1:
                        resolution = abs(transform[0])
                        md.append(f"- **空间分辨率**: {resolution} 度 (约 {resolution * 111:.2f} km)\n")
            md.append("\n")
        
        # 属性信息
        if "sample_properties" in dataset_info and dataset_info["sample_properties"]:
            md.append("## 🏷️ 属性信息\n")
            md.append("以下是第一张影像的示例属性：\n\n")
            md.append("| 属性名称 | 示例值 |\n")
            md.append("|---------|--------|\n")
            for key, value in dataset_info["sample_properties"].items():
                if isinstance(value, (int, float, str, bool)):
                    md.append(f"| `{key}` | `{value}` |\n")
                else:
                    md.append(f"| `{key}` | `{type(value).__name__}` |\n")
            md.append("\n")
        
        # 使用示例
        md.append("## 💻 使用示例\n")
        md.append("### Python (Earth Engine API)\n")
        md.append("```python\n")
        md.append("import ee\n")
        md.append("ee.Initialize()\n\n")
        md.append(f'# 加载数据集\n')
        md.append(f'dataset = ee.ImageCollection("{dataset_id}")\n\n')
        md.append('# 过滤时间范围\n')
        md.append('filtered = dataset.filterDate("2021-01-01", "2021-12-31")\n\n')
        md.append('# 过滤空间范围\n')
        md.append('roi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])\n')
        md.append('filtered = filtered.filterBounds(roi)\n\n')
        if dataset_info.get("bands"):
            md.append(f'# 选择波段\n')
            first_band = dataset_info["bands"][0]
            md.append(f'selected = filtered.select("{first_band}")\n')
        md.append("```\n\n")
        
        # 数据访问
        md.append("## 🔗 数据访问\n")
        md.append(f"- **GEE 数据目录**: https://developers.google.com/earth-engine/datasets/catalog/{dataset_id.replace('/', '_')}\n")
        md.append(f"- **代码编辑器**: https://code.earthengine.google.com/\n")
        md.append("\n")
        
        # 引用信息
        md.append("## 📚 引用信息\n")
        md.append("> TODO: 添加数据集的引用信息\n")
        md.append("\n")
        
        # 注意事项
        md.append("## ⚠️ 注意事项\n")
        md.append("- 本文档由自动脚本生成，部分信息需要人工补充\n")
        md.append("- 使用前请查阅 GEE 官方文档获取最新信息\n")
        md.append("- 某些数据集可能需要特定的访问权限\n")
        md.append("\n")
        
        return "".join(md)


def main():
    """主函数：获取所有数据集信息并生成文档"""
    
    # 项目中使用的数据集列表
    datasets = {
        "IMERG": [
            "NASA/GPM_L3/IMERG_V07",
            "NASA/GPM_L3/IMERG_V06"
        ],
        "ERA5-Land": [
            "ECMWF/ERA5_LAND/DAILY_AGGR",
            "ECMWF/ERA5_LAND/HOURLY"
        ],
        "MODIS NDVI": [
            "MODIS/061/MOD13Q1",
            "MODIS/006/MOD13Q1",
            "MODIS/061/MYD13Q1"
        ]
    }
    
    # 初始化检查器
    inspector = GEEDatasetInspector()
    
    # 为每个数据集生成文档
    for category, dataset_ids in datasets.items():
        print(f"\n{'='*60}")
        print(f"处理类别: {category}")
        print(f"{'='*60}")
        
        for dataset_id in dataset_ids:
            print(f"\n📡 正在获取数据集信息: {dataset_id}")
            
            # 获取数据集信息
            info = inspector.get_dataset_info(dataset_id)
            
            # 生成 Markdown
            markdown = inspector.generate_markdown(info)
            
            # 保存文件
            safe_name = dataset_id.replace("/", "_")
            filename = f"GEE_{safe_name}.md"
            filepath = f"/home/hl/workspace/rs_kalman_soil/knowledge/{filename}"
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            print(f"✅ 已生成文档: {filename}")
            
            # 打印摘要
            if info.get("status") == "可访问":
                print(f"   - 波段数: {len(info.get('bands', []))}")
                print(f"   - 首张影像日期: {info.get('first_image_date', '未知')}")
            else:
                print(f"   - 错误: {info.get('error', '未知错误')}")
    
    print(f"\n{'='*60}")
    print("✅ 所有数据集文档已生成完成！")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
