"""
AI辅助报告生成服务
"""
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from openai import OpenAI


class ReportGeneratorService:
    """报告生成服务类"""
    
    def __init__(self):
        """初始化OpenAI客户端"""
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        return self.client is not None
    
    def get_report_template(self, report_type: str) -> Dict:
        """
        获取报告模板
        
        Args:
            report_type: 报告类型
            
        Returns:
            Dict: 报告模板
        """
        templates = {
            'technical_optimization': {
                'name': '技术路线优化报告',
                'sections': [
                    '执行摘要',
                    '技术方案对比',
                    '经济性分析',
                    '风险评估',
                    '实施建议'
                ],
                'prompt_template': """
请生成一份关于"{title}"的技术路线优化报告。

需求描述：
{description}

报告应包含以下部分：
1. 执行摘要 - 简要概述分析结果和核心建议
2. 技术方案对比 - 详细对比不同技术方案的优劣
3. 经济性分析 - 分析各方案的投资回报和成本效益
4. 风险评估 - 识别潜在风险和应对措施
5. 实施建议 - 提供可执行的实施路径

请以专业、客观的语气撰写，包含具体数据和案例支持。
"""
            },
            'regional_market': {
                'name': '区域市场布局报告',
                'sections': [
                    '执行摘要',
                    '区域市场分析',
                    '竞争格局分析',
                    '进入策略建议',
                    '风险提示'
                ],
                'prompt_template': """
请生成一份关于"{title}"的区域市场布局报告。

需求描述：
{description}

报告应包含以下部分：
1. 执行摘要 - 简要概述市场机会和核心建议
2. 区域市场分析 - 分析目标区域的市场规模、增长趋势、政策环境
3. 竞争格局分析 - 分析主要竞争对手和市场份额
4. 进入策略建议 - 提供市场进入的具体策略和时机
5. 风险提示 - 识别市场风险和应对措施

请以专业、客观的语气撰写，包含具体数据和案例支持。
"""
            },
            'policy_analysis': {
                'name': '政策影响分析报告',
                'sections': [
                    '执行摘要',
                    '政策解读',
                    '影响评估',
                    '应对策略',
                    '机会识别'
                ],
                'prompt_template': """
请生成一份关于"{title}"的政策影响分析报告。

需求描述：
{description}

报告应包含以下部分：
1. 执行摘要 - 简要概述政策要点和核心影响
2. 政策解读 - 深度解读政策内容、背景和目标
3. 影响评估 - 评估政策对企业的正面和负面影响
4. 应对策略 - 提供具体的应对措施和调整建议
5. 机会识别 - 识别政策带来的新机会

请以专业、客观的语气撰写，包含具体数据和案例支持。
"""
            },
            'competitor_analysis': {
                'name': '竞争对手分析报告',
                'sections': [
                    '执行摘要',
                    '竞争对手画像',
                    '战略分析',
                    '优劣势对比',
                    '应对建议'
                ],
                'prompt_template': """
请生成一份关于"{title}"的竞争对手分析报告。

需求描述：
{description}

报告应包含以下部分：
1. 执行摘要 - 简要概述竞争态势和核心建议
2. 竞争对手画像 - 详细描述主要竞争对手的基本情况
3. 战略分析 - 分析竞争对手的战略意图和动向
4. 优劣势对比 - 对比我方与竞争对手的优劣势
5. 应对建议 - 提供针对性的竞争策略

请以专业、客观的语气撰写，包含具体数据和案例支持。
"""
            },
            'investment_decision': {
                'name': '投资决策支持报告',
                'sections': [
                    '执行摘要',
                    '项目可行性分析',
                    '财务测算',
                    '风险评估',
                    '投资建议'
                ],
                'prompt_template': """
请生成一份关于"{title}"的投资决策支持报告。

需求描述：
{description}

报告应包含以下部分：
1. 执行摘要 - 简要概述投资机会和核心建议
2. 项目可行性分析 - 分析项目的技术、市场、政策可行性
3. 财务测算 - 提供详细的投资回报分析和财务预测
4. 风险评估 - 识别投资风险和应对措施
5. 投资建议 - 提供明确的投资决策建议

请以专业、客观的语气撰写，包含具体数据和案例支持。
"""
            }
        }
        
        return templates.get(report_type, templates['technical_optimization'])
    
    def generate_report_content(
        self,
        report_type: str,
        title: str,
        description: str,
        additional_context: Optional[Dict] = None
    ) -> Dict:
        """
        使用AI生成报告内容
        
        Args:
            report_type: 报告类型
            title: 报告标题
            description: 需求描述
            additional_context: 额外上下文信息
            
        Returns:
            Dict: 生成的报告内容
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'AI服务未配置或不可用',
                'content': None
            }
        
        try:
            # 获取报告模板
            template = self.get_report_template(report_type)
            
            # 构建提示词
            prompt = template['prompt_template'].format(
                title=title,
                description=description
            )
            
            # 添加额外上下文
            if additional_context:
                context_str = "\n\n额外信息：\n"
                for key, value in additional_context.items():
                    context_str += f"- {key}: {value}\n"
                prompt += context_str
            
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的能源行业分析师，擅长撰写深度分析报告。你的报告应该数据详实、逻辑清晰、建议可行。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            # 提取生成的内容
            content = response.choices[0].message.content
            
            return {
                'success': True,
                'content': content,
                'template': template,
                'tokens_used': response.usage.total_tokens,
                'model': self.model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': None
            }
    
    def format_report_to_markdown(
        self,
        title: str,
        company_name: str,
        report_type_display: str,
        content: str,
        generated_at: Optional[datetime] = None
    ) -> str:
        """
        将报告内容格式化为Markdown
        
        Args:
            title: 报告标题
            company_name: 企业名称
            report_type_display: 报告类型显示名称
            content: 报告内容
            generated_at: 生成时间
            
        Returns:
            str: Markdown格式的报告
        """
        if generated_at is None:
            generated_at = datetime.now()
        
        markdown = f"""# {title}

