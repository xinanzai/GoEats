"""
用户注册 → 登录 → 浏览商家 → 查看商品 → 加入购物车 → 提交订单 → 支付 → 查看订单状态
全流程联调测试
测试目标：任务 5.1 用户流程联调
测试环境：真实后端服务 (http://localhost:8000)
测试流程：
1. 清理测试数据并设置测试商家和商品
2. 用户注册
3. 用户登录
4. 浏览商家列表
5. 查看商家详情
6. 查看商品列表
7. 查看商品详情
8. 查看分类列表
9. 添加收货地址
10. 提交订单
11. 查看订单列表
12. 查看订单详情
13. 支付订单
14. 查看订单状态变更
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
            test_usernames = ["user_flow_test", "user_flow_merchant"]
            for username in test_usernames:
                await session.execute(text("DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE user_id IN (SELECT id FROM users WHERE username=:username))"), {"username": username})
                await session.execute(text("DELETE FROM orders WHERE user_id IN (SELECT id FROM users WHERE username=:username)"), {"username": username})
                await session.execute(text("DELETE FROM addresses WHERE user_id IN (SELECT id FROM users WHERE username=:username)"), {"username": username})
            
            # 删除商家相关数据
            await session.execute(text("DELETE FROM products WHERE merchant_id IN (SELECT id FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='user_flow_merchant'))"))
            await session.execute(text("DELETE FROM categories WHERE merchant_id IN (SELECT id FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='user_flow_merchant'))"))
            await session.execute(text("DELETE FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='user_flow_merchant')"))
            
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
                username="user_flow_merchant",
                phone="13900000000",
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
                business_name="用户流程测试餐厅",
                contact_phone="13900000001",
                address="深圳市南山区测试路666号",
                description="这是一家用于用户流程测试的餐厅",
                status="approved",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(merchant)
            await session.flush()
            
            # 创建分类
            category1 = Category(
                merchant_id=merchant.id,
                name="招牌菜品",
                sort_order=1,
                created_at=datetime.now(timezone.utc),
            )
            session.add(category1)
            
            category2 = Category(
                merchant_id=merchant.id,
                name="特色饮品",
                sort_order=2,
                created_at=datetime.now(timezone.utc),
            )
            session.add(category2)
            await session.flush()
            
            # 创建商品
            product1 = Product(
                merchant_id=merchant.id,
                category_id=category1.id,
                name="测试红烧肉",
                description="精选五花肉，入口即化",
                price=D("58.00"),
                stock=100,
                is_available=True,
                sort_order=1,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(product1)
            
            product2 = Product(
                merchant_id=merchant.id,
                category_id=category1.id,
                name="测试清蒸鲈鱼",
                description="新鲜鲈鱼，清淡美味",
                price=D("68.00"),
                stock=50,
                is_available=True,
                sort_order=2,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(product2)
            
            product3 = Product(
                merchant_id=merchant.id,
                category_id=category2.id,
                name="测试酸梅汤",
                description="冰镇酸梅汤，解暑佳品",
                price=D("12.00"),
                stock=200,
                is_available=True,
                sort_order=1,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(product3)
            await session.flush()
            
            # 在 commit 前获取 ID
            merchant_id_value = merchant.id
            product1_id = product1.id
            product2_id = product2.id
            product3_id = product3.id
            
            await session.commit()
            
            print(f"✅ 商家和商品创建成功")
            print(f"   商家ID: {merchant_id_value}")
            print(f"   商品1 ID: {product1_id} (红烧肉)")
            print(f"   商品2 ID: {product2_id} (清蒸鲈鱼)")
            print(f"   商品3 ID: {product3_id} (酸梅汤)")
            return merchant_id_value, product1_id, product2_id, product3_id
    finally:
        await engine.dispose()

async def run_user_flow_test():
    all_passed = True
    user_token = None
    merchant_id = None
    product1_id = None
    product2_id = None
    product3_id = None
    address_id = None
    order_id = None

    # 清理测试数据
    print("\n" + "="*80)
    print("前置条件：清理之前的测试数据")
    print("="*80)
    await cleanup_test_data()

    # 设置商家和商品
    print("\n" + "="*80)
    print("前置条件：设置测试商家和商品")
    print("="*80)
    merchant_id, product1_id, product2_id, product3_id = await setup_merchant_and_products()

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:

        # ==================== 第一步：用户注册 ====================
        print("\n" + "="*80)
        print("第一步：用户注册")
        print("="*80)

        await rate_limit_delay()

        user_reg_data = {
            "username": "user_flow_test",
            "phone": "13700000000",
            "password": "user123456",
        }

        try:
            resp = await client.post("/auth/register", json=user_reg_data)
            if resp.status_code == 201:
                user_info = resp.json()
                passed = log_step(
                    "用户注册", "PASS",
                    f"用户注册成功: {user_info['username']}，手机号: {user_info['phone']}，角色: {user_info['role']}",
                    user_info
                )
            elif resp.status_code == 400:
                passed = log_step("用户注册", "PASS", f"用户已存在（重复测试），继续使用: {resp.json()}")
            else:
                passed = log_step("用户注册", "FAIL", f"注册失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("用户注册", "FAIL", f"注册异常: {e}")
            all_passed = False

        # ==================== 第二步：用户登录 ====================
        print("\n" + "="*80)
        print("第二步：用户登录")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.post("/auth/login", json={
                "phone": "13700000000",
                "password": "user123456"
            })
            if resp.status_code == 200:
                login_result = resp.json()
                user_token = login_result["access_token"]
                passed = log_step(
                    "用户登录", "PASS",
                    f"用户登录成功，获取 JWT Token",
                    {
                        "access_token": login_result["access_token"][:50] + "...",
                    }
                )
            else:
                passed = log_step("用户登录", "FAIL", f"登录失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("用户登录", "FAIL", f"登录异常: {e}")
            all_passed = False

        user_headers = {"Authorization": f"Bearer {user_token}"} if user_token else {}

        # ==================== 第三步：获取用户信息 ====================
        print("\n" + "="*80)
        print("第三步：获取用户信息")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get("/auth/me", headers=user_headers)
            if resp.status_code == 200:
                me_info = resp.json()
                passed = log_step(
                    "获取用户信息", "PASS",
                    f"当前用户: {me_info['username']}，角色: {me_info['role']}",
                    me_info
                )
            else:
                passed = log_step("获取用户信息", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("获取用户信息", "FAIL", f"获取异常: {e}")
            all_passed = False

        # ==================== 第四步：浏览商家列表 ====================
        print("\n" + "="*80)
        print("第四步：浏览商家列表")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get("/merchants", params={"page": 1, "page_size": 10})
            if resp.status_code == 200:
                merchants_list = resp.json()
                target_merchant = None
                for m in merchants_list["items"]:
                    if m["id"] == merchant_id:
                        target_merchant = m
                        break
                if target_merchant:
                    passed = log_step(
                        "浏览商家列表", "PASS",
                        f"共 {merchants_list['total']} 个商家，找到测试商家: {target_merchant['business_name']}",
                        {
                            "total": merchants_list["total"],
                            "target_merchant": {
                                "id": target_merchant["id"],
                                "business_name": target_merchant["business_name"],
                                "status": target_merchant["status"],
                            }
                        }
                    )
                else:
                    passed = log_step("浏览商家列表", "FAIL", f"未找到测试商家，列表: {merchants_list['items']}")
            else:
                passed = log_step("浏览商家列表", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("浏览商家列表", "FAIL", f"浏览异常: {e}")
            all_passed = False

        # ==================== 第五步：查看商家详情 ====================
        print("\n" + "="*80)
        print("第五步：查看商家详情")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get(f"/merchants/{merchant_id}")
            if resp.status_code == 200:
                merchant_detail = resp.json()
                passed = log_step(
                    "查看商家详情", "PASS",
                    f"商家: {merchant_detail['business_name']}，地址: {merchant_detail['address']}，状态: {merchant_detail['status']}",
                    merchant_detail
                )
            else:
                passed = log_step("查看商家详情", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("查看商家详情", "FAIL", f"查看异常: {e}")
            all_passed = False

        # ==================== 第六步：查看商家分类 ====================
        print("\n" + "="*80)
        print("第六步：查看商家分类列表")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get("/categories", params={"merchant_id": merchant_id})
            if resp.status_code == 200:
                categories = resp.json()
                passed = log_step(
                    "查看分类列表", "PASS",
                    f"共 {len(categories)} 个分类",
                    {"categories": [{"id": c["id"], "name": c["name"]} for c in categories]}
                )
            else:
                passed = log_step("查看分类列表", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("查看分类列表", "FAIL", f"查看异常: {e}")
            all_passed = False

        # ==================== 第七步：浏览商品列表 ====================
        print("\n" + "="*80)
        print("第七步：浏览商品列表")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get("/products", params={"merchant_id": merchant_id, "page": 1, "page_size": 10})
            if resp.status_code == 200:
                products_list = resp.json()
                passed = log_step(
                    "浏览商品列表", "PASS",
                    f"共 {products_list['total']} 个商品",
                    {
                        "total": products_list["total"],
                        "products": [
                            {
                                "id": p["id"],
                                "name": p["name"],
                                "price": str(p["price"]),
                                "stock": p["stock"],
                            }
                            for p in products_list["items"]
                        ]
                    }
                )
            else:
                passed = log_step("浏览商品列表", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("浏览商品列表", "FAIL", f"浏览异常: {e}")
            all_passed = False

        # ==================== 第八步：查看商品详情 ====================
        print("\n" + "="*80)
        print("第八步：查看商品详情")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get(f"/products/{product1_id}")
            if resp.status_code == 200:
                product_detail = resp.json()
                passed = log_step(
                    "查看商品详情", "PASS",
                    f"商品: {product_detail['name']}，价格: ¥{product_detail['price']}，库存: {product_detail['stock']}",
                    product_detail
                )
            else:
                passed = log_step("查看商品详情", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("查看商品详情", "FAIL", f"查看异常: {e}")
            all_passed = False

        # ==================== 第九步：添加收货地址 ====================
        print("\n" + "="*80)
        print("第九步：添加收货地址")
        print("="*80)

        await rate_limit_delay()

        address_data = {
            "receiver": "测试用户",
            "phone": "13700000000",
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区",
            "detail_address": "科技园路100号用户大厦A座",
            "is_default": True,
        }

        try:
            resp = await client.post("/users/addresses", json=address_data, headers=user_headers)
            if resp.status_code == 201:
                address_info = resp.json()
                address_id = address_info["id"]
                passed = log_step(
                    "添加收货地址", "PASS",
                    f"收货地址添加成功，ID={address_id}，默认地址: {address_info['is_default']}",
                    address_info
                )
            else:
                passed = log_step("添加收货地址", "FAIL", f"添加失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("添加收货地址", "FAIL", f"添加异常: {e}")
            all_passed = False

        # ==================== 第十步：查看地址列表 ====================
        print("\n" + "="*80)
        print("第十步：查看地址列表")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get("/users/addresses", headers=user_headers)
            if resp.status_code == 200:
                addresses_list = resp.json()
                passed = log_step(
                    "查看地址列表", "PASS",
                    f"共 {len(addresses_list)} 个地址",
                    addresses_list
                )
            else:
                passed = log_step("查看地址列表", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("查看地址列表", "FAIL", f"查看异常: {e}")
            all_passed = False

        # ==================== 第十一步：提交订单 ====================
        print("\n" + "="*80)
        print("第十一步：提交订单")
        print("="*80)

        await rate_limit_delay()

        if address_id and merchant_id:
            order_data = {
                "merchant_id": merchant_id,
                "address_id": address_id,
                "items": [
                    {
                        "product_id": product1_id,
                        "quantity": 2,
                    },
                    {
                        "product_id": product2_id,
                        "quantity": 1,
                    },
                    {
                        "product_id": product3_id,
                        "quantity": 3,
                    }
                ],
                "remark": "测试订单，请少辣",
            }

            try:
                resp = await client.post("/orders", json=order_data, headers=user_headers)
                if resp.status_code == 201:
                    order_info = resp.json()
                    order_id = order_info["id"]
                    passed = log_step(
                        "提交订单", "PASS",
                        f"订单创建成功，订单号: {order_info['order_no']}，状态: {order_info['status']}，应付金额: ¥{order_info['pay_amount']}",
                        {
                            "order_no": order_info["order_no"],
                            "status": order_info["status"],
                            "total_price": str(order_info["total_price"]),
                            "delivery_fee": str(order_info["delivery_fee"]),
                            "pay_amount": str(order_info["pay_amount"]),
                            "items_count": len(order_info["items"]),
                        }
                    )
                else:
                    passed = log_step("提交订单", "FAIL", f"下单失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("提交订单", "FAIL", f"下单异常: {e}")
                all_passed = False
        else:
            log_step("提交订单", "FAIL", "跳过：地址或商家ID未获取")
            all_passed = False

        # ==================== 第十二步：查看订单列表 ====================
        print("\n" + "="*80)
        print("第十二步：查看订单列表")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get("/orders/users/me", headers=user_headers)
            if resp.status_code == 200:
                orders_list = resp.json()
                passed = log_step(
                    "查看订单列表", "PASS",
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
                passed = log_step("查看订单列表", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("查看订单列表", "FAIL", f"获取异常: {e}")
            all_passed = False

        # ==================== 第十三步：查看订单详情 ====================
        print("\n" + "="*80)
        print("第十三步：查看订单详情")
        print("="*80)

        await rate_limit_delay()

        if order_id:
            try:
                resp = await client.get(f"/orders/users/me/{order_id}", headers=user_headers)
                if resp.status_code == 200:
                    order_detail = resp.json()
                    passed = log_step(
                        "查看订单详情", "PASS",
                        f"订单号: {order_detail['order_no']}，状态: {order_detail['status']}，商品数: {len(order_detail['items'])}",
                        {
                            "order_no": order_detail["order_no"],
                            "status": order_detail["status"],
                            "pay_amount": str(order_detail["pay_amount"]),
                            "items": [
                                {
                                    "product_name": item["product_name"],
                                    "quantity": item["quantity"],
                                    "price": str(item["price"]),
                                }
                                for item in order_detail["items"]
                            ]
                        }
                    )
                else:
                    passed = log_step("查看订单详情", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("查看订单详情", "FAIL", f"查看异常: {e}")
                all_passed = False
        else:
            log_step("查看订单详情", "FAIL", "跳过：订单未创建")
            all_passed = False

        # ==================== 第十四步：支付订单 ====================
        print("\n" + "="*80)
        print("第十四步：支付订单")
        print("="*80)

        await rate_limit_delay()

        if order_id:
            try:
                resp = await client.post(f"/orders/users/me/{order_id}/pay", headers=user_headers)
                if resp.status_code == 200:
                    order_info = resp.json()
                    passed = log_step(
                        "支付订单", "PASS",
                        f"订单支付成功，状态变更为: {order_info['status']}",
                        {
                            "order_no": order_info["order_no"],
                            "status": order_info["status"],
                            "pay_status": order_info.get("pay_status"),
                        }
                    )
                else:
                    passed = log_step("支付订单", "FAIL", f"支付失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("支付订单", "FAIL", f"支付异常: {e}")
                all_passed = False
        else:
            log_step("支付订单", "FAIL", "跳过：订单未创建")
            all_passed = False

        # ==================== 第十五步：再次查看订单状态 ====================
        print("\n" + "="*80)
        print("第十五步：再次查看订单状态（支付后）")
        print("="*80)

        await rate_limit_delay()

        if order_id:
            try:
                resp = await client.get(f"/orders/users/me/{order_id}", headers=user_headers)
                if resp.status_code == 200:
                    order_detail = resp.json()
                    passed = log_step(
                        "查看订单状态", "PASS",
                        f"订单号: {order_detail['order_no']}，当前状态: {order_detail['status']}，支付状态: {order_detail.get('pay_status')}",
                        {
                            "order_no": order_detail["order_no"],
                            "status": order_detail["status"],
                            "pay_status": order_detail.get("pay_status"),
                            "created_at": order_detail["created_at"],
                        }
                    )
                else:
                    passed = log_step("查看订单状态", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("查看订单状态", "FAIL", f"查看异常: {e}")
                all_passed = False
        else:
            log_step("查看订单状态", "FAIL", "跳过：订单未创建")
            all_passed = False

        # ==================== 第十六步：搜索商家 ====================
        print("\n" + "="*80)
        print("第十六步：搜索商家")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get("/merchants", params={"keyword": "用户流程测试"})
            if resp.status_code == 200:
                search_result = resp.json()
                passed = log_step(
                    "搜索商家", "PASS",
                    f"搜索到 {search_result['total']} 个商家",
                    {
                        "keyword": "用户流程测试",
                        "total": search_result["total"],
                    }
                )
            else:
                passed = log_step("搜索商家", "FAIL", f"搜索失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("搜索商家", "FAIL", f"搜索异常: {e}")
            all_passed = False

        # ==================== 第十七步：搜索商品 ====================
        print("\n" + "="*80)
        print("第十七步：搜索商品")
        print("="*80)

        await rate_limit_delay()

        try:
            resp = await client.get("/products", params={"merchant_id": merchant_id, "keyword": "测试"})
            if resp.status_code == 200:
                search_result = resp.json()
                passed = log_step(
                    "搜索商品", "PASS",
                    f"搜索到 {search_result['total']} 个商品",
                    {
                        "keyword": "测试",
                        "total": search_result["total"],
                        "products": [
                            {
                                "name": p["name"],
                                "price": str(p["price"]),
                            }
                            for p in search_result["items"]
                        ]
                    }
                )
            else:
                passed = log_step("搜索商品", "FAIL", f"搜索失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("搜索商品", "FAIL", f"搜索异常: {e}")
            all_passed = False

    # ==================== 测试报告 ====================
    print("\n" + "="*80)
    print("用户流程联调测试报告")
    print("="*80)
    
    passed_count = sum(1 for r in report if r["status"] == "PASS")
    failed_count = sum(1 for r in report if r["status"] == "FAIL")
    total_count = len(report)
    
    print(f"\n总计: {total_count} 个测试步骤")
    print(f"通过: {passed_count} 个")
    print(f"失败: {failed_count} 个")
    print(f"通过率: {passed_count/total_count*100:.1f}%" if total_count > 0 else "通过率: 0%")
    
    if failed_count > 0:
        print("\n失败的测试步骤:")
        for r in report:
            if r["status"] == "FAIL":
                print(f"  ❌ {r['step']}: {r['message']}")
    
    print("\n" + "="*80)
    
    return all_passed

if __name__ == "__main__":
    print("\n" + "🚀"*40)
    print("用户流程联调测试开始")
    print("🚀"*40)
    
    result = asyncio.run(run_user_flow_test())
    
    if result:
        print("\n✅ 用户流程联调测试全部通过！")
        sys.exit(0)
    else:
        print("\n❌ 用户流程联调测试存在失败项！")
        sys.exit(1)
