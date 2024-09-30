INSERT INTO keeper_bench.keeper_bench SELECT rand(1)%100, rand(2) FROM numbers(40000)
    SETTINGS max_block_size=1,
    min_insert_block_size_bytes=1,
    min_insert_block_size_rows=1,
    insert_deduplicate=0,
    max_threads=128,
    max_insert_threads=128;