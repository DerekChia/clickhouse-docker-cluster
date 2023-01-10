import shutil
import argparse
from pprint import pprint
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# internal_replication = True


def _generate_embedded_keeper_context(args):
    context = {
        "keeper_hostnames": [],
        "node_hostnames": [],
        "keeper_server_ids": [],
        "shards": [],
        "replicas": [],
        "native_protocol_ports": [],
        "http_api_ports": [],
        "keeper_ports": [],
        "keeper_raft_ports": [],
    }

    # chkeeper
    keeper_port = args.keeper_port
    keeper_raft_port = args.keeper_raft_port

    for count in range(1, args.keeper_count + 1):
        context["keeper_hostnames"].append(
            f"{args.chnode_prefix}_with_{args.chkeeper_prefix}{count}"
        )
        context["keeper_server_ids"].append(f"{count}")
        context["keeper_ports"].append(f"{keeper_port}")
        context["keeper_raft_ports"].append(f"{keeper_raft_port}")
        keeper_port += 1
        keeper_raft_port += 1

    # chnode
    for count in range(args.keeper_count + 1, args.shard * args.replica + 1):
        context["node_hostnames"].append(f"{args.chnode_prefix}{count}")

    # all
    native_protocol_port = args.native_protocol_port
    http_api_port = args.http_api_port

    for shard in range(1, args.shard + 1):
        for replica in range(1, args.replica + 1):
            context["shards"].append(f"{shard}")
            context["replicas"].append(f"{replica}")
            context["native_protocol_ports"].append(f"{native_protocol_port}")
            context["http_api_ports"].append(f"{http_api_port}")
            native_protocol_port += 1
            http_api_port += 1

    return context


def _generate_standalone_keeper_context(args):
    context = {
        "keeper_hostnames": [],
        "node_hostnames": [],
        "keeper_server_ids": [],
        "shards": [],
        "replicas": [],
        "native_protocol_ports": [],
        "http_api_ports": [],
        "keeper_ports": [],
        "keeper_raft_ports": [],
    }

    # chkeeper
    keeper_port = args.keeper_port
    keeper_raft_port = args.keeper_raft_port

    for count in range(1, args.keeper_count + 1):
        context["keeper_hostnames"].append(f"{args.chkeeper_prefix}{count}")
        context["keeper_server_ids"].append(f"{count}")
        context["keeper_ports"].append(f"{keeper_port}")
        context["keeper_raft_ports"].append(f"{keeper_raft_port}")
        keeper_port += 1
        keeper_raft_port += 1

    # chnode
    for count in range(1, args.shard * args.replica + 1):
        context["node_hostnames"].append(f"{args.chnode_prefix}{count}")

    # all
    native_protocol_port = args.native_protocol_port
    http_api_port = args.http_api_port

    for shard in range(1, args.shard + 1):
        for replica in range(1, args.replica + 1):
            context["shards"].append(f"{shard}")
            context["replicas"].append(f"{replica}")
            context["native_protocol_ports"].append(f"{native_protocol_port}")
            context["http_api_ports"].append(f"{http_api_port}")
            native_protocol_port += 1
            http_api_port += 1

    return context


def _generate_zookeeper_context(args):
    raise NotImplementedError


def generate_context(args):
    """Generate context"""
    if args.keeper_mode == "embedded":
        context = _generate_embedded_keeper_context(args)
        pprint(context)
        return context
    elif args.keeper_mode == "standalone":
        context = _generate_standalone_keeper_context(args)
        pprint(context)
        return context
    elif args.keeper_mode == "zookeeper":
        return None
    else:
        raise ValueError("Valid keeper_mode: embedded, standalone, zookeeper")


def _delete_cluster_generated(cluster_root_dir):
    """Delete cluster directories"""
    path = Path(cluster_root_dir)
    if path.is_dir():
        shutil.rmtree(path)


def create_cluster_generated(cluster_root_dir):
    """Create cluster directories"""
    _delete_cluster_generated(cluster_root_dir)
    Path(cluster_root_dir).mkdir(parents=True, exist_ok=True)
    Path(f"{cluster_root_dir}/configs").mkdir(parents=True, exist_ok=True)


def generate_docker_compose(args, context):
    """Generate docker-compose.yml file for cluster"""
    environment = Environment(loader=FileSystemLoader("templates/"))

    # select docker-compose template
    if args.keeper_mode == "embedded":
        template = environment.get_template("docker-compose-embedded-keeper.txt")

    elif args.keeper_mode == "standalone":
        template = environment.get_template("docker-compose-standalone-keeper.txt")

    elif args.keeper_mode == "zookeeper":
        raise NotImplementedError
        template = environment.get_template("docker-compose-zookeeper.txt")

    # create docker-compose.yml
    filename = f"{args.directory}/docker-compose.yml"
    content = template.render(
        context,
        version=args.version,
        cpus=args.cpus,
        mem_limit=args.mem_limit,
        keeper_count=args.keeper_count,
    )
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(content)


