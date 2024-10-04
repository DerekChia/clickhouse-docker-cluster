import clickhouse_connect

client = clickhouse_connect.get_client(host='localhost', port=28123, username='default', password='')
result = client.query('select 1;')
print(result.result_rows)
# [(1,)]