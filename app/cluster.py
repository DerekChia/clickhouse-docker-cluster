import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class Keeper:
    def __init__(
        self,
        hostname,
        version,
        server_id,
        cpu,
        memory,
        keeper_port,
        keeper_port_external,
        keeper_raft_port,
        keeper_raft_port_external,
        keeper_prometheus_port,
        keeper_prometheus_port_external,
        internal_replication,
        cluster_directory,
    ):
        self.hostname = hostname
        self.version = version
        self.server_id = server_id
        self.cpu = cpu
        self.memory = memory
        self.keeper_port = keeper_port
        self.keeper_port_external = keeper_port_external
        self.keeper_raft_port = keeper_raft_port
        self.keeper_raft_port_external = keeper_raft_port_external
        self.keeper_prometheus_port = keeper_prometheus_port
        self.keeper_prometheus_port_external = keeper_prometheus_port_external
        self.internal_replication = internal_replication
        self.config_directory = str(Path(cluster_directory) / "configs" / hostname)

    def __repr__(self):
        return str(self.__dict__)

    def prepare():
        return None


class Node:
    def __init__(
        self,
        hostname,
        version,
        shard_id,
        replica_id,
        cpu,
        memory,
        native_protocol_port,
        native_protocol_port_external,
        http_api_port,
        http_api_port_external,
        ch_prometheus_port,
        ch_prometheus_port_external,
        cluster_directory,
    ):
        self.hostname = hostname
        self.version = version
        self.shard_id = shard_id
        self.replica_id = replica_id
        self.cpu = cpu
        self.memory = memory
        self.native_protocol_port = native_protocol_port
        self.native_protocol_port_external = native_protocol_port_external
        self.http_api_port = http_api_port
        self.http_api_port_external = http_api_port_external
        self.ch_prometheus_port = ch_prometheus_port
        self.ch_prometheus_port_external = ch_prometheus_port_external
        self.config_directory = str(Path(cluster_directory) / "configs" / hostname)

    def __repr__(self):
        return str(self.__dict__)

    def prepare():
        return None