**报告类型**: {report_type_display}  
**委托企业**: {company_name}  
**生成时间**: {generated_at.strftime('%Y年%m月%d日')}

---

{content}

---

## 免责声明

本报告由AI辅助生成，仅供参考。报告中的数据、分析和建议可能存在偏差或不准确之处。在做出重要决策前，请务必进行独立验证和专业咨询。

**生成方式**: AI辅助生成  
**模型版本**: {self.model}  
**生成时间**: {generated_at.isoformat()}
"""
        
        return markdown
    
    def generate_report_summary(self, content: str) -> str:
        """
        生成报告摘要
        
        Args:
            content: 报告内容
            
        Returns:
            str: 报告摘要
        """
        if not self.is_available():
            # 如果AI不可用，返回简单摘要
            lines = content.split('\n')
            summary_lines = [line for line in lines if line.strip()][:5]
            return '\n'.join(summary_lines)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的文档摘要专家。请用简洁的语言提取核心要点。"
                    },
                    {
                        "role": "user",
                        "content": f"请为以下报告生成一个200字以内的摘要，突出核心结论和建议：\n\n{content[:2000]}"
                    }
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # 出错时返回简单摘要
            lines = content.split('\n')
            summary_lines = [line for line in lines if line.strip()][:5]
            return '\n'.join(summary_lines)
    
    def get_available_templates(self) -> List[Dict]:
        """
        获取所有可用的报告模板
        
        Returns:
            List[Dict]: 模板列表
        """
        templates = []
        
        for report_type in ['technical_optimization', 'regional_market', 'policy_analysis', 
                           'competitor_analysis', 'investment_decision']:
            template = self.get_report_template(report_type)
            templates.append({
                'type': report_type,
                'name': template['name'],
                'sections': template['sections']
            })
        
        return templates
