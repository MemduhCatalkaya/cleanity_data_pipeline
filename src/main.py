
import logging
import time

from pathlib import Path

from database import initialize_database, get_connection
from sync import sync_all


SYNC_INTERVAL_SECONDS = 10


# LOGGING
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / "pipeline.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def sync_once():
    logger.info("Sync started.")

    try:
        new_customers, new_orders = sync_all()

    except Exception:
        logger.exception("Sync failed.")
        return

    logger.info(
        "Sync completed | Customers: %s | Orders: %s",
        new_customers,
        new_orders
    )


def continuous_sync():
    logger.info("Continuous sync started.")
    logger.info(
        "Checking for new data every %s seconds.",
        SYNC_INTERVAL_SECONDS
    )
    print("Press Ctrl+C to stop.\n")

    
    try:
        while True:
            try:
                new_customers, new_orders = sync_all()

                logger.info(
                    "Sync completed | Customers: %s | Orders: %s",
                    new_customers,
                    new_orders
                )

            except Exception:
                logger.exception("Sync failed.")

            time.sleep(SYNC_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("Continuous sync stopped by user.")


def show_status():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]

        print("\nSQL Server Status")
        print("-----------------")
        print(f"Products  : {product_count}")
        print(f"Customers : {customer_count}")
        print(f"Orders    : {order_count}\n")

    except Exception:
        logger.exception("Failed to retrieve database status.")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


def show_menu():
    print("========================================")
    print("       CLEANITY DATA PIPELINE")
    print("========================================")
    print()
    print("Source      : Cleanity REST API")
    print("Destination : Microsoft SQL Server")
    print("Sync Mode   : Incremental")
    print(f"Interval    : {SYNC_INTERVAL_SECONDS} seconds")
    print()
    print("1 - Sync Once")
    print("2 - Start Continuous Sync")
    print("3 - Status")
    print("0 - Exit")
    print()


def main():
    try:
        initialize_database()

    except Exception:
        logger.exception("Database initialization failed.")
        print("\nUnable to initialize SQL Server database.")
        return

    logger.info("Cleanity Data Pipeline initialized.")

    while True:
        show_menu()

        try:
            choice = input("Select: ").strip()

        except (KeyboardInterrupt, EOFError):
            logger.info("Pipeline stopped by user.")
            break

        if choice == "1":
            sync_once()
            time.sleep(3)

        elif choice == "2":
            continuous_sync()
            time.sleep(3)

        elif choice == "3":
            show_status()
            time.sleep(3)

        elif choice == "0":
            logger.info("Pipeline stopped.")
            break

        else:
            print("\nInvalid selection.\n")
            time.sleep(3)


if __name__ == "__main__":
    main()
