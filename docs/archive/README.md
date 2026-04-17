# 文档归档说明

## 概述

本目录包含项目开发过程中产生的中间文档、测试报告和历史记录。这些文档已被归档，不再作为主要参考文档。

## 归档时间

2026-04-17

## 归档原因

- 减少项目根目录的文件数量
- 保持文档结构清晰
- 保留历史记录供参考

## 当前核心文档

项目根目录保留的核心文档：

1. **README.md** - 项目总览和快速开始
2. **QUICKSTART.md** - 快速启动指南
3. **DOCKER_DEPLOYMENT_GUIDE.md** - Docker部署完整指南
4. **DOCKER_QUICK_REFERENCE.md** - Docker命令快速参考
5. **DAILY_BRIEF_SHARE_FEATURE.md** - 早报分享功能文档
6. **PUSH_CHANNEL_CONFIG_GUIDE.md** - 推送渠道配置指南
7. **CRAWLER_SITES_CONFIG.md** - 爬虫站点配置
8. **TROUBLESHOOTING.md** - 故障排查指南

## 归档文档分类

### 爬虫相关（约80个文件）
- CRAWL4AI_*.md - Crawl4AI迁移相关
- CRAWLER_*.md - 爬虫开发、测试、优化记录
- *_CRAWLER_*.md - 各种爬虫实现报告

### 订阅系统（约20个文件）
- SUBSCRIPTION_*.md - 订阅系统开发记录
- PHASE*_*.md - 各阶段完成报告

### 推送系统（约15个文件）
- IM_PUSH_*.md - IM推送功能开发
- PUSH_*.md - 推送相关配置和测试

### 企业功能（约10个文件）
- ENTERPRISE_*.md - 企业信息功能
- COMPANY_*.md - 企业画像功能
- DIGITAL_TWIN_*.md - 数字分身功能

### 部署和环境（约15个文件）
- LOCAL_*.md - 本地环境配置
- DOCKER_*.md - Docker部署记录
- PORT_*.md - 端口配置问题

### 测试报告（约30个文件）
- TEST_*.md - 各种测试报告
- *_TEST_*.md - 功能测试记录

### 其他（约29个文件）
- 各种修复记录
- 优化报告
- 状态总结
- 临时文档

## 如何查找历史文档

如果需要查找某个功能的开发历史：

```bash
# 搜索文件名
ls docs/archive/ | grep "关键词"

# 搜索文件内容
grep -r "关键词" docs/archive/

# 查看特定文件
cat docs/archive/文件名.md
```

## 注意事项

1. 归档文档仅供参考，可能包含过时信息
2. 以项目根目录的核心文档为准
3. 如需恢复某个文档，可从归档目录复制

## 清理建议

如果确认不再需要这些历史文档，可以删除整个归档目录：

```bash
rm -rf docs/archive/
```

**警告**：删除后无法恢复，请谨慎操作！
