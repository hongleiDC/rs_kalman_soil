# CYGNSS L1 v3.2 Structure Scan

## Files Sampled
- /media/hl/Expansion/CYGNSS/CYGNSS_L1_V3.2/2021/7/cyg01.ddmi.s20210701-000000-e20210701-235959.l1.power-brcs.a32.d33.nc
- /media/hl/Expansion/CYGNSS/CYGNSS_L1_V3.2/2021/7/cyg02.ddmi.s20210701-000000-e20210701-235959.l1.power-brcs.a32.d33.nc
- /media/hl/Expansion/CYGNSS/CYGNSS_L1_V3.2/2021/7/cyg03.ddmi.s20210701-000000-e20210701-235959.l1.power-brcs.a32.d33.nc
- /media/hl/Expansion/CYGNSS/CYGNSS_L1_V3.2/2021/7/cyg04.ddmi.s20210701-000000-e20210701-235959.l1.power-brcs.a32.d33.nc
- /media/hl/Expansion/CYGNSS/CYGNSS_L1_V3.2/2021/7/cyg05.ddmi.s20210701-000000-e20210701-235959.l1.power-brcs.a32.d33.nc
- /media/hl/Expansion/CYGNSS/CYGNSS_L1_V3.2/2021/7/cyg06.ddmi.s20210701-000000-e20210701-235959.l1.power-brcs.a32.d33.nc
- /media/hl/Expansion/CYGNSS/CYGNSS_L1_V3.2/2021/7/cyg07.ddmi.s20210701-000000-e20210701-235959.l1.power-brcs.a32.d33.nc
- /media/hl/Expansion/CYGNSS/CYGNSS_L1_V3.2/2021/7/cyg08.ddmi.s20210701-000000-e20210701-235959.l1.power-brcs.a32.d33.nc

## NetCDF Dimensions
| Dimension | Min Size | Max Size | Examples |
| --- | --- | --- | --- |
| ddm | 4 | 4 | 4, 4, 4, 4… |
| delay | 17 | 17 | 17, 17, 17, 17… |
| doppler | 11 | 11 | 11, 11, 11, 11… |
| lat_5km | 5 | 5 | 5, 5, 5, 5… |
| lon_5km | 5 | 5 | 5, 5, 5, 5… |
| sample | 170240 | 172778 | 172778, 170240, 172306, 172778… |

## Key Coordinates
| Coordinate | Dims (files) | Long Name | Units |
| --- | --- | --- | --- |
| ddm_timestamp_utc | sample (8 files) | DDM sample timestamp - UTC |  |
| sp_lat | sample×ddm (8 files) | Specular point latitude | degrees_north |
| sp_lon | sample×ddm (8 files) | Specular point longitude | degrees_east |
| sp_inc_angle | sample×ddm (8 files) | Specular point incidence angle | degree |

## Reflectivity Candidates
| Variable | Units | Valid % | Mean | Std |
| --- | --- | --- | --- | --- |
| reflectivity_peak | linear | 86.2% | 0.042 | 5.962 |
| ddm_nbrcs | 1 | 53.5% | 54.168 | 1961.490 |
| ddm_nbrcs_center | 1 | 23.3% | 200.072 | 2207.366 |
| ddm_nbrcs_peak | 1 | 23.3% | 600.157 | 6037.359 |

## ddm_ant Distribution
| ddm_ant value | Observations |
| --- | --- |
| 2 | 3093919 |
| 3 | 2409893 |

## quality_flags_2 Sample
| quality_flags_2 value | Files containing |
| --- | --- |
| 0 | 8 |
| 2 | 8 |
| 16 | 8 |
| 512 | 8 |
| 514 | 8 |
| 1024 | 8 |
| 1026 | 8 |
| 1040 | 8 |
| 1536 | 8 |
| 1538 | 8 |

## CYGNSS Level-1 v3.2 Data Dictionary (Excel Extract)

**Document Metadata**
- Version 11
- UM Document 0148-0346-1
- S. Musko, T. Butler, A. Russel, C. Ruf, D. McKague, S. Gleason, M. Al-Khaldi
- Date 2025-02-xx

**Changes from version 10**
- 1. Adding non-fatal "preliminary_gps_ant_knowledge" flag
- 2. Reserving spare bit for CDR trackwise operations

**Acronyms and Abbreviations**
| Acronym | Definition |
| --- | --- |
| BRCS | Bistatic Radar Cross Section |
| CCSDS | Consultative Committee for Space Data Systems |
| CF | Climate and Forecast |
| DDM | Delay Doppler Map |
| DDMI | Delay Doppler Map Instrument |
| E2ES | CYGNSS End to End Simulator |
| ECEF | Earth Centered, Earth Fixed |
| ECI | Earth Centered Inertial |
| EIRP | Effective Isotropic Radiated Power |
| FOM | Figure of Merit |
| FSW | Flight Software |
| GPS | Global Positioning System |
| L1 | Level 1 |
| LNA | Low Noise Amplifier |
| NBRCS | Normalized BRCS |
| NST | Nano Start Tracker |
| PRN | Pseudo Random Noise |
| RCG | Range Corrected Gain |
| SP | Specular Point |
| SV | GPS Space Vehicle |
| UM | University of Michigan |
| UTC | Coordinated Universal Time |

**Fill Values**: Unless otherwise indicated, -9999 is used to represent invalid short, int, float and double values. Unless otherwise indicated, -99 is used to represent invalid byte values.

