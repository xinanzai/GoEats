import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from app.config import settings


class TestPasswordHashing:
    """密码哈希测试"""

    def test_hash_password(self):
        """测试密码哈希生成"""
        password = "SecurePass123!"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert hashed.startswith("$2")

    def test_hash_password_is_unique(self):
        """测试相同密码生成不同哈希（盐值不同）"""
        password = "SamePassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_hash_password_length(self):
        """测试哈希密码长度"""
        password = "test"
        hashed = get_password_hash(password)

        assert len(hashed) > 50


class TestPasswordVerification:
    """密码验证测试"""

    def test_verify_correct_password(self):
        """测试正确密码验证"""
        password = "MyPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """测试错误密码验证"""
        password = "CorrectPassword"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_verify_empty_password(self):
        """测试空密码验证"""
        password = "RealPassword"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False

    def test_verify_case_sensitive(self):
        """测试密码大小写敏感"""
        password = "CaseSensitive123"
        hashed = get_password_hash(password)

        assert verify_password("casesensitive123", hashed) is False
        assert verify_password("CASESENSITIVE123", hashed) is False

    def test_verify_special_characters(self):
        """测试特殊字符密码验证"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("P@ssw0rd", hashed) is False

    def test_verify_unicode_password(self):
        """测试Unicode密码验证"""
        password = "密码123中文测试"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_against_wrong_hash(self):
        """测试使用错误哈希验证"""
        password = "MyPassword"
        hashed1 = get_password_hash(password)
        hashed2 = get_password_hash("DifferentPassword")

        assert verify_password(password, hashed2) is False
        assert verify_password(password, hashed1) is True


class TestTokenCreation:
    """Token 创建测试"""

    def test_create_access_token_default(self):
        """测试创建默认过期时间 Token"""
        data = {"sub": "1", "username": "testuser", "role": "user"}
        token = create_access_token(data=data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "1"
        assert payload["username"] == "testuser"
        assert payload["role"] == "user"
        assert "exp" in payload

    def test_create_access_token_custom_expires(self):
        """测试创建自定义过期时间 Token"""
        data = {"sub": "2", "username": "admin"}
        expires = timedelta(minutes=30)
        before = datetime.now(timezone.utc)
        token = create_access_token(data=data, expires_delta=expires)
        after = datetime.now(timezone.utc)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "2"
        assert payload["username"] == "admin"

        # 添加 ±2 秒容差以处理时间精度问题
        tolerance = 2
        expected_exp_min = before.timestamp() + expires.total_seconds() - tolerance
        expected_exp_max = after.timestamp() + expires.total_seconds() + tolerance
        assert expected_exp_min <= payload["exp"] <= expected_exp_max

    def test_create_access_token_preserves_data(self):
        """测试 Token 保留所有原始数据"""
        data = {
            "sub": "3",
            "username": "merchant_user",
            "role": "merchant",
            "phone": "13800000001",
        }
        token = create_access_token(data=data)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "3"
        assert payload["username"] == "merchant_user"
        assert payload["role"] == "merchant"
        assert payload["phone"] == "13800000001"

    def test_create_access_token_does_not_mutate_original(self):
        """测试 Token 创建不修改原始数据"""
        original_data = {"sub": "4", "username": "test"}
        data_copy = original_data.copy()
        create_access_token(data=original_data)

        assert original_data == data_copy
        assert "exp" not in original_data

    def test_create_tokens_have_valid_structure(self):
        """测试创建的 Token 具有正确的 JWT 结构"""
        data = {"sub": "5", "username": "test"}
        token1 = create_access_token(data=data)
        token2 = create_access_token(data=data)

        assert isinstance(token1, str)
        assert "." in token1
        assert len(token1.split(".")) == 3


class TestTokenDecoding:
    """Token 解码测试"""

    def test_decode_valid_token(self):
        """测试解码有效 Token"""
        data = {"sub": "10", "username": "decoder_test", "role": "admin"}
        token = create_access_token(data=data)

        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "10"
        assert payload["username"] == "decoder_test"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_decode_expired_token(self):
        """测试解码过期 Token 返回 None"""
        data = {"sub": "11", "username": "expired_user"}
        token = create_access_token(data=data, expires_delta=timedelta(seconds=-1))

        payload = decode_access_token(token)
        assert payload is None

    def test_decode_invalid_token(self):
        """测试解码无效 Token 返回 None"""
        payload = decode_access_token("invalid.token.here")
        assert payload is None

    def test_decode_empty_token(self):
        """测试解码空字符串返回 None"""
        payload = decode_access_token("")
        assert payload is None

    def test_decode_modified_token(self):
        """测试解码被篡改的 Token 返回 None"""
        data = {"sub": "12", "username": "test"}
        token = create_access_token(data=data)
        parts = token.split(".")
        parts[1] = "modified"
        tampered_token = ".".join(parts)

        payload = decode_access_token(tampered_token)
        assert payload is None

    def test_decode_token_with_wrong_secret(self):
        """测试使用错误密钥解码返回 None"""
        data = {"sub": "13", "username": "test"}
        token = jwt.encode(data, "wrong-secret-key", algorithm=settings.ALGORITHM)

        payload = decode_access_token(token)
        assert payload is None

    def test_decode_token_missing_claims(self):
        """测试解码缺少声明的 Token"""
        data = {"sub": "14"}
        token = create_access_token(data=data)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "14"
        assert "username" not in payload

    def test_decode_token_returns_dict(self):
        """测试解码返回值类型"""
        data = {"sub": "15", "username": "type_test"}
        token = create_access_token(data=data)

        payload = decode_access_token(token)
        assert isinstance(payload, dict)


class TestTokenRoundTrip:
    """Token 创建到解码完整流程测试"""

    def test_create_and_decode_roundtrip(self):
        """测试 Token 创建后能正确解码"""
        original_data = {
            "sub": "100",
            "username": "roundtrip_user",
            "role": "user",
            "phone": "13900000001",
        }
        token = create_access_token(data=original_data)
        payload = decode_access_token(token)

        assert payload["sub"] == original_data["sub"]
        assert payload["username"] == original_data["username"]
        assert payload["role"] == original_data["role"]
        assert payload["phone"] == original_data["phone"]

    def test_token_verify_password_flow(self):
        """测试密码验证和 Token 创建完整流程"""
        password = "FlowTest123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

        data = {"sub": "200", "username": "flow_user", "role": "admin"}
        token = create_access_token(data=data)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "200"
        assert payload["role"] == "admin"
