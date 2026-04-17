"""
定制报告API
Custom Reports API
"""
from flask import request, jsonify, send_file
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.report_service import ReportService
from app import db
import os
from werkzeug.utils import secure_filename

reports_bp = Blueprint('reports', 'reports', url_prefix='/api/reports', description='定制报告接口')

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
UPLOAD_FOLDER = 'uploads/reports'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@reports_bp.route('/types', methods=['GET'])
@jwt_required()
def get_report_types():
    """获取报告类型列表"""
    try:
        report_service = ReportService(db)
        types = report_service.get_report_types()
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': types
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取报告类型失败: {str(e)}'}), 500


@reports_bp.route('/quota', methods=['GET'])
@jwt_required()
def get_quota():
    """获取用户配额"""
    try:
        current_user_id = get_jwt_identity()
        report_service = ReportService(db)
        
        quota = report_service.get_quota_usage(current_user_id)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': quota
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取配额失败: {str(e)}'}), 500


@reports_bp.route('/requests', methods=['POST'])
@jwt_required()
def create_request():
    """创建报告申请"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['report_type', 'title', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'code': 400, 'message': f'{field}不能为空'}), 400
        
        # 获取用户的企业ID
        user = db.session.execute(
            'SELECT company_id FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or not user[0]:
            return jsonify({'code': 400, 'message': '请先绑定企业信息'}), 400
        
        company_id = user[0]
        
        # 创建申请
        report_service = ReportService(db)
        request_id = report_service.create_request(current_user_id, company_id, data)
        
        return jsonify({
            'code': 200,
            'message': '申请提交成功',
            'data': {
                'request_id': request_id
            }
        })
        
    except ValueError as e:
        return jsonify({'code': 400, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建申请失败: {str(e)}'}), 500


@reports_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_requests():
    """获取用户的报告申请列表"""
    try:
        current_user_id = get_jwt_identity()
        status = request.args.get('status')
        
        report_service = ReportService(db)
        requests = report_service.get_user_requests(current_user_id, status)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': requests
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取申请列表失败: {str(e)}'}), 500


@reports_bp.route('/requests/<int:request_id>', methods=['GET'])
@jwt_required()
def get_request_detail(request_id):
    """获取报告申请详情"""
    try:
        current_user_id = get_jwt_identity()
        
        report_service = ReportService(db)
        detail = report_service.get_request_detail(request_id)
        
        if not detail:
            return jsonify({'code': 404, 'message': '申请不存在'}), 404
        
        # 验证权限
        if detail['user_id'] != current_user_id:
            # 检查是否是管理员
            user = db.session.execute(
                'SELECT role FROM users WHERE id = :id',
                {'id': current_user_id}
            ).fetchone()
            
            if not user or user[0] not in ['admin', 'editor']:
                return jsonify({'code': 403, 'message': '无权限访问该申请'}), 403
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': detail
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取申请详情失败: {str(e)}'}), 500


@reports_bp.route('/requests/<int:request_id>/files', methods=['POST'])
@jwt_required()
def upload_report_file(request_id):
    """上传报告文件（管理员）"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查管理员权限
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] not in ['admin', 'editor']:
            return jsonify({'code': 403, 'message': '无权限上传文件'}), 403
        
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'code': 400, 'message': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'code': 400, 'message': '不支持的文件类型'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # 保存文件记录
        report_service = ReportService(db)
        file_id = report_service.add_report_file(request_id, {
            'file_name': filename,
            'file_path': file_path,
            'file_type': file_type,
            'file_size': file_size,
            'uploaded_by': current_user_id
        })
        
        # 更新申请状态为已完成
        report_service.update_request_status(request_id, 'completed')
        
        return jsonify({
            'code': 200,
            'message': '文件上传成功',
            'data': {
                'file_id': file_id,
                'file_name': filename
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'上传文件失败: {str(e)}'}), 500


@reports_bp.route('/requests/<int:request_id>/files/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_report_file(request_id, file_id):
    """下载报告文件"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取申请信息
        report_service = ReportService(db)
        detail = report_service.get_request_detail(request_id)
        
        if not detail:
            return jsonify({'code': 404, 'message': '申请不存在'}), 404
        
        # 验证权限
        if detail['user_id'] != current_user_id:
            user = db.session.execute(
                'SELECT role FROM users WHERE id = :id',
                {'id': current_user_id}
            ).fetchone()
            
            if not user or user[0] not in ['admin', 'editor']:
                return jsonify({'code': 403, 'message': '无权限下载文件'}), 403
        
        # 获取文件信息
        file_info = None
        for file in detail['files']:
            if file['id'] == file_id:
                file_info = file
                break
        
        if not file_info:
            return jsonify({'code': 404, 'message': '文件不存在'}), 404
        
        # 发送文件
        return send_file(
            file_info['file_path'],
            as_attachment=True,
            download_name=file_info['file_name']
        )
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'下载文件失败: {str(e)}'}), 500


@reports_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取统计数据"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查是否是管理员
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        report_service = ReportService(db)
        
        if user and user[0] in ['admin', 'editor']:
            # 管理员查看全局统计
            stats = report_service.get_statistics()
        else:
            # 普通用户查看个人统计
            stats = report_service.get_statistics(current_user_id)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': stats
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取统计数据失败: {str(e)}'}), 500


# ==================== 管理员接口 ====================

@reports_bp.route('/admin/requests', methods=['GET'])
@jwt_required()
def admin_get_requests():
    """管理员获取所有申请"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查管理员权限
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] not in ['admin', 'editor']:
            return jsonify({'code': 403, 'message': '无权限访问'}), 403
        
        status = request.args.get('status')
        
        # 查询所有申请
        if status:
            requests = db.session.execute(
                '''SELECT r.*, c.name as company_name, u.nickname as user_name
                   FROM report_requests r
                   LEFT JOIN companies c ON r.company_id = c.id
                   LEFT JOIN users u ON r.user_id = u.id
                   WHERE r.status = :status
                   ORDER BY r.created_at DESC''',
                {'status': status}
            ).fetchall()
        else:
            requests = db.session.execute(
                '''SELECT r.*, c.name as company_name, u.nickname as user_name
                   FROM report_requests r
                   LEFT JOIN companies c ON r.company_id = c.id
                   LEFT JOIN users u ON r.user_id = u.id
                   ORDER BY r.created_at DESC'''
            ).fetchall()
        
        result = []
        for req in requests:
            result.append({
                'id': req[0],
                'user_id': req[1],
                'user_name': req[15],
                'company_id': req[2],
                'company_name': req[14],
                'report_type': req[3],
                'title': req[4],
                'description': req[5],
                'expected_delivery_date': req[6].isoformat() if req[6] else None,
                'status': req[8],
                'created_at': req[13].isoformat() if req[13] else None
            })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取申请列表失败: {str(e)}'}), 500


@reports_bp.route('/admin/requests/<int:request_id>/assign', methods=['POST'])
@jwt_required()
def admin_assign_request(request_id):
    """管理员分配申请"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查管理员权限
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] not in ['admin', 'editor']:
            return jsonify({'code': 403, 'message': '无权限操作'}), 403
        
        data = request.get_json()
        assigned_to = data.get('assigned_to', current_user_id)
        
        report_service = ReportService(db)
        report_service.update_request_status(request_id, 'assigned', assigned_to=assigned_to)
        
        return jsonify({
            'code': 200,
            'message': '分配成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'分配失败: {str(e)}'}), 500


@reports_bp.route('/admin/requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def admin_reject_request(request_id):
    """管理员拒绝申请"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查管理员权限
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] not in ['admin', 'editor']:
            return jsonify({'code': 403, 'message': '无权限操作'}), 403
        
        data = request.get_json()
        reason = data.get('reason', '')
        
        report_service = ReportService(db)
        report_service.update_request_status(request_id, 'rejected', rejected_reason=reason)
        
        return jsonify({
            'code': 200,
            'message': '已拒绝申请'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'操作失败: {str(e)}'}), 500


