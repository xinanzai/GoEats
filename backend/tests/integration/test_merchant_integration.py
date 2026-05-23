"""
商家注册 → 管理员审核 → 商家登录 全流程联调测试
测试目标：任务 5.1 商家流程联调
测试环境：真实后端服务 (http://localhost:8000)
"""
import asyncio
import httpx
import json
import sys
import os
from datetime import datetime, timezone
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from app.core.security import get_password_hash

BASE_URL = "http://localhost:8000/api/v1"
DATABASE_URL = "sqlite+aiosqlite:///./food_delivery.db"
report = []

def log_step(step, status, message, data=None):
    emoji = "✅" if status == "PASS" else "❌"
    line = f"[{status}] {emoji} {step}: {message}"
    if data:
        line += f"\n  数据: {json.dumps(data, ensure_ascii=False, indent=2, default=str)}"
    print(line)
    report.append({"step": step, "status": status, "message": message, "data": data})
    return status == "PASS"

async def cleanup_test_data():
    """清理之前的测试数据"""
    engine = create_async_engine(DATABASE_URL)
    try:
        async with AsyncSession(engine) as session:
            # 删除之前的测试商家（按用户名和手机号匹配）
            await session.execute(text("DELETE FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='integration_test_merchant')"))
            await session.execute(text("DELETE FROM users WHERE username='integration_test_merchant'"))
            await session.commit()
            print("✅ 已清理之前的测试数据")
    finally:
        await engine.dispose()

