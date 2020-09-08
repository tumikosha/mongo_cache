# mongo_cache
Python module for caching function calls in mongoDB with TTL and  decorator

First function parameter is used as a key

Example:

	import datetime
	import mongo_cache
	
	@mongo_cache(MONGO_URI, db_name="FB", collection="cache", ttl=datetime.timedelta(seconds=5))
	def go(function_arg_as_MONGO_ID, function_arg2, function_arg3):
		return 100

	clear_cache(MONGO_URI, db_name="FB", collection="cache")
	print(go(1, 2, 3))
	time.sleep(1)
	print(go(1, 2, 3))
	time.sleep(5)
	print(go(1, 2, 3))
