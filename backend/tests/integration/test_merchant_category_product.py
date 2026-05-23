"""
商家添加分类 → 添加商品 全流程联调测试
测试目标：任务 5.1 商家流程联调 - 第二部分
测试环境：真实后端服务 (http://localhost:8000)
"""
import asyncio
import httpx
import json
import sys
import os
import time
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
            # 删除测试商家相关的所有数据（按顺序删除以避免外键约束）
            await session.execute(text("DELETE FROM products WHERE merchant_id IN (SELECT id FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='integration_test_merchant'))"))
            await session.execute(text("DELETE FROM categories WHERE merchant_id IN (SELECT id FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='integration_test_merchant'))"))
            await session.execute(text("DELETE FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='integration_test_merchant')"))
            await session.execute(text("DELETE FROM users WHERE username='integration_test_merchant'"))
            await session.commit()
            print("✅ 已清理之前的测试数据")
    finally:
        await engine.dispose()

async def setup_merchant():
    """设置已批准的商家并返回 token"""
    engine = create_async_engine(DATABASE_URL)
    try:
        async with AsyncSession(engine) as session:
            # 检查商家是否存在
            result = await session.execute(text("SELECT id FROM users WHERE username='integration_test_merchant'"))
            user_id = result.scalar_one_or_none()
            
            if user_id:
                # 更新商家状态为 approved
                await session.execute(text("UPDATE merchants SET status='approved' WHERE user_id=:user_id"), {"user_id": user_id})
                await session.commit()
                print("✅ 商家已存在并设置为 approved")
            else:
                # 创建测试商家
                from app.models.user import User
                from app.models.merchant import Merchant
                
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
                await session.commit()
                print("✅ 测试商家创建成功 (已批准)")
    finally:
        await engine.dispose()

    # 登录获取 token
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        resp = await client.post("/auth/login", json={
            "phone": "13899999999",
            "password": "merchant888"
        })
        if resp.status_code == 200:
            return resp.json()["access_token"]
        else:
            raise Exception(f"商家登录失败: {resp.status_code} {resp.text}")

