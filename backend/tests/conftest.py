import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from decimal import Decimal

from app.main import app
from app.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.merchant import Merchant
from app.models.category import Category
from app.models.product import Product
from app.models.address import Address
from app.models.order import Order
from app.models.order_item import OrderItem


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_food_delivery.db"

engine = create_async_engine(
    TEST_DATABASE_URL,
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


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """每个测试前后创建和清理数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """创建测试数据库会话"""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """创建测试 HTTP 客户端"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def _create_user(
    session: AsyncSession,
    username: str = "testuser",
    phone: str = "13800000001",
    password: str = "password123",
    role: str = "user",
    is_active: bool = True,
):
    """辅助函数：创建用户"""
    user = User(
        username=username,
        phone=phone,
        password_hash=get_password_hash(password),
        role=role,
        is_active=is_active,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def _create_admin(
    session: AsyncSession,
    username: str = "admin",
    phone: str = "13800000000",
    password: str = "admin123",
):
    """辅助函数：创建管理员用户"""
    return await _create_user(session, username=username, phone=phone, password=password, role="admin")


async def _create_merchant_user(
    session: AsyncSession,
    username: str = "merchant_user",
    phone: str = "13800000002",
    password: str = "merchant123",
):
    """辅助函数：创建商家用户"""
    return await _create_user(session, username=username, phone=phone, password=password, role="merchant")


async def _create_merchant(
    session: AsyncSession,
    user: User = None,
    business_name: str = "测试商家",
    status: str = "approved",
    approved_by: int = None,
):
    """辅助函数：创建商家"""
    if user is None:
        user = await _create_merchant_user(session)
    merchant = Merchant(
        user_id=user.id,
        business_name=business_name,
        contact_phone="13900000001",
        address="测试地址",
        description="这是一个测试商家",
        status=status,
        approved_by=approved_by,
        approved_at=datetime.utcnow() if status == "approved" else None,
    )
    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant


async def _create_category(
    session: AsyncSession,
    merchant: Merchant = None,
    name: str = "测试分类",
    sort_order: int = 0,
):
    """辅助函数：创建商品分类"""
    if merchant is None:
        user = await _create_merchant_user(session)
        merchant = await _create_merchant(session, user=user)
    category = Category(
        merchant_id=merchant.id,
        name=name,
        sort_order=sort_order,
    )
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _create_product(
    session: AsyncSession,
    merchant: Merchant = None,
    category: Category = None,
    name: str = "测试商品",
    price: Decimal = Decimal("29.90"),
    stock: int = 100,
    is_available: bool = True,
    description: str = "测试商品描述",
):
    """辅助函数：创建商品"""
    if merchant is None:
        user = await _create_merchant_user(session)
        merchant = await _create_merchant(session, user=user)
    if category is None:
        category = await _create_category(session, merchant=merchant)
    product = Product(
        merchant_id=merchant.id,
        category_id=category.id,
        name=name,
        description=description,
        price=price,
        stock=stock,
        is_available=is_available,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def _create_address(
    session: AsyncSession,
    user: User = None,
    receiver: str = "张三",
    phone: str = "13700000001",
    is_default: bool = True,
):
    """辅助函数：创建用户地址"""
    if user is None:
        user = await _create_user(session)
    if is_default:
        from sqlalchemy import select
        result = await session.execute(
            select(Address).where(Address.user_id == user.id, Address.is_default == True)
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.is_default = False
    address = Address(
        user_id=user.id,
        receiver=receiver,
        phone=phone,
        province="北京市",
        city="北京市",
        district="朝阳区",
        detail_address="测试街道123号",
        is_default=is_default,
    )
    session.add(address)
    await session.commit()
    await session.refresh(address)
    return address


async def _create_order(
    session: AsyncSession,
    user: User = None,
    merchant: Merchant = None,
    address: Address = None,
    status: str = "pending",
    total_price: Decimal = Decimal("99.90"),
):
    """辅助函数：创建订单"""
    if user is None:
        user = await _create_user(session)
    if merchant is None:
        m_user = await _create_merchant_user(session)
        merchant = await _create_merchant(session, user=m_user)
    if address is None:
        address = await _create_address(session, user=user)
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
        discount_amount=Decimal("0"),
        delivery_fee=Decimal("5.00"),
        pay_amount=total_price + Decimal("5.00"),
        status=status,
        remark="测试订单",
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def _create_order_item(
    session: AsyncSession,
    order: Order = None,
    product: Product = None,
    quantity: int = 1,
    price: Decimal = None,
):
    """辅助函数：创建订单项"""
    if order is None:
        user = await _create_user(session)
        m_user = await _create_merchant_user(session)
        merchant = await _create_merchant(session, user=m_user)
        addr = await _create_address(session, user=user)
        order = await _create_order(session, user=user, merchant=merchant, address=addr)
    if product is None:
        m_user = await _create_merchant_user(session)
        merchant = await _create_merchant(session, user=m_user)
        cat = await _create_category(session, merchant=merchant)
        product = await _create_product(session, merchant=merchant, category=cat)
    if price is None:
        price = product.price
    subtotal = price * quantity
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_image=product.image_url,
        price=price,
        quantity=quantity,
        subtotal=subtotal,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


def generate_test_token(
    user_id: int = 1,
    username: str = "testuser",
    role: str = "user",
    phone: str = "13800000001",
) -> str:
    """生成测试用 JWT Token"""
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "phone": phone,
    }
    return create_access_token(data=payload)


def get_test_headers(
    user_id: int = 1,
    username: str = "testuser",
    role: str = "user",
    phone: str = "13800000001",
) -> dict:
    """获取带认证信息的测试请求头"""
    token = generate_test_token(user_id=user_id, username=username, role=role, phone=phone)
    return {"Authorization": f"Bearer {token}"}


def get_admin_headers() -> dict:
    """获取管理员测试请求头"""
    return get_test_headers(user_id=1, username="admin", role="admin", phone="13800000000")


def get_merchant_headers() -> dict:
    """获取商家测试请求头"""
    return get_test_headers(user_id=2, username="merchant_user", role="merchant", phone="13800000002")