def generate_config(args, context):
    """Generate config folder for each node in cluster"""
    environment = Environment(loader=FileSystemLoader(f"templates/configs/"))

    if args.keeper_mode == "embedded":
        all_hostnames = context["keeper_hostnames"] + context["node_hostnames"]

        # [all] create configs directory
        for hostname in all_hostnames:
            Path(f"{args.directory}/configs/{hostname}").mkdir(
                parents=True, exist_ok=True
            )

        # [all] docker_related_config.xml
        filename = f"templates/configs/docker_related_config.xml"
        for hostname in all_hostnames:
            filename_generated = (
                f"{args.directory}/configs/{hostname}/docker_related_config.xml"
            )
            shutil.copyfile(filename, filename_generated)

        # [chnode_with_keeper only] keeper_enable.xml
        template = environment.get_template("keeper_enable.txt")

        for count in range(args.keeper_count):
            keeper_hostname = context["keeper_hostnames"][count]

            filename_generated = (
                f"{args.directory}/configs/{keeper_hostname}/keeper_enable.xml"
            )
            content = template.render(
                context,
                keeper_server_id=count + 1,
                keeper_count=args.keeper_count,
                keeper_raft_port=args.keeper_raft_port,  # static port
            )
            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

        # [all] keeper_use.xml
        template = environment.get_template("keeper_use.txt")

        for hostname in all_hostnames:
            filename_generated = f"{args.directory}/configs/{hostname}/keeper_use.xml"
            content = template.render(context, keeper_count=args.keeper_count)
            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

        # [all] macros.xml
        template = environment.get_template("macros.txt")

        for count, hostname in enumerate(all_hostnames):
            shard = context["shards"][count]
            replica = context["replicas"][count]

            filename_generated = f"{args.directory}/configs/{hostname}/macros.xml"
            content = template.render(
                cluster_name=args.cluster_name, shard=shard, replica=replica
            )
            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

        # [all] remote_servers.xml
        template = environment.get_template("remote_servers.txt")

        for count, hostname in enumerate(all_hostnames):
            filename_generated = (
                f"{args.directory}/configs/{hostname}/remote_servers.xml"
            )
            content = template.render(
                hostnames=all_hostnames,
                cluster_name=args.cluster_name,
                internal_replication=args.internal_replication,
                num_shard=args.shard,
                num_replica=args.replica,
            )
            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

        # [all] prometheus.xml
        template = environment.get_template("prometheus.txt")

        for count, hostname in enumerate(all_hostnames):
            filename_generated = f"{args.directory}/configs/{hostname}/prometheus.xml"
            content = template.render(
                hostnames=all_hostnames,
                cluster_name=args.cluster_name,
                internal_replication=args.internal_replication,
                num_shard=args.shard,
                num_replica=args.replica,
            )
            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

    elif args.keeper_mode == "standalone":
        raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # version
    parser.add_argument(
        "--version",
        type=float,
        default=22.12,
        required=True,
        help="ClickHouse version",
    )

    # shard
    parser.add_argument(
        "--shard", type=int, default=1, required=True, help="Number of shard"
    )

    # replica
    parser.add_argument(
        "--replica",
        type=int,
        default=1,
        required=True,
        help="Number of replica",
    )

    ## keeper
    # keeper_mode
    parser.add_argument(
        "--keeper-mode",
        type=str,
        default="embedded",  # standalone
        help="Standalone or emebdded keeper",
    )
    # num_keepers
    parser.add_argument(
        "--keeper-count",
        type=int,
        default=3,
        required=True,
        help="Number of Keepers (Min. 3)",
    )

    # cpus
    parser.add_argument("--cpus", type=int, default=1, help="CPUs for each node")

    # mem_limit
    parser.add_argument(
        "--mem-limit", type=str, default="8192m", help="RAM (mb) for each node"
    )

    # root directory for config
    parser.add_argument("--directory", type=str, default="cluster")

    # ports
    parser.add_argument("--native-protocol-port", type=int, default=9000)
    parser.add_argument("--http-api-port", type=int, default=8123)
    parser.add_argument("--keeper-port", type=int, default=9181)
    parser.add_argument("--keeper-raft-port", type=int, default=9234)
    parser.add_argument("--prometheus-port", type=int, default=9363)

    # internal_replication
    parser.add_argument("--internal-replication", type=str, default="true")

    # node_prefix
    parser.add_argument("--chnode-prefix", type=str, default="chnode")

    # chkeeper_prefix
    parser.add_argument("--chkeeper-prefix", type=str, default="chkeeper")

    # zookeeper_prefix
    parser.add_argument("--zookeeper-prefix", type=str, default="zookeeper")

    args = parser.parse_args()

    # cluster_name
    args.cluster_name = f"cluster_{args.shard}S_{args.replica}R"

    print(f"{args}")

    context = generate_context(args)

    create_cluster_generated(args.directory)

    generate_docker_compose(args, context)

    generate_config(args, context)