### Global Values
| Name | Long Name | Type | Units | Dimensions | Comment | Comment (CN) |
| --- | --- | --- | --- | --- | --- | --- |
| time_coverage_start | <none> | file attribute, string | <none> | <none> | ddm_timestamp_utc of the first sample in the file in ISO-8601 form | 文件中第一个样本的 ddm_timestamp_utc，格式为 ISO-8601 |
| time_coverage_end | <none> | file attribute, string | <none> | <none> | ddm_timestamp_utc of the last sample in the file in ISO-8601 form | 文件中最后一个样本的 ddm_timestamp_utc，格式为 ISO-8601 |
| time_coverage_duration | <none> | file attribute, string | <none> | <none> | The time interval between time_coverage_start and time_coverage_end in ISO1806 form | time_coverage_start 和 time_coverage_end 之间的时间间隔，格式为 ISO-1806 |
| time_coverage_resolution | <none> | file attribute, string | <none> | <none> | The nominal time interval between samples in ISO1806 form | 样本之间的名义时间间隔，格式为 ISO-1806 |
| spacecraft_id | CCSDS spacecraft identifier | short | 1 | <none> | The CCSDS spacecraft identifier: 0xF7 (247): CYGNSS 1 0xF9 (249): CYGNSS 2 0x2B (43): CYGNSS 3 0x2C (44): CYGNSS 4 0x2F (47): CYGNSS 5 0x36 (54): CYGNSS 6 0x37 (55): CYGNSS 7 0x49 (73): CYGNSS 8 0x00 (0): E2ES 0x0E (14): engineering model 0x0D (15): default 0xFF (255): unknown | CCSDS 航天器标识符： 0xF7 (247): CYGNSS 1 0xF9 (249): CYGNSS 2 0x2B (43): CYGNSS 3 0x2C (44): CYGNSS 4 0x2F (47): CYGNSS 5 0x36 (54): CYGNSS 6 0x37 (55): CYGNSS 7 0x49 (73): CYGNSS 8 0x00 (0): E2ES 0x0E (14): 工程模型 0x0D (15): 默认 0xFF (255): 未知 |
| spacecraft_num | CYGNSS spacecraft number | byte | 1 | <none> | The CYGNSS spacecraft number: Ranges from 1 through 8 and 99. 1 through 8 are on-orbit spacecraft. 99 is the CYGNSS end-to-end simulator. | CYGNSS 航天器编号：范围从 1 到 8 和 99。1 到 8 是在轨航天器。99 是 CYGNSS 端到端模拟器。 |
| ddm_source | Level 0 data source | byte | <none> | <none> | The source of the Level 0 DDM raw counts and metadata. 0 = End-End Simulator (E2ES) 1 = GPS signal simulator 2 = CYGNSS spacecraft 3 = Source unknown | 级别 0 DDM 原始计数和元数据的来源。 0 = 端到端模拟器 (E2ES) 1 = GPS 信号模拟器 2 = CYGNSS 航天器 3 = 来源未知 |
| ddm_time_type_selector | DDM sample time type selector | byte | <none> | <none> | Determines the position of ddm_timestamp_utc relative to the DDM sampling period. Set to "Middle of DDM sampling period" for nominal science operations. Other settings are used for pre-launch testing only. 0 = Start of DDM sampling period (used for pre-launch testing only) 1 = Middle of DDM sampling period 2 = End of DDM sampling period (used for pre-launch testing only) 3 = pvt_timestamp_utc (used for pre-launch testing only) | 确定 ddm_timestamp_utc 相对于 DDM 采样周期的位置。对于名义科学操作设置为“DDM 采样周期的中间”。其他设置仅用于发射前测试。 0 = DDM 采样周期开始 (仅用于发射前测试) 1 = DDM 采样周期中间 2 = DDM 采样周期结束 (仅用于发射前测试) 3 = pvt_timestamp_utc (仅用于发射前测试) |
| delay_resolution | DDM delay bin resolution | float | 1 | <none> | DDM delay bin resolution in chips. One chip is equal to 1/1,023,000 seconds. | DDM 延迟箱分辨率，以芯片为单位。一个芯片等于 1/1,023,000 秒。 |
| dopp_resolution | DDM Doppler bin resolution | float | s-1 | <none> | DDM Doppler bin resolution in Hz | DDM 多普勒箱分辨率，以赫兹为单位。 |
| l1_algorithm_version | <none> | file attribute, string | <none> | <none> | The version number of the L1 processing algorithm. | L1 处理算法的版本号。 |
| l1_data_version | <none> | file attribute, string | <none> | <none> | The version number of the L1 data. | L1 数据的版本号。 |
| lna_data_version | <none> | file attribute, string | <none> | <none> | The version number of the LNA data lookup table. | LNA 数据查找表的版本号。 |
| eff_scatter_version | <none> | file attribute, string | <none> | <none> | The version number of the effective scattering area lookup table. | 有效散射面积查找表的版本号。 |
| nadir_ant_data_version | <none> | file attribute, string | <none> | <none> | The version number of the nadir antenna data lookup table. | 近天顶天线数据查找表的版本号。 |
| zenith_ant_data_version | <none> | file attribute, string | <none> | <none> | The version number of the zenith antenna data lookup table. | 天顶天线数据查找表的版本号。 |
| ant_temp_version | <none> | file attribute, string | <none> | <none> | The version number of the radiometric antenna temperature lookup table. | 辐射天线温度查找表的版本号。 |
| prn_sv_maps_version | <none> | file attribute, string | <none> | <none> | The version number of the PRN to SV lookup table. | PRN 到 SV 查找表的版本号。 |
| gps_eirp_param_version | <none> | file attribute, string | <none> | <none> | The version number of the GPS effective isotropic radiated power parameter lookup table | GPS 有效各向同性辐射功率参数查找表的版本号。 |
| land_mask_version | <none> | file attribute, string | <none> | <none> | The version number of the Earth land mask lookup table. | 地球陆地掩模查找表的版本号。 |
| near_land_mask_version | <none> | file attribute, string | <none> | <none> | The version number of the Earth near-land mask lookup table. | 地球近陆掩模查找表的版本号。 |
| very_near_land_mask_version | <none> | file attribute, string | <none> | <none> | The version number of the Earth very-near-land mask lookup table. | 地球非常近陆掩模查找表的版本号。 |
| open_ocean_mask_version | <none> | file attribute, string | <none> | <none> | The version number of the open ocean mask lookup table. | 开放海洋掩模查找表的版本号。 |
| ddm_a2d_version | <none> | file attribute, string | <none> | <none> | The version number of the DDM digital to analog power conversion lookup table. | DDM 数字到模拟功率转换查找表的版本号。 |
| milky_way_version | <none> | file attribute, string | <none> | <none> | The version number of the Milky Way mask lookup table. | 银河掩模查找表的版本号。 |
| fresnel_coeff_version | <none> | file attribute, string | <none> | <none> | The version number of the Fresnel coefficient lookup table. | 菲涅尔系数查找表的版本号。 |
| brcs_uncert_lut_version | <none> | file attribute, string | <none> | <none> | The version number of the BRCS uncertainty lookup table. | BRCS 不确定性查找表的版本号。 |
| ddma_les_sel_luts_version | <none> | file attribute, string | <none> | <none> | The version number of the NBRCS (formerly known as DDMA) and LES bin selection table. | NBRCS（以前称为 DDMA）和 LES 选择表的版本号。 |
| mean_sea_surface_version | <none> | file attribute, string | <none> | <none> | The version of the mean sea surface lookup table. | 平均海面查找表的版本号。 |
| zenith_specular_ratio_gain_version | <none> | file attribute, string | <none> | <none> | The version of the zenith speculat ratio gain lookup table. | 天顶镜面反射比增益查找表的版本号。 |
| zenith_calibration_params_version | <none> | file attribute, string | <none> | <none> | The version of the zenith calibration parameters lookup table. | 天顶校准参数查找表的版本号。 |
| anomalous_sampling_periods_version | <none> | file attribute, string | <none> | <none> | The version of the anomalous sampling periods lookup table. | 异常采样周期查找表的版本号。 |
| zenith_sig_i2_q2_correction_version | <none> | file attribute, string | <none> | <none> | The version of the zenith signal I2 Q2 correction factor lookup table. | 天顶信号 I2 Q2 校正因子查找表的版本号。 |
| ddm_nbrcs_scale_factor_version | <none> | file attribute, string | <none> | <none> | The version of the DDM NBRCS correction factor lookup table. | DDM NBRCS 校正因子查找表的版本号。 |
| eirp_scale_factor_version | <none> | file attribute, string | <none> | <none> | The version of the EIRP correction factor for the Feb 14, 2020 power shift lookup table. | 2020年2月14日功率转移的 EIRP 校正因子查找表的版本号。 |
| zenith_lna_gain_correction_version | <none> | file attribute, string | <none> | <none> | The version of the zenith LNA gain correction lookup table. | 天顶 LNA 增益校正查找表的版本号。 |
| bin_ratio_qc_version | <none> | file attribute, string | <none> | <none> | The version of the bin ratio QC correction factor lookup table. | 箱比 QC 校正因子查找表的版本号。 |
| modis_land_cover_version | <none> | file attribute, string | <none> | <none> | The version of the MODIS land cover lookup table. | MODIS 土地覆盖查找表的版本号。 |
| srtm_dem_version | <none> | file attribute, string | <none> | <none> | The version of the STRM DEM lookup table. Derived from 2018 Global Surface Water Explorer | SRTM DEM 查找表的版本号。 来源于 2018 年全球表面水探测器 |
| dtu_10_version | <none> | file attribute, string | <none> | <none> | The version of the DTU10 lookup table. | DTU10 查找表的版本号。 |
| srtm_slope_version | <none> | file attribute, string | <none> | <none> | The version of the SRTM slope lookup table. Derived from 2018 Global Surface Water Explorer | SRTM 斜率查找表的版本号。 来源于 2018 年全球表面水探测器 |
| surface_water_map_version | <none> | file attribute, string | <none> | <none> | The version of the Pekel surface water map lookup table. Derived from 2018 Global Surface Water Explorer | Pekel 表面水地图查找表的版本号。 来源于 2018 年全球表面水探测器 |
| per_bin_ant_version | <none> | file attribute, string | <none> | <none> | The version of the per-bin antenna gain lookup table. | 每个箱的天线增益查找表的版本号。 |
| Per-Sample Values |  |  |  |  |  | 每个样本值 |
| ddm_timestamp_utc | DDM sample timestamp - UTC | double | seconds since time_coverage_start | sample | DDM sample time. The number of seconds since time_coverage_start with nanosecond resolution. Its position relative to the DDM sampling period is determined by ddm_time_type_selector. Some metadata required for DDM calibration are generated relative to pvt_timestamp_utc or att_timestamp_utc. These metadata are interpolated to ddm_timestamp_utc before being used for DDM calibration. Note that the DDM sampling period is not synchronized with the UTC change of second and can occur at any time relative to the UTC change of second. | DDM 样本时间。自 time_coverage_start 起的秒数，精确到纳秒。其相对 DDM 采样周期的位置由 ddm_time_type_selector 决定。一些用于 DDM 校准的元数据是相对于 pvt_timestamp_utc 或 att_timestamp_utc 生成的，这些元数据在用于 DDM 校准之前插值到 ddm_timestamp_utc。请注意，DDM 采样周期与 UTC 秒的变化不同步，可以在 UTC 秒的任何时候发生。 |
| ddm_timestamp_gps_week | DDM sample timestamp - GPS week | int | week | sample | The GPS week number of ddm_timestamp_utc | ddm_timestamp_utc 的 GPS 周编号 |
| ddm_timestamp_gps_sec | DDM sample timestamp - GPS seconds | double | second | sample | The GPS second of week of ddm_timestamp_utc with nanosecond resolution | ddm_timestamp_utc 所在周的 GPS 秒，精确到纳秒。 |
| pvt_timestamp_utc | PVT timestamp - UTC | double | seconds since time_coverage_start | sample | The spacecraft position and velocity epoch. The number of seconds since time_coverage_start with nanosecond resolution. This is the timestamp of the position and velocity reported by the DDMI. This is also the timestamp of the most recent GPS pulse per second. | 航天器位置和速度的纪元。自 time_coverage_start 起的秒数，精确到纳秒。这是 DDMI 所报告的位置信息和速度的时间戳，也是最近的 GPS 每秒脉冲的时间戳。 |
| pvt_timestamp_gps_week | PVT timestamp - GPS Week | int | week | sample | The GPS week number of pvt_timestamp_utc | pvt_timestamp_utc 的 GPS 周编号 |
| pvt_timestamp_gps_sec | PVT timestamp - GPS Seconds | double | second | sample | The GPS second of week of pvt_timestamp_utc with nanosecond resolution. | pvt_timestamp_utc 所在周的 GPS 秒，精确到纳秒。 |
| att_timestamp_utc | Attitude timestamp - UTC | double | seconds since time_coverage_start | sample | The spacecraft attitude epoch. The number of seconds since time_coverage_start with nanosecond resolution. This is the timestamp of the spacecraft attitude reported by the spacecraft attitude determinination system. | 航天器姿态的纪元。自 time_coverage_start 起的秒数，精确到纳秒。这是航天器姿态由航天器姿态确定系统报送的时间戳。 |
| att_timestamp_gps_week | Attitude timestamp - GPS Week | int | week | sample | The GPS week number of att_timestamp_utc | att_timestamp_utc 的 GPS 周编号 |
| att_timestamp_gps_sec | Attitude timestamp - GPS Seconds | double | second | sample | The GPS second of week of att_timestamp_utc with nanosecond resolution | att_timestamp_utc 所在周的 GPS 秒，精确到纳秒。 |
| sc_pos_x | Spacecraft position X at DDM sample time | int | meter | sample | The X component of the spacecraft WGS84 reference frame ECEF position, in meters, at ddm_timestamp_utc. Fill value is -99999999. | 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 位置的 X 组件，单位为米。填充值为 -99999999。 |
| sc_pos_y | Spacecraft position Y at DDM sample time | int | meter | sample | The Y component of the spacecraft WGS84 reference frame ECEF position, in meters, at ddm_timestamp_utc. Fill value is -99999999. | 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 位置的 Y 组件，单位为米。填充值为 -99999998。 |
| sc_pos_z | Spacecraft position Z at DDM sample time | int | meter | sample | The Z component of the spacecraft WGS84 reference frame ECEF position, in meters, at ddm_timestamp_utc. Fill value is -99999999. | 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 位置的 Z 组件，单位为米。填充值为 -99999998。 |
| sc_vel_x | Spacecraft velocity X at DDM sample time | int | meter s-1 | sample | The X component of the spacecraft WGS84 reference frame ECEF velocity, in m/s, at ddm_timestamp_utc | 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 速度的 X 组件，单位为米/秒。 |
| sc_vel_y | Spacecraft velocity Y at DDM sample time | int | meter s-1 | sample | The Y component of the spacecraft WGS84 reference frame ECEF velocity, in m/s, at ddm_timestamp_utc | 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 速度的 Y 组件，单位为米/秒。 |
| sc_vel_z | Spacecraft velocity Z at DDM sample time | int | meter s-1 | sample | The Z component of the spacecraft WGS84 reference frame ECEF velocity , in m/s, at ddm_timestamp_utc. | 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 速度的 Z 组件，单位为米/秒。 |
| sc_pos_x_pvt | Spacecraft position X at PVT time | int | meter | sample | The X component of the spacecraft WGS84 reference frame ECEF position, in meters, at pvt_timestamp_utc. Fill value is -99999999. | 航天器在 pvt_timestamp_utc 时的 WGS84 参考框架 ECEF 位置的 X 组件，单位为米。填充值为 -99999999。 |
| sc_pos_y_pvt | Spacecraft position Y at PVT time | int | meter | sample | The Y component of the spacecraft WGS84 reference frame ECEF position, in meters, at pvt_timestamp_utc. Fill value is -99999999. | 航天器在 pvt_timestamp_utc 时的 WGS84 参考框架 ECEF 位置的 Y 组件，单位为米。填充值为 -99999999。 |
| sc_pos_z_pvt | Spacecraft position Z at PVT time | int | meter | sample | The Z component of the spacecraft WGS84 reference frame ECEF position, in meters, at pvt_timestamp_utc. Fill value is -99999999. | 航天器在 pvt_timestamp_utc 时的 WGS84 参考框架 ECEF 位置的 Z 组件，单位为米。填充值为 -99999999。 |
| sc_vel_x_pvt | Spacecraft velocity X at PVT time | int | meter s-1 | sample | The X component of the spacecraft WGS84 reference frame ECEF velocity, in m/s, at pvt_timestamp_utc | 航天器在 pvt_timestamp_utc 时的 WGS84 参考框架 ECEF 速度的 X 组件，单位为米/秒。 |
| sc_vel_y_pvt | Spacecraft velocity Y at PVT time | int | meter s-1 | sample | The Y component of the spacecraft WGS84 reference frame ECEF velocity, in m/s, at pvt_timestamp_utc | 航天器在 pvt_timestamp_utc 时的 WGS84 参考框架 ECEF 速度的 Y 组件，单位为米/秒。 |
| sc_vel_z_pvt | Spacecraft velocity Z at PVT time | int | meter s-1 | sample | The Z component of the spacecraft WGS84 reference frame ECEF velocity, in m/s, at pvt_timestamp_utc | 航天器在 pvt_timestamp_utc 时的 WGS84 参考框架 ECEF 速度的 Z 组件，单位为米/秒。 |
| nst_att_status | NST attitude status | byte | <none> | sample | The nano star tracker attitude status. 0 = OK 1 = NOT_USED2 2 = BAD 3 = TOO_FEW_STARS 4 = QUEST_FAILED 5 = RESIDUALS_TOO_HIGH 6 = TOO_CLOSE_TO_EDGE 7 = PIX_AMP_TOO_LOW 8 = PIX_AMP_TOO_HIGH 9 = BACKGND_TOO_HIGH 10 = TRACK_FAILURE 11 = PIX_SUM_TOO_LOW 12 = UNUSED 13 = TOO_DIM_FOR_STARID 14 = TOO_MANY_GROUPS 15 = TOO_FEW_GROUPS 16 = CHANNEL_DISABLED 17 = TRACK_BLK_OVERLAP 18 = OK_FOR_STARID 19 = TOO_CLOSE_TO_OTHER 20 = TOO_MANY_PIXELS 21 = TOO_MANY_COLUMNS 22 = TOO_MANY_ROWS | 纳米星跟踪器的姿态状态。 0 = 正常 1 = 未使用 2 = 错误 3 = 星星数量过少 4 = 追踪失败 5 = 残差过高 6 = 过于接近边缘 7 = 像素增益过低 8 = 像素增益过高 9 = 背景噪声过高 10 = 追踪失败 11 = 像素和过低 12 = 未使用 13 = 太暗以至于无法识别星星 14 = 星群过多 15 = 星群过少 16 = 通道被禁用 17 = 追踪块重叠 18 = 适合星星识别 19 = 过于接近其他 20 = 像素过多 21 = 列过多 22 = 行过多 |
| sc_roll | Spacecraft attitude roll angle at DDM sample time | float | radian | sample | Spacecraft roll angle relative to the orbit frame, in radians at ddm_timestamp_utc | 航天器相对于轨道框架的滚转角，单位为弧度，时间为 ddm_timestamp_utc。 |
| sc_pitch | Spacecraft attitude pitch angle at DDM sample time | float | radian | sample | Spacecraft pitch angle relative to the orbit frame, in radians at ddm_timestamp_utc | 航天器相对于轨道框架的俯仰角，单位为弧度，时间为 ddm_timestamp_utc。 |
| sc_yaw | Spacecraft attitude yaw angle at DDM sample time | float | radian | sample | Spacecraft yaw angle relative to the orbit frame, in radians at ddm_timestamp_utc | 航天器相对于轨道框架的偏航角，单位为弧度，时间为 ddm_timestamp_utc。 |
| sc_roll_att | Spacecraft attitude roll angle at attitude time | float | radian | sample | Spacecraft roll angle relative to the orbit frame, in radians at att_timestamp_utc | 航天器相对于轨道框架的滚转角，单位为弧度，时间为 att_timestamp_utc。 |
| sc_pitch_att | Spacecraft attitude pitch angle at attitude time | float | radian | sample | Spacecraft pitch angle relative to the orbit frame, in radians at att_timestamp_utc | 航天器相对于轨道框架的俯仰角，单位为弧度，时间为 att_timestamp_utc。 |
| sc_yaw_att | Spacecraft attitude yaw angle at attitude time | float | radian | sample | Spacecraft yaw angle relative to the orbit frame, in radians at att_timestamp_utc | 航天器相对于轨道框架的偏航角，单位为弧度，时间为 att_timestamp_utc。 |
| sc_lat | Sub-satellite point latitude | float | degrees_north | sample | Subsatellite point latitude, in degrees North, at ddm_timestamp_utc | 副卫星点纬度，单位为北度，时间为 ddm_timestamp_utc。 |
| sc_lon | Sub-satellite point longitude | float | degrees_east | sample | Subsatellite point longitude, in degrees East, at ddm_timestamp_utc | 副卫星点经度，单位为东度，时间为 ddm_timestamp_utc。 |
| sc_alt | Spacecraft altitude | int | meter | sample | Spacecraft altitude above WGS-84 ellipsoid, in meters, at ddm_timestamp_utc | 航天器相对于 WGS-84 椭球体的高度，单位为米，时间为 ddm_timestamp_utc。 |
| commanded_sc_roll | Commanded spacecraft attitude roll angle | float | radians | sample | Commanded spacecraft attitude roll angle, in radians at ddm_timestamp_utc. This value is updated every 10 seconds from the ENG_HI packet. | 命令的航天器姿态滚转角，单位为弧度，时间为 ddm_timestamp_utc。该值每 10 秒从 ENG_HI 数据包更新一次。 |
| rx_clk_bias | GPS receiver clock bias | float | meter | sample | The receiver clock bias (in seconds) multiplied by the speed of light as reported by the DDMI, interpolated to ddm_timestamp_utc, in meters. | 接收器时钟偏差（以秒为单位）乘以光速，经过 DDMI 报告，插值到 ddm_timestamp_utc，单位为米。 |
| rx_clk_bias_rate | GPS receiver clock bias rate | float | meter s-1 | sample | The receiver clock bias rate (in seconds/second) multiplied by the speed of light as reported by the DDMI, interpolated to ddm_timestamp_utc, in m/s. | 接收器时钟偏差率（以秒/秒为单位）乘以光速，经过 DDMI 报告，插值到 ddm_timestamp_utc，单位为米/秒。 |
| rx_clk_bias_pvt | GPS receiver clock bias at PVT time | float | meter | sample | The receiver clock bias (in seconds) multiplied by the speed of light as reported by the DDMI at pvt_timestamp_utc, in meters. | 接收器时钟偏差（以秒为单位）乘以光速，经过 DDMI 报告，时间为 pvt_timestamp_utc，单位为米。 |
| rx_clk_bias_rate_pvt | GPS receiver clock bias rate at PVT time | float | meter s-1 | sample | The receiver clock bias rate (in seconds/second) multiplied by the speed of light as reported by the DDMI, at pvt_timestamp_utc, in m/s. | 接收器时钟偏差率（以秒/秒为单位）乘以光速，经过 DDMI 报告，时间为 pvt_timestamp_utc，单位为米/秒。 |
| lna_temp_nadir_starboard | Starboard antenna LNA temperature | float | degree_Celsius | sample | The temperature of the starboard antenna LNA at ddm_timestamp_utc, in degrees C. | 右舷天线在 ddm_timestamp_utc 时的 LNA 温度，单位为摄氏度。 |
| lna_temp_nadir_port | Port antenna LNA temperature | float | degree_Celsius | sample | The temperature of the port antenna LNA at ddm_timestamp_utc, in degrees C. | 左舷天线在 ddm_timestamp_utc 时的 LNA 温度，单位为摄氏度。 |
| lna_temp_zenith | Zenith antenna LNA temperature | float | degree_Celsius | sample | The temperature of the zenith antenna LNA at ddm_timestamp_utc, in degrees C. | 天顶天线在 ddm_timestamp_utc 时的 LNA 温度，单位为摄氏度。 |
| ddm_end_time_offset | DDM end time offset | int | 1e-9 s | sample | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L1 netCDF 诊断变量。 |
| bit_ratio_lo_hi_starboard | Starboard low/high bit counter ratio | float | 1 | sample | Bin ratio of the of the starboard antenna defined as (plus_1_cnts + minus_1_cnts) / (plus_3_cnts + minus_3_cnts). | 右舷天线的箱比率，定义为 (plus_1_cnts + minus_1_cnts) / (plus_3_cnts + minus_3_cnts)。 |
| bit_ratio_lo_hi_port | Port low/high bit counter ratio | float | 1 | sample | Bin ratio of the of the port antenna defined as (plus_1_cnts + minus_1_cnts) / (plus_3_cnts + minus_3_cnts). | 左舷天线的箱比率，定义为 (plus_1_cnts + minus_1_cnts) / (plus_3_cnts + minus_3_cnts)。 |
| bit_ratio_lo_hi_zenith | Zenith low/high bit counter ratio | float | 1 | sample | Bin ratio of the of the zenith antenna defined as (plus_1_cnts + minus_1_cnts) / (plus_3_cnts + minus_3_cnts). | 天顶天线的箱比率，定义为 (plus_1_cnts + minus_1_cnts) / (plus_3_cnts + minus_3_cnts)。 |
| bit_null_offset_starboard | Starboard bit count null offset | float | 1 | sample | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L1 netCDF 诊断变量。 |
| bit_null_offset_port | Port bit count null offset | float | 1 | sample | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L2 netCDF 诊断变量。 |
| bit_null_offset_zenith | Zenith bit count null offset | float | 1 | sample | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L3 netCDF 诊断变量。 |
| status_flags_one_hz | 1 Hz status flags | int | <none> | sample | One H+A112:F129z status flags. These flags apply to all four DDMs. 1 indicates presence of condition. Flag masks: 1 = Milky way in zenith antenna field of view 2 = Sun in zenith antenna field of view 4 = Sub-satellite point over open ocean 8 = Subsatellite point latitude ascending, i.e. sc_lat is increasing. | 1 Hz 状态标志。这些标志适用于所有四个 DDM。 1 表示存在条件。 标志掩码： 1 = 银河系在天顶天线视场中 2 = 太阳在天顶天线视场中 4 = 副卫星点位于开放海洋上 8 = 副卫星点纬度上升，即 sc_lat 正在增加。" |

