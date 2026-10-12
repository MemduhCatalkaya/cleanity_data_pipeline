from api_client import get_products, get_customers, get_orders
from database import get_connection


def sync_products():
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        products = get_products()

        for product in products:
            cursor.execute(
                """
                INSERT INTO products (
                    product_id,
                    product_name,
                    category,
                    unit_cost_cents,
                    unit_price_cents
                )
                SELECT ?, ?, ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM products
                    WHERE product_id = ?
                )
                """,
                (
                    product["product_id"],
                    product["product_name"],
                    product["category"],
                    product["unit_cost_cents"],
                    product["unit_price_cents"],
                    product["product_id"]
                )
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def sync_customers():
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT MAX(customer_id)
            FROM customers
            """
        )

        last_customer_id = cursor.fetchone()[0] or 0

        customers = get_customers(last_customer_id)

        if customers:
            customer_rows = [
                (
                    customer["customer_id"],
                    customer["first_name"],
                    customer["last_name"],
                    customer["city"],
                    customer["state"],
                    customer["registered_at"]
                )
                for customer in customers
            ]

            cursor.executemany(
                """
                INSERT INTO customers (
                    customer_id,
                    first_name,
                    last_name,
                    city,
                    state,
                    registered_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                customer_rows
            )

            connection.commit()

        return len(customers)

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def sync_orders():
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT MAX(order_id)
            FROM orders
            """
        )

        last_order_id = cursor.fetchone()[0] or 0

        orders = get_orders(last_order_id)

        if orders:
            order_rows = [
                (
                    order["order_id"],
                    order["customer_id"],
                    order["product_id"],
                    order["quantity"],
                    order["unit_price_cents"],
                    order["order_date"],
                    order["sales_channel"]
                )
                for order in orders
            ]

            cursor.executemany(
                """
                INSERT INTO orders (
                    order_id,
                    customer_id,
                    product_id,
                    quantity,
                    unit_price_cents,
                    order_date,
                    sales_channel
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                order_rows
            )

            connection.commit()

        return len(orders)

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def sync_all():
    sync_products()

    new_customers = sync_customers()
    new_orders = sync_orders()

    return new_customers, new_orders