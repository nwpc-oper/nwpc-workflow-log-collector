import json
import datetime

import click

from nwpc_workflow_log_collector.util import get_record_class, get_collector_module
from nwpc_workflow_log_collector._config import load_config
from nwpc_workflow_log_collector.log_info import get_log_info_from_local_file


@click.group()
def cli():
    pass


@cli.command("info")
@click.option("-c", "--config", help="config file path")
@click.option("-o", "--owner", help="owner name")
@click.option("-r", "--repo", help="repo name")
@click.option(
    "-t",
    "--workflow-type",
    "workflow_type",
    help="workflow type",
    required=True,
    type=click.Choice(["sms", "ecflow"]),
)
@click.option("-l", "--log-file", help="log file path")
@click.option(
    "--output-type",
    type=click.Choice(["print", "json"]),
    default="json",
    help="output type",
)
def info(config, owner, repo, workflow_type, log_file, output_type):
    """
    Print information of workflow log files, including:
        - file path
        - line count
        - time range
    """
    config_object = load_config(config)
    record_class = get_record_class(workflow_type)
    log_info = get_log_info_from_local_file(log_file, record_class)
    result = {
        "app": "ecflow_local_log_collector",
        "timestamp": datetime.datetime.now().timestamp(),
        "data": {"log_info": log_info},
    }
    click.echo(json.dumps(result, indent=2))


@cli.command("load")
@click.option("-c", "--config", help="config file path")
@click.option("-o", "--owner", help="owner name")
@click.option("-r", "--repo", help="repo name")
@click.option(
    "-t",
    "--workflow-type",
    "workflow_type",
    help="workflow type",
    required=True,
    type=click.Choice(["sms", "ecflow"]),
)
@click.option("-l", "--log-file", help="log file path")
@click.option("-v", "--verbose", count=True, help="verbose level")
def load(config, owner, repo, workflow_type, log_file, verbose):
    config_object = load_config(config)
    collector_module = get_collector_module(workflow_type)
    collector_module.collect_log_from_local_file(
        config_object, owner, repo, log_file, verbose
    )


@cli.command("load_range")
@click.option("-c", "--config", help="config file path")
@click.option("-o", "--owner", help="owner name")
@click.option("-r", "--repo", help="repo name")
@click.option(
    "-t",
    "--workflow-type",
    "workflow_type",
    help="workflow type",
    required=True,
    type=click.Choice(["sms", "ecflow"]),
)
@click.option("-l", "--log-file", help="log file path")
@click.option("--start-date", default=None, help="begin date, date range: [start_date, stop_date), YYYY-MM-dd")
@click.option("--stop-date", default=None, help="end date, date range: [start_date, stop_date), YYYY-MM-dd")
@click.option("-v", "--verbose", count=True, help="verbose level")
def load_range(
    config, owner, repo, workflow_type, log_file, start_date, stop_date, verbose
):
    config_object = load_config(config)
    collector_module = get_collector_module(workflow_type)
    collector_module.collect_log_from_local_file_by_range(
        config_object, owner, repo, log_file, start_date, stop_date, verbose
    )


if __name__ == "__main__":
    cli()
