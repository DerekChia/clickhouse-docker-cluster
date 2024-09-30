import argparse
from cluster import Cluster

if __name__ == "__main__":
    """
    Different configurations:
    -
    """
    parser = argparse.ArgumentParser()

    # general
    parser.add_argument(
        "--ch-version", type=str, default="24.8", help="ClickHouse version"
    )
    parser.add_argument("--shard", type=int, default=1, help="Number of shard")
    parser.add_argument("--replica", type=int, default=3, help="Number of replica")
    parser.add_argument("--cluster-directory", type=str, default="cluster_1")

    # node configuration
    parser.add_argument("--cpu", type=int, default=1, help="CPUs for each node")
    parser.add_argument(
        "--memory", type=str, default="8192m", help="RAM (mb) for each node"
    )

    # keeper_mode
    parser.add_argument(
        "--keeper-mode",
        type=str,
        choices=["chkeeper", "zookeeper", "embedded"],
        help="chkeeper, zookeeper, embedded",
    )
    parser.add_argument(
        "--keeper-count", type=int, default=3, help="Number of Keepers (Min. 3)"
    )

    # keeper node configuration
    parser.add_argument("--cpu-keeper", type=int, default=1, help="CPUs for each node")
    parser.add_argument(
        "--memory-keeper", type=str, default="4096m", help="RAM (mb) for each node"
    )

    # ports
    parser.add_argument("--native-protocol-port", type=int, default=9000)
    parser.add_argument("--http-api-port", type=int, default=8123)
    parser.add_argument("--ch-prometheus-port", type=int, default=9363)
    parser.add_argument("--keeper-raft-port", type=int, default=9234)  # 9444
    parser.add_argument("--keeper-internal-replication", type=str, default="true")

    # misc.
    parser.add_argument("--chnode-prefix", type=str, default="chnode")
    parser.add_argument("--cluster-name", type=str, default="default")
    parser.add_argument("--jinja-template-directory", type=str, default="default")
    # args.cluster_name = f"cluster_{args.shard}S_{args.replica}R"

    args = parser.parse_args()

    # values depend on keeper_mode
    if args.keeper_mode == "chkeeper":
        setattr(args, "keeper_prefix", "chkeeper")
        setattr(args, "keeper_port", 9181)
        setattr(args, "keeper_version", "24.8")
        setattr(args, "keeper_prometheus_port", 9363)
    elif args.keeper_mode == "zookeeper":
        setattr(args, "keeper_prefix", "zookeeper")
        setattr(args, "keeper_port", 2181)
        setattr(args, "keeper_version", "3.8")
        setattr(args, "keeper_prometheus_port", 7000)

    print(f"{args}")

    # create cluster
    c = Cluster(args)
    c.prepare()
    c.generate_obj()
    c.generate_docker_compose()
    c.generate_config()
