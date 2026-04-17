# 新增爬虫快速参考

## 🎯 新增的4个爬虫

| 爬虫名称 | 显示名称 | 类目 | URL |
|---------|---------|------|-----|
| `ccer` | 全国温室气体自愿减排交易系统 | carbon_trading | https://www.ccer.com.cn/ |
| `mysteel` | 我的钢铁网 | steel | https://www.mysteel.com/ |
| `cnmn_paper` | 中国有色金属报 | nonferrous_metals | https://paper.cnmn.com.cn/ |
| `smm_metal` | 上海有色金属网 | nonferrous_metals | https://www.metal.com/ |

## 🚀 快速命令

### 运行单个爬虫
```bash
cd crawler
scrapy crawl ccer          # 碳交易
scrapy crawl mysteel       # 钢铁
scrapy crawl cnmn_paper    # 有色金属报
scrapy crawl smm_metal     # 有色金属网
```

### 运行所有新爬虫
```bash
./test_new_crawlers.sh
```

### 查看数据统计
```bash
cd backend
source venv/bin/activate
python check_data.py
```

### 查看爬虫列表
```bash
cd crawler
scrapy list
```

## 📊 预期效果

| 爬虫 | 单次抓取 | 每日次数 | 每日总量 |
|------|---------|---------|---------|
| ccer | 10-15篇 | 2次 | 20-30篇 |
| mysteel | 20-25篇 | 3次 | 60-75篇 |
| cnmn_paper | 15-20篇 | 2次 | 30-40篇 |
| smm_metal | 15-20篇 | 2次 | 30-40篇 |
| **总计** | **60-80篇** | **9次** | **140-185篇** |

## 📁 重要文件

| 文件 | 说明 |
|------|------|
| `IMPLEMENTATION_COMPLETE.md` | 完整实施报告 |
| `NEW_CRAWLERS_IMPLEMENTED.md` | 技术详细文档 |
| `INDUSTRY_WEBSITES_SUMMARY.md` | 网站调研总结 |
| `test_new_crawlers.sh` | 自动化测试脚本 |

## ✅ 系统状态

- **爬虫总数**: 13个（原9个 + 新4个）
- **行业覆盖**: 6个（原3个 + 新3个）
- **抓取能力**: +53-70%
- **数据源**: 10个

## 🎉 新增行业

1. **碳交易** (carbon_trading) - CCER官方平台
2. **钢铁** (steel) - 我的钢铁网
3. **有色金属** (nonferrous_metals) - 中国有色金属报 + 上海有色金属网

## 📞 快速帮助

**测试爬虫**: `./test_new_crawlers.sh`  
**查看日志**: `scrapy crawl ccer -s LOG_LEVEL=INFO`  
**管理后台**: http://localhost:3000/admin/crawler  
**查看数据**: `python check_data.py`

---

**状态**: ✅ 已完成，可以开始测试  
**时间**: 2026-04-11
