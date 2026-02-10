"""CLI entry point for MSA MultiCat converter."""

import sys
from pathlib import Path

import click

from msa_converter.builder import build_records
from msa_converter.config import DistributorConfig, load_config
from msa_converter.reader import read_input
from msa_converter.validator import validate_input, validate_output
from msa_converter.writer import write_msa


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output .msa file path. Defaults to <input_stem>.msa")
@click.option("-c", "--config", "config_path", default=None, type=click.Path(exists=True), help="Distributor config YAML file")
@click.option("--test/--live", default=True, help="Test or live submission (default: test)")
@click.option("--distributor-id", default=None, help="Override distributor ID from config")
def convert(input_file, output, config_path, test, distributor_id):
    """Convert a CSV/XLS tobacco sales file to MSA MultiCat format."""
    input_path = Path(input_file)

    # Load config
    if config_path:
        config = load_config(config_path)
    else:
        config = DistributorConfig()

    # Apply CLI overrides
    config.test_mode = test
    if distributor_id:
        config.distributor_id = distributor_id

    # Determine output path
    if output is None:
        output = input_path.with_suffix(".msa")

    # Read input
    click.echo(f"Reading {input_path}")
    df = read_input(input_path)
    click.echo(f"Loaded {len(df)} rows")

    # Validate input
    input_result = validate_input(df)
    input_result.report()
    if not input_result.is_valid:
        click.echo("Aborting due to input validation errors.", err=True)
        sys.exit(1)

    # Build records
    hid, bids, sids, purs, tot = build_records(df, config)
    click.echo(f"Built {len(bids)} BID, {len(sids)} SID, {len(purs)} PUR records")

    # Validate output
    output_result = validate_output(bids, sids, purs, tot)
    output_result.report()
    if not output_result.is_valid:
        click.echo("Aborting due to output validation errors.", err=True)
        sys.exit(1)

    # Write output
    write_msa(output, hid, bids, sids, purs, tot)
    click.echo(f"Wrote {output} ({1 + len(bids) + len(sids) + len(purs) + 1} lines)")


if __name__ == "__main__":
    convert()