### Per-DDM Values
| Name | Long Name | Type | Units | Dimensions | Comment | Comment (CN) |
| --- | --- | --- | --- | --- | --- | --- |
| prn_code | GPS PRN code | byte | 1 | sample, ddm | The PRN code of the GPS signal associated with the DDM. Ranges from 0 to 32. 0 = reflectometry channel idle. 1 through 32 = GPS PRN codes. | 与 DDM 相关的 GPS 信号的 PRN 代码。范围从 0 到 32。0 = 反射通道空闲。1 到 32 = GPS PRN 代码。 |
| sv_num | GPS space vehicle number | int | 1 | sample, ddm | The GPS unique space vehicle number that transmitted prn_code. | 发送 prn_code 的 GPS 唯一空间交通工具编号。 |
| track_id | DDM track ID | int | 1 | sample, ddm | A track is a temporally contiguous series of DDMs that have the same prn_code. Each track in the file is assigned a unique track_id starting with one. track_id ranges from 1 to N, where N is the total number of tracks in the file. | 一条跟踪是具有相同 prn_code 的 DDM 的时间连续系列。文件中的每条跟踪分配一个唯一的 track_id，从 1 开始。track_id 范围从 1 到 N，其中 N 是文件中的跟踪总数。 |
| ddm_ant | DDM antenna | byte | <none> | sample, ddm | The antenna that received the reflected GPS signal associated with the DDM. 0 = none 1 = zenith (never used) 2 = nadir_starboard 3 = nadir_port | 接收与 DDM 相关的反射 GPS 信号的天线。 0 = 无 1 = 天顶（从不使用） 2 = 近天顶右侧 3 = 近天顶左侧 |
| zenith_code_phase | Zenith signal code phase | float | 1 | sample, ddm | The DDMI-measured code phase of the direct GPS signal for prn_code interpolated to ddm_timestamp_utc. 0 <= zenith_code_phase < 1023.0. | DDMI 测量的与 prn_code 相关的直接 GPS 信号的码相位，插值到 ddm_timestamp_utc。0 <= zenith_code_phase < 1023.0. |
| sp_ddmi_delay_correction | Correction to DDMI specular point delay | float | 1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L1 netCDF 诊断变量。 |
| sp_ddmi_dopp_correction | Correction to DDMI specular point Doppler | float | s-1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L2 netCDF 诊断变量。 |
| add_range_to_sp | Additional range to specular point at DDM sample time | float | 1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L3 netCDF 诊断变量。 |
| add_range_to_sp_pvt | Additional range to specular point at PVT time | float | 1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L4 netCDF 诊断变量。 |
| sp_ddmi_dopp | DDMI Doppler at specular point | float | s-1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L5 netCDF 诊断变量。 |
| sp_fsw_delay | Flight software specular point delay | float | 1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L6 netCDF 诊断变量。 |
| sp_delay_error | Flight software specular point delay error | float | 1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L7 netCDF 诊断变量。 |
| sp_dopp_error | Flight software specular point Doppler error | float | s-1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L8 netCDF 诊断变量。 |
| fsw_comp_delay_shift | Flight software DDM compression delay shift | float | 1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L9 netCDF 诊断变量。 |
| fsw_comp_dopp_shift | Flight software DDM compression Doppler shift | float | s-1 | sample, ddm | For diagnostic use only. See UM document 148-0372 CYGNSS L1 netCDF Diagnostic Variables for more information. | 仅供诊断使用。有关更多信息，请参见 UM 文档 148-0372 CYGNSS L10 netCDF 诊断变量。 |
| prn_fig_of_merit | PRN selection Figure of Merit | byte | 1 | sample, ddm | The RCG Figure of Merit (FOM) for the DDM. Ranges from 0 through 15.The DDMI selects the four strongest specular points (SP) for DDM production. It ranks the strength of SPs using an antenna RCG map. The map converts the position of the SP in antenna azimuth and declination angles to an RCG FOM. 0 represents the least FOM value. 15 represents the greatest FOM value. | DDM 的 RCG 绩效指标 (FOM)。范围从 0 到 15。DDMI 选择四个最强的镜面点（SP）用于 DDM 生产。它使用天线 RCG 图进行排名，图将 SP 在天线方位和仰角的位置转换为 RCG FOM。0 表示最低的 FOM 值。15 表示最高的 FOM 值。 |
| tx_clk_bias | GPS transmitter clock bias | float | meter | sample, ddm | The GPS spacecraft (sv_num) clock time minus GPS constellation time in seconds times the speed of light, in meters. | GPS 航天器 (sv_num) 时钟时间减去 GPS 星座时间（单位为秒）乘以光速，单位为米。 |
| sp_lat | Specular point latitude | float | degrees_north | sample, ddm | Specular point latitude, in degrees North, at ddm_timestamp_utc | 镜面点纬度，单位为北度，时间为 ddm_timestamp_utc。 |
| sp_lon | Specular point longitude | float | degrees_east | sample, ddm | Specular point longitude, in degrees East, at ddm_timestamp_utc | 镜面点经度，单位为东度，时间为 ddm_timestamp_utc。 |
| sp_alt | Specular point altitude | float | meter | sample, ddm | Altitude of the specular point relative to the WGS 84 datum in meters, at ddm_timestamp_utc, as calculated on the ground. Note that an approximated DTU10 mean sea surface height model is used to calculate the specular point altitude. | 镜面点相对于 WGS 84 基准面的高度，单位为米，时间为 ddm_timestamp_utc。请注意，使用了近似的 DTU10 平均海平面高度模型来计算镜面点高度。 |
| sp_pos_x | Specular point position X | int | meter | sample, ddm | The X component of the specular point position in the ECEF coordinate system, in meters, at ddm_timestamp_utc, as calculated on the ground. Fill value is -99999999. | 镜面点在 ECEF 坐标系中的位置的 X 组件，单位为米，时间为 ddm_timestamp_utc。填充值为 -99999999。 |
| sp_pos_y | Specular point position Y | int | meter | sample, ddm | The Y component of the specular point position in the ECEF coordinate system, in meters, at ddm_timestamp_utc, as calculated on the ground. Fill value is -99999999. | 镜面点在 ECEF 坐标系中的位置的 Y 组件，单位为米，时间为 ddm_timestamp_utc。填充值为 -99999999。 |
| sp_pos_z | Specular point position Z | int | meter | sample, ddm | The Z component of the specular point position in the ECEF coordinate system, in meters, at ddm_timestamp_utc, as calculated on the ground. Fill value is -99999999. | 镜面点在 ECEF 坐标系中的位置的 Z 组件，单位为米，时间为 ddm_timestamp_utc。填充值为 -99999999。 |
| sp_vel_x | Specular point velocity X | int | meter s-1 | sample, ddm | The X component of the specular point velocity in the ECEF coordinate system, in m/s, at ddm_timestamp_utc, as calculated on the ground. | 镜面点在 ECEF 坐标系中的速度的 X 组件，单位为米/秒，时间为 ddm_timestamp_utc。 |
| sp_vel_y | Specular point velocity Y | int | meter s-1 | sample, ddm | The Y component of the specular point velocity in the ECEF coordinate system, in m/s, at ddm_timestamp_utc, as calculated on the ground. | 镜面点在 ECEF 坐标系中的速度的 Y 组件，单位为米/秒，时间为 ddm_timestamp_utc。 |
| sp_vel_z | Specular point velocity Z | int | meter s-1 | sample, ddm | The Z component of the specular point velocity in the ECEF coordinate system, in m/s, at ddm_timestamp_utc, as calculated on the ground. | 镜面点在 ECEF 坐标系中的速度的 Z 组件，单位为米/秒，时间为 ddm_timestamp_utc。 |
| sp_inc_angle | Specular point incidence angle | float | degree | sample, ddm | The specular point incidence angle, in degrees, at ddm_timestamp_utc. This is the angle between the line normal to the Earth's surface at the specular point and the line extending from the specular point to the spacecraft. See UM Doc. 148-0336, CYGNSS Science Data Processing Coordinate Systems Definitions. | 镜面点的入射角，单位为度，时间为 ddm_timestamp_utc。该角度是与镜面点表面法线之间的夹角。参见 UM 文档 148-0336，CYGNSS 科学数据处理坐标系定义。 |
| sp_theta_orbit | Specular point orbit frame theta angle | float | degree | sample, ddm | The angle between the orbit frame +Z axis and the line extending from the spacecraft to the specular point, in degrees, at ddm_timestamp_utc. See UM Doc. 148-0336, CYGNSS Science Data Processing Coordinate Systems Definitions. | 轨道框架 +Z 轴与从航天器延伸到镜面点之间的线的夹角，单位为度，时间为 ddm_timestamp_utc。参见 UM 文档 148-0336，CYGNSS 科学数据处理坐标系定义。 |
| sp_az_orbit | Specular point orbit frame azimuth angle | float | degree | sample, ddm | Let line A be the line that extends from the spacecraft to the specular point at ddm_timestamp_utc. Let line B be the projection of line A onto the orbit frame XY plane. sp_az_orbit is the angle between the orbit frame +X axis (the velocity vector) and line B, in degrees, at ddm_timestamp_utc. See UM Doc. 148-0336, CYGNSS Science Data Processing Coordinate Systems Definitions. | 让线 A 是从航天器延伸到镜面点的线（在 ddm_timestamp_utc）。让线 B 是线 A 投影到轨道框架 XY 平面上的线。sp_az_orbit 是轨道框架 +X 轴（速度向量）与线 B 之间的夹角，单位为度，时间为 ddm_timestamp_utc。参见 UM 文档 148-0336，CYGNSS 科学数据处理坐标系定义。 |
| sp_theta_body | Specular point body frame theta angle | float | degree | sample, ddm | The angle between the spacecraft body frame +Z axis and the line extending from the spacecraft to the specular point, in degrees, at ddm_timestamp_utc. See UM Doc. 148-0336, CYGNSS Science Data Processing Coordinate Systems Definitions. | 航天器机体框架 +Z 轴与从航天器延伸到镜面点之间的线的夹角，单位为度，时间为 ddm_timestamp_utc。参见 UM 文档 148-0336，CYGNSS 科学数据处理坐标系定义。 |
| sp_az_body | Specular point body frame azimuth angle | float | degree | sample, ddm | Let line A be the line that extends from the spacecraft to the specular point, at ddm_timestamp_utc. Let line B be the projection of line A onto the spacecraft body frame XY plane. sp_az_body is the angle between the spacecraft body frame +X axis and line B, in degrees, at ddm_timestamp_utc. See UM Doc. 148-0336, CYGNSS Science Data Processing Coordinate Systems Definitions. | 让线 A 是从航天器延伸到镜面点的线（在 ddm_timestamp_utc）。让线 B 是线 A 投影到航天器机体框架 XY 平面上的线。sp_az_body 是航天器机体框架 +X 轴与线 B 之间的夹角，单位为度，时间为 ddm_timestamp_utc。参见 UM 文档 148-0336，CYGNSS 科学数据处理坐标系定义。 |
| sp_rx_gain | Specular point Rx antenna gain | float | dBi | sample, ddm | The receive antenna gain in the direction of the specular point, in dBi, at ddm_timestamp_utc. | 镜面点方向上的接收天线增益，单位为 dBi，时间为 ddm_timestamp_utc。 |
| gps_eirp | GPS effective isotropic radiated power | float | watt | sample, ddm | The effective isotropic radiated power (EIRP) of the L1 C/A code signal within ± 1 MHz of the L1 carrier radiated by space vehicle, sv_num, in the direction of the specular point, in Watts, at ddm_timestamp_utc. Variations in GPS transmit power are tracked by the direct signal power measured by the navigation receiver. One second samples are smoothed by a +/- 10 second running average. | 在 ddm_timestamp_utc 时，GPS 航天器 (sv_num) 辐射的 ± 1 MHz 内 L1 C/A 信号的有效各向同性辐射功率 (EIRP)，单位为瓦特。GPS 传输功率的变化由导航接收机测量的直接信号功率跟踪。每秒的样本通过 +/- 10 秒的移动平均进行平滑处理。 |
| static_gps_eirp | Static GPS effective isotropic radiated power | float | watt | sample, ddm | Heritage version of gps_eirp (v2.1 and earlier) that assumed a static value for the power level of the L1 signal transmitted by the GPS satellite, prior to implementation of dynamic gps_eirp monitoring in August 2018. | GPS_eirp（版本 2.1 及之前）的传统版本，假定 GPS 卫星发射的 L1 信号功率水平为静态值，此前实施动态 gps_eirp 监测于 2018 年 8 月。 |
| gps_tx_power_db_w | GPS SV transmit power | float | dbW | sample, ddm | Power input to SV Tx antenna. Referenced from the heritage version of gps_eirp (v2.1 and earlier). | 输入到 SV Tx 天线的功率。参照 GPS_eirp（版本 2.1 及之前）的传统版本。 |
| gps_ant_gain_db_i | GPS SV transmit antenna gain | float | dBi | sample, ddm | SV antenna gain in the direction of the specular point. Referenced from the heritage version of gps_eirp (v2.1 and earlier). | SV 天线在镜面点方向上的增益。参照 GPS_eirp（版本 2.1 及之前）的传统版本。 |
| gps_off_boresight_angle_deg | GPS off boresight angle | float | degree | sample, ddm | SV antenna off boresight angle in the direction of the specular point | SV 天线在镜面点方向上的离轴角。 |
| ddm_snr | DDM signal to noise ratio | float | dB | sample, ddm | 10log(Smax/Navg), where Smax is the maximum value (in raw counts) in a single DDM bin and Navg is the the average per-bin raw noise counts. ddm_snr is in dB, at ddm_timestamp_utc. | 10log(Smax/Navg)，其中 Smax 是单个 DDM 盒中最大值（原始计数），Navg 是每盒的平均原始噪声计数。ddm_snr 易为 dB，时间为 ddm_timestamp_utc。 |
| ddm_noise_floor | DDM noise floor | float | 1 | sample, ddm | For non-black-body DDMs: Is equal to the average bin raw counts in the first 45 delay rows of the uncompressed 20 x 128 DDM, in counts, at ddm_timestamp_utc. For black body DDMs: Is equal to the average bin raw counts in all 128 delay rows of the uncompressed 20 x 128 DDM, in counts, at ddm_timestamp_utc. | 对于非黑体 DDM：等于未压缩的 20 x 128 DDM 的前 45 个延迟行中的平均盒原始计数，单位为计数，时间为 ddm_timestamp_utc。对于黑体 DDM：等于未压缩的 20 x 128 DDM 的所有 128 个延迟行中的平均盒原始计数，单位为计数，时间为 ddm_timestamp_utc。 |
| inst_gain | Instrument gain | float | 1 | sample, ddm | The black body noise counts divided by the sum of the black body power and the instrument noise power, in count/W, at ddm_timestamp_utc. | 黑体噪声计数除以黑体功率和仪器噪声功率之和，单位为 count/W，时间为 ddm_timestamp_utc。 |
| lna_noise_figure | LNA noise figure | float | dB | sample, ddm | The LNA noise figure, in dB, at ddm_timestamp_utc. Estimated from pre-launch characterization of LNA performance as a function of LNA temperature. | LNA 噪声系数，单位为 dB，时间为 ddm_timestamp_utc。根据 LNA 性能与 LNA 温度的关系进行预发射表征时估计。 |
| rx_to_sp_range | Rx to specular point range | int | meter | sample, ddm | The distance between the CYGNSS spacecraft and the specular point, in meters, at ddm_timestamp_utc. | CYGNSS 航天器与镜面点之间的距离，单位为米，时间为 ddm_timestamp_utc。 |
| tx_to_sp_range | Tx to specular point range | int | meter | sample, ddm | The distance between the GPS spacraft and the specular point, in meters, at ddm_timestamp_utc. | GPS 航天器与镜面点之间的距离，单位为米，时间为 ddm_timestamp_utc。 |
| tx_pos_x | GPS Tx position X | int | meter | sample, ddm | The X component of the GPS spacecraft WGS84 reference frame ECEF position, in meters, at ddm_timestamp_utc. Fill value is -99999999. | GPS 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 位置的 X 组件，单位为米。填充值为 -99999999。 |
| tx_pos_y | GPS Tx position Y | int | meter | sample, ddm | The Y component of the GPS spacecraft WGS84 reference frame ECEF position, in meters, at ddm_timestamp_utc. Fill value is -99999999. | GPS 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 位置的 Y 组件，单位为米。填充值为 -99999999。 |
| tx_pos_z | GPS Tx position Z | int | meter | sample, ddm | The Z component of the GPS spacecraft WGS84 reference frame ECEF position, in meters, at ddm_timestamp_utc. Fill value is -99999999. | GPS 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 位置的 Z 组件，单位为米。填充值为 -99999999。 |
| tx_vel_x | GPS Tx velocity X | int | meter s-1 | sample, ddm | The X component of the GPS spacecraft WGS84 reference frame ECEF velocity in meters, at ddm_timestamp_utc | GPS 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 速度的 X 组件，单位为米/秒。 |
| tx_vel_y | GPS Tx velocity Y | int | meter s-1 | sample, ddm | The Y component of the GPS spacecraft WGS84 reference frame ECEF velocity in meters, at ddm_timestamp_utc | GPS 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 速度的 Y 组件，单位为米/秒。 |
| tx_vel_z | GPS Tx velocity Z | int | meter s-1 | sample, ddm | The Z component of the GPS spacecraft WGS84 reference frame ECEF velocity in meters, at ddm_timestamp_utc | GPS 航天器在 ddm_timestamp_utc 时的 WGS84 参考框架 ECEF 速度的 Z 组件，单位为米/秒。 |
| bb_nearest | Time to most recent black body reading | float | second | sample, ddm | The time between ddm_timestamp_utc and the ddm_timestamp_utc of the closest (in time) black body reading, in signed seconds. A positive value indicates that the black body reading occurred after ddm_timestamp_utc. A negative value indicates that the block body reading occurred before ddm_timestamp_utc. | ddm_timestamp_utc 与最近（时间上）的黑体读数的 ddm_timestamp_utc 之间的时间，以带符号秒为单位。正值表示黑体读数发生在 ddm_timestamp_utc 之后；负值表示黑体读数发生在 ddm_timestamp_utc 之前。 |
| fresnel_coeff | Fresnel power reflection coefficient at specular point | float | 1 | sample, ddm | The SQUARE of the left hand circularly polarized Fresnel electromagnetic voltage reflection coefficient at 1575 MHz for a smooth ocean surface at the specular point location and incidence angle. See UM document 148-0361 Fresnel Coefficient Calculation for more information. | 在镜面点位置和入射角下，1575 MHz 时的左旋圆偏振菲涅尔电压反射系数的平方，见 UM 文档 148-0361 菲涅尔系数计算获取更多信息。 |
| ddm_nbrcs | Normalized BRCS | float | 1 | sample, ddm | Normalized BRCS over an interpolated 3 delay x 5 Doppler region around the precise inter-bin specular point location [2]. The specular point bin is in the top (least delay) row and the center Doppler column of the 3 x 5 box. This value is computed only over the ocean due to the high confidence in the ocean specular point location. For land NBRCS values use ddm_nbrcs_center and ddm_nbrcs_peak. | 在准确的镜面点位置 [2] 周围插值得到的 3 延迟 x 5 多普勒区域上的归一化 BRCS。镜面点在 3 x 5 盒子的顶部（最少延迟）行和中心多普勒列中。此值仅在海洋上计算，因为对海洋镜面点位置的高度置信度。对于陆地 NBRCS 值，使用 ddm_nbrcs_center 和 ddm_nbrcs_peak。 |
| ddm_nbrcs_scale_factor | Normalized BRCS Scale Factor | float | 1 | sample, ddm | Scale factor applied to the ddm_nbrcs during the statistical de-biasing process. Computed as a function of FM, antenna, SVN, and incidence angle. | 在统计去偏差过程中应用于 ddm_nbrcs 的缩放因子。计算为 FM、天线、SVN 和入射角的函数。 |
| ddm_les | Leading edge slope | float | 1 | sample, ddm | Leading edge slope of a 3 delay x 5 Doppler bin box that include the specular point bin. The specular point bin is in the top (least delay) row and the center Doppler column of the 3 x 5 box. | 包含镜面点单元的 3 延迟 x 5 多普勒盒的领先边缘斜率。镜面点单元位于 3 x 5 盒子的顶部（最少延迟）行和中心多普勒列中。 |
| nbrcs_scatter_area | NBRCS scattering area | float | meter2 | sample, ddm | The scattering area of the 3 x 5 region of the ddm used to calculate ddm_nbrcs. | 用于计算 ddm_nbrcs 的 ddm 的 3 x 5 区域的散射面积。 |
| les_scatter_area | LES scattering area | float | meter2 | sample, ddm | The scattering area of the 3 x 5 region of the ddm used to calculate ddm_les. | 用于计算 ddm_les 的 ddm 的 3 x 5 区域的散射面积。 |
| brcs_ddm_peak_bin_delay_row | BRCS DDM peak bin delay row | byte | 1 | sample, ddm | The zero-based delay row of the peak value in the bistatic radar cross section DDM (brcs). Ranges from 0 to 16. | 双静态雷达反射截面 DDM (brcs) 中峰值的零基延迟行。范围从 0 到 16。 |
| brcs_ddm_peak_bin_dopp_col | BRCS DDM peak bin Doppler column | byte | 1 | sample, ddm | The zero-based Doppler column of the peak value in the bistatic radar cross section DDM (brcs). Ranges from 0 to 10. | 双静态雷达反射截面 DDM (brcs) 中峰值的零基多普勒列。范围从 0 到 10。 |
| brcs_ddm_sp_bin_delay_row | BRCS DDM specular point delay row | float | 1 | sample, ddm | The zero-based delay row of the specular point delay in the bistatic radar cross section DDM (brcs). Note that this is a floating point value. | 双静态雷达反射截面 DDM (brcs) 中镜面点延迟的零基延迟行。注意，这是一个浮点值。 |
| brcs_ddm_sp_bin_dopp_col | BRCS DDM specular point Doppler column | float | 1 | sample, ddm | The zero-based Doppler column of the specular point Doppler in the bistatic radar cross section DDM (brcs). Note that this is a floating point value. | 双静态雷达反射截面 DDM (brcs) 中镜面点多普勒的零基多普勒列。注意，这是一个浮点值。 |
| ddm_brcs_uncert | DDM BRCS uncertainty | float | 1 | sample,ddm | Uncertainty of the BRCS. | BRCS 的不确定性。 |
| bb_power_temperature_density | Black Body Power Temperature Density | float | Counts/Kelvin | sample,ddm | Raw counts of detected power radiated by the blackbody calibration target, divided by receiver gain and blackbody physical temperature in Kelvins, gives the detected power per unit absolute temperature. | 黑体校准目标辐射的检测功率的原始计数除以接收机增益和黑体物理温度（开尔文），得到单位绝对温度下的检测功率。 |
| ddm_nadir_signal_correction | Nadir Signal Correction Factor | float | 1 | sample,ddm | The correction factor applied to signal value based on the nadir bin ratio. | 根据近天顶单元比率应用于信号值的修正因子。 |
| ddm_nadir_bb_correction_prev | Nadir BB Correction Factor Previous | float | 1 | sample,ddm | The correction factor applied to the previous blackbody value based on the nadir bin ratio. | 根据近天顶单元比率应用于先前黑体值的修正因子。 |
| ddm_nadir_bb_correction_next | Nadir BB Correction Factor Next | float | 1 | sample,ddm | The correction factor applied to the next blackbody value based on the nadir bin ratio. | 根据近天顶单元比率应用于下一次黑体值的修正因子。 |
| zenith_sig_i2q2 | Zenith Signal I2Q2 | int | 1 | sample,ddm | Raw counts of detected power in direct GPS L1 C/A signal received by zenith navigation antenna and detected by navigation receiver. | 在天顶导航天线接收到的直接 GPS L1 C/A 信号中的检测功率的原始计数，由导航接收机检测。 |
| zenith_sig_i2q2_corrected | Zenith Signal I2Q2 Corrected | float | 1 | sample,ddm | The zenith_sig_i2q2 after a correction factor, based on the zenith antenna bin ratio, has been applied. | 应用了基于天顶天线单元比率的修正因子的 zenith_sig_i2q2。 |
| zenith_sig_i2q2_mult_correction | Zenith Signal I2Q2 Multiplicative Correction Factor | float | 1 | sample,ddm | The multiplicative correction factor applied with zenith_sig_i2q2_corrected = 10*log10(zenith_sig_i2q2*zenith_sig_i2q2_mult_correction)-zenith_sig_i2q2_add_correction. | 应用的乘法修正因子，使用公式 zenith_sig_i2q2_corrected = 10log10(zenith_sig_i2q2zenith_sig_i2q2_mult_correction)-zenith_sig_i2q2_add_correction。 |
| zenith_sig_i2q2_add_correction | Zenith Signal I2Q2 Additive Correction Factor | float | 1 | sample,ddm | The additive correction factor applied with zenith_sig_i2q2_corrected = 10*log10(zenith_sig_i2q2*zenith_sig_i2q2_mult_correction)-zenith_sig_i2q2_add_correction. | 应用的加法修正因子，使用公式 zenith_sig_i2q2_corrected = 10log10(zenith_sig_i2q2zenith_sig_i2q2_mult_correction)-zenith_sig_i2q2_add_correction。 |
| starboard_gain_setting | The Nadir-Starboard Gain Setting | int | dB | sample,ddm | The Nadir-Starboard Gain Setting (dB, 0=Automatic) | 近天顶-右舷增益设置（dB，0=自动）。 |
| port_gain_setting | The Nadir-Port Gain Setting | int | dB | sample,ddm | The Nadir-Port Gain Setting (dB, 0=Automatic) | 近天顶-左舷增益设置（dB，0=自动）。 |
| ddm_kurtosis | DDM Kurtosis | float | 1 | sample,ddm | The kurtosis of the DDM noise floor. For diagnostic use only. See UM document 148-0347 DDM RFI Algorithm for more information. | DDM 噪声底的峰度。仅供诊断使用。有关更多信息，请参见 UM 文档 148-0347 DDM RFI 算法。 |
| modis_land_cover | MODIS Land Cover classification | byte | 1 | sample,ddm | The MODIS Land Cover Classification type at the specular point latitude and longitude | 镜面点纬度和经度的 MODIS 土地覆盖分类类型。 |
| srtm_dem_alt | SRTM DEM altitude | float | meter | sample,ddm | Altitude at the specular point calculated using the 1km resolution SRTM DEM. Land observations only. | 使用 1 公里分辨率的 SRTM DEM 计算的镜面点高度。仅适用于陆地观测。 |
| srtm_slope | SRTM DEM slope | float | degree | sample,ddm | Surface slope at the specular point calculated using the 1km resolution SRTM DEM. Land observations only. | 使用 1 公里分辨率的 SRTM DEM 计算的镜面点表面斜率。仅适用于陆地观测。 |
| reflectivity_peak | Peak linear reflectivity | float | linear | sample,ddm | Surface reflectivity calculate at the DDM peak power bin [3]. | 在 DDM 峰值功率箱中计算的表面反射率 [3]。 |
| ddm_nbrcs_center | DDM NBRCS calculated around the central bin | float | 1 | sample,ddm | Approximation of the DDM NBRCS using a fixed and centered delay/Doppler grid in the BRCS DDM. Calculated by dividing the sum of a 3x5 grid of the BRCS DDM (brcs) by the sum of the equivalent grid from the effective scattering area DDM (eff_scatter). The grid region consists of 3 delay bins and 5 Doppler bins centered at delay bin 9 and Doppler bin 5 (using zero based indexing) of the BRCS and effective area DDMs. Computed only over land. | 使用 BRCS DDM 中固定和集中延迟/频率网络近似 DDM NBRCS。通过将 BRCS DDM (brcs) 的 3x5 网格的总和除以有效散射区域 DDM (eff_scatter) 的等效网格的总和，计算出。该区域由 3 个延迟单元和 5 个多普勒单元组成，中心位于 BRCS 和有效散射区域 DDM 的延迟单元 9 和多普勒单元 5（使用零基索引）。仅在陆地上计算。 |
| ddm_nbrcs_peak | DDM NBRCS calculated at the peak bin | float | 1 | sample,ddm | Approximation of the DDM NBRCS using the peak DDM only. Calculated by dividing the BRCS DDM peak bin (brcs) by the single central effective scatter area bin (eff_scatter). Computed only over land. | 使用单个中心有效散射区域单元的 BRCS DDM 峰值 (brcs) 除以峰值 DDM 仅计算的 NBRCS 近似值。仅在陆地上计算。 |
| coherency_state | Coherency State | byte | 1 | sample,ddm | Meaning of each confidence state value: 0 = Not coherent 1 = Coherent 2 = Mixed Coherence 3 = Indeterminate Coherence | 每个置信度状态值的含义： 0 = 不相干 1 = 相干 2 = 混合相干 3 = 不确定相干 |
| coherency_ratio | Coherency Ratio | float | 1 | sample,ddm | Estimation of the ratio of received power between the central bins and periphery bins of the raw_counts DDM after the elimination of noise bins [4]. A higher ratio is more indicative of signal coherence | 在排除噪声单元 [4] 之后的中心单元与边缘单元之间的接收功率比的估计。更高的比率更能指示信号的相干性。 |
| sp_land_valid | Is land SP valid? | byte | 1 | sample,ddm | Land specular point location estimate is valid with reasonable confidence, as per the calculation algorithm described in [4]. This flag is set to 1 (valid) if the sp_land_confidence value is either 3 or 4, and set to 0 (invalid) otherwise. | 根据 [4] 中描述的计算算法，陆地镜面点位置估计有效且具有合理的置信度。如果 sp_land_confidence 值为 3 或 4，则该标志设置为 1（有效），否则设置为 0（无效）。 |
| sp_land_confidence | Confidence in land specular point | byte | 1 | sample,ddm | Meaning of each confidence value: 0 = Lowest confidence, land SP wrong 1 = Land SP probably wrong, but low SNR is the cause 2 = Land SP probably OK, despite low SNR 3 = Highest confidence, land SP OK | 各个置信度值的含义： 0 = 最低置信度，陆地 SP 错误 1 = 陆地 SP 可能错误，但低 SNR是原因 2 = 陆地 SP 可能正常，尽管 SNR 较低 3 = 最高置信度，陆地 SP 正常 |
| ddmi_tracker_delay_center | DDMI Tracker Delay Center | float | 1 | sample,ddm | The navigation receiver clock drift contribution to the received signal Doppler frequency. Estimated during the 1Hz DMR navigation velocity solution as receiver clock bias rate, converted to frequency (Hz). | 导航接收机时钟漂移对接收信号多普勒频率的影响。在每秒 1 Hz DMR 导航速度解算期间估计，作为接收机时钟偏差率转换为频率（Hz）。 |
| rx_clk_doppler | Rx Clock Doppler | int | dB | sample,ddm | The navigation receiver clock drift contribution to the received signal Doppler frequency. Estimated during the 1Hz DMR navigation velocity solution as receiver clock bias rate, converted to frequency (Hz). | 导航接收机时钟漂移对接收信号多普勒频率的贡献。在每秒 1 Hz DMR 导航速度解算期间估计，作为接收机时钟偏差率转换为频率（Hz）。 |
| pekel_sp_water_percentage | Percentage of water at SP | byte | 1 | sample,ddm | The interpolated lookup of the percentage of water on a high resolution (30m) Pekel water mask. | 在高分辨率 (30m) Pekel 水掩模上的插值查找水的百分比。 |
| pekel_sp_water_flag | Possible surface water at SP | byte | 1 | sample,ddm | If pekel_sp_water_percentage > 0, pekel_sp_water_flag = 1, else 0. Water presence estimated in the vicinity of the SP using high resolution (30m) Pekel water mask. | 如果 pekel_sp_water_percentage > 0，则 pekel_sp_water_flag = 1，否则为 0。在镜面点附近使用高分辨率 (30m) Pekel 水掩模估计水的存在。 |
| pekel_sp_water_percentage_2km | Percentage of water within 2km of SP | byte | 1 | sample,ddm | The percentage of water within a 2km circular region centered at the SP. Water presence estimated in the vicinity of the SP using high resolution (30m) Pekel water mask. | 在以 SP 为中心的 2 公里圆形区域内的水百分比。 |
| pekel_sp_water_flag_2km | Water estimated within 2km of SP | byte | 1 | sample,ddm | If pekel_sp_water_percentage_2km > 0, pekel_sp_water_flag_2km = 1, else 0. Water presence estimated in the vicinity of the SP using high resolution (30m) Pekel water mask. | 如果 pekel_sp_water_percentage_2km > 0，则 pekel_sp_water_flag_2km = 1，否则为 0。在镜面点附近使用高分辨率 (30m) Pekel 水掩模估计水的存在。 |
| pekel_sp_water_percentage_5km | Percentage of water within 5km of SP | byte | 1 | sample,ddm | The percentage of water within a 5km circular region centered at the SP. Water presence estimated in the vicinity of the SP using high resolution (30m) Pekel water mask. | 在以 SP 为中心的 5 公里圆形区域内的水百分比。 |
| pekel_sp_water_flag_5km | Water estimated within 5km of SP | byte | 1 | sample,ddm | If pekel_sp_water_percentage_5km > 0, pekel_sp_water_flag_5km = 1, else 0. Water presence estimated in the vicinity of the SP using high resolution (30m) Pekel water mask. | 如果 pekel_sp_water_percentage_5km > 0，则 pekel_sp_water_flag_5km = 1，否则为 0。在镜面点附近使用高分辨率 (30m) Pekel 水掩模估计水的存在。 |
| pekel_sp_water_percentage_10km | Percentage of water within 10km of SP | byte | 1 | sample,ddm | The percentage of water within a 10km circular region centered at the SP. Water presence estimated in the vicinity of the SP using high resolution (30m) Pekel water mask. | 在以 SP 为中心的 10 公里圆形区域内的水百分比。 |
| pekel_sp_water_flag_10km | Water estimated within 10km of SP | byte | 1 | sample,ddm | If pekel_sp_water_percentage_10km > 0, pekel_sp_water_flag_10km = 1, else 0. Water presence estimated in the vicinity of the SP using high resolution (30m) Pekel water mask. | 如果 pekel_sp_water_percentage_10km > 0，则 pekel_sp_water_flag_10km = 1，否则为 0。在镜面点附近使用高分辨率 (30m) Pekel 水掩模估计水的存在。 |
| pekel_sp_water_local_map_5km | Local area map of the water mask | byte | 1 | sample,ddm,lat_5km, lon_5km | A 5 km x 5 km local area grid of Pekel percentage of surface water. Each cell of the local area map is 1km x 1km. The reported sp_lat, sp_lon, and sp_land_alt is the center cell of the local area map. | 5 公里 x 5 公里的水百分比的 Pekel 局部区域网格。局部区域地图的每个单元格为 1 公里 x 1 公里。报告的 sp_lat、sp_lon 和 sp_land_alt 是局部区域地图的中心单元。 |
| sp_calc_method | Specular point calculation method | byte | 1 | sample,ddm | Method used for Specular Point Calcualtion: 0 = Ocean, uses DTU10 for altitude 1 = Land, uses SRTM for altitude | 用于镜面点计算的方法： 0 = 海洋，使用 DTU10 计算高度 1 = 陆地，使用 SRTM 计算高度 |
| quality_flags | Per-DDM quality flags 1 | int | <none> | sample, ddm | First group of the Per-DDM quality flags. 1 indicates presence of condition. More quality flags can be found in quality_flags_2. Flag bit masks: | 每 DDM 质量标志的第一组。如果存在条件则为 1。更多的质量标志可以在 quality_flags_2 中找到。标志位掩码： |
| quality_flags_2 | Per-DDM quality flags 2 | int | <none> | sample, ddm | Second group of the Per-DDM quality flags. 1 indicates presence of condition. The first group of quality flags can be found in quality_flags. Flag bit masks: | 每 DDM 质量标志的第二组。如果存在条件则为 1。第一个质量标志组可在 quality_flags 中找到。标志位掩码： |

