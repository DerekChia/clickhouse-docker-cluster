from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import shutil

version = "22.12"
shards = 1
replicas = 5
num_keepers = 3
cluster_name = f"cluster_{shards}S_{replicas}R"
context = {
    "hostnames": [],
    "server_ids": [],
    "shards": [],
    "replicas": [],
    "port_ones": [],
    "port_twos": [],
    "port_threes": [],
}
internal_replication = True
port_one = 9001
port_two = 8123
port_three = 9181

node_count = 0
for shard in range(1, shards + 1):
    for replica in range(1, replicas + 1):
        node_count += 1
        context["hostnames"].append(f"chnode{node_count}")
        context["server_ids"].append(f"{node_count}")
        context["shards"].append(f"{shard}")
        context["replicas"].append(f"{replica}")
        context["port_ones"].append(f"{port_one}")
        context["port_twos"].append(f"{port_two}")
        context["port_threes"].append(f"{port_three}")
        port_one += 1
        port_two += 1
        port_three += 1

print(context)
print(cluster_name)


def delete_cluster_generated(cluster_generated_name):
    path = Path(cluster_generated_name)
    if path.is_dir():
        shutil.rmtree(path)


def create_cluster_generated(cluster_generated_name):
    Path(cluster_generated_name).mkdir(parents=True, exist_ok=True)
    Path(f"{cluster_generated_name}/configs").mkdir(parents=True, exist_ok=True)


def generate_docker_compose():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("docker-compose.txt")

    filename = f"cluster-generated/docker-compose.yml"
    content = template.render(context, version=version)
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(content)


def generate_config(context):
    environment = Environment(loader=FileSystemLoader(f"templates/configs/"))

    # create configs directory
    for hostname in context["hostnames"]:
        Path(f"cluster-generated/configs/{hostname}").mkdir(parents=True, exist_ok=True)

    # docker_related_config.xml
    filename = f"templates/configs/docker_related_config.xml"
    for hostname in context["hostnames"]:
        filename_generated = (
            f"cluster-generated/configs/{hostname}/docker_related_config.xml"
        )
        shutil.copyfile(filename, filename_generated)

    # keeper_enable.xml
    template = environment.get_template("keeper_enable.txt")

    for count in range(len(context["hostnames"])):
        if count < num_keepers:
            hostname = context["hostnames"][count]
            server_id = context["server_ids"][count]

            filename_generated = (
                f"cluster-generated/configs/{hostname}/keeper_enable.xml"
            )
            content = template.render(
                context, server_id=server_id, num_keepers=num_keepers
            )
            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

    # keeper_use.xml
    template = environment.get_template("keeper_use.txt")

    for count in range(len(context["hostnames"])):
        hostname = context["hostnames"][count]
        server_id = context["server_ids"][count]

        filename_generated = f"cluster-generated/configs/{hostname}/keeper_use.xml"
        content = template.render(context, num_keepers=num_keepers)
        with open(filename_generated, mode="w", encoding="utf-8") as f:
            f.write(content)

    # macros.xml
    template = environment.get_template("macros.txt")

    for count in range(len(context["hostnames"])):
        hostname = context["hostnames"][count]
        shard = context["shards"][count]
        replica = context["replicas"][count]

        filename_generated = f"cluster-generated/configs/{hostname}/macros.xml"
        content = template.render(
            cluster_name=cluster_name, shard=shard, replica=replica
        )
        with open(filename_generated, mode="w", encoding="utf-8") as f:
            f.write(content)

    # remote_servers.xml
    template = environment.get_template("remote_servers.txt")

    for count in range(len(context["hostnames"])):
        hostname = context["hostnames"][count]
        shard = context["shards"][count]
        replica = context["replicas"][count]

        filename_generated = f"cluster-generated/configs/{hostname}/remote_servers.xml"
        content = template.render(
            context,
            cluster_name=cluster_name,
            internal_replication=internal_replication,
            num_shard=shards,
            num_replica=replicas,
        )
        with open(filename_generated, mode="w", encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    delete_cluster_generated("cluster-generated")
    create_cluster_generated("cluster-generated")
    generate_docker_compose()
    generate_config(context)
