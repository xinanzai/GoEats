import asyncio
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import Base
from app.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.merchant import Merchant
from app.models.category import Category
from app.models.product import Product
from app.models.address import Address
from app.models.order import Order
from app.models.order_item import OrderItem


async def seed_database():
    """填充测试数据"""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
    )

    TestingSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with TestingSessionLocal() as session:
        try:
            await create_all_tables(session)
            await create_users(session)
            await create_merchants(session)
            await create_categories(session)
            await create_products(session)
            await create_addresses(session)
            await create_orders(session)
            print("测试数据填充成功！")
        except Exception as e:
            await session.rollback()
            print(f"测试数据填充失败: {e}")
            raise
        finally:
            await engine.dispose()


async def create_all_tables(session: AsyncSession):
    """创建所有数据表"""
    async with session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_users(session: AsyncSession):
    """创建测试用户"""
    users_data = [
        {
            "username": "admin",
            "phone": "13800000000",
            "password": "admin123",
            "role": "admin",
            "avatar": None,
        },
        {
            "username": "user1",
            "phone": "13800000001",
            "password": "user123",
            "role": "user",
            "avatar": None,
        },
        {
            "username": "user2",
            "phone": "13800000002",
            "password": "user123",
            "role": "user",
            "avatar": None,
        },
        {
            "username": "merchant1_owner",
            "phone": "13900000001",
            "password": "merchant123",
            "role": "merchant",
            "avatar": None,
        },
        {
            "username": "merchant2_owner",
            "phone": "13900000002",
            "password": "merchant123",
            "role": "merchant",
            "avatar": None,
        },
    ]

    users = []
    for data in users_data:
        user = User(
            username=data["username"],
            phone=data["phone"],
            password_hash=get_password_hash(data["password"]),
            role=data["role"],
            avatar=data["avatar"],
            is_active=True,
        )
        session.add(user)
        users.append(user)

    await session.flush()
    for user in users:
        await session.refresh(user)


async def create_merchants(session: AsyncSession):
    """创建测试商家"""
    from sqlalchemy import select

    merchant_owners = (
        await session.execute(
            select(User).where(User.username.in_(["merchant1_owner", "merchant2_owner"]))
        )
    ).scalars().all()

    merchants_data = [
        {
            "user": merchant_owners[0],
            "business_name": "美味快餐店",
            "contact_phone": "13900000011",
            "address": "北京市朝阳区建国路100号",
            "description": "正宗中式快餐，口味地道，配送迅速",
            "logo": None,
            "status": "approved",
        },
        {
            "user": merchant_owners[1],
            "business_name": "意大利餐厅",
            "contact_phone": "13900000022",
            "address": "北京市朝阳区建国路200号",
            "description": "正宗意大利美食，环境优雅",
            "logo": None,
            "status": "approved",
        },
    ]

    for data in merchants_data:
        merchant = Merchant(
            user_id=data["user"].id,
            business_name=data["business_name"],
            contact_phone=data["contact_phone"],
            address=data["address"],
            description=data["description"],
            logo=data["logo"],
            status=data["status"],
            approved_at=datetime.utcnow(),
            approved_by=1,
        )
        session.add(merchant)

    await session.flush()
    for data in merchants_data:
        merchant = (await session.execute(
            select(Merchant).where(Merchant.business_name == data["business_name"])
        )).scalar_one_or_none()
        if merchant:
            await session.refresh(merchant)


async def create_categories(session: AsyncSession):
    """创建测试分类"""
    from sqlalchemy import select

    merchants = (
        await session.execute(
            select(Merchant).where(Merchant.business_name.in_(["美味快餐店", "意大利餐厅"]))
        )
    ).scalars().all()

    categories_data = {
        "美味快餐店": ["热销菜品", "主食类", "小吃类", "饮品"],
        "意大利餐厅": ["意面", "披萨", "沙拉", "甜品"],
    }

    for merchant in merchants:
        name_list = categories_data.get(merchant.business_name, [])
        for idx, name in enumerate(name_list):
            category = Category(
                merchant_id=merchant.id,
                name=name,
                sort_order=idx,
            )
            session.add(category)

    await session.flush()


async def create_products(session: AsyncSession):
    """创建测试商品"""
    from sqlalchemy import select

    categories = (await session.execute(select(Category))).scalars().all()

    products_data = [
        {"category": "热销菜品", "name": "红烧肉", "price": "38.00", "stock": 50},
        {"category": "热销菜品", "name": "宫保鸡丁", "price": "32.00", "stock": 60},
        {"category": "主食类", "name": "扬州炒饭", "price": "18.00", "stock": 100},
        {"category": "主食类", "name": "蛋炒饭", "price": "15.00", "stock": 100},
        {"category": "小吃类", "name": "春卷", "price": "12.00", "stock": 80},
        {"category": "小吃类", "name": "锅贴", "price": "16.00", "stock": 80},
        {"category": "饮品", "name": "冰镇酸梅汤", "price": "8.00", "stock": 200},
        {"category": "饮品", "name": "鲜榨果汁", "price": "15.00", "stock": 150},
        {"category": "意面", "name": "番茄肉酱意面", "price": "48.00", "stock": 40},
        {"category": "意面", "name": "黑胡椒牛柳意面", "price": "58.00", "stock": 35},
        {"category": "披萨", "name": "玛格丽特披萨", "price": "68.00", "stock": 30},
        {"category": "披萨", "name": "夏威夷披萨", "price": "78.00", "stock": 25},
        {"category": "沙拉", "name": "凯撒沙拉", "price": "35.00", "stock": 50},
        {"category": "甜品", "name": "提拉米苏", "price": "28.00", "stock": 40},
    ]

    for product_data in products_data:
        category = (
            await session.execute(
                select(Category).where(Category.name == product_data["category"])
            )
        ).scalar_one_or_none()

        if category:
            product = Product(
                merchant_id=category.merchant_id,
                category_id=category.id,
                name=product_data["name"],
                description=f"{product_data['name']}，口感鲜美",
                price=Decimal(product_data["price"]),
                stock=product_data["stock"],
                is_available=True,
            )
            session.add(product)

    await session.flush()