### Per-Bin Values
| Name | Long Name | Type | Units | Dimensions | Comment | Comment (CN) |
| --- | --- | --- | --- | --- | --- | --- |
| raw_counts | DDM bin raw counts | int | 1 | sample, ddm, delay, doppler | 17 x 11 array of DDM bin raw counts. These are the uncalibrated power values produced by the DDMI. | 17 x 11 的 DDM 单元原始计数数组。这些是由 DDMI 产生的未校准功率值。 |
| power_analog | DDM bin analog power | float | watt | sample, ddm, delay, doppler | 17 x 11 array of DDM bin analog power, Watts. analog_power is the true power that would have been measured by an ideal (analog) power sensor. power_digital is the power measured by the actual 2-bit sensor, which includes quantization effects. power_analog has been corrected for quantization effects. | 17 x 11 的 DDM 单元模拟功率数组，单位为瓦特。analog_power 是理想（模拟）功率传感器应该測量的真实功率。power_digital 是由实际的 2 位传感器测量的功率，包含量化效应。power_analog 已校正量化效应。 |
| brcs | DDM bin bistatic radar cross section | float | meter2 | sample, ddm, delay, doppler | 17 x 11 array of DDM bin bistatic radar cross section, m^2. The specular point is located in DDM bin round(brcs_ddm_sp_bin_delay_row), round(brcs_ddm_sp_bin_dopp_col ). | 17 x 11 的 DDM 单元双静态雷达反射截面数组，单位为 m²。镜面点位于 DDM 单元 round(brcs_ddm_sp_bin_delay_row), round(brcs_ddm_sp_bin_dopp_col)。 |
| eff_scatter | DDM bin effective scattering area | float | meter2 | sample, ddm, delay, doppler | 17 x 11 array of DDM bin effective scattering area, m^2. This is an estimate of the true surface scattering area that contributes power to each DDM bin, after accounting for the GPS signal spreading function. It is calculated by convolving the GPS ambiguity function with the surface area that contributes power to a given DDM bin as determined by its delay and Doppler values and the measurement geometry. The specular point bin location matches the specular point bin location in brcs. | 17 x 11 的 DDM 单元有效散射面积数组，单位为 m²。此值是对每个 DDM 单元的真实表面散射面积的估计，考虑到 GPS 信号扩散函数。它是通过将 GPS 模糊函数与在其延迟和多普勒值下贡献功率到给定 DDM 单元的表面积进行卷积计算的。镜面点单元位置与 brcs 中镜面点单元位置匹配。 |

