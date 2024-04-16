from mongo_db.database import CacheDatabase


def get_or_create_table_name(store_name):
    try:
        # Create a new database object
        db = CacheDatabase.get_instance()

        # Check if the table exists
        if db.check_store_exists(store_name):
            return store_name
        else:
            # Create the table
            table_name = db.add_store(store_name)
            return table_name
    
    except Exception as e:
        raise Exception(f"Error in get_or_create_table_name function: {e}")


