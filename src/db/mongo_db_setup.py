import pymongo
import json
from time import time


def mongo_connect(conn_string, db_name):
    print("------ Connecting to MongoDB database")
    try:
        client = pymongo.MongoClient(conn_string)
        print("Connected, displaying server information:\n{0}\n\n-- database names:\n{1}\n"
              .format(client.server_info(), client.list_database_names()))
        print("Getting database '{0}'".format(db_name))
        db = client[db_name]
        print("Collection names:\n{0}".format(db.list_collection_names()))
        return client, db

    except pymongo.errors.OperationFailure as err:
        # do whatever you need
        print("{0} Error when connecting to database:\n{1}".format('-' * 15, err))


def json_to_mongo(db, collection_name, json_path):
    db[collection_name].drop()
    collection = db[collection_name]
    t = time()
    with open(json_path, 'r') as f_in:
        lines = f_in.readlines()
        row = 0
        for line in lines:
            if row % 50000 == 0:
                elpsd = time() - t
                print("Inserted {0:,.0f} rows, so far took {1:,.2f} seconds ({2:,.2f} minutes)"
                      .format(row, elpsd, elpsd / 60))
            row += 1
            line_json = json.loads(line)
            collection.insert_one(line_json)
        elapsed = time() - t
        print("Data inserted, took {0:,.2f} seconds ({1:,.2f} minutes)"
              .format(elapsed, elapsed / 60))
    return collection


def mongo_index(db, idx_dict):
    print("-- Creating index on the field '{0}' of collection '{1}', index type {2}"
          .format(idx_dict['idx_col_name'], idx_dict['cole_name'], idx_dict['type']))
    t = time()
    try:
        try:
            db[idx_dict['cole_name']].drop_index("{0}_{1}"
                                                 .format(idx_dict['idx_col_name'], idx_dict['type']))
            print("Old index dropped, creating new index...")
        except pymongo.errors.OperationFailure as err:
            print("{0}, creating new index...".format(err))
            pass
        db[idx_dict['cole_name']].create_index([
            (idx_dict['idx_col_name'], idx_dict['type'])
        ])
        elapsed = time() - t
        print("Index created, took {0:,.2f} seconds ({1:,.2f} minutes)\n"
              .format(elapsed, elapsed / 60))

    except pymongo.errors.OperationFailure as err:
        print("\n\n{0} Error when creating index\n{1}\n".format('-' * 15, err))
