
from mssql_python import connect


MASTER_CONNECTION_STRING = (
    "Server=localhost;"
    "Database=master;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

CLEANITY_CONNECTION_STRING = (
    "Server=localhost;"
    "Database=Cleanity;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def create_database():
    connection = connect(
        MASTER_CONNECTION_STRING,
        autocommit=True
    )

    try:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                IF DB_ID('Cleanity') IS NULL
                BEGIN
                    CREATE DATABASE Cleanity
                END
                """
            )

        finally:
            cursor.close()

    finally:
        connection.close()


def get_connection():
    return connect(CLEANITY_CONNECTION_STRING)


def create_tables():
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        # PRODUCTS
        cursor.execute(
            """
            IF NOT EXISTS (
                SELECT 1
                FROM sys.tables
                WHERE name = 'products'
            )
            BEGIN
                CREATE TABLE products (
                    product_id INT PRIMARY KEY,
                    product_name VARCHAR(100),
                    category VARCHAR(50),
                    unit_cost_cents INT,
                    unit_price_cents INT
                )
            END
            """
        )

        # CUSTOMERS
        cursor.execute(
            """
            IF NOT EXISTS (
                SELECT 1
                FROM sys.tables
                WHERE name = 'customers'
            )
            BEGIN
                CREATE TABLE customers (
                    customer_id INT PRIMARY KEY,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    city VARCHAR(100),
                    state VARCHAR(50),
                    registered_at DATETIME2(0)
                )
            END
            """
        )

        # ORDERS
        cursor.execute(
            """
            IF NOT EXISTS (
                SELECT 1
                FROM sys.tables
                WHERE name = 'orders'
            )
            BEGIN
                CREATE TABLE orders (
                    order_id INT PRIMARY KEY,
                    customer_id INT,
                    product_id INT,
                    quantity INT,
                    unit_price_cents INT,
                    order_date DATETIME2(0),
                    sales_channel VARCHAR(50),

                    FOREIGN KEY (customer_id)
                        REFERENCES customers(customer_id),

                    FOREIGN KEY (product_id)
                        REFERENCES products(product_id)
                )
            END
            """
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def initialize_database():
    create_database()
    create_tables()
