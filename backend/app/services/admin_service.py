from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.merchant import Merchant
from app.models.order import Order
from app.models.product import Product
from app.core.exceptions import NotFoundException


class AdminService:
    """管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表盘统计数据。

        Returns:
            统计数据字典。
        """
        # 用户总数
        user_count_result = await self.db.execute(select(func.count(User.id)))
        user_count = user_count_result.scalar()

        # 商家总数
        merchant_count_result = await self.db.execute(select(func.count(Merchant.id)))
        merchant_count = merchant_count_result.scalar()

        # 待审核商家数
        pending_merchant_result = await self.db.execute(
            select(func.count(Merchant.id)).where(Merchant.status == "pending")
        )
        pending_merchant_count = pending_merchant_result.scalar()

        # 订单总数
        order_count_result = await self.db.execute(select(func.count(Order.id)))
        order_count = order_count_result.scalar()

        # 今日订单数
        today = datetime.utcnow().date()
        today_order_result = await self.db.execute(
            select(func.count(Order.id)).where(func.date(Order.created_at) == today)
        )
        today_order_count = today_order_result.scalar()

        # 本月订单数
        this_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_order_result = await self.db.execute(
            select(func.count(Order.id)).where(Order.created_at >= this_month)
        )
        month_order_count = month_order_result.scalar()

        # 今日收入（已支付订单）
        today_revenue_result = await self.db.execute(
            select(func.sum(Order.pay_amount)).where(
                func.date(Order.created_at) == today,
                Order.status != "cancelled",
                Order.status != "refunded",
            )
        )
        today_revenue = today_revenue_result.scalar() or Decimal("0")

        # 本月收入
        month_revenue_result = await self.db.execute(
            select(func.sum(Order.pay_amount)).where(
                Order.created_at >= this_month,
                Order.status != "cancelled",
                Order.status != "refunded",
            )
        )
        month_revenue = month_revenue_result.scalar() or Decimal("0")

        return {
            "user_count": user_count,
            "merchant_count": merchant_count,
            "pending_merchant_count": pending_merchant_count,
            "order_count": order_count,
            "today_order_count": today_order_count,
            "month_order_count": month_order_count,
            "today_revenue": today_revenue,
            "month_revenue": month_revenue,
        }

    async def get_order_statistics(
        self,
        days: int = 30,
    ) -> Dict[str, Any]:
        """获取订单统计数据（按天）。

        Args:
            days: 统计天数。

        Returns:
            订单统计数据。
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # 按天统计订单数和收入
        result = await self.db.execute(
            select(
                func.date(Order.created_at).label("date"),
                func.count(Order.id).label("order_count"),
                func.sum(Order.pay_amount).label("revenue"),
            )
            .where(
                Order.created_at >= start_date,
                Order.status != "cancelled",
                Order.status != "refunded",
            )
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at).asc())
        )
        rows = result.fetchall()

        return {
            "days": days,
            "data": [
                {
                    "date": row.date.strftime("%Y-%m-%d") if hasattr(row.date, "strftime") else str(row.date),
                    "order_count": row.order_count,
                    "revenue": row.revenue or Decimal("0"),
                }
                for row in rows
            ],
        }

    async def get_popular_products(
        self,
        limit: int = 10,
    ) -> list[Dict[str, Any]]:
        """获取热销商品排行榜。

        Args:
            limit: 返回数量。

        Returns:
            热销商品列表。
        """
        from app.models.order_item import OrderItem

        result = await self.db.execute(
            select(
                Product.id,
                Product.name,
                Product.image_url,
                Product.merchant_id,
                func.sum(OrderItem.quantity).label("total_sold"),
                func.sum(OrderItem.subtotal).label("total_revenue"),
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .where(
                Order.status != "cancelled",
                Order.status != "refunded",
            )
            .group_by(Product.id)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
        rows = result.fetchall()

        return [
            {
                "id": row.id,
                "name": row.name,
                "image_url": row.image_url,
                "merchant_id": row.merchant_id,
                "total_sold": row.total_sold,
                "total_revenue": row.total_revenue or Decimal("0"),
            }
            for row in rows
        ]

    async def list_orders(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[list[Order], int]:
        """获取订单列表（管理员）。

        Args:
            page: 页码。
            page_size: 每页大小。
            status: 状态筛选。
            start_date: 开始日期。
            end_date: 结束日期。

        Returns:
            订单列表和总数的元组。
        """
        conditions = []
        if status:
            conditions.append(Order.status == status)
        if start_date:
            conditions.append(Order.created_at >= start_date)
        if end_date:
            conditions.append(Order.created_at <= end_date)

        # 查询总数
        count_query = select(func.count(Order.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 查询数据
        query = select(Order)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(Order.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        orders = result.scalars().all()

        return list(orders), total

    async def get_order_details(self, order_id: int) -> Optional[Order]:
        """获取订单详情（管理员）。

        Args:
            order_id: 订单 ID。

        Returns:
            订单对象或 None。
        """
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def get_user_details(self, user_id: int) -> Optional[User]:
        """获取用户详情（管理员）。

        Args:
            user_id: 用户 ID。

        Returns:
            用户对象或 None。
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_merchant_details(self, merchant_id: int) -> Optional[Merchant]:
        """获取商家详情（管理员）。

        Args:
            merchant_id: 商家 ID。

        Returns:
            商家对象或 None。
        """
        result = await self.db.execute(select(Merchant).where(Merchant.id == merchant_id))
        return result.scalar_one_or_none()
