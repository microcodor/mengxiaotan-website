from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.api import auth_bp
from app.models import User
from app.schemas import LoginSchema, RegisterSchema, UserSchema
from app import db
from datetime import datetime

@auth_bp.route('/register')
class Register(MethodView):
    @auth_bp.arguments(RegisterSchema)
    @auth_bp.response(201, UserSchema)
    def post(self, data):
        """用户注册"""
        if User.query.filter_by(phone=data['phone']).first():
            abort(400, message='手机号已注册')
        
        user = User(
            phone=data['phone'],
            nickname=data.get('nickname', f"用户{data['phone'][-4:]}")
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return user

@auth_bp.route('/login')
class Login(MethodView):
    @auth_bp.arguments(LoginSchema)
    def post(self, data):
        """用户登录"""
        user = User.query.filter_by(phone=data['phone']).first()
        
        if not user or not user.check_password(data['password']):
            abort(401, message='手机号或密码错误')
        
        if user.status != 'active':
            abort(403, message='账号已被禁用')
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': UserSchema().dump(user)
        }

@auth_bp.route('/refresh')
class RefreshToken(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        """刷新访问令牌"""
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return {'access_token': access_token}

@auth_bp.route('/me')
class CurrentUser(MethodView):
    @jwt_required()
    @auth_bp.response(200, UserSchema)
    def get(self):
        """获取当前用户信息"""
        current_user_id = int(get_jwt_identity())
        user = User.query.get_or_404(current_user_id)
        return user
