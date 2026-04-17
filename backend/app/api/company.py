"""
企业信息管理 API
"""
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from flask import request
from app.api import company_bp
from app.models import User, Company, CompanyBusiness
from app import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os


def get_current_user():
    """获取当前用户"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        abort(404, message='用户不存在')
    return user


def admin_required():
    """管理员权限装饰器"""
    user = get_current_user()
    if user.role not in ['admin', 'editor']:
        abort(403, message='需要管理员权限')
    return user


# 预设数据
BUSINESS_TYPES = {
    'coal': {'name': '煤炭', 'subtypes': ['煤炭开采', '煤炭洗选', '煤炭贸易', '煤炭运输', '煤炭深加工']},
    'power': {'name': '电力', 'subtypes': ['火力发电', '水力发电', '风力发电', '光伏发电', '电力销售', '电力工程']},
    'oil_gas': {'name': '油气', 'subtypes': ['石油开采', '天然气开采', '油气炼化', '油气贸易', '油气储运']},
    'new_energy': {'name': '新能源', 'subtypes': ['光伏组件', '风电设备', '储能系统', '新能源汽车', '氢能']},
    'steel': {'name': '钢铁', 'subtypes': ['钢铁冶炼', '钢材加工', '钢材贸易', '废钢回收']},
    'chemical': {'name': '化工', 'subtypes': ['基础化工', '精细化工', '化工贸易', '化工设备']},
    'equipment': {'name': '设备制造', 'subtypes': ['能源设备', '环保设备', '自动化设备', '设备维修']},
    'service': {'name': '服务', 'subtypes': ['技术咨询', '工程设计', '项目管理', '检测认证', '培训教育']},
    'trade': {'name': '贸易', 'subtypes': ['能源贸易', '大宗商品', '进出口贸易', '供应链管理']},
    'other': {'name': '其他', 'subtypes': ['其他业务']}
}

EMPLOYEE_COUNT_OPTIONS = ['1-50人', '51-100人', '101-500人', '501-1000人', '1001-5000人', '5000人以上']
ANNUAL_REVENUE_OPTIONS = ['100万以下', '100万-500万', '500万-1000万', '1000万-5000万', '5000万-1亿', '1亿-10亿', '10亿以上']
INDUSTRY_CATEGORIES = [
    {'code': 'coal', 'name': '煤炭'},
    {'code': 'power', 'name': '电力'},
    {'code': 'oil_gas', 'name': '油气'},
    {'code': 'new_energy', 'name': '新能源'},
    {'code': 'steel', 'name': '钢铁'},
    {'code': 'nonferrous_metals', 'name': '有色金属'},
    {'code': 'chemical', 'name': '化工'},
    {'code': 'cement', 'name': '水泥建材'},
    {'code': 'equipment', 'name': '设备制造'},
    {'code': 'service', 'name': '技术服务'},
    {'code': 'trade', 'name': '贸易流通'},
    {'code': 'other', 'name': '其他'}
]


@company_bp.route('/options')
class CompanyOptions(MethodView):
    def get(self):
        """获取企业信息选项（公开接口）"""
        return {
            'business_types': BUSINESS_TYPES,
            'employee_count_options': EMPLOYEE_COUNT_OPTIONS,
            'annual_revenue_options': ANNUAL_REVENUE_OPTIONS,
            'industry_categories': INDUSTRY_CATEGORIES
        }


@company_bp.route('/my')
class MyCompany(MethodView):
    @jwt_required()
    def get(self):
        """获取当前用户的企业信息"""
        user = get_current_user()
        
        if not user.company_id:
            return {'company': None}
        
        company = Company.query.get(user.company_id)
        if not company:
            return {'company': None}
        
        return {
            'company': {
                'id': company.id,
                'name': company.name,
                'short_name': company.short_name,
                'unified_social_credit_code': company.unified_social_credit_code,
                'legal_representative': company.legal_representative,
                'registered_capital': company.registered_capital,
                'establishment_date': company.establishment_date.isoformat() if company.establishment_date else None,
                'contact_person': company.contact_person,
                'contact_phone': company.contact_phone,
                'contact_email': company.contact_email,
                'province': company.province,
                'city': company.city,
                'district': company.district,
                'address': company.address,
                'employee_count': company.employee_count,
                'annual_revenue': company.annual_revenue,
                'industry': company.industry,
                'industry_category': company.industry_category,
                'description': company.description,
                'website': company.website,
                'logo': company.logo,
                'business_license': company.business_license,
                'is_verified': company.is_verified,
                'verified_at': company.verified_at.isoformat() if company.verified_at else None,
                'status': company.status,
                'created_at': company.created_at.isoformat(),
                'updated_at': company.updated_at.isoformat()
            }
        }
    
    @jwt_required()
    def post(self):
        """创建企业信息"""
        user = get_current_user()
        
        if user.company_id:
            abort(400, message='您已经创建了企业信息')
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'contact_person', 'contact_phone']
        for field in required_fields:
            if not data.get(field):
                abort(400, message=f'{field} 不能为空')
        
        # 检查统一社会信用代码是否已存在
        if data.get('unified_social_credit_code'):
            existing = Company.query.filter_by(
                unified_social_credit_code=data['unified_social_credit_code']
            ).first()
            if existing:
                abort(400, message='该统一社会信用代码已被使用')
        
        # 创建企业
        company = Company(
            name=data['name'],
            short_name=data.get('short_name'),
            unified_social_credit_code=data.get('unified_social_credit_code'),
            legal_representative=data.get('legal_representative'),
            registered_capital=data.get('registered_capital'),
            establishment_date=datetime.strptime(data['establishment_date'], '%Y-%m-%d').date() if data.get('establishment_date') else None,
            contact_person=data['contact_person'],
            contact_phone=data['contact_phone'],
            contact_email=data.get('contact_email'),
            province=data.get('province'),
            city=data.get('city'),
            district=data.get('district'),
            address=data.get('address'),
            employee_count=data.get('employee_count'),
            annual_revenue=data.get('annual_revenue'),
            industry=data.get('industry'),
            industry_category=data.get('industry_category'),
            description=data.get('description'),
            website=data.get('website'),
            status='pending',
            created_by=user.id
        )
        
        db.session.add(company)
        db.session.flush()
        
        # 关联用户
        user.company_id = company.id
        db.session.commit()
        
        return {'message': '企业信息创建成功', 'company_id': company.id}, 201
    
    @jwt_required()
    def put(self):
        """更新企业信息"""
        user = get_current_user()
        
        if not user.company_id:
            abort(404, message='您还没有创建企业信息')
        
        company = Company.query.get(user.company_id)
        if not company:
            abort(404, message='企业信息不存在')
        
        data = request.get_json()
        
        # 更新字段
        if data.get('name'):
            company.name = data['name']
        if 'short_name' in data:
            company.short_name = data['short_name']
        if 'unified_social_credit_code' in data and data['unified_social_credit_code'] != company.unified_social_credit_code:
            existing = Company.query.filter_by(
                unified_social_credit_code=data['unified_social_credit_code']
            ).first()
            if existing:
                abort(400, message='该统一社会信用代码已被使用')
            company.unified_social_credit_code = data['unified_social_credit_code']
        if 'legal_representative' in data:
            company.legal_representative = data['legal_representative']
        if 'registered_capital' in data:
            company.registered_capital = data['registered_capital']
        if 'establishment_date' in data:
            company.establishment_date = datetime.strptime(data['establishment_date'], '%Y-%m-%d').date() if data['establishment_date'] else None
        if 'contact_person' in data:
            company.contact_person = data['contact_person']
        if 'contact_phone' in data:
            company.contact_phone = data['contact_phone']
        if 'contact_email' in data:
            company.contact_email = data['contact_email']
        if 'province' in data:
            company.province = data['province']
        if 'city' in data:
            company.city = data['city']
        if 'district' in data:
            company.district = data['district']
        if 'address' in data:
            company.address = data['address']
        if 'employee_count' in data:
            company.employee_count = data['employee_count']
        if 'annual_revenue' in data:
            company.annual_revenue = data['annual_revenue']
        if 'industry' in data:
            company.industry = data['industry']
        if 'industry_category' in data:
            company.industry_category = data['industry_category']
        if 'description' in data:
            company.description = data['description']
        if 'website' in data:
            company.website = data['website']
        
        company.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'message': '企业信息更新成功'}


@company_bp.route('/my/businesses')
class MyCompanyBusinesses(MethodView):
    @jwt_required()
    def get(self):
        """获取企业主营业务列表"""
        user = get_current_user()
        
        if not user.company_id:
            return {'items': []}
        
        businesses = CompanyBusiness.query.filter_by(company_id=user.company_id)\
            .order_by(CompanyBusiness.is_primary.desc(), CompanyBusiness.sort_order).all()
        
        return {
            'items': [{
                'id': b.id,
                'business_type': b.business_type,
                'business_name': b.business_name,
                'business_scope': b.business_scope,
                'annual_output': b.annual_output,
                'market_share': b.market_share,
                'service_area': b.service_area,
                'core_products': b.core_products,
                'certifications': b.certifications,
                'sort_order': b.sort_order,
                'is_primary': b.is_primary,
                'is_active': b.is_active,
                'created_at': b.created_at.isoformat(),
                'updated_at': b.updated_at.isoformat()
            } for b in businesses]
        }
    
    @jwt_required()
    def post(self):
        """创建主营业务"""
        user = get_current_user()
        
        if not user.company_id:
            abort(400, message='请先创建企业信息')
        
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('business_type') or not data.get('business_name'):
            abort(400, message='业务类型和业务名称不能为空')
        
        business = CompanyBusiness(
            company_id=user.company_id,
            business_type=data['business_type'],
            business_name=data['business_name'],
            business_scope=data.get('business_scope'),
            annual_output=data.get('annual_output'),
            market_share=data.get('market_share'),
            service_area=data.get('service_area'),
            core_products=data.get('core_products', []),
            certifications=data.get('certifications', []),
            sort_order=data.get('sort_order', 0),
            is_primary=data.get('is_primary', False),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(business)
        db.session.commit()
        
        return {'message': '业务创建成功', 'business_id': business.id}, 201


@company_bp.route('/my/businesses/<int:business_id>')
class MyCompanyBusinessDetail(MethodView):
    @jwt_required()
    def put(self, business_id):
        """更新主营业务"""
        user = get_current_user()
        
        business = CompanyBusiness.query.get_or_404(business_id)
        
        if business.company_id != user.company_id:
            abort(403, message='无权操作该业务')
        
        data = request.get_json()
        
        if 'business_type' in data:
            business.business_type = data['business_type']
        if 'business_name' in data:
            business.business_name = data['business_name']
        if 'business_scope' in data:
            business.business_scope = data['business_scope']
        if 'annual_output' in data:
            business.annual_output = data['annual_output']
        if 'market_share' in data:
            business.market_share = data['market_share']
        if 'service_area' in data:
            business.service_area = data['service_area']
        if 'core_products' in data:
            business.core_products = data['core_products']
        if 'certifications' in data:
            business.certifications = data['certifications']
        if 'sort_order' in data:
            business.sort_order = data['sort_order']
        if 'is_primary' in data:
            business.is_primary = data['is_primary']
        if 'is_active' in data:
            business.is_active = data['is_active']
        
        business.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'message': '业务更新成功'}
    
    @jwt_required()
    def delete(self, business_id):
        """删除主营业务"""
        user = get_current_user()
        
        business = CompanyBusiness.query.get_or_404(business_id)
        
        if business.company_id != user.company_id:
            abort(403, message='无权操作该业务')
        
        db.session.delete(business)
        db.session.commit()
        
        return {'message': '业务删除成功'}


@company_bp.route('/my/businesses/<int:business_id>/set-primary')
class SetPrimaryBusiness(MethodView):
    @jwt_required()
    def post(self, business_id):
        """设置为主营业务"""
        user = get_current_user()
        
        business = CompanyBusiness.query.get_or_404(business_id)
        
        if business.company_id != user.company_id:
            abort(403, message='无权操作该业务')
        
        # 取消其他主营业务
        CompanyBusiness.query.filter_by(company_id=user.company_id, is_primary=True)\
            .update({'is_primary': False})
        
        # 设置当前为主营
        business.is_primary = True
        db.session.commit()
        
        return {'message': '已设置为主营业务'}


# 管理员接口
@company_bp.route('/admin/list')
class AdminCompanyList(MethodView):
    @jwt_required()
    def get(self):
        """管理员获取企业列表"""
        admin_required()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = Company.query
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(Company.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = []
        for company in pagination.items:
            creator = User.query.get(company.created_by) if company.created_by else None
            items.append({
                'id': company.id,
                'name': company.name,
                'unified_social_credit_code': company.unified_social_credit_code,
                'contact_person': company.contact_person,
                'contact_phone': company.contact_phone,
                'industry_category': company.industry_category,
                'is_verified': company.is_verified,
                'status': company.status,
                'creator_name': creator.nickname if creator else None,
                'created_at': company.created_at.isoformat()
            })
        
        return {
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }


@company_bp.route('/admin/<int:company_id>/verify')
class AdminVerifyCompany(MethodView):
    @jwt_required()
    def post(self, company_id):
        """管理员审核企业"""
        admin = admin_required()
        
        company = Company.query.get_or_404(company_id)
        data = request.get_json()
        
        approved = data.get('approved', False)
        
        if approved:
            company.is_verified = True
            company.verified_at = datetime.utcnow()
            company.verified_by = admin.id
            company.status = 'active'
            message = '企业认证通过'
        else:
            company.is_verified = False
            company.status = 'inactive'
            message = '企业认证未通过'
        
        db.session.commit()
        
        return {'message': message}


@company_bp.route('/admin/<int:company_id>')
class AdminCompanyDetail(MethodView):
    @jwt_required()
    def get(self, company_id):
        """管理员获取企业详情"""
        admin_required()
        
        company = Company.query.get_or_404(company_id)
        
        return {
            'company': {
                'id': company.id,
                'name': company.name,
                'short_name': company.short_name,
                'unified_social_credit_code': company.unified_social_credit_code,
                'legal_representative': company.legal_representative,
                'registered_capital': company.registered_capital,
                'establishment_date': company.establishment_date.isoformat() if company.establishment_date else None,
                'contact_person': company.contact_person,
                'contact_phone': company.contact_phone,
                'contact_email': company.contact_email,
                'province': company.province,
                'city': company.city,
                'district': company.district,
                'address': company.address,
                'employee_count': company.employee_count,
                'annual_revenue': company.annual_revenue,
                'industry': company.industry,
                'industry_category': company.industry_category,
                'description': company.description,
                'website': company.website,
                'logo': company.logo,
                'business_license': company.business_license,
                'is_verified': company.is_verified,
                'verified_at': company.verified_at.isoformat() if company.verified_at else None,
                'status': company.status,
                'created_at': company.created_at.isoformat(),
                'updated_at': company.updated_at.isoformat()
            }
        }
