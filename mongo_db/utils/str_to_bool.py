# mongo_db/utils/str_to_bool.py

def str_to_bool(s):
    return s.lower() in ['true', '1', 't', 'y', 'yes']
