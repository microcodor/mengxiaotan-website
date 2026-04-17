import requests
from typing import List, Dict, Optional
from datetime import datetime, date
import os

class AIService:
    """AI 内容生成服务 - MiniMax API"""
    
    def __init__(self):
        self.api_key = os.getenv('MINIMAX_API_KEY', '')
        self.group_id = os.getenv('MINIMAX_GROUP_ID', '')
        self.base_url = 'https://api.minimax.chat/v1'
    
    def generate_daily_brief(self, articles: List[Dict]) -> Dict:
        """生成每日简报
        
        Args:
            articles: 文章列表，每篇文章包含 title, summary, category, source
            
        Returns:
            {
                'brief_date': date,
                'content': {
                    'headline': str,  # 今日要闻标题
                    'summary': str,   # 整体摘要
                    'ndrc': str,      # 发改委动态
                    'coal': str,      # 煤炭要闻
                    'power': str,     # 电力动态
                    'new_energy': str # 新能源进展
                },
                'ai_suggestion': str  # 今日一句话建议
            }
        """
        # 按分类整理文章
        categorized = {
            'ndrc': [],
            'coal': [],
            'power': [],
            'new_energy': []
        }
        
        for article in articles:
            category = article.get('category', 'other')
            if category in categorized:
                categorized[category].append(article)
        
        # 构建提示词
        prompt = self._build_brief_prompt(categorized)
        
        # 调用 AI 生成
        response = self._call_minimax(prompt)
        
        if response:
            content = self._parse_brief_response(response)
            suggestion = self.generate_suggestion(articles)
            
            return {
                'brief_date': date.today(),
                'content': content,
                'ai_suggestion': suggestion
            }
        
        return None
    
    def generate_suggestion(self, articles: List[Dict]) -> str:
        """生成今日一句话建议"""
        # 提取关键信息
        titles = [a.get('title', '') for a in articles[:10]]
        
        prompt = f"""基于以下能源行业今日要闻，生成一句话决策建议（50-80字）：

要闻标题：
{chr(10).join(f'{i+1}. {t}' for i, t in enumerate(titles))}

要求：
1. 简洁专业，直击要点
2. 包含具体的行动建议或趋势判断
3. 适合能源企业高管阅读
4. 50-80字

一句话建议："""
        
        response = self._call_minimax(prompt, max_tokens=200)
        return response.strip() if response else "关注最新政策动态，把握市场机遇。"
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        prompt = f"""从以下文本中提取{top_k}个最重要的关键词，用逗号分隔：

文本：
{text[:500]}

关键词："""
        
        response = self._call_minimax(prompt, max_tokens=100)
        if response:
            keywords = [k.strip() for k in response.split(',')]
            return keywords[:top_k]
        return []
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """生成文章摘要"""
        if len(content) <= max_length:
            return content
        
        prompt = f"""请为以下文章生成{max_length}字以内的摘要：

文章内容：
{content[:1000]}

摘要："""
        
        response = self._call_minimax(prompt, max_tokens=300)
        return response.strip() if response else content[:max_length]
    
    def _build_brief_prompt(self, categorized: Dict) -> str:
        """构建简报生成提示词"""
        prompt = "你是能源行业资深分析师，请基于以下分类资讯生成今日简报：\n\n"
        
        categories = {
            'ndrc': '发改委动态',
            'coal': '煤炭要闻',
            'power': '电力动态',
            'new_energy': '新能源进展'
        }
        
        for cat_key, cat_name in categories.items():
            articles = categorized.get(cat_key, [])
            if articles:
                prompt += f"## {cat_name}\n"
                for i, article in enumerate(articles[:5], 1):
                    prompt += f"{i}. {article.get('title', '')}\n"
                prompt += "\n"
        
        prompt += """
请生成结构化简报，包含：
1. 今日要闻标题（10字以内）
2. 整体摘要（100字）
3. 各分类要点（每个50-80字）

格式：
【今日要闻】标题
【整体摘要】内容
【发改委动态】内容
【煤炭要闻】内容
【电力动态】内容
【新能源进展】内容
"""
        return prompt
    
    def _parse_brief_response(self, response: str) -> Dict:
        """解析简报响应"""
        content = {
            'headline': '',
            'summary': '',
            'ndrc': '',
            'coal': '',
            'power': '',
            'new_energy': ''
        }
        
        # 简单解析（实际应用中可以更复杂）
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if '【今日要闻】' in line:
                content['headline'] = line.replace('【今日要闻】', '').strip()
            elif '【整体摘要】' in line:
                current_section = 'summary'
                content['summary'] = line.replace('【整体摘要】', '').strip()
            elif '【发改委动态】' in line:
                current_section = 'ndrc'
                content['ndrc'] = line.replace('【发改委动态】', '').strip()
            elif '【煤炭要闻】' in line:
                current_section = 'coal'
                content['coal'] = line.replace('【煤炭要闻】', '').strip()
            elif '【电力动态】' in line:
                current_section = 'power'
                content['power'] = line.replace('【电力动态】', '').strip()
            elif '【新能源进展】' in line:
                current_section = 'new_energy'
                content['new_energy'] = line.replace('【新能源进展】', '').strip()
            elif current_section and line:
                content[current_section] += ' ' + line
        
        return content
    
    def _call_minimax(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """调用 MiniMax API"""
        if not self.api_key:
            # 如果没有配置 API Key，返回模拟数据
            return self._mock_response(prompt)
        
        try:
            url = f"{self.base_url}/text/chatcompletion_v2"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'abab6.5-chat',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': 0.7
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        except Exception as e:
            print(f"AI API 调用失败: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """模拟响应（用于开发测试）"""
        if '一句话建议' in prompt:
            return "根据最新政策和市场动态，建议关注发改委近期发布的煤炭保供政策，预计短期内煤价将保持稳定。新能源领域，光伏装机量持续增长，建议关注相关产业链投资机会。"
        
        if '关键词' in prompt:
            return "能源政策, 煤炭价格, 电力供应, 新能源, 碳排放, 清洁能源, 发改委, 市场动态"
        
        if '摘要' in prompt:
            return "本文介绍了能源行业最新动态，包括政策调整、市场变化和技术进展等方面的重要信息。"
        
        # 简报响应
        return """【今日要闻】能源保供政策持续发力
【整体摘要】今日能源行业聚焦政策保障与市场稳定。发改委发布新一轮煤炭保供措施，电力供应总体平稳，新能源装机持续增长，行业整体呈现稳中向好态势。
【发改委动态】发改委召开能源保供专题会议，部署下一阶段工作重点，强调要确保能源安全稳定供应，推动能源结构优化升级。
【煤炭要闻】主产区煤炭产量稳步提升，港口库存处于合理水平，动力煤价格保持平稳，市场供需基本平衡。
【电力动态】全国电力供应总体充足，新能源发电量占比持续提升，电网运行安全稳定，迎峰度冬准备工作扎实推进。
【新能源进展】光伏、风电装机规模持续扩大，氢能产业加快布局，绿色低碳转型步伐加快，清洁能源发展势头良好。"""


# 创建全局实例
ai_service = AIService()
