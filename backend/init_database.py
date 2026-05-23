import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from seed_data import seed_database


def main():
    db_path = os.path.join(os.path.dirname(__file__), 'food_delivery.db')
    if os.path.exists(db_path):
        answer = input(f'数据库文件 {db_path} 已存在，是否删除并重新初始化？(y/N): ')
        if answer.lower() == 'y':
            os.remove(db_path)
            print(f'已删除 {db_path}')
        else:
            print('取消初始化')
            return

    print('开始初始化数据库...')
    asyncio.run(seed_database())
    print('\n数据库初始化完成！')
    print('\n测试账号信息：')
    print('=' * 50)
    print('管理员账号：')
    print('  手机号: 13800000000')
    print('  密码: admin123')
    print('\n普通用户账号：')
    print('  手机号: 13800000001')
    print('  密码: user123')
    print('\n商家账号：')
    print('  手机号: 13900000001')
    print('  密码: merchant123')
    print('=' * 50)


if __name__ == '__main__':
    main()