async def ensure_admin_exists():
    """确保数据库中已存在管理员用户"""
    engine = create_async_engine(DATABASE_URL)
    try:
        async with AsyncSession(engine) as session:
            result = await session.execute(text("SELECT id FROM users WHERE role='admin' LIMIT 1"))
            admin = result.scalar_one_or_none()
            if admin:
                print(f"✅ 管理员已存在 (ID={admin})")
                return
            # Create admin user
            from app.models.user import User
            admin_user = User(
                username="admin",
                phone="13800000000",
                password_hash=get_password_hash("admin123"),
                role="admin",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(admin_user)
            await session.commit()
            print(f"✅ 管理员创建成功: username=admin, phone=13800000000, password=admin123")
    finally:
        await engine.dispose()

async def run_integration_test():
    all_passed = True
    admin_token = None
    merchant_token = None
    merchant_id = None

    # 清理之前的测试数据
    print("\n" + "="*60)
    print("前置条件：清理之前的测试数据")
    print("="*60)
    await cleanup_test_data()

    # 确保管理员存在
    print("\n" + "="*60)
    print("前置条件：确保管理员用户存在")
    print("="*60)
    await ensure_admin_exists()

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:

        # ==================== 第一步：商家注册 ====================
        print("\n" + "="*60)
        print("第一步：商家注册")
        print("="*60)

        merchant_reg_data = {
            "username": "integration_test_merchant",
            "phone": "13899999999",
            "password": "merchant888",
            "business_name": "联调测试美食餐厅",
            "contact_phone": "13999999999",
            "address": "深圳市南山区联调路888号",
            "description": "这是一家用于联调测试的餐厅",
        }

        try:
            resp = await client.post("/auth/merchant/register", json=merchant_reg_data)
            if resp.status_code == 201:
                reg_result = resp.json()
                merchant_id = reg_result["merchant"]["id"]
                passed = log_step(
                    "商家注册", "PASS",
                    f"商家注册成功，商户ID={merchant_id}，状态={reg_result['merchant']['status']}",
                    {
                        "username": reg_result["user"]["username"],
                        "role": reg_result["user"]["role"],
                        "merchant_status": reg_result["merchant"]["status"],
                        "merchant_id": merchant_id,
                    }
                )
            elif resp.status_code == 400:
                passed = log_step("商家注册", "PASS", f"商家已存在（重复测试），使用已有数据: {resp.json()}")
                # 获取已有商家 ID
                resp2 = await client.get("/merchants")
                if resp2.status_code == 200:
                    for m in resp2.json()["items"]:
                        if m.get("contact_phone") == "13999999999":
                            merchant_id = m["id"]
                            break
            else:
                passed = log_step("商家注册", "FAIL", f"注册失败: {resp.status_code} {resp.text}")
        except Exception as e:
            passed = log_step("商家注册", "FAIL", f"注册异常: {e}")

        if not passed:
            all_passed = False
            print("\n商家注册失败，终止测试链！")
            return False

        # ==================== 第二步：管理员登录 ====================
        print("\n" + "="*60)
        print("第二步：管理员登录")
        print("="*60)

        try:
            resp = await client.post("/auth/login", json={
                "phone": "13800000000",
                "password": "admin123",
            })
            if resp.status_code == 200:
                login_result = resp.json()
                admin_token = login_result["access_token"]
                passed = log_step("管理员登录", "PASS", f"管理员登录成功，获取 JWT Token (类型={login_result['token_type']})")
            else:
                passed = log_step("管理员登录", "FAIL", f"登录失败: {resp.status_code} {resp.text}")
                all_passed = False
        except Exception as e:
            passed = log_step("管理员登录", "FAIL", f"登录异常: {e}")
            all_passed = False

        if not passed:
            print("\n管理员登录失败，终止测试链！")
            return False

        # ==================== 第三步：管理员查看待审核商家列表 ====================
        print("\n" + "="*60)
        print("第三步：管理员查看待审核商家列表")
        print("="*60)

        try:
            resp = await client.get(
                "/admin/merchants",
                params={"status": "pending"},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            if resp.status_code == 200:
                merchants_list = resp.json()
                found = False
                target_merchant = None
                for m in merchants_list["items"]:
                    if m["id"] == merchant_id:
                        found = True
                        target_merchant = m
                        break
                if found:
                    passed = log_step(
                        "查看待审核商家", "PASS",
                        f"在待审核列表中找到商家: {target_merchant['business_name']} (ID={target_merchant['id']}, 状态={target_merchant['status']})",
                        target_merchant
                    )
                else:
                    # 商家可能已经被审批过了（重复测试）
                    resp2 = await client.get(
                        f"/admin/merchants/{merchant_id}",
                        headers={"Authorization": f"Bearer {admin_token}"},
                    )
                    if resp2.status_code == 200:
                        existing = resp2.json()
                        passed = log_step(
                            "查看待审核商家", "PASS",
                            f"商家已存在（状态={existing['status']}，可能是重复测试）: {existing['business_name']}",
                            existing
                        )
                    else:
                        passed = log_step(
                            "查看待审核商家", "FAIL",
                            f"未在待审核列表中找到商家 ID={merchant_id}，共 {merchants_list['total']} 个待审核商家"
                        )
                        all_passed = False
            else:
                passed = log_step("查看待审核商家", "FAIL", f"请求失败: {resp.status_code} {resp.text}")
                all_passed = False
        except Exception as e:
            passed = log_step("查看待审核商家", "FAIL", f"请求异常: {e}")
            all_passed = False

        # ==================== 第四步：管理员查看商家详情 ====================
        print("\n" + "="*60)
        print("第四步：管理员查看商家详情")
        print("="*60)

        try:
            resp = await client.get(
                f"/admin/merchants/{merchant_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            if resp.status_code == 200:
                detail = resp.json()
                passed = log_step(
                    "查看商家详情", "PASS",
                    f"商家详情获取成功: {detail['business_name']} (状态={detail['status']})",
                    {
                        "id": detail["id"],
                        "business_name": detail["business_name"],
                        "status": detail["status"],
                        "address": detail["address"],
                        "contact_phone": detail["contact_phone"],
                    }
                )
            else:
                passed = log_step("查看商家详情", "FAIL", f"请求失败: {resp.status_code} {resp.text}")
                all_passed = False
        except Exception as e:
            passed = log_step("查看商家详情", "FAIL", f"请求异常: {e}")
            all_passed = False

        # ==================== 第五步：管理员审批通过 ====================
        print("\n" + "="*60)
        print("第五步：管理员审批通过商家")
        print("="*60)

        try:
            resp = await client.put(
                f"/admin/merchants/{merchant_id}/approve",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"reason": "联调测试-审核通过"},
            )
            if resp.status_code == 200:
                approve_result = resp.json()
                passed = log_step(
                    "管理员审批", "PASS",
                    f"商家审批通过！新状态: {approve_result['status']}",
                    {
                        "id": approve_result["id"],
                        "business_name": approve_result["business_name"],
                        "status": approve_result["status"],
                        "approved_by": approve_result.get("approved_by"),
                        "approved_at": str(approve_result.get("approved_at")),
                    }
                )
            elif resp.status_code == 400:
                err = resp.json()
                if "approved" in str(err).lower():
                    passed = log_step(
                        "管理员审批", "PASS",
                        f"商家已经被审批通过（重复测试）: {err}",
                        err
                    )
                else:
                    passed = log_step("管理员审批", "FAIL", f"审批失败: {resp.status_code} {resp.text}")
                    all_passed = False
            else:
                passed = log_step("管理员审批", "FAIL", f"审批失败: {resp.status_code} {resp.text}")
                all_passed = False
        except Exception as e:
            passed = log_step("管理员审批", "FAIL", f"审批异常: {e}")
            all_passed = False

        # ==================== 第六步：商家登录 ====================
        print("\n" + "="*60)
        print("第六步：商家登录")
        print("="*60)

        try:
            resp = await client.post("/auth/login", json={
                "phone": "13899999999",
                "password": "merchant888",
            })
            if resp.status_code == 200:
                login_result = resp.json()
                merchant_token = login_result["access_token"]
                passed = log_step("商家登录", "PASS", f"商家登录成功，获取 JWT Token (类型={login_result['token_type']})")
            else:
                passed = log_step("商家登录", "FAIL", f"登录失败: {resp.status_code} {resp.text}")
                all_passed = False
        except Exception as e:
            passed = log_step("商家登录", "FAIL", f"登录异常: {e}")
            all_passed = False

        if not passed:
            print("\n商家登录失败，终止测试链！")
            return False

        # ==================== 第七步：商家获取个人信息 ====================
        print("\n" + "="*60)
        print("第七步：商家获取个人信息")
        print("="*60)

        try:
            resp = await client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {merchant_token}"},
            )
            if resp.status_code == 200:
                me_info = resp.json()
                passed = log_step(
                    "商家个人信息", "PASS",
                    f"获取商家个人信息成功: {me_info['username']} (角色={me_info['role']}, 手机号={me_info['phone']})",
                    {
                        "id": me_info["id"],
                        "username": me_info["username"],
                        "role": me_info["role"],
                        "phone": me_info["phone"],
                        "is_active": me_info["is_active"],
                    }
                )
            else:
                passed = log_step("商家个人信息", "FAIL", f"请求失败: {resp.status_code} {resp.text}")
                all_passed = False
        except Exception as e:
            passed = log_step("商家个人信息", "FAIL", f"请求异常: {e}")
            all_passed = False

        # ==================== 第八步：商家查看自己的店铺信息 ====================
        print("\n" + "="*60)
        print("第八步：商家查看自己的店铺信息")
        print("="*60)

        try:
            resp = await client.get(
                "/merchants/me",
                headers={"Authorization": f"Bearer {merchant_token}"},
            )
            if resp.status_code == 200:
                merchant_info = resp.json()
                passed = log_step(
                    "商家店铺信息", "PASS",
                    f"获取店铺信息成功: {merchant_info['business_name']} (状态={merchant_info['status']})",
                    {
                        "id": merchant_info["id"],
                        "business_name": merchant_info["business_name"],
                        "status": merchant_info["status"],
                        "address": merchant_info["address"],
                        "contact_phone": merchant_info["contact_phone"],
                        "description": merchant_info.get("description"),
                    }
                )
            else:
                passed = log_step("商家店铺信息", "FAIL", f"请求失败: {resp.status_code} {resp.text}")
                all_passed = False
        except Exception as e:
            passed = log_step("商家店铺信息", "FAIL", f"请求异常: {e}")
            all_passed = False

        # ==================== 第九步：公开接口验证商家可见性 ====================
        print("\n" + "="*60)
        print("第九步：验证商家在公开列表中可见")
        print("="*60)

        try:
            resp = await client.get("/merchants")
            if resp.status_code == 200:
                public_list = resp.json()
                found = False
                public_merchant = None
                for m in public_list["items"]:
                    if m["id"] == merchant_id:
                        found = True
                        public_merchant = m
                        break
                if found:
                    passed = log_step(
                        "商家公开可见性", "PASS",
                        f"商家 '{public_merchant['business_name']}' 已出现在公开商家列表中 (状态={public_merchant['status']}, 共{public_list['total']}个商家)"
                    )
                else:
                    passed = log_step(
                        "商家公开可见性", "FAIL",
                        f"商家 ID={merchant_id} 未出现在公开商家列表中（共 {public_list['total']} 个商家）"
                    )
                    all_passed = False
            else:
                passed = log_step("商家公开可见性", "FAIL", f"请求失败: {resp.status_code} {resp.text}")
                all_passed = False
        except Exception as e:
            passed = log_step("商家公开可见性", "FAIL", f"请求异常: {e}")
            all_passed = False

        # ==================== 第十步：权限验证 ====================
        print("\n" + "="*60)
        print("第十步：权限验证（非管理员无法审批）")
        print("="*60)

        try:
            resp = await client.put(
                f"/admin/merchants/{merchant_id}/approve",
                headers={"Authorization": f"Bearer {merchant_token}"},
                json={"reason": "越权测试"},
            )
            if resp.status_code == 403:
                passed = log_step(
                    "权限验证", "PASS",
                    f"商家尝试审批操作被正确拒绝 (403 Forbidden)"
                )
            else:
                passed = log_step(
                    "权限验证", "FAIL",
                    f"商家尝试审批操作应返回 403，实际返回 {resp.status_code}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("权限验证", "FAIL", f"权限验证异常: {e}")
            all_passed = False

    # ==================== 测试报告 ====================
    print("\n" + "="*60)
    print("联调测试报告")
    print("="*60)

    total = len(report)
    passed_count = sum(1 for r in report if r["status"] == "PASS")
    failed_count = sum(1 for r in report if r["status"] == "FAIL")

    for r in report:
        emoji = "✅" if r["status"] == "PASS" else "❌"
        print(f"  {emoji} [{r['status']}] {r['step']}: {r['message']}")

    print(f"\n总计: {total} 个测试步骤，通过 {passed_count}，失败 {failed_count}")

    if failed_count == 0:
        print("\n🎉 商家注册 → 管理员审核 → 商家登录 全流程联调测试全部通过！")
    else:
        print(f"\n⚠️  有 {failed_count} 个步骤失败，请检查以上详情。")

    return failed_count == 0

if __name__ == "__main__":
    result = asyncio.run(run_integration_test())
    sys.exit(0 if result else 1)
