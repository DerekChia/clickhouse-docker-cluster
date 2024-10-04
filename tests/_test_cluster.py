import time
import clickhouse_connect
import pandas
import pytest
# test cluster with distributed table

client = clickhouse_connect.get_client(host='localhost', port=28123, username='default', password='')

# @pytest.fixture(scope="module"):
def clean_up():
    # clean up
    client.command("drop table if exists tbl_local on cluster `{cluster}`")
    client.command("drop table if exists tbl_distributed on cluster `{cluster}`")

    result = client.query_df("select * from system.tables where table in ('tbl_local', 'tbl_distributed')")
    return result.empty

def create_distributed_table(num_row):
    # create underlying local table in all nodes
    client.command("drop table if exists tbl_local on cluster `{cluster}`")
    client.command("create table tbl_local on cluster `{cluster}` (a UInt32) Engine=ReplicatedMergeTree order by a")

    # create distributed table based off local table in all nodes
    client.command("drop table if exists tbl_distributed on cluster `{cluster}`")
    client.command("create table tbl_distributed on cluster `{cluster}` Engine = Distributed(`{cluster}`, default, tbl_local, rand())")

    # insert rows into distributed table
    client.command(f"insert into tbl_distributed select rand() from numbers({num_row})")

    # sleep before counting
    client.command(f"select sleep(3)")

    # check rows
    result = client.query_df("select count() from tbl_distributed")

    return result.values

def test_cluster_availability():
    assert create_distributed_table(1_000_000) == 1_000_000
    assert clean_up()