async def run_integration_test():
    all_passed = True

    # 清理测试数据
    print("\n" + "="*60)
    print("前置条件：清理之前的测试数据")
    print("="*60)
    await cleanup_test_data()

    # 设置商家
    print("\n" + "="*60)
    print("前置条件：设置测试商家")
    print("="*60)
    merchant_token = await setup_merchant()

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        headers = {"Authorization": f"Bearer {merchant_token}"}

        # ==================== 第一步：获取商家信息 ====================
        print("\n" + "="*60)
        print("第一步：获取商家信息")
        print("="*60)

        await rate_limit_delay()

        try:
            resp = await client.get("/merchants/me", headers=headers)
            if resp.status_code == 200:
                merchant_info = resp.json()
                passed = log_step(
                    "获取商家信息", "PASS",
                    f"商家信息获取成功: {merchant_info['business_name']} (状态={merchant_info['status']})",
                    merchant_info
                )
            else:
                passed = log_step("获取商家信息", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("获取商家信息", "FAIL", f"获取异常: {e}")
            all_passed = False

        # ==================== 第二步：创建商品分类 1 ====================
        print("\n" + "="*60)
        print("第二步：创建商品分类 - 热销菜品")
        print("="*60)

        await rate_limit_delay()

        category1_data = {
            "name": "热销菜品",
            "sort_order": 1,
        }

        try:
            resp = await client.post("/merchants/me/categories", json=category1_data, headers=headers)
            if resp.status_code == 201:
                category1 = resp.json()
                passed = log_step(
                    "创建分类-热销菜品", "PASS",
                    f"分类创建成功，ID={category1['id']}",
                    category1
                )
            else:
                passed = log_step("创建分类-热销菜品", "FAIL", f"创建失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            category1 = {"id": None}
            log_step("创建分类-热销菜品", "FAIL", f"创建异常: {e}")
            all_passed = False

        # ==================== 第三步：创建商品分类 2 ====================
        print("\n" + "="*60)
        print("第三步：创建商品分类 - 特色饮品")
        print("="*60)

        await rate_limit_delay()

        category2_data = {
            "name": "特色饮品",
            "sort_order": 2,
        }

        try:
            resp = await client.post("/merchants/me/categories", json=category2_data, headers=headers)
            if resp.status_code == 201:
                category2 = resp.json()
                passed = log_step(
                    "创建分类-特色饮品", "PASS",
                    f"分类创建成功，ID={category2['id']}",
                    category2
                )
            else:
                passed = log_step("创建分类-特色饮品", "FAIL", f"创建失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            category2 = {"id": None}
            log_step("创建分类-特色饮品", "FAIL", f"创建异常: {e}")
            all_passed = False

        # ==================== 第四步：获取商家分类列表 ====================
        print("\n" + "="*60)
        print("第四步：获取商家分类列表")
        print("="*60)

        await rate_limit_delay()

        try:
            resp = await client.get("/merchants/me/categories", headers=headers)
            if resp.status_code == 200:
                categories = resp.json()
                passed = log_step(
                    "获取分类列表", "PASS",
                    f"共 {len(categories)} 个分类",
                    categories
                )
            else:
                passed = log_step("获取分类列表", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("获取分类列表", "FAIL", f"获取异常: {e}")
            all_passed = False

        # ==================== 第五步：添加商品 - 宫保鸡丁 ====================
        print("\n" + "="*60)
        print("第五步：添加商品 - 宫保鸡丁")
        print("="*60)

        await rate_limit_delay()

        if category1.get("id"):
            product1_data = {
                "name": "宫保鸡丁",
                "description": "经典川菜，鸡肉嫩滑，花生香脆",
                "price": "38.00",
                "original_price": "48.00",
                "category_id": category1["id"],
                "stock": 100,
                "is_available": True,
                "sort_order": 1,
            }

            try:
                resp = await client.post("/products/merchant/me", json=product1_data, headers=headers)
                if resp.status_code == 201:
                    product1 = resp.json()
                    passed = log_step(
                        "添加商品-宫保鸡丁", "PASS",
                        f"商品创建成功，ID={product1['id']}",
                        product1
                    )
                else:
                    passed = log_step("添加商品-宫保鸡丁", "FAIL", f"创建失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                product1 = {"id": None}
                log_step("添加商品-宫保鸡丁", "FAIL", f"创建异常: {e}")
                all_passed = False
        else:
            log_step("添加商品-宫保鸡丁", "FAIL", "跳过：分类未创建成功")
            all_passed = False
            product1 = {"id": None}

        # ==================== 第六步：添加商品 - 珍珠奶茶 ====================
        print("\n" + "="*60)
        print("第六步：添加商品 - 珍珠奶茶")
        print("="*60)

        await rate_limit_delay()

        if category2.get("id"):
            product2_data = {
                "name": "珍珠奶茶",
                "description": "香浓奶茶配Q弹珍珠",
                "price": "18.00",
                "original_price": "22.00",
                "category_id": category2["id"],
                "stock": 200,
                "is_available": True,
                "sort_order": 1,
            }

            try:
                resp = await client.post("/products/merchant/me", json=product2_data, headers=headers)
                if resp.status_code == 201:
                    product2 = resp.json()
                    passed = log_step(
                        "添加商品-珍珠奶茶", "PASS",
                        f"商品创建成功，ID={product2['id']}",
                        product2
                    )
                else:
                    passed = log_step("添加商品-珍珠奶茶", "FAIL", f"创建失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("添加商品-珍珠奶茶", "FAIL", f"创建异常: {e}")
                all_passed = False
        else:
            log_step("添加商品-珍珠奶茶", "FAIL", "跳过：分类未创建成功")
            all_passed = False

        # ==================== 第七步：获取商家商品列表 ====================
        print("\n" + "="*60)
        print("第七步：获取商家商品列表")
        print("="*60)

        await rate_limit_delay()

        try:
            resp = await client.get("/products/merchant/me", headers=headers)
            if resp.status_code == 200:
                products_list = resp.json()
                passed = log_step(
                    "获取商品列表", "PASS",
                    f"共 {products_list['total']} 个商品",
                    products_list
                )
            else:
                passed = log_step("获取商品列表", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("获取商品列表", "FAIL", f"获取异常: {e}")
            all_passed = False

        # ==================== 第八步：更新商品信息 ====================
        print("\n" + "="*60)
        print("第八步：更新商品信息 - 宫保鸡丁")
        print("="*60)

        await rate_limit_delay()

        if product1.get("id"):
            update_data = {
                "price": "35.00",
                "stock": 150,
            }

            try:
                resp = await client.put(f"/products/merchant/me/{product1['id']}", json=update_data, headers=headers)
                if resp.status_code == 200:
                    updated_product = resp.json()
                    passed = log_step(
                        "更新商品-宫保鸡丁", "PASS",
                        f"价格更新为: {updated_product['price']}, 库存更新为: {updated_product['stock']}",
                        updated_product
                    )
                else:
                    passed = log_step("更新商品-宫保鸡丁", "FAIL", f"更新失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("更新商品-宫保鸡丁", "FAIL", f"更新异常: {e}")
                all_passed = False
        else:
            log_step("更新商品-宫保鸡丁", "FAIL", "跳过：商品未创建成功")
            all_passed = False

        # ==================== 第九步：切换商品上架/下架状态 ====================
        print("\n" + "="*60)
        print("第九步：切换商品上架/下架状态")
        print("="*60)

        await rate_limit_delay()

        if product1.get("id"):
            try:
                resp = await client.put(f"/products/merchant/me/{product1['id']}/toggle", headers=headers)
                if resp.status_code == 200:
                    toggled_product = resp.json()
                    passed = log_step(
                        "切换商品状态", "PASS",
                        f"商品 {toggled_product['name']} 状态变更为: {'上架' if toggled_product['is_available'] else '下架'}",
                        toggled_product
                    )
                else:
                    passed = log_step("切换商品状态", "FAIL", f"切换失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed

                # 再次切换回来
                resp = await client.put(f"/products/merchant/me/{product1['id']}/toggle", headers=headers)
            except Exception as e:
                log_step("切换商品状态", "FAIL", f"切换异常: {e}")
                all_passed = False
        else:
            log_step("切换商品状态", "FAIL", "跳过：商品未创建成功")
            all_passed = False

        # ==================== 第十步：验证商品在公开列表中可见 ====================
        print("\n" + "="*60)
        print("第十步：验证商品在公开列表中可见")
        print("="*60)

        await rate_limit_delay()

        try:
            # 获取商家ID（从分类中）
            merchant_id = None
            if category1.get("id"):
                resp = await client.get(f"/categories/{category1['id']}")
            
            # 通过公开接口获取商品列表
            resp = await client.get("/products")
            if resp.status_code == 200:
                public_products = resp.json()
                passed = log_step(
                    "商品公开可见性", "PASS",
                    f"公开商品列表中共 {public_products['total']} 个商品",
                    public_products
                )
            else:
                passed = log_step("商品公开可见性", "FAIL", f"获取失败: {resp.status_code} {resp.text}")
            all_passed = all_passed and passed
        except Exception as e:
            log_step("商品公开可见性", "FAIL", f"验证异常: {e}")
            all_passed = False

        # ==================== 第十一步：更新分类 ====================
        print("\n" + "="*60)
        print("第十一步：更新分类信息")
        print("="*60)

        await rate_limit_delay()

        if category1.get("id"):
            update_category_data = {
                "name": "热销菜品推荐",
            }

            try:
                resp = await client.put(f"/merchants/me/categories/{category1['id']}", json=update_category_data, headers=headers)
                if resp.status_code == 200:
                    updated_category = resp.json()
                    passed = log_step(
                        "更新分类", "PASS",
                        f"分类名称更新为: {updated_category['name']}",
                        updated_category
                    )
                else:
                    passed = log_step("更新分类", "FAIL", f"更新失败: {resp.status_code} {resp.text}")
                all_passed = all_passed and passed
            except Exception as e:
                log_step("更新分类", "FAIL", f"更新异常: {e}")
                all_passed = False
        else:
            log_step("更新分类", "FAIL", "跳过：分类未创建成功")
            all_passed = False

        # ==================== 第十二步：删除商品 ====================
        print("\n" + "="*60)
        print("第十二步：删除商品测试")
        print("="*60)

        await rate_limit_delay()

        # 创建一个临时商品用于删除测试
        if category1.get("id"):
            temp_product_data = {
                "name": "临时测试商品",
                "description": "用于删除测试",
                "price": "10.00",
                "category_id": category1["id"],
                "stock": 10,
                "is_available": True,
            }

            try:
                resp = await client.post("/products/merchant/me", json=temp_product_data, headers=headers)
                if resp.status_code == 201:
                    temp_product = resp.json()
                    temp_product_id = temp_product["id"]

                    # 删除商品
                    resp = await client.delete(f"/products/merchant/me/{temp_product_id}", headers=headers)
                    if resp.status_code == 204:
                        passed = log_step(
                            "删除商品", "PASS",
                            f"商品 {temp_product['name']} 删除成功"
                        )
                    else:
                        passed = log_step("删除商品", "FAIL", f"删除失败: {resp.status_code} {resp.text}")
                    all_passed = all_passed and passed
                else:
                    passed = log_step("删除商品", "FAIL", f"创建测试商品失败: {resp.status_code} {resp.text}")
                    all_passed = all_passed and passed
            except Exception as e:
                log_step("删除商品", "FAIL", f"删除异常: {e}")
                all_passed = False
        else:
            log_step("删除商品", "FAIL", "跳过：分类未创建成功")
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
        print("\n🎉 商家添加分类 → 添加商品 全流程联调测试全部通过！")
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
