from django.db import connection
from contextlib import closing

def get_product_by_id(product_id):
    with closing(connection.cursor()) as cursor:
        cursor.execute("""
        select id, title as name, description, image, price,category_id from product where id = %s""",
                       [product_id])
        product = dict_fetchone(cursor)
    return product


def get_order_max_id():
    with closing(connection.cursor()) as cursor:
        cursor.execute("""select max(id) from order""")
        order_id = dict_fetchone(cursor)
    return order_id


def get_product():
    with closing(connection.cursor()) as cursor:
        cursor.execute("""select * from product""")
        products = dict_fetchall(cursor)
    return products

def get_product_by_category_id(pk):
    with closing(connection.cursor()) as cursor:
        cursor.execute(f"""select * from product where category_id ={pk}""")
        products = dict_fetchall(cursor)
    return products


def get_product_price(pk):
    with closing(connection.cursor()) as cursor:
        cursor.execute("""select price from product where id = %s""", [pk])
        price = dict_fetchone(cursor)
    return price


def get_category():
    with closing(connection.cursor()) as cursor:
        cursor.execute("""select * from category  """)
        categories = dict_fetchall(cursor)
    return categories

def create_user(chat_id,created_at):
    with closing(connection.cursor()) as cursor:
        cursor.execute(f"""insert into user_bot(chat_id,created_at) values ({chat_id},'{created_at}')""")


def get_user_id(chat_id):
    with closing(connection.cursor()) as cursor:
        cursor.execute(f"""select * from user_bot where chat_id={chat_id}""")
        user_id = dict_fetchone(cursor)
    return user_id

def create_cart(user_id,status,created_at):
    with closing(connection.cursor()) as cursor:
        cursor.execute(f"""insert into cart_bot(user_id,status,created_at) values ({user_id},{status},'{created_at}')""")

# def get_product_from_cart(user_id):
#     with closing(connection.cursor()) as cursor:
#         cursor.execute(f"""insert into cart_bot(user_id,status,created_at) values ({user_id},{status},'{created_at}')""")



def update_user(state, chat_id, data):
     with closing(connection.cursor()) as cursor:
        if state == 1:
            cursor.execute(
                """UPDATE user_bot SET first_name = %s WHERE chat_id = %s""",
                [data, chat_id]
            )
        elif state == 2:
            cursor.execute(
                """UPDATE user_bot SET last_name = %s WHERE chat_id = %s""",
                [data, chat_id]
            )

        elif state == 3:
            cursor.execute(
                """UPDATE user_bot SET phone = %s WHERE chat_id = %s""",
                [data, chat_id]
            )
        elif state == 4:
            cursor.execute(
                """UPDATE user_bot SET address = %s WHERE chat_id = %s""",
                [data, chat_id]
            )

def create_order(user_id,products,status,total_price,created_at):
    with closing(connection.cursor()) as cursor:
        cursor.execute("""insert into "order"(user_bot_id,products,status,total_price,created_at) values (%s, %s, %s, %s, %s)""",
            [user_id,products,status,total_price,created_at])


def product_of_order(user_id):
    with closing(connection.cursor()) as cursor:
        cursor.execute(f"""select * from "order" where user_bot_id={user_id} order by created_at""")
        user_id = dict_fetchall(cursor)
    return user_id


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row))
            for row in cursor.fetchall()]


def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))
