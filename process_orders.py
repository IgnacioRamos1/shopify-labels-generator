from request_orders import request_orders
from filter_orders import filter_and_group_by_family
from send_email import send_products_missing_email
from utils import create_zip_in_memory, get_parameter, generate_presigned_url
from send_whatsapp_message import send_whatsapp_group_message, send_whatsapp_message
from save_to_bucket import async_save_to_s3, save_to_s3

from datetime import datetime
import asyncio


async def process_orders(credentials):
    try:
        date = datetime.now().strftime('%Y-%m-%d')
        total_orders, total_orders_count = await request_orders(credentials)
        grouped_orders = filter_and_group_by_family(total_orders)
        from_email = get_parameter('from_email')
        to_email = get_parameter('to_email')

        all_not_added_products = []
        all_not_added_orders = []

        for shop in grouped_orders:
            tasks = []
            in_memory_csvs = {}
            orders_breakdown = {}
            not_added_orders_for_shop = []  # List to store orders not added for this specific shop

            for product, orders in grouped_orders[shop].items():
                task = asyncio.ensure_future(async_save_to_s3(shop, product, grouped_orders))
                tasks.append(task)

            completed_tasks = await asyncio.gather(*tasks)

            for csv_data, file_name, not_added_products, not_added_orders in completed_tasks:
                all_not_added_products.extend(not_added_products)
                not_added_orders_for_shop.extend(not_added_orders)
                if csv_data and file_name and len(csv_data.splitlines()) > 1:
                    in_memory_csvs[file_name] = csv_data

            for file_name, csv_content in in_memory_csvs.items():
                product_name = file_name.split('-')[2].strip()
                orders_breakdown[product_name] = len(csv_content.splitlines()) - 1

            total_orders_count[shop] = sum(orders_breakdown.values())

            all_not_added_orders.extend(not_added_orders_for_shop)

            if in_memory_csvs:
                _, zip_buffer = create_zip_in_memory(shop, in_memory_csvs)
                save_to_s3(shop, zip_buffer.getvalue(), f"{date}.zip")

                # Send the ZIP file to WhatsApp
                formatted_shop_name = shop.lower().replace(" ", "-")
                s3_presigned_url = generate_presigned_url(formatted_shop_name, f"{date}.zip")
                group_chat_id = [store["group_chat_id"] for store in credentials if store["shop_name"] == shop][0]
                send_whatsapp_group_message(date, shop, total_orders_count, s3_presigned_url, group_chat_id)
                
                # Send not added orders message to WhatsApp if there are any
                if not_added_orders_for_shop:
                    group_chat_id = [store["group_chat_id"] for store in credentials if store["shop_name"] == shop][0]
                    message = "\n".join([f"{order['person']} - {order['item']} - {order['reason']}" for order in not_added_orders_for_shop])
                    send_whatsapp_message(group_chat_id, message)

        # Send email with not added orders
        if all_not_added_orders:
            send_products_missing_email(from_email, to_email, all_not_added_products)

    except Exception as e:
        raise Exception(f"Error in process_orders function: {e}")
