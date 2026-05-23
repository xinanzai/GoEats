"""
商家查看订单 → 处理订单 全流程联调测试
测试目标：任务 5.1 商家流程联调 - 第三部分
测试环境：真实后端服务 (http://localhost:8000)
测试流程：
1. 创建测试用户并注册
2. 用户登录并添加收货地址
3. 用户下单
4. 用户支付
5. 商家查看订单
6. 商家处理订单（接单 → 制作 → 配送 → 完成）
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

async def rate_limit_delay():
    """限流延迟 - 避免触发 429"""
    await asyncio.sleep(0.5)

async def cleanup_test_data():
    """清理之前的测试数据"""
    engine = create_async_engine(DATABASE_URL)
    try:
        async with AsyncSession(engine) as session:
            # 删除测试用户相关的所有数据
            test_usernames = ["integration_test_user", "integration_test_merchant"]
            for username in test_usernames:
                await session.execute(text("DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE user_id IN (SELECT id FROM users WHERE username=:username))"), {"username": username})
                await session.execute(text("DELETE FROM orders WHERE user_id IN (SELECT id FROM users WHERE username=:username)"), {"username": username})
                await session.execute(text("DELETE FROM orders WHERE merchant_id IN (SELECT id FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username=:username))"), {"username": username})
                await session.execute(text("DELETE FROM addresses WHERE user_id IN (SELECT id FROM users WHERE username=:username)"), {"username": username})
            
            # 删除商家相关数据
            await session.execute(text("DELETE FROM products WHERE merchant_id IN (SELECT id FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='integration_test_merchant'))"))
            await session.execute(text("DELETE FROM categories WHERE merchant_id IN (SELECT id FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='integration_test_merchant'))"))
            await session.execute(text("DELETE FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='integration_test_merchant')"))
            
            # 删除测试用户和商家
            for username in test_usernames:
                await session.execute(text("DELETE FROM users WHERE username=:username"), {"username": username})
            
            await session.commit()
            print("✅ 已清理之前的测试数据")
    finally:
        await engine.dispose()

async def setup_merchant_and_products():
    """设置已批准的商家和商品"""
    engine = create_async_engine(DATABASE_URL)
    try:
        async with AsyncSession(engine) as session:
            from app.models.user import User
            from app.models.merchant import Merchant
            from app.models.category import Category
            from app.models.product import Product
            from decimal import Decimal as D
            
            # 创建商家用户
            merchant_user = User(
                username="integration_test_merchant",
                phone="13899999999",
                password_hash=get_password_hash("merchant888"),
                role="merchant",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(merchant_user)
            await session.flush()
            
            # 创建商家信息
            merchant = Merchant(
                user_id=merchant_user.id,
                business_name="联调测试美食餐厅",
                contact_phone="13999999999",
                address="深圳市南山区联调路888号",
                description="这是一家用于联调测试的餐厅",
                status="approved",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(merchant)
            await session.flush()
            
            # 创建分类
            category = Category(
                merchant_id=merchant.id,
                name="热销菜品",
                sort_order=1,
                created_at=datetime.now(timezone.utc),
            )
            session.add(category)
            await session.flush()
            
            # 创建商品
            product = Product(
                merchant_id=merchant.id,
                category_id=category.id,
                name="测试宫保鸡丁",
                description="经典川菜",
                price=D("38.00"),
                stock=100,
                is_available=True,
                sort_order=1,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(product)
            await session.flush()
            
            # 在 commit 前获取 ID（commit 会使属性过期）
            merchant_id_value = merchant.id
            product_id_value = product.id
            
            await session.commit()
            
            print(f"✅ 商家和商品创建成功 (商家ID={merchant_id_value}, 商品ID={product_id_value})")
            return merchant_id_value, product_id_value
    finally:
        await engine.dispose()

async def run_integration_test():
    all_passed = True
    merchant_token = None
    user_token = None
    merchant_id = None
    product_id = None
    address_id = None
    order_id = None

    # 清理测试数据
    print("\n" + "="*60)
    print("前置条件：清理之前的测试数据")
    print("="*60)
    await cleanup_test_data()

    # 设置商家和商品
    print("\n" + "="*60)
    print("前置条件：设置测试商家和商品")
    print("="*60)
    merchant_id, product_id = await setup_merchant_and_products()

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:

        # ==================== 第一步：注册测试用户 ====================
        print("\n" + "="*60)
        print("第一步：注册测试用户")
        print("="*60)

        await rate_limit_delay()

        user_reg_data = {
            "username": "integration_test_user",
            "phone": "13888888888",
            "password": "user888",
        }

        try:
            resp = await client.post("/auth/register", json=user_reg_data)
            if resp.status_code == 201:
                user_info = resp.json()
                passed = log_step(
                    "用户注册", "PASS",
                    f"用户注册成功: {user_info['username']}",
                    user_info
                )
            else:
                passed = log_step("用户注册", "FAIL", f"注册失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("用户注册", "FAIL", f"注册异常: {e}")
            all_passed = False

        # ==================== 第二步：用户登录 ====================
        print("\n" + "="*60)
        print("第二步：用户登录")
        print("="*60)

        await rate_limit_delay()

        try:
            resp = await client.post("/auth/login", json={
                "phone": "13888888888",
                "password": "user888"
            })
            if resp.status_code == 200:
                login_result = resp.json()
                user_token = login_result["access_token"]
                passed = log_step(
                    "用户登录", "PASS",
                    f"用户登录成功，获取 Token"
                )
            else:
                passed = log_step("用户登录", "FAIL", f"登录失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("用户登录", "FAIL", f"登录异常: {e}")
            all_passed = False

        user_headers = {"Authorization": f"Bearer {user_token}"} if user_token else {}

        # ==================== 第三步：商家登录 ====================
        print("\n" + "="*60)
        print("第三步：商家登录")
        print("="*60)

        await rate_limit_delay()

        try:
            resp = await client.post("/auth/login", json={
                "phone": "13899999999",
                "password": "merchant888"
            })
            if resp.status_code == 200:
                login_result = resp.json()
                merchant_token = login_result["access_token"]
                passed = log_step(
                    "商家登录", "PASS",
                    f"商家登录成功，获取 Token"
                )
            else:
                passed = log_step("商家登录", "FAIL", f"登录失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("商家登录", "FAIL", f"登录异常: {e}")
            all_passed = False

        merchant_headers = {"Authorization": f"Bearer {merchant_token}"} if merchant_token else {}

        # ==================== 第四步：用户添加收货地址 ====================
        print("\n" + "="*60)
        print("第四步：用户添加收货地址")
        print("="*60)

        await rate_limit_delay()

        address_data = {
            "receiver": "测试用户",
            "phone": "13888888888",
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区",
            "detail_address": "科技园路88号",
            "is_default": True,
        }

        try:
            resp = await client.post("/users/addresses", json=address_data, headers=user_headers)
            if resp.status_code == 201:
                address_info = resp.json()
                address_id = address_info["id"]
                passed = log_step(
                    "添加收货地址", "PASS",
                    f"收货地址添加成功，ID={address_id}",
                    address_info
                )
            else:
                passed = log_step("添加收货地址", "FAIL", f"添加失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("添加收货地址", "FAIL", f"添加异常: {e}")
            all_passed = False

        # ==================== 第五步：用户下单 ====================
        print("\n" + "="*60)
        print("第五步：用户下单")
        print("="*60)

        await rate_limit_delay()

        if address_id and merchant_id:
            order_data = {
                "merchant_id": merchant_id,
                "address_id": address_id,
                "items": [
                    {
                        "product_id": product_id,
                        "quantity": 2,
                    }
                ],
                "remark": "测试订单",
            }

            try:
                resp = await client.post("/orders", json=order_data, headers=user_headers)
                if resp.status_code == 201:
                    order_info = resp.json()
                    order_id = order_info["id"]
                    passed = log_step(
                        "用户下单", "PASS",
                        f"订单创建成功，订单号: {order_info['order_no']}，状态: {order_info['status']}",
                        {
                            "order_no": order_info["order_no"],
                            "status": order_info["status"],
                            "total_price": str(order_info["total_price"]),
                            "pay_amount": str(order_info["pay_amount"]),
                        }
                    )
                else:
                    passed = log_step("用户下单", "FAIL", f"下单失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("用户下单", "FAIL", f"下单异常: {e}")
                all_passed = False
        else:
            log_step("用户下单", "FAIL", "跳过：地址或商家ID未获取")
            all_passed = False

        # ==================== 第六步：用户支付订单 ====================
        print("\n" + "="*60)
        print("第六步：用户支付订单")
        print("="*60)

        await rate_limit_delay()

        if order_id:
            try:
                resp = await client.post(f"/orders/users/me/{order_id}/pay", headers=user_headers)
                if resp.status_code == 200:
                    order_info = resp.json()
                    passed = log_step(
                        "用户支付", "PASS",
                        f"订单支付成功，状态变更为: {order_info['status']}",
                        {
                            "order_no": order_info["order_no"],
                            "status": order_info["status"],
                        }
                    )
                else:
                    passed = log_step("用户支付", "FAIL", f"支付失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("用户支付", "FAIL", f"支付异常: {e}")
                all_passed = False
        else:
            log_step("用户支付", "FAIL", "跳过：订单未创建")
            all_passed = False

        # ==================== 第七步：商家查看待处理订单 ====================
        print("\n" + "="*60)
        print("第七步：商家查看待处理订单")
        print("="*60)

        await rate_limit_delay()

        try:
            resp = await client.get("/orders/merchant/me", headers=merchant_headers)
            if resp.status_code == 200:
                orders_list = resp.json()
                passed = log_step(
                    "商家查看订单列表", "PASS",
                    f"共 {orders_list['total']} 个订单",
                    {
                        "total": orders_list["total"],
                        "orders": [
                            {
                                "order_no": o["order_no"],
                                "status": o["status"],
                                "pay_amount": str(o["pay_amount"]),
                            }
                            for o in orders_list["items"]
                        ]
                    }
                )
            else:
                passed = log_step("商家查看订单列表", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("商家查看订单列表", "FAIL", f"获取异常: {e}")
            all_passed = False

        # ==================== 第八步：商家开始制作 ====================
        print("\n" + "="*60)
        print("第八步：商家开始制作 (preparing)")
        print("="*60)

        await rate_limit_delay()

        if order_id:
            try:
                resp = await client.post(f"/orders/merchant/me/{order_id}/prepare", headers=merchant_headers)
                if resp.status_code == 200:
                    order_info = resp.json()
                    passed = log_step(
                        "商家开始制作", "PASS",
                        f"订单状态变更为: {order_info['status']}",
                        {
                            "order_no": order_info["order_no"],
                            "status": order_info["status"],
                        }
                    )
                else:
                    passed = log_step("商家开始制作", "FAIL", f"开始制作失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("商家开始制作", "FAIL", f"开始制作异常: {e}")
                all_passed = False
        else:
            log_step("商家开始制作", "FAIL", "跳过：订单未创建")
            all_passed = False

        # ==================== 第九步：商家开始配送 ====================
        print("\n" + "="*60)
        print("第九步：商家开始配送 (delivering)")
        print("="*60)

        await rate_limit_delay()

        if order_id:
            try:
                resp = await client.post(f"/orders/merchant/me/{order_id}/deliver", headers=merchant_headers)
                if resp.status_code == 200:
                    order_info = resp.json()
                    passed = log_step(
                        "商家开始配送", "PASS",
                        f"订单状态变更为: {order_info['status']}",
                        {
                            "order_no": order_info["order_no"],
                            "status": order_info["status"],
                        }
                    )
                else:
                    passed = log_step("商家开始配送", "FAIL", f"开始配送失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("商家开始配送", "FAIL", f"开始配送异常: {e}")
                all_passed = False
        else:
            log_step("商家开始配送", "FAIL", "跳过：订单未创建")
            all_passed = False

        # ==================== 第十步：商家完成订单 ====================
        print("\n" + "="*60)
        print("第十步：商家完成订单 (completed)")
        print("="*60)

        await rate_limit_delay()

        if order_id:
            try:
                resp = await client.post(f"/orders/merchant/me/{order_id}/complete", headers=merchant_headers)
                if resp.status_code == 200:
                    order_info = resp.json()
                    passed = log_step(
                        "商家完成订单", "PASS",
                        f"订单已完成，最终状态: {order_info['status']}",
                        {
                            "order_no": order_info["order_no"],
                            "status": order_info["status"],
                            "completed_at": order_info.get("completed_at"),
                        }
                    )
                else:
                    passed = log_step("商家完成订单", "FAIL", f"完成订单失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("商家完成订单", "FAIL", f"完成订单异常: {e}")
                all_passed = False
        else:
            log_step("商家完成订单", "FAIL", "跳过：订单未创建")
            all_passed = False

        # ==================== 第十一步：用户查看订单最终状态 ====================
        print("\n" + "="*60)
        print("第十一步：用户查看订单最终状态")
        print("="*60)

        await rate_limit_delay()

        if order_id:
            try:
                resp = await client.get(f"/orders/users/me/{order_id}", headers=user_headers)
                if resp.status_code == 200:
                    order_info = resp.json()
                    passed = log_step(
                        "用户查看订单状态", "PASS",
                        f"订单最终状态: {order_info['status']}",
                        {
                            "order_no": order_info["order_no"],
                            "status": order_info["status"],
                            "completed_at": order_info.get("completed_at"),
                        }
                    )
                else:
                    passed = log_step("用户查看订单状态", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("用户查看订单状态", "FAIL", f"获取异常: {e}")
                all_passed = False
        else:
            log_step("用户查看订单状态", "FAIL", "跳过：订单未创建")
            all_passed = False

    # ==================== 测试报告 ====================
    print("\n" + "="*60)
    print("联调测试报告")
    print("="*60)
    passed_count = sum(1 for r in report if r["status"] == "PASS")
    failed_count = sum(1 for r in report if r["status"] == "FAIL")

    for r in report:
        emoji = "✅" if r["status"] == "PASS" else "❌"
        print(f"  {emoji} [{r['status']}] {r['step']}: {r['message']}")

    print(f"\n总计: {len(report)} 个测试步骤，通过 {passed_count}，失败 {failed_count}")

    if all_passed:
        print("\n🎉 商家查看订单 → 处理订单 全流程联调测试全部通过！")
    else:
        print("\n⚠️  部分测试未通过，请检查上面的错误信息")

    return all_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(run_integration_test())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
