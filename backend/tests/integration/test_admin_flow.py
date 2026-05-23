"""
管理员流程联调测试
测试目标：任务 5.2 管理员流程联调
测试环境：真实后端服务 (http://localhost:8000)
测试流程：
1. 确保管理员用户存在
2. 管理员登录
3. 查看仪表盘统计数据
4. 查看用户列表
5. 查看用户详情
6. 管理用户状态（启用/禁用）
7. 查看商家列表
8. 查看待审核商家
9. 审核商家（通过）
10. 审核商家（拒绝）
11. 查看订单列表
12. 查看数据统计
"""
import asyncio
import httpx
import json
import sys
import os
from datetime import datetime, timezone

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


async def rate_limit_delay():
    """限流延迟 - 避免触发 429"""
    await asyncio.sleep(0.5)


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


async def setup_test_data():
    """设置测试数据 - 创建待审核商家和测试用户"""
    engine = create_async_engine(DATABASE_URL)
    try:
        async with AsyncSession(engine) as session:
            from app.models.user import User
            from app.models.merchant import Merchant
            
            # 创建两个待审核商家
            merchant_users = []
            for i, (username, phone) in enumerate([
                ("admin_test_merchant1", "13900000001"),
                ("admin_test_merchant2", "13900000002"),
            ], 1):
                # 检查是否已存在
                result = await session.execute(
                    text("SELECT id FROM users WHERE phone=:phone"),
                    {"phone": phone}
                )
                existing = result.scalar_one_or_none()
                if existing is None:
                    merchant_user = User(
                        username=username,
                        phone=phone,
                        password_hash=get_password_hash("merchant888"),
                        role="merchant",
                        is_active=True,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    session.add(merchant_user)
                    await session.flush()
                    merchant_users.append(merchant_user)
                    
                    merchant = Merchant(
                        user_id=merchant_user.id,
                        business_name=f"管理员测试餐厅{i}",
                        contact_phone=phone,
                        address=f"深圳市南山区测试路{i}号",
                        description=f"这是管理员流程联调测试餐厅{i}",
                        status="pending",
                    )
                    session.add(merchant)
                else:
                    result2 = await session.execute(
                        text("SELECT id FROM users WHERE phone=:phone"),
                        {"phone": phone}
                    )
                    merchant_users.append(result2.scalar_one())
            
            # 创建测试用户
            test_user_phone = "13700000001"
            result = await session.execute(
                text("SELECT id FROM users WHERE phone=:phone"),
                {"phone": test_user_phone}
            )
            existing_user = result.scalar_one_or_none()
            if existing_user is None:
                test_user = User(
                    username="admin_test_user",
                    phone=test_user_phone,
                    password_hash=get_password_hash("user123456"),
                    role="user",
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                session.add(test_user)
            
            await session.commit()
            print("✅ 测试数据设置完成")
    finally:
        await engine.dispose()


async def cleanup_test_data():
    """清理测试数据"""
    engine = create_async_engine(DATABASE_URL)
    try:
        async with AsyncSession(engine) as session:
            test_phones = ["13900000001", "13900000002", "13700000001"]
            for phone in test_phones:
                await session.execute(
                    text("DELETE FROM merchants WHERE user_id IN (SELECT id FROM users WHERE phone=:phone)"),
                    {"phone": phone}
                )
                await session.execute(
                    text("DELETE FROM users WHERE phone=:phone"),
                    {"phone": phone}
                )
            await session.commit()
            print("✅ 已清理测试数据")
    finally:
        await engine.dispose()


async def run_admin_flow_test():
    """运行管理员流程联调测试"""
    all_passed = True
    admin_token = None
    
    print("\n" + "=" * 60)
    print("管理员流程联调测试")
    print("=" * 60)
    
    # 前置条件：清理测试数据
    print("\n" + "=" * 60)
    print("前置条件：清理测试数据")
    print("=" * 60)
    await cleanup_test_data()
    
    # 前置条件：确保管理员存在
    print("\n" + "=" * 60)
    print("前置条件：确保管理员用户存在")
    print("=" * 60)
    await ensure_admin_exists()
    
    # 前置条件：设置测试数据
    print("\n" + "=" * 60)
    print("前置条件：设置测试数据")
    print("=" * 60)
    await setup_test_data()
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        
        # ==================== 第一步：管理员登录 ====================
        print("\n" + "=" * 60)
        print("第一步：管理员登录")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.post("/auth/login", json={
                "phone": "13800000000",
                "password": "admin123",
            })
            if resp.status_code == 200:
                login_result = resp.json()
                admin_token = login_result["access_token"]
                passed = log_step(
                    "管理员登录", "PASS",
                    f"管理员登录成功，获取 JWT Token",
                    {"access_token": admin_token[:50] + "..."}
                )
            else:
                passed = log_step(
                    "管理员登录", "FAIL",
                    f"登录失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("管理员登录", "FAIL", f"登录异常: {e}")
            all_passed = False
        
        if not passed:
            print("\n管理员登录失败，终止测试链！")
            return False
        
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # ==================== 第二步：查看仪表盘统计数据 ====================
        print("\n" + "=" * 60)
        print("第二步：查看仪表盘统计数据")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/dashboard", headers=admin_headers)
            if resp.status_code == 200:
                stats = resp.json()
                passed = log_step(
                    "查看仪表盘", "PASS",
                    f"仪表盘数据获取成功",
                    {
                        "用户总数": stats.get("user_count"),
                        "商家总数": stats.get("merchant_count"),
                        "待审核商家数": stats.get("pending_merchant_count"),
                        "订单总数": stats.get("order_count"),
                        "今日订单数": stats.get("today_order_count"),
                        "本月订单数": stats.get("month_order_count"),
                        "今日收入": str(stats.get("today_revenue")),
                        "本月收入": str(stats.get("month_revenue")),
                    }
                )
            else:
                passed = log_step(
                    "查看仪表盘", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("查看仪表盘", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第三步：查看用户列表 ====================
        print("\n" + "=" * 60)
        print("第三步：查看用户列表")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/users", params={"page": 1, "page_size": 10}, headers=admin_headers)
            if resp.status_code == 200:
                users_data = resp.json()
                passed = log_step(
                    "查看用户列表", "PASS",
                    f"用户列表获取成功，共 {users_data.get('total')} 个用户，当前页 {users_data.get('page')}/{users_data.get('total_pages')}",
                    {
                        "total": users_data.get("total"),
                        "page": users_data.get("page"),
                        "page_size": users_data.get("page_size"),
                        "total_pages": users_data.get("total_pages"),
                        "用户数": len(users_data.get("items", [])),
                    }
                )
                if users_data.get("items"):
                    first_user = users_data["items"][0]
                    print(f"  第一个用户: {first_user.get('username')} ({first_user.get('role')})")
            else:
                passed = log_step(
                    "查看用户列表", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("查看用户列表", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第四步：按角色筛选用户 ====================
        print("\n" + "=" * 60)
        print("第四步：按角色筛选用户")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/users", params={"role": "user"}, headers=admin_headers)
            if resp.status_code == 200:
                users_data = resp.json()
                passed = log_step(
                    "按角色筛选用户", "PASS",
                    f"普通用户筛选成功，共 {users_data.get('total')} 个普通用户",
                    {"role": "user", "total": users_data.get("total")}
                )
            else:
                passed = log_step(
                    "按角色筛选用户", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("按角色筛选用户", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第五步：查看用户详情 ====================
        print("\n" + "=" * 60)
        print("第五步：查看用户详情")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/users", params={"phone": "13700000001"}, headers=admin_headers)
            if resp.status_code == 200:
                users_list = resp.json()
                if users_list.get("items"):
                    test_user = users_list["items"][0]
                    test_user_id = test_user["id"]
                    
                    resp2 = await client.get(f"/admin/users/{test_user_id}", headers=admin_headers)
                    if resp2.status_code == 200:
                        user_detail = resp2.json()
                        passed = log_step(
                            "查看用户详情", "PASS",
                            f"用户详情获取成功: {user_detail.get('username')}",
                            {
                                "id": user_detail.get("id"),
                                "username": user_detail.get("username"),
                                "phone": user_detail.get("phone"),
                                "role": user_detail.get("role"),
                                "is_active": user_detail.get("is_active"),
                            }
                        )
                    else:
                        passed = log_step(
                            "查看用户详情", "FAIL",
                            f"请求失败: {resp2.status_code} {resp2.text}"
                        )
                        all_passed = False
                else:
                    passed = log_step(
                        "查看用户详情", "FAIL",
                        f"未找到测试用户"
                    )
                    all_passed = False
            else:
                passed = log_step(
                    "查看用户详情", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("查看用户详情", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第六步：管理用户状态 ====================
        print("\n" + "=" * 60)
        print("第六步：管理用户状态（禁用/启用）")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/users", params={"phone": "13700000001"}, headers=admin_headers)
            if resp.status_code == 200:
                users_list = resp.json()
                if users_list.get("items"):
                    test_user = users_list["items"][0]
                    test_user_id = test_user["id"]
                    
                    # 禁用用户
                    resp2 = await client.put(
                        f"/admin/users/{test_user_id}/status",
                        headers=admin_headers,
                        json={"is_active": False}
                    )
                    if resp2.status_code == 200:
                        updated_user = resp2.json()
                        log_step(
                            "禁用用户", "PASS",
                            f"用户已禁用: {updated_user.get('username')} (is_active={updated_user.get('is_active')})"
                        )
                        
                        # 重新启用用户
                        await rate_limit_delay()
                        resp3 = await client.put(
                            f"/admin/users/{test_user_id}/status",
                            headers=admin_headers,
                            json={"is_active": True}
                        )
                        if resp3.status_code == 200:
                            reactivated_user = resp3.json()
                            passed = log_step(
                                "启用用户", "PASS",
                                f"用户已重新启用: {reactivated_user.get('username')} (is_active={reactivated_user.get('is_active')})"
                            )
                        else:
                            passed = log_step(
                                "启用用户", "FAIL",
                                f"请求失败: {resp3.status_code} {resp3.text}"
                            )
                            all_passed = False
                    else:
                        passed = log_step(
                            "禁用用户", "FAIL",
                            f"请求失败: {resp2.status_code} {resp2.text}"
                        )
                        all_passed = False
                else:
                    passed = log_step(
                        "管理用户状态", "FAIL",
                        f"未找到测试用户"
                    )
                    all_passed = False
            else:
                passed = log_step(
                    "管理用户状态", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("管理用户状态", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第七步：查看商家列表 ====================
        print("\n" + "=" * 60)
        print("第七步：查看商家列表")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/merchants", params={"page": 1, "page_size": 10}, headers=admin_headers)
            if resp.status_code == 200:
                merchants_data = resp.json()
                passed = log_step(
                    "查看商家列表", "PASS",
                    f"商家列表获取成功，共 {merchants_data.get('total')} 个商家",
                    {
                        "total": merchants_data.get("total"),
                        "page": merchants_data.get("page"),
                        "商家数": len(merchants_data.get("items", [])),
                    }
                )
            else:
                passed = log_step(
                    "查看商家列表", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("查看商家列表", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第八步：查看待审核商家 ====================
        print("\n" + "=" * 60)
        print("第八步：查看待审核商家")
        print("=" * 60)
        
        pending_merchant_ids = []
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/merchants", params={"status": "pending"}, headers=admin_headers)
            if resp.status_code == 200:
                merchants_data = resp.json()
                pending_merchant_ids = [m["id"] for m in merchants_data.get("items", [])]
                passed = log_step(
                    "查看待审核商家", "PASS",
                    f"待审核商家列表获取成功，共 {merchants_data.get('total')} 个待审核商家",
                    {
                        "total": merchants_data.get("total"),
                        "商家ID列表": pending_merchant_ids,
                    }
                )
                if merchants_data.get("items"):
                    for m in merchants_data["items"][:2]:
                        print(f"  待审核商家: {m.get('business_name')} (ID={m.get('id')}, 状态={m.get('status')})")
            else:
                passed = log_step(
                    "查看待审核商家", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("查看待审核商家", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第九步：审核商家（通过） ====================
        print("\n" + "=" * 60)
        print("第九步：审核商家（通过）")
        print("=" * 60)
        
        if pending_merchant_ids:
            approve_merchant_id = pending_merchant_ids[0]
            try:
                await rate_limit_delay()
                resp = await client.put(
                    f"/admin/merchants/{approve_merchant_id}/approve",
                    headers=admin_headers,
                )
                if resp.status_code == 200:
                    approved_merchant = resp.json()
                    passed = log_step(
                        "审核商家通过", "PASS",
                        f"商家审核通过！{approved_merchant.get('business_name')} (状态: {approved_merchant.get('status')})",
                        {
                            "id": approved_merchant.get("id"),
                            "business_name": approved_merchant.get("business_name"),
                            "status": approved_merchant.get("status"),
                            "approved_by": approved_merchant.get("approved_by"),
                            "approved_at": str(approved_merchant.get("approved_at")),
                        }
                    )
                else:
                    passed = log_step(
                        "审核商家通过", "FAIL",
                        f"请求失败: {resp.status_code} {resp.text}"
                    )
                    all_passed = False
            except Exception as e:
                passed = log_step("审核商家通过", "FAIL", f"请求异常: {e}")
                all_passed = False
        else:
            passed = log_step(
                "审核商家通过", "FAIL",
                f"没有待审核的商家"
            )
            all_passed = False
        
        # ==================== 第十步：审核商家（拒绝） ====================
        print("\n" + "=" * 60)
        print("第十步：审核商家（拒绝）")
        print("=" * 60)
        
        if len(pending_merchant_ids) > 1:
            reject_merchant_id = pending_merchant_ids[1]
            try:
                await rate_limit_delay()
                resp = await client.put(
                    f"/admin/merchants/{reject_merchant_id}/reject",
                    headers=admin_headers,
                    json={"reason": "测试拒绝原因：资料不完整"}
                )
                if resp.status_code == 200:
                    rejected_merchant = resp.json()
                    passed = log_step(
                        "审核商家拒绝", "PASS",
                        f"商家审核拒绝！{rejected_merchant.get('business_name')} (状态: {rejected_merchant.get('status')})",
                        {
                            "id": rejected_merchant.get("id"),
                            "business_name": rejected_merchant.get("business_name"),
                            "status": rejected_merchant.get("status"),
                            "rejection_reason": rejected_merchant.get("rejection_reason"),
                        }
                    )
                else:
                    passed = log_step(
                        "审核商家拒绝", "FAIL",
                        f"请求失败: {resp.status_code} {resp.text}"
                    )
                    all_passed = False
            except Exception as e:
                passed = log_step("审核商家拒绝", "FAIL", f"请求异常: {e}")
                all_passed = False
        else:
            passed = log_step(
                "审核商家拒绝", "FAIL",
                f"没有足够待审核的商家用于拒绝测试"
            )
            all_passed = False
        
        # ==================== 第十一步：查看商家详情 ====================
        print("\n" + "=" * 60)
        print("第十一步：查看商家详情（管理端）")
        print("=" * 60)
        
        if pending_merchant_ids:
            view_merchant_id = pending_merchant_ids[0]
            try:
                await rate_limit_delay()
                resp = await client.get(f"/admin/merchants/{view_merchant_id}", headers=admin_headers)
                if resp.status_code == 200:
                    merchant_detail = resp.json()
                    passed = log_step(
                        "查看商家详情", "PASS",
                        f"商家详情获取成功: {merchant_detail.get('business_name')}",
                        {
                            "id": merchant_detail.get("id"),
                            "business_name": merchant_detail.get("business_name"),
                            "status": merchant_detail.get("status"),
                            "address": merchant_detail.get("address"),
                            "contact_phone": merchant_detail.get("contact_phone"),
                        }
                    )
                else:
                    passed = log_step(
                        "查看商家详情", "FAIL",
                        f"请求失败: {resp.status_code} {resp.text}"
                    )
                    all_passed = False
            except Exception as e:
                passed = log_step("查看商家详情", "FAIL", f"请求异常: {e}")
                all_passed = False
        else:
            passed = log_step(
                "查看商家详情", "FAIL",
                f"没有商家可查看详情"
            )
            all_passed = False
        
        # ==================== 第十二步：按状态筛选商家 ====================
        print("\n" + "=" * 60)
        print("第十二步：按状态筛选商家")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/merchants", params={"status": "approved"}, headers=admin_headers)
            if resp.status_code == 200:
                approved_merchants = resp.json()
                passed = log_step(
                    "按状态筛选商家", "PASS",
                    f"已审核商家筛选成功，共 {approved_merchants.get('total')} 个已审核商家",
                    {"status": "approved", "total": approved_merchants.get("total")}
                )
            else:
                passed = log_step(
                    "按状态筛选商家", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("按状态筛选商家", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第十三步：查看订单列表 ====================
        print("\n" + "=" * 60)
        print("第十三步：查看订单列表（管理端）")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/orders", params={"page": 1, "page_size": 5}, headers=admin_headers)
            if resp.status_code == 200:
                orders_data = resp.json()
                passed = log_step(
                    "查看订单列表", "PASS",
                    f"订单列表获取成功，共 {orders_data.get('total')} 个订单",
                    {
                        "total": orders_data.get("total"),
                        "page": orders_data.get("page"),
                        "订单数": len(orders_data.get("items", [])),
                    }
                )
                if orders_data.get("items"):
                    first_order = orders_data["items"][0]
                    print(f"  第一个订单: {first_order.get('order_no')} (状态={first_order.get('status')}, 金额=¥{first_order.get('pay_amount')})")
            else:
                passed = log_step(
                    "查看订单列表", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("查看订单列表", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第十四步：按状态筛选订单 ====================
        print("\n" + "=" * 60)
        print("第十四步：按状态筛选订单")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/orders", params={"status": "paid"}, headers=admin_headers)
            if resp.status_code == 200:
                paid_orders = resp.json()
                passed = log_step(
                    "按状态筛选订单", "PASS",
                    f"已支付订单筛选成功，共 {paid_orders.get('total')} 个已支付订单",
                    {"status": "paid", "total": paid_orders.get("total")}
                )
            else:
                passed = log_step(
                    "按状态筛选订单", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("按状态筛选订单", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第十五步：查看数据统计 ====================
        print("\n" + "=" * 60)
        print("第十五步：查看数据统计")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/statistics", params={"days": 7}, headers=admin_headers)
            if resp.status_code == 200:
                stats_data = resp.json()
                order_stats = stats_data.get("order_statistics", {})
                popular_products = stats_data.get("popular_products", [])
                passed = log_step(
                    "查看数据统计", "PASS",
                    f"数据统计获取成功，近7天数据，{len(popular_products)} 个热销商品",
                    {
                        "统计天数": order_stats.get("days"),
                        "订单数据条数": len(order_stats.get("data", [])),
                        "热销商品数": len(popular_products),
                    }
                )
                if popular_products:
                    print(f"  最热销商品: {popular_products[0].get('name')} (销量={popular_products[0].get('total_sold')})")
            else:
                passed = log_step(
                    "查看数据统计", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("查看数据统计", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第十六步：搜索用户 ====================
        print("\n" + "=" * 60)
        print("第十六步：搜索用户")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/users", params={"search": "admin_test"}, headers=admin_headers)
            if resp.status_code == 200:
                search_result = resp.json()
                passed = log_step(
                    "搜索用户", "PASS",
                    f"用户搜索成功，关键词 'admin_test'，找到 {search_result.get('total')} 个用户",
                    {"search": "admin_test", "total": search_result.get("total")}
                )
            else:
                passed = log_step(
                    "搜索用户", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("搜索用户", "FAIL", f"请求异常: {e}")
            all_passed = False
        
        # ==================== 第十七步：搜索商家 ====================
        print("\n" + "=" * 60)
        print("第十七步：搜索商家")
        print("=" * 60)
        
        try:
            await rate_limit_delay()
            resp = await client.get("/admin/merchants", params={"search": "管理员测试"}, headers=admin_headers)
            if resp.status_code == 200:
                search_result = resp.json()
                passed = log_step(
                    "搜索商家", "PASS",
                    f"商家搜索成功，关键词 '管理员测试'，找到 {search_result.get('total')} 个商家",
                    {"search": "管理员测试", "total": search_result.get("total")}
                )
            else:
                passed = log_step(
                    "搜索商家", "FAIL",
                    f"请求失败: {resp.status_code} {resp.text}"
                )
                all_passed = False
        except Exception as e:
            passed = log_step("搜索商家", "FAIL", f"请求异常: {e}")
            all_passed = False
    
    # 打印测试报告
    print("\n" + "=" * 60)
    print("测试报告")
    print("=" * 60)
    
    passed_count = sum(1 for r in report if r["status"] == "PASS")
    failed_count = sum(1 for r in report if r["status"] == "FAIL")
    total_count = len(report)
    
    print(f"\n总计: {total_count} 个测试步骤")
    print(f"通过: {passed_count}")
    print(f"失败: {failed_count}")
    
    if failed_count > 0:
        print("\n失败的测试步骤:")
        for r in report:
            if r["status"] == "FAIL":
                print(f"  ❌ {r['step']}: {r['message']}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 管理员流程联调测试全部通过！")
    else:
        print("❌ 管理员流程联调测试存在失败项")
    print("=" * 60)
    
    return all_passed


async def main():
    """主函数"""
    try:
        success = await run_admin_flow_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试执行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