class Cluster:
    def __init__(self, args):
        self.args = args
        self._keepers = None
        self._chnodes = None

    def __repr__(self) -> str:
        name = ""
        for n in self._keepers + self._chnodes:
            name += str(n) + "\n"
        return name.strip()

    def generate_keeper_obj(self):
        keepers = []
        for count in range(1, self.args.keeper_count + 1):
            hostname = f"{self.args.keeper_prefix}{count}"
            version = self.args.keeper_version
            server_id = f"{count}"
            cpu = self.args.cpu_keeper
            memory = self.args.memory_keeper
            keeper_port = self.args.keeper_port
            keeper_port_external = self.args.keeper_port + count - 1 + 10_000
            keeper_raft_port = self.args.keeper_raft_port
            keeper_raft_port_external = self.args.keeper_raft_port + count - 1 + 10_000
            keeper_prometheus_port = self.args.keeper_prometheus_port
            keeper_prometheus_port_external = (
                self.args.keeper_prometheus_port + count - 1 + 10_000
            )
            internal_replication = self.args.keeper_internal_replication
            cluster_directory = self.args.cluster_directory
            k = Keeper(
                hostname,
                version,
                server_id,
                cpu,
                memory,
                keeper_port,
                keeper_port_external,
                keeper_raft_port,
                keeper_raft_port_external,
                keeper_prometheus_port,
                keeper_prometheus_port_external,
                internal_replication,
                cluster_directory,
            )
            keepers.append(k)
        return keepers

    def generate_chnode_obj(self):
        chnodes = []
        shard_replica_id = []
        for shard in range(1, self.args.shard + 1):
            for replica in range(1, self.args.replica + 1):
                shard_replica_id.append((shard, replica))

        for count in range(1, self.args.shard * self.args.replica + 1):
            hostname = f"{self.args.chnode_prefix}{count}"
            version = self.args.ch_version
            cpu = self.args.cpu
            memory = self.args.memory
            native_protocol_port = self.args.native_protocol_port
            native_protocol_port_external = (
                self.args.native_protocol_port + count - 1 + 20_000
            )
            http_api_port = self.args.http_api_port
            http_api_port_external = self.args.http_api_port + count - 1 + 20_000
            ch_prometheus_port = self.args.ch_prometheus_port
            ch_prometheus_port_external = (
                self.args.ch_prometheus_port + count - 1 + 20_000
            )
            cluster_directory = self.args.cluster_directory
            shard_id = shard_replica_id[count - 1][0]
            replica_id = shard_replica_id[count - 1][1]
            chnode = Node(
                hostname,
                version,
                shard_id,
                replica_id,
                cpu,
                memory,
                native_protocol_port,
                native_protocol_port_external,
                http_api_port,
                http_api_port_external,
                ch_prometheus_port,
                ch_prometheus_port_external,
                cluster_directory,
            )
            chnodes.append(chnode)
        return chnodes

    def _delete_cluster_directory(self):
        """Delete cluster directories"""
        path = Path(self.args.cluster_directory)
        if path.is_dir():
            shutil.rmtree(path)

    def _create_cluster_directory(self):
        """Create cluster directories"""
        Path(self.args.cluster_directory).mkdir(parents=True, exist_ok=True)
        Path(f"{self.args.cluster_directory}/configs").mkdir(
            parents=True, exist_ok=True
        )

    def prepare(self):
        """Delete and create cluster directory"""
        self._delete_cluster_directory()
        self._create_cluster_directory()

    def generate_obj(self):
        """Generate objects"""
        self._keepers = self.generate_keeper_obj()
        self._chnodes = self.generate_chnode_obj()

    def objs_to_context(self):
        return {
            "keeper_hostnames": [keeper.hostname for keeper in self._keepers],
            "keeper_versions": [keeper.version for keeper in self._keepers],
            "keeper_server_ids": [keeper.server_id for keeper in self._keepers],
            "keeper_cpus": [keeper.cpu for keeper in self._keepers],
            "keeper_memorys": [keeper.memory for keeper in self._keepers],
            "keeper_ports_external": [
                keeper.keeper_port_external for keeper in self._keepers
            ],
            "keeper_prometheus_ports_external": [
                keeper.keeper_prometheus_port_external for keeper in self._keepers
            ],
            "keeper_internal_replications": [
                keeper.internal_replication for keeper in self._keepers
            ],
            "keeper_config_directorys": [
                keeper.config_directory for keeper in self._keepers
            ],
            "node_hostnames": [chnode.hostname for chnode in self._chnodes],
            "node_versions": [chnode.version for chnode in self._chnodes],
            "node_shard_ids": [chnode.shard_id for chnode in self._chnodes],
            "node_replica_ids": [chnode.replica_id for chnode in self._chnodes],
            "node_cpus": [chnode.cpu for chnode in self._chnodes],
            "node_memorys": [chnode.memory for chnode in self._chnodes],
            "node_native_protocol_ports_external": [
                chnode.native_protocol_port_external for chnode in self._chnodes
            ],
            "node_http_api_ports_external": [
                chnode.http_api_port_external for chnode in self._chnodes
            ],
            "node_prometheus_ports_external": [
                chnode.ch_prometheus_port_external for chnode in self._chnodes
            ],
            "node_config_directorys": [
                chnode.config_directory for chnode in self._chnodes
            ],
        }

    def generate_docker_compose(self):
        """Generate docker compose file"""
        environment = Environment(
            loader=FileSystemLoader(f"{Path(__file__).parent}/templates/")
        )

        if self.args.shard == 0 or self.args.replica == 0:  # only keepers
            if self.args.keeper_mode == "chkeeper":
                template = environment.get_template(
                    "docker-compose-clickhousekeeper-only.yml.jinja"
                )
            elif self.args.keeper_mode == "zookeeper":
                template = environment.get_template(
                    "docker-compose-zookeeper-only.yml.jinja"
                )
        else:  # CH with keepers
            if self.args.keeper_mode == "chkeeper":
                template = environment.get_template(
                    "docker-compose-clickhousekeeper.yml.jinja"
                )
            elif self.args.keeper_mode == "zookeeper":
                template = environment.get_template(
                    "docker-compose-zookeeper.yml.jinja"
                )
            elif self.args.keeper_mode == "embedded": # todo
                template = environment.get_template(
                    "docker-compose-embedded-keeper.yml.jinja"
                )

        filename = f"{self.args.cluster_directory}/docker-compose.yml"
        context = self.objs_to_context()

        content = template.render(context)
        with open(filename, mode="w", encoding="utf-8") as f:
            f.write(content)

    def generate_config(self):
        environment = Environment(
            loader=FileSystemLoader(f"{Path(__file__).parent}/templates/configs/")
        )

        context = self.objs_to_context() # duplicated, to update - let's not generated twice
        keeper_hostnames = context["keeper_hostnames"]
        node_hostnames = context["node_hostnames"]
        all_hostnames = keeper_hostnames + node_hostnames

        if self.args.keeper_mode == "chkeeper":
            # [keeper+chnode] create configs directory using hostname
            for hostname in all_hostnames:
                Path(f"{self.args.cluster_directory}/configs/{hostname}").mkdir(
                    parents=True, exist_ok=True
                )

            # [keeper+chnode] create prometheus directory
            Path(f"{self.args.cluster_directory}/configs/prometheus").mkdir(
                parents=True, exist_ok=True
            )

            # [keeper+chnode] create grafana directory
            Path(f"{self.args.cluster_directory}/configs/grafana").mkdir(
                parents=True, exist_ok=True
            )
            Path(f"{self.args.cluster_directory}/configs/grafana/dashboards").mkdir(
                parents=True, exist_ok=True
            )

            # [chnode] others.xml
            filename = f"{Path(__file__).parent}/templates/configs/others.xml"
            for hostname in node_hostnames:
                filename_generated = (
                    f"{self.args.cluster_directory}/configs/{hostname}/others.xml"
                )
                shutil.copyfile(filename, filename_generated)

            # [keeper] keeper_config.xml
            template = environment.get_template("keeper_config.xml.jinja")

            for count, keeper_hostname in enumerate(keeper_hostnames):
                filename_generated = f"{self.args.cluster_directory}/configs/{keeper_hostname}/keeper_config.xml"
                content = template.render(
                    context,
                    keeper_server_id=context["keeper_server_ids"][count],
                    keeper_port=self.args.keeper_port,  # static port
                    keeper_raft_port=self.args.keeper_raft_port,  # static port
                )
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [chnode] keeper_use.xml
            template = environment.get_template("keeper_use.xml.jinja")

            for node_hostname in node_hostnames:
                filename_generated = f"{self.args.cluster_directory}/configs/{node_hostname}/keeper_use.xml"
                content = template.render(
                    context,
                    keeper_count=len(context["keeper_hostnames"]),
                    keeper_port=self.args.keeper_port,  # static port
                )
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [chnode] macros.xml
            template = environment.get_template("macros.xml.jinja")

            for count, node_hostname in enumerate(node_hostnames):
                shard = context["node_shard_ids"][count]
                replica = context["node_replica_ids"][count]

                filename_generated = (
                    f"{self.args.cluster_directory}/configs/{node_hostname}/macros.xml"
                )
                content = template.render(
                    cluster_name=self.args.cluster_name, shard=shard, replica=replica
                )
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [chnode] remote_servers.xml
            template = environment.get_template("remote_servers.xml.jinja")

            for count, node_hostname in enumerate(node_hostnames):
                filename_generated = f"{self.args.cluster_directory}/configs/{node_hostname}/remote_servers.xml"
                content = template.render(
                    hostnames=node_hostnames,
                    cluster_name=self.args.cluster_name,
                    internal_replication=self.args.keeper_internal_replication,
                    num_shard=len(set(context["node_shard_ids"])),
                    num_replica=len(set(context["node_replica_ids"])),
                )
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [chnode] prometheus.xml
            template = environment.get_template("prometheus_enable.xml.jinja")

            for count, node_hostname in enumerate(node_hostnames):
                filename_generated = f"{self.args.cluster_directory}/configs/{node_hostname}/prometheus_enable.xml"
                content = template.render()
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [prometheus] prometheus.yml
            template = environment.get_template(
                "prometheus/prometheus_config.yml.jinja"
            )

            content = template.render(
                node_hostnames=node_hostnames,
                keeper_hostnames=keeper_hostnames,
                ch_prometheus_port=self.args.ch_prometheus_port,
                keeper_prometheus_port=self.args.keeper_prometheus_port,
            )
            filename_generated = f"{self.args.cluster_directory}/configs/prometheus/prometheus_config.yml"

            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

            # [grafana - chnode] dashboard.yml
            template_filename = f"{Path(__file__).parent}/templates/configs/grafana/clickhouse-dashboard.yml"
            generated_filename = f"{self.args.cluster_directory}/configs/grafana/clickhouse-dashboard.yml"
            shutil.copyfile(template_filename, generated_filename)

            # [grafana - chnode] datasource.yml
            template = environment.get_template(
                "grafana/clickhouse-datasource.yml.jinja"
            )

            content = template.render(hostnames=node_hostnames)
            filename_generated = f"{self.args.cluster_directory}/configs/grafana/clickhouse-datasource.yml"

            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

            # [grafana - chnode] dashboards/{cluster-analysis,data-analysis,query-analysis}-{HOSTNAME}.json
            template = environment.get_template(
                "grafana/dashboards/cluster-analysis-.json.jinja"
            )
            for hostname in node_hostnames:
                content = template.render(hostname=hostname)
                filename_generated = f"{self.args.cluster_directory}/configs/grafana/dashboards/cluster-analysis-{hostname}.json"
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            template = environment.get_template(
                "grafana/dashboards/data-analysis-.json.jinja"
            )
            for hostname in node_hostnames:
                content = template.render(hostname=hostname)
                filename_generated = f"{self.args.cluster_directory}/configs/grafana/dashboards/data-analysis-{hostname}.json"
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            template = environment.get_template(
                "grafana/dashboards/query-analysis-.json.jinja"
            )
            for hostname in node_hostnames:
                content = template.render(hostname=hostname)
                filename_generated = f"{self.args.cluster_directory}/configs/grafana/dashboards/query-analysis-{hostname}.json"
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [prometheus-dashboard]
            shutil.copyfile(
                f"{Path(__file__).parent}/templates/configs/grafana/dashboards/prometheus-dashboard.json",
                f"{self.args.cluster_directory}/configs/grafana/dashboards/prometheus-dashboard.json",
            )

        elif self.args.keeper_mode == "zookeeper":
            # [chnode] create configs directory using hostname
            for hostname in node_hostnames:
                Path(f"{self.args.cluster_directory}/configs/{hostname}").mkdir(
                    parents=True, exist_ok=True
                )

            # [keeper+chnode] create prometheus directory
            Path(f"{self.args.cluster_directory}/configs/prometheus").mkdir(
                parents=True, exist_ok=True
            )

            # [keeper+chnode] create grafana directory
            Path(f"{self.args.cluster_directory}/configs/grafana").mkdir(
                parents=True, exist_ok=True
            )
            Path(f"{self.args.cluster_directory}/configs/grafana/dashboards").mkdir(
                parents=True, exist_ok=True
            )

            # [chnode] others.xml
            filename = f"{Path(__file__).parent}/templates/configs/others.xml"
            for hostname in node_hostnames:
                filename_generated = (
                    f"{self.args.cluster_directory}/configs/{hostname}/others.xml"
                )
                shutil.copyfile(filename, filename_generated)

            # # [keeper] keeper_config.xml
            # template = environment.get_template("keeper_config.xml.jinja")

            # for count, keeper_hostname in enumerate(keeper_hostnames):
            #     filename_generated = f"{self.args.cluster_directory}/configs/{keeper_hostname}/keeper_config.xml"
            #     content = template.render(
            #         context,
            #         keeper_server_id=context["keeper_server_ids"][count],
            #         keeper_port=self.args.keeper_port,  # static port
            #         keeper_raft_port=self.args.keeper_raft_port,  # static port
            #     )
            #     with open(filename_generated, mode="w", encoding="utf-8") as f:
            #         f.write(content)

            # [chnode] keeper_use.xml
            template = environment.get_template("keeper_use.xml.jinja")

            for node_hostname in node_hostnames:
                filename_generated = f"{self.args.cluster_directory}/configs/{node_hostname}/keeper_use.xml"
                content = template.render(
                    context,
                    keeper_count=len(context["keeper_hostnames"]),
                    keeper_port=self.args.keeper_port,  # static port
                )
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [chnode] macros.xml
            template = environment.get_template("macros.xml.jinja")

            for count, node_hostname in enumerate(node_hostnames):
                shard = context["node_shard_ids"][count]
                replica = context["node_replica_ids"][count]

                filename_generated = (
                    f"{self.args.cluster_directory}/configs/{node_hostname}/macros.xml"
                )
                content = template.render(
                    cluster_name=self.args.cluster_name, shard=shard, replica=replica
                )
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [chnode] remote_servers.xml
            template = environment.get_template("remote_servers.xml.jinja")

            for count, node_hostname in enumerate(node_hostnames):
                filename_generated = f"{self.args.cluster_directory}/configs/{node_hostname}/remote_servers.xml"
                content = template.render(
                    hostnames=node_hostnames,
                    cluster_name=self.args.cluster_name,
                    internal_replication=self.args.keeper_internal_replication,
                    num_shard=len(set(context["node_shard_ids"])),
                    num_replica=len(set(context["node_replica_ids"])),
                )
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [chnode] prometheus.xml
            template = environment.get_template("prometheus_enable.xml.jinja")

            for count, node_hostname in enumerate(node_hostnames):
                filename_generated = f"{self.args.cluster_directory}/configs/{node_hostname}/prometheus_enable.xml"
                content = template.render()
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [prometheus] prometheus.yml
            template = environment.get_template(
                "prometheus/prometheus_config.yml.jinja"
            )

            content = template.render(
                node_hostnames=node_hostnames,
                keeper_hostnames=keeper_hostnames,
                ch_prometheus_port=self.args.ch_prometheus_port,
                keeper_prometheus_port=self.args.keeper_prometheus_port,
            )
            filename_generated = f"{self.args.cluster_directory}/configs/prometheus/prometheus_config.yml"

            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

            # [grafana - chnode] dashboard.yml
            template_filename = f"{Path(__file__).parent}/templates/configs/grafana/clickhouse-dashboard.yml"
            generated_filename = f"{self.args.cluster_directory}/configs/grafana/clickhouse-dashboard.yml"
            shutil.copyfile(template_filename, generated_filename)

            # [grafana - chnode] datasource.yml
            template = environment.get_template(
                "grafana/clickhouse-datasource.yml.jinja"
            )

            content = template.render(hostnames=node_hostnames)
            filename_generated = f"{self.args.cluster_directory}/configs/grafana/clickhouse-datasource.yml"

            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

            # [grafana - chnode] dashboards/{cluster-analysis,data-analysis,query-analysis}-{HOSTNAME}.json
            template = environment.get_template(
                "grafana/dashboards/cluster-analysis-.json.jinja"
            )
            for hostname in node_hostnames:
                content = template.render(hostname=hostname)
                filename_generated = f"{self.args.cluster_directory}/configs/grafana/dashboards/cluster-analysis-{hostname}.json"
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            template = environment.get_template(
                "grafana/dashboards/data-analysis-.json.jinja"
            )
            for hostname in node_hostnames:
                content = template.render(hostname=hostname)
                filename_generated = f"{self.args.cluster_directory}/configs/grafana/dashboards/data-analysis-{hostname}.json"
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            template = environment.get_template(
                "grafana/dashboards/query-analysis-.json.jinja"
            )
            for hostname in node_hostnames:
                content = template.render(hostname=hostname)
                filename_generated = f"{self.args.cluster_directory}/configs/grafana/dashboards/query-analysis-{hostname}.json"
                with open(filename_generated, mode="w", encoding="utf-8") as f:
                    f.write(content)

            # [prometheus-dashboard]
            shutil.copyfile(
                f"{Path(__file__).parent}/templates/configs/grafana/dashboards/prometheus-dashboard.json",
                f"{self.args.cluster_directory}/configs/grafana/dashboards/prometheus-dashboard.json",
            )