async def create_addresses(session: AsyncSession):
    """创建测试地址"""
    from sqlalchemy import select

    users = (
        await session.execute(
            select(User).where(User.username.in_(["user1", "user2"]))
        )
    ).scalars().all()

    addresses_data = [
        {
            "user": "user1",
            "receiver": "张三",
            "phone": "13700000001",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail": "建国路100号",
            "is_default": True,
        },
        {
            "user": "user1",
            "receiver": "张三",
            "phone": "13700000001",
            "province": "北京市",
            "city": "北京市",
            "district": "海淀区",
            "detail": "中关村大街10号",
            "is_default": False,
        },
        {
            "user": "user2",
            "receiver": "李四",
            "phone": "13700000002",
            "province": "北京市",
            "city": "北京市",
            "district": "西城区",
            "detail": "金融街8号",
            "is_default": True,
        },
    ]

    for data in addresses_data:
        user = next(u for u in users if u.username == data["user"])
        address = Address(
            user_id=user.id,
            receiver=data["receiver"],
            phone=data["phone"],
            province=data["province"],
            city=data["city"],
            district=data["district"],
            detail_address=data["detail"],
            is_default=data["is_default"],
        )
        session.add(address)

    await session.flush()


async def create_orders(session: AsyncSession):
    """创建测试订单"""
    from sqlalchemy import select
    import uuid

    users = (
        await session.execute(
            select(User).where(User.username.in_(["user1", "user2"]))
        )
    ).scalars().all()

    merchants = (
        await session.execute(
            select(Merchant).where(Merchant.business_name.in_(["美味快餐店", "意大利餐厅"]))
        )
    ).scalars().all()

    addresses = (await session.execute(select(Address))).scalars().all()
    products = (await session.execute(select(Product))).scalars().all()

    orders_data = [
        {
            "user": "user1",
            "merchant": "美味快餐店",
            "status": "paid",
            "items": [
                {"product": "红烧肉", "quantity": 1},
                {"product": "扬州炒饭", "quantity": 2},
            ],
        },
        {
            "user": "user1",
            "merchant": "意大利餐厅",
            "status": "preparing",
            "items": [
                {"product": "玛格丽特披萨", "quantity": 1},
                {"product": "凯撒沙拉", "quantity": 1},
            ],
        },
        {
            "user": "user2",
            "merchant": "美味快餐店",
            "status": "pending",
            "items": [
                {"product": "宫保鸡丁", "quantity": 1},
                {"product": "冰镇酸梅汤", "quantity": 2},
            ],
        },
        {
            "user": "user2",
            "merchant": "意大利餐厅",
            "status": "delivering",
            "items": [
                {"product": "番茄肉酱意面", "quantity": 1},
                {"product": "提拉米苏", "quantity": 2},
            ],
        },
        {
            "user": "user1",
            "merchant": "美味快餐店",
            "status": "completed",
            "items": [
                {"product": "锅贴", "quantity": 1},
                {"product": "鲜榨果汁", "quantity": 1},
            ],
        },
    ]

    for order_data in orders_data:
        user = next(u for u in users if u.username == order_data["user"])
        merchant = next(m for m in merchants if m.business_name == order_data["merchant"])
        address = next(a for a in addresses if a.user_id == user.id and a.is_default)

        total_price = Decimal("0")
        items = []
        for item_data in order_data["items"]:
            product = next(p for p in products if p.name == item_data["product"])
            quantity = item_data["quantity"]
            subtotal = product.price * quantity
            total_price += subtotal
            items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            })

        delivery_fee = Decimal("5.00")
        discount_amount = Decimal("0")
        pay_amount = total_price - discount_amount + delivery_fee

        import uuid
        order = Order(
            order_no=str(uuid.uuid4()).replace("-", "")[:32],
            user_id=user.id,
            merchant_id=merchant.id,
            address_id=address.id,
            receiver=address.receiver,
            receiver_phone=address.phone,
            receiver_address=f"{address.province}{address.city}{address.district}{address.detail_address}",
            total_price=total_price,
            discount_amount=discount_amount,
            delivery_fee=delivery_fee,
            pay_amount=pay_amount,
            status=order_data["status"],
            remark="测试订单",
            paid_at=datetime.utcnow() if order_data["status"] in ["paid", "preparing", "delivering", "completed"] else None,
            completed_at=datetime.utcnow() if order_data["status"] == "completed" else None,
        )
        session.add(order)
        await session.flush()
        await session.refresh(order)

        for item_data in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                product_name=item_data["product"].name,
                product_image=item_data["product"].image_url,
                price=item_data["product"].price,
                quantity=item_data["quantity"],
                subtotal=item_data["subtotal"],
            )
            session.add(order_item)

    await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_database())
