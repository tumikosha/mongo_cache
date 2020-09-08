# -*- coding: utf-8 -*-
"""
Python module for caching function calls in mongoDB with TTL and  decorator
First function parameter is used as key
Collection is zipped

Example:
	@mongo_cache(MONGO_URI, db_name="FB", collection="cache", ttl=datetime.timedelta(seconds=5), verbose=False)
	def go(function_arg1, function_arg2, function_arg3):
		return 100

	clear_cache(MONGO_URI, db_name="FB", collection="cache")
	print(go(1, 2, 3))
	time.sleep(1)
	print(go(1, 2, 3))
	time.sleep(5)
	print(go(1, 2, 3))


"""

import datetime, time
import pymongo

MONGO_URI = "mongodb://127.0.0.1:27017/"

client = None


def create_zlib_collection(xdb, name):
	"""makes mongodb collection in ZIPPED MODE"""
	print('[X]creating collection: ', xdb, name)
	try:
		xdb.create_collection(name,
							  storageEngine={'wiredTiger': {'configString': 'block_compressor=zlib'}})
		print('ZLIB collection created')
	except:
		print('Collection already exists')


def ensure_index(xdb, collection, field, direction):
	"""create index if it is not exists"""
	print('[X]creating index:', collection, field, direction)
	try:
		response = xdb[collection].create_index([(field, direction)])
		print(response)
	except Exception as e:
		print(str(e))


def prepare_database(mongo_uri, db_name):
	""" singletone
	makes database connection
	:return: (client, database)
	"""
	global db, client
	if client is not None:
		return client, db

	client = pymongo.MongoClient(mongo_uri)
	db = client[db_name]
	create_zlib_collection(db, "users")
	ensure_index(db, 'users', 'created_at', pymongo.ASCENDING)
	return client, db


def clear_cache(mongo_uri, db_name="cache", collection="cache"):
	client, db = prepare_database(mongo_uri, db_name)
	db[collection].delete_many({})
	print("# cache cleared")


def mongo_cache(mongo_uri, db_name="cache", collection="cache", ttl="1 second ago", verbose=False):
	def decorator(func):
		def wrapper(*args, **kwargs):
			# delta = datetime.datetime.now() - dateparser.parse(ttl)
			delta = ttl
			# print("delta", delta)
			client, db = prepare_database(mongo_uri, db_name)
			# print("====", db)
			key = args[0]
			# print("# caching to: ", db, collection, ttl, mongo_uri)
			# print("key = ", key)
			record = db[collection].find_one({'_id': key})
			if record is not None:  # возвращаем из кэша
				if record['created_at'] + delta > datetime.datetime.now():
					if verbose: print('# returned from cache')
					return record['value']
				else:
					if verbose: print('# Presented in cache but TTL expired. DELETE')
					db[collection].delete_one({'_id': key})
			if verbose: print('# Not present in  cache')
			res = func(*args)
			db[collection].insert_one({'_id': key, 'value': res, 'created_at': datetime.datetime.now()})
			return res

		return wrapper

	return decorator


@mongo_cache(MONGO_URI, db_name="FB", collection="cache", ttl=datetime.timedelta(seconds=5), verbose=True)
def go(function_arg1, function_arg2, function_arg3):
	return 100


if __name__ == '__main__':
	clear_cache(MONGO_URI, db_name="FB", collection="cache")
	print(go(1, 2, 3))
	time.sleep(1)
	print(go(1, 2, 3))
	time.sleep(5)
	print(go(1, 2, 3))
