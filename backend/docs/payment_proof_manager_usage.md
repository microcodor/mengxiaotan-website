# PaymentProofManager 使用文档

## 概述

`PaymentProofManager` 是订阅系统完善功能的核心组件，负责处理支付凭证的上传、验证和存储。

## 功能特性

- ✅ 支持 JPG、PNG、PDF 格式
- ✅ 文件大小限制 5MB
- ✅ 文件名安全处理（使用 werkzeug.utils.secure_filename）
- ✅ 按年月组织的存储结构
- ✅ 完整的错误处理和验证

## 存储路径

```
uploads/payment_proofs/{year}/{month}/{order_id}_{timestamp}.{ext}
```

示例：
```
uploads/payment_proofs/2024/01/123_1705305600.jpg
```

## API 端点

### 1. 上传支付凭证

**端点**: `POST /api/subscriptions/orders/{order_id}/payment-proof`

**请求**:
```http
POST /api/subscriptions/orders/123/payment-proof
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

file: [binary data]
```

**响应**:
```json
{
  "success": true,
  "data": {
    "file_url": "/uploads/payment_proofs/2024/01/123_1705305600.jpg",
    "order_id": 123
  },
  "message": "支付凭证上传成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "不支持的文件格式，仅支持JPG、PNG、PDF"
}
```

### 2. 获取支付凭证

**端点**: `GET /api/subscriptions/orders/{order_id}/payment-proof`

**请求**:
```http
GET /api/subscriptions/orders/123/payment-proof
Authorization: Bearer {jwt_token}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "file_url": "/uploads/payment_proofs/2024/01/123_1705305600.jpg",
    "order_id": 123
  }
}
```

### 3. 删除支付凭证

**端点**: `DELETE /api/subscriptions/orders/{order_id}/payment-proof`

**请求**:
```http
DELETE /api/subscriptions/orders/123/payment-proof
Authorization: Bearer {jwt_token}
```

**响应**:
```json
{
  "success": true,
  "message": "支付凭证已删除"
}
```

## 代码示例

### 在 Python 中使用

```python
from app.services.payment_proof_manager import PaymentProofManager
from werkzeug.datastructures import FileStorage

# 创建管理器实例
manager = PaymentProofManager()

# 验证文件
is_valid, error_message = manager.validate_file(file)
if not is_valid:
    print(f"验证失败: {error_message}")
    return

# 上传文件
result = manager.upload_proof(file, order_id=123)
if result['success']:
    print(f"上传成功: {result['file_url']}")
else:
    print(f"上传失败: {result['error']}")

# 获取支付凭证URL
file_url = manager.get_proof_url(order_id=123)
```

### 在前端使用 (JavaScript/TypeScript)

```typescript
// 上传支付凭证
async function uploadPaymentProof(orderId: number, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`/api/subscriptions/orders/${orderId}/payment-proof`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('上传成功:', result.data.file_url);
  } else {
    console.error('上传失败:', result.error);
  }
}

// 获取支付凭证
async function getPaymentProof(orderId: number) {
  const response = await fetch(`/api/subscriptions/orders/${orderId}/payment-proof`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const result = await response.json();
  return result.data.file_url;
}
```

## 验证规则

### 文件格式
- **允许**: JPG, JPEG, PNG, PDF
- **MIME类型**: image/jpeg, image/jpg, image/png, application/pdf

### 文件大小
- **最大**: 5MB (5,242,880 bytes)
- **最小**: 不能为空

### 文件名
- 自动使用 `secure_filename` 清理
- 格式: `{order_id}_{timestamp}.{ext}`

## 错误处理

| 错误类型 | HTTP状态码 | 错误信息 |
|---------|-----------|---------|
| 未选择文件 | 400 | "未选择文件" |
| 文件格式不支持 | 400 | "不支持的文件格式，仅支持JPG、PNG、PDF" |
| MIME类型不支持 | 400 | "不支持的文件类型: {mimetype}" |
| 文件过大 | 400 | "文件大小超过5MB限制 (当前: {size}MB)" |
| 文件为空 | 400 | "文件为空" |
| 订单状态不允许 | 400 | "订单状态不允许上传支付凭证" |
| 上传失败 | 400 | "文件上传失败，请稍后重试" |

## 测试

运行单元测试：

```bash
cd backend
./venv/bin/pytest tests/test_payment_proof_manager.py -v
```

测试覆盖：
- ✅ 文件格式验证（JPG, PNG, PDF）
- ✅ 文件大小验证（边界测试）
- ✅ MIME类型验证
- ✅ 文件上传成功
- ✅ 目录结构创建
- ✅ 错误处理

## 安全考虑

1. **文件名清理**: 使用 `secure_filename` 防止路径遍历攻击
2. **MIME类型验证**: 检查文件的实际类型，不仅依赖扩展名
3. **文件大小限制**: 防止大文件攻击
4. **权限检查**: 只允许订单所有者上传凭证
5. **状态检查**: 只允许 pending 状态的订单上传凭证

## 配置

在 `config.py` 中配置：

```python
# Upload
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
```

## 依赖

- Flask
- werkzeug
- SQLAlchemy

## 相关需求

- **需求 1.1**: 允许用户上传支付凭证
- **需求 1.2**: 支持 JPG、PNG、PDF 格式，最大 5MB
- **需求 1.3**: 存储文件并记录 URL
- **需求 1.7**: 返回明确的错误信息

## 下一步

Task 2.1 已完成，实现了：
- ✅ PaymentProofManager 类
- ✅ upload_proof() 方法
- ✅ validate_file() 方法
- ✅ 文件名 sanitization
- ✅ 安全存储路径
- ✅ API 端点集成
- ✅ 完整的单元测试

后续任务将实现：
- Task 2.2: OCR 支付信息提取
- Task 2.3: 退款流程
- Task 2.4: 关键词推送引擎