**References**
- [1] Ruf, C., P. Chang, M.P. Clarizia, S. Gleason, Z. Jelenak, J. Murray, M. Morris, S. Musko, D. Posselt, D. Provost, D. Starkenburg, V. Zavorotny, CYGNSS Handbook, Ann Arbor, MI, Michigan Pub., "ISBN 978-1-60785-380-0, 154 pp, 1 Apr 2016. http://clasp-research.engin.umich.edu/missions/cygnss/reference/cygnss-mission/CYGNSS_Handbook_April2016.pdf "
- [2] S. Gleason, C. S. Ruf, A. J. O’Brien and D. S. McKague, 'The CYGNSS Level 1 Calibration Algorithm and Error Analysis Based on On-Orbit Measurements,' in IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, vol. 12, no. 1, pp. 37-49, Jan. 2019, doi: 10.1109/JSTARS.2018.2832981.
- [3] Gleason, S., O’Brien, A., Russel, A., Al-Khaldi, M. M., & Johnson, J. T. (2020). Geolocation, calibration and surface resolution of CYGNSS GNSS-R land observations. Remote Sensing, 12, 1317. doi:10.3390/rs12081317
- [4] M. M. Al-Khaldi, J. T. Johnson, S. Gleason, E. Loria, A. J. O’Brien and Y. Yi, "An Algorithm for Detecting Coherence in Cyclone Global Navigation Satellite System Mission Level-1 Delay-Doppler Maps," in IEEE Transactions on Geoscience and Remote Sensing, vol. 59, no. 5, pp. 4454-4463, May 2021, doi: 10.1109/TGRS.2020.3009784.
