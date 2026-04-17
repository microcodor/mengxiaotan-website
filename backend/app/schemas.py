from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    phone = fields.Str(required=True)
    nickname = fields.Str()
    avatar = fields.Str()
    role = fields.Str()
    status = fields.Str()
    last_login = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)

class LoginSchema(Schema):
    phone = fields.Str(required=True, validate=validate.Length(min=11, max=11))
    password = fields.Str(required=True, validate=validate.Length(min=6))

class RegisterSchema(Schema):
    phone = fields.Str(required=True, validate=validate.Length(min=11, max=11))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    nickname = fields.Str()

class ArticleSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    summary = fields.Str()
    content = fields.Str()
    cover_image = fields.Str()
    source = fields.Str()
    source_url = fields.Str()
    category = fields.Str()
    tags = fields.List(fields.Str())
    view_count = fields.Int()
    like_count = fields.Int()
    is_reviewed = fields.Bool()
    is_top = fields.Bool()
    is_carousel = fields.Bool()
    published_at = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ArticleListQuerySchema(Schema):
    page = fields.Int(load_default=1)
    per_page = fields.Int(load_default=20)
    category = fields.Str()
    keyword = fields.Str()
    start_date = fields.DateTime()
    end_date = fields.DateTime()

class SubscriptionPlanSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Decimal(as_string=True)
    duration_days = fields.Int()
    features = fields.Dict()
    sort_order = fields.Int()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)

class SubscriptionSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    plan_id = fields.Int(required=True)
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    status = fields.Str()
    auto_renew = fields.Bool()
    push_channels = fields.Dict()
    custom_keywords = fields.List(fields.Str())
    created_at = fields.DateTime(dump_only=True)
    plan = fields.Nested(SubscriptionPlanSchema, dump_only=True)

class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    order_no = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    plan_id = fields.Int(required=True)
    amount = fields.Decimal(as_string=True, dump_only=True)
    payment_method = fields.Str(required=True)
    payment_status = fields.Str(dump_only=True)
    payment_time = fields.DateTime(dump_only=True)
    payment_proof = fields.Str()
    contact_info = fields.Dict()
    remark = fields.Str()
    admin_note = fields.Str()
    confirmed_by = fields.Int(dump_only=True)
    confirmed_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    plan = fields.Nested(SubscriptionPlanSchema, dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)