# 导入datetime
from datetime import datetime


# ==================== AI生成接口 ====================

@reports_bp.route('/ai/templates', methods=['GET'])
@jwt_required()
def get_ai_templates():
    """获取AI报告模板列表"""
    try:
        from app.services.report_generator_service import ReportGeneratorService
        
        generator = ReportGeneratorService()
        templates = generator.get_available_templates()
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'available': generator.is_available(),
                'templates': templates
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取模板失败: {str(e)}'}), 500


@reports_bp.route('/ai/generate', methods=['POST'])
@jwt_required()
def generate_report_with_ai():
    """使用AI生成报告内容"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查管理员权限
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] not in ['admin', 'editor']:
            return jsonify({'code': 403, 'message': '无权限使用AI生成功能'}), 403
        
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({'code': 400, 'message': '缺少request_id参数'}), 400
        
        # 获取申请详情
        report_service = ReportService(db)
        detail = report_service.get_request_detail(request_id)
        
        if not detail:
            return jsonify({'code': 404, 'message': '申请不存在'}), 404
        
        # 使用AI生成报告
        from app.services.report_generator_service import ReportGeneratorService
        
        generator = ReportGeneratorService()
        
        if not generator.is_available():
            return jsonify({
                'code': 503,
                'message': 'AI服务未配置或不可用，请检查OPENAI_API_KEY环境变量'
            }), 503
        
        # 生成报告内容
        result = generator.generate_report_content(
            report_type=detail['report_type'],
            title=detail['title'],
            description=detail['description'],
            additional_context={
                '企业名称': detail['company_name'],
                '申请时间': detail['created_at']
            }
        )
        
        if not result['success']:
            return jsonify({
                'code': 500,
                'message': f'AI生成失败: {result["error"]}'
            }), 500
        
        # 格式化为Markdown
        markdown_content = generator.format_report_to_markdown(
            title=detail['title'],
            company_name=detail['company_name'],
            report_type_display=detail['report_type_display'],
            content=result['content']
        )
        
        # 生成摘要
        summary = generator.generate_report_summary(result['content'])
        
        return jsonify({
            'code': 200,
            'message': 'AI生成成功',
            'data': {
                'content': markdown_content,
                'summary': summary,
                'tokens_used': result.get('tokens_used', 0),
                'model': result.get('model', 'unknown')
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'生成报告失败: {str(e)}'}), 500


@reports_bp.route('/ai/generate-and-save', methods=['POST'])
@jwt_required()
def generate_and_save_report():
    """使用AI生成报告并保存为文件"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查管理员权限
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] not in ['admin', 'editor']:
            return jsonify({'code': 403, 'message': '无权限使用AI生成功能'}), 403
        
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({'code': 400, 'message': '缺少request_id参数'}), 400
        
        # 获取申请详情
        report_service = ReportService(db)
        detail = report_service.get_request_detail(request_id)
        
        if not detail:
            return jsonify({'code': 404, 'message': '申请不存在'}), 404
        
        # 使用AI生成报告
        from app.services.report_generator_service import ReportGeneratorService
        import markdown
        from weasyprint import HTML
        
        generator = ReportGeneratorService()
        
        if not generator.is_available():
            return jsonify({
                'code': 503,
                'message': 'AI服务未配置或不可用'
            }), 503
        
        # 生成报告内容
        result = generator.generate_report_content(
            report_type=detail['report_type'],
            title=detail['title'],
            description=detail['description'],
            additional_context={
                '企业名称': detail['company_name'],
                '申请时间': detail['created_at']
            }
        )
        
        if not result['success']:
            return jsonify({
                'code': 500,
                'message': f'AI生成失败: {result["error"]}'
            }), 500
        
        # 格式化为Markdown
        markdown_content = generator.format_report_to_markdown(
            title=detail['title'],
            company_name=detail['company_name'],
            report_type_display=detail['report_type_display'],
            content=result['content']
        )
        
        # 保存为Markdown文件
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"report_{request_id}_{timestamp}.md"
        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        file_size = os.path.getsize(file_path)
        
        # 保存文件记录
        file_id = report_service.add_report_file(request_id, {
            'file_name': filename,
            'file_path': file_path,
            'file_type': 'md',
            'file_size': file_size,
            'uploaded_by': current_user_id
        })
        
        # 更新申请状态为已完成
        report_service.update_request_status(request_id, 'completed')
        
        return jsonify({
            'code': 200,
            'message': 'AI生成并保存成功',
            'data': {
                'file_id': file_id,
                'file_name': filename,
                'tokens_used': result.get('tokens_used', 0)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'生成报告失败: {str(e)}'}), 500


@reports_bp.route('/admin/statistics', methods=['GET'])
@jwt_required()
def admin_get_statistics():
    """管理员获取统计信息"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查管理员权限
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] not in ['admin', 'editor']:
            return jsonify({'code': 403, 'message': '无权限访问'}), 403
        
        # 统计各状态的申请数量
        stats = db.session.execute(
            '''SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'assigned' THEN 1 ELSE 0 END) as assigned,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
               FROM report_requests'''
        ).fetchone()
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total': stats[0] or 0,
                'by_status': {
                    'pending': stats[1] or 0,
                    'assigned': stats[2] or 0,
                    'in_progress': stats[3] or 0,
                    'completed': stats[4] or 0,
                    'rejected': stats[5] or 0
                }
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取统计信息失败: {str(e)}'}), 500


@reports_bp.route('/admin/requests/<int:request_id>/status', methods=['PUT'])
@jwt_required()
def admin_update_status(request_id):
    """管理员更新申请状态"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查管理员权限
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] not in ['admin', 'editor']:
            return jsonify({'code': 403, 'message': '无权限操作'}), 403
        
        data = request.get_json()
        status = data.get('status')
        rejected_reason = data.get('rejected_reason')
        
        if not status:
            return jsonify({'code': 400, 'message': '缺少status参数'}), 400
        
        report_service = ReportService(db)
        report_service.update_request_status(
            request_id,
            status,
            rejected_reason=rejected_reason
        )
        
        return jsonify({
            'code': 200,
            'message': '状态更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新状态失败: {str(e)}'}), 500


@reports_bp.route('/admin/requests/<int:request_id>/upload', methods=['POST'])
@jwt_required()
def admin_upload_file(request_id):
    """管理员上传报告文件"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查管理员权限
        user = db.session.execute(
            'SELECT role FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] not in ['admin', 'editor']:
            return jsonify({'code': 403, 'message': '无权限上传文件'}), 403
        
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'code': 400, 'message': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'code': 400, 'message': '不支持的文件类型'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # 保存文件记录
        report_service = ReportService(db)
        file_id = report_service.add_report_file(request_id, {
            'file_name': filename,
            'file_path': file_path,
            'file_type': file_type,
            'file_size': file_size,
            'uploaded_by': current_user_id
        })
        
        # 更新申请状态为已完成
        report_service.update_request_status(request_id, 'completed')
        
        return jsonify({
            'code': 200,
            'message': '文件上传成功',
            'data': {
                'file_id': file_id,
                'file_name': filename
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'上传文件失败: {str(e)}'}), 500
