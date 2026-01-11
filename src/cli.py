"""CLI interface for SPU Processing Tool.

Usage:
    spu-tool generate --input INPUT.xlsx --template TEMPLATE.xlsx [--output OUTPUT.xlsx]
    spu-tool validate --input INPUT.xlsx
    spu-tool batch --input-dir INPUT/ --template TEMPLATE.xlsx [--output-dir OUTPUT/]
    spu-tool gui
    spu-tool config --show-rru-types
"""

import os
import sys
import glob
import json
import click
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.excel_handler import ExcelHandler
from src.processor import SPUProcessor
from src.utils import get_config_path, get_input_folder, get_template_folder, get_output_folder, ensure_output_folder
from src.logger import setup_logger, get_logger
from src.validator import CDDValidator


@click.group()
@click.version_option(version="2.0.0", prog_name="spu-tool")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """SPU Processing Tool - Generate SPU configurations from CDD Excel files.

    This tool processes Cell Design Document (CDD) Excel files and generates
    SPU planning configurations based on templates and config.json mappings.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    setup_logger(verbose=verbose)


@cli.command()
@click.option('--input', '-i', 'input_file', required=True, type=click.Path(exists=True),
              help='Path to CDD input Excel file')
@click.option('--template', '-t', 'template_file', required=True, type=click.Path(exists=True),
              help='Path to SPU template Excel file')
@click.option('--output', '-o', 'output_file', type=click.Path(),
              help='Path for output file (default: auto-generated in Output folder)')
@click.option('--version', 'config_version', default='V1.70.26',
              help='Config version to use (default: V1.70.26)')
@click.option('--validate/--no-validate', default=True,
              help='Validate input data before processing (default: True)')
@click.pass_context
def generate(ctx, input_file, template_file, output_file, config_version, validate):
    """Generate SPU configuration from CDD input file.

    Example:
        spu-tool generate -i Input/cdd.xlsx -t Template/template.xlsx
    """
    logger = get_logger()
    logger.info(f"Starting SPU generation")
    logger.info(f"Input: {input_file}")
    logger.info(f"Template: {template_file}")

    try:
        # Initialize handlers
        excel_handler = ExcelHandler()
        processor = SPUProcessor()
        processor.version = config_version

        # Read input file
        click.echo(f"Reading input file: {input_file}")
        data = excel_handler.read_input_file(input_file)
        logger.info(f"Loaded {len(data)} sheets from input file")

        # Show loaded sheets
        for sheet_name, df in data.items():
            if not df.empty:
                click.echo(f"  - {sheet_name}: {len(df)} rows")
                logger.debug(f"Sheet {sheet_name}: {len(df)} rows, columns: {list(df.columns)}")

        # Validate input data if requested
        if validate:
            click.echo("\nValidating input data...")
            validator = CDDValidator(data, get_config_path())
            errors, warnings = validator.validate()

            if warnings:
                click.echo(click.style(f"\nWarnings ({len(warnings)}):", fg='yellow'))
                for warning in warnings[:10]:  # Show first 10 warnings
                    click.echo(f"  - {warning}")
                if len(warnings) > 10:
                    click.echo(f"  ... and {len(warnings) - 10} more warnings")

            if errors:
                click.echo(click.style(f"\nErrors ({len(errors)}):", fg='red'))
                for error in errors[:10]:  # Show first 10 errors
                    click.echo(f"  - {error}")
                if len(errors) > 10:
                    click.echo(f"  ... and {len(errors) - 10} more errors")

                if not click.confirm('\nContinue despite errors?'):
                    raise click.Abort()
            else:
                click.echo(click.style("  Validation passed!", fg='green'))

        # Set input data and template
        processor.set_input_data(data)
        processor.set_template(template_file)

        # Process
        click.echo(f"\nProcessing with config version: {config_version}")

        def progress_callback(message, percentage):
            if ctx.obj['verbose']:
                click.echo(f"  [{percentage}%] {message}")

        output_files = processor.process(progress_callback)

        # Show results
        click.echo(click.style("\nGeneration complete!", fg='green'))
        click.echo("Output files:")
        for f in output_files:
            click.echo(f"  - {f}")
            logger.info(f"Generated: {f}")

    except click.Abort:
        logger.warning("Generation aborted by user")
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', 'input_file', required=True, type=click.Path(exists=True),
              help='Path to CDD input Excel file')
@click.option('--strict', is_flag=True, help='Treat warnings as errors')
@click.pass_context
def validate(ctx, input_file, strict):
    """Validate CDD input file without generating output.

    Example:
        spu-tool validate -i Input/cdd.xlsx
    """
    logger = get_logger()
    logger.info(f"Validating: {input_file}")

    try:
        # Read input file
        excel_handler = ExcelHandler()
        click.echo(f"Reading: {input_file}")
        data = excel_handler.read_input_file(input_file)

        # Validate
        click.echo("Validating...")
        validator = CDDValidator(data, get_config_path())
        errors, warnings = validator.validate()

        # Report results
        click.echo(f"\n{'='*60}")
        click.echo(f"Validation Results for: {os.path.basename(input_file)}")
        click.echo(f"{'='*60}")

        # Summary
        click.echo(f"\nSheets loaded:")
        for sheet_name, df in data.items():
            if not df.empty:
                click.echo(f"  - {sheet_name}: {len(df)} rows")

        # Warnings
        if warnings:
            click.echo(click.style(f"\nWarnings ({len(warnings)}):", fg='yellow'))
            for warning in warnings:
                click.echo(f"  - {warning}")

        # Errors
        if errors:
            click.echo(click.style(f"\nErrors ({len(errors)}):", fg='red'))
            for error in errors:
                click.echo(f"  - {error}")

        # Final status
        if errors or (strict and warnings):
            click.echo(click.style("\nValidation FAILED", fg='red', bold=True))
            sys.exit(1)
        elif warnings:
            click.echo(click.style("\nValidation PASSED with warnings", fg='yellow', bold=True))
        else:
            click.echo(click.style("\nValidation PASSED", fg='green', bold=True))

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.option('--input-dir', '-i', 'input_dir', required=True, type=click.Path(exists=True),
              help='Directory containing CDD input files')
@click.option('--template', '-t', 'template_file', required=True, type=click.Path(exists=True),
              help='Path to SPU template Excel file')
@click.option('--output-dir', '-o', 'output_dir', type=click.Path(),
              help='Directory for output files (default: Output folder)')
@click.option('--pattern', '-p', default='*.xlsx', help='File pattern to match (default: *.xlsx)')
@click.option('--version', 'config_version', default='V1.70.26',
              help='Config version to use (default: V1.70.26)')
@click.pass_context
def batch(ctx, input_dir, template_file, output_dir, pattern, config_version):
    """Process multiple CDD files in batch.

    Example:
        spu-tool batch -i Input/ -t Template/template.xlsx
    """
    logger = get_logger()
    logger.info(f"Batch processing: {input_dir}")

    try:
        # Find input files
        input_pattern = os.path.join(input_dir, pattern)
        input_files = glob.glob(input_pattern)

        # Exclude temp files
        input_files = [f for f in input_files if not os.path.basename(f).startswith('~$')]
        input_files = [f for f in input_files if not os.path.basename(f).startswith('.~')]

        if not input_files:
            click.echo(click.style(f"No files matching '{pattern}' found in {input_dir}", fg='yellow'))
            return

        click.echo(f"Found {len(input_files)} input file(s)")
        for f in input_files:
            click.echo(f"  - {os.path.basename(f)}")

        # Set output directory
        if output_dir is None:
            output_dir = ensure_output_folder()
        else:
            os.makedirs(output_dir, exist_ok=True)

        # Process each file
        success_count = 0
        error_count = 0
        results = []

        click.echo(f"\nProcessing...")
        with click.progressbar(input_files, label='Processing files') as files:
            for input_file in files:
                try:
                    excel_handler = ExcelHandler()
                    processor = SPUProcessor()
                    processor.version = config_version

                    data = excel_handler.read_input_file(input_file)
                    processor.set_input_data(data)
                    processor.set_template(template_file)

                    output_files = processor.process()

                    success_count += 1
                    results.append({
                        'input': os.path.basename(input_file),
                        'status': 'success',
                        'outputs': [os.path.basename(f) for f in output_files]
                    })
                    logger.info(f"Processed: {input_file}")

                except Exception as e:
                    error_count += 1
                    results.append({
                        'input': os.path.basename(input_file),
                        'status': 'error',
                        'error': str(e)
                    })
                    logger.error(f"Failed to process {input_file}: {e}")

        # Show results
        click.echo(f"\n{'='*60}")
        click.echo("Batch Processing Results")
        click.echo(f"{'='*60}")
        click.echo(f"Total: {len(input_files)}, Success: {success_count}, Errors: {error_count}")

        if error_count > 0:
            click.echo(click.style("\nFailed files:", fg='red'))
            for r in results:
                if r['status'] == 'error':
                    click.echo(f"  - {r['input']}: {r['error']}")

        if success_count > 0:
            click.echo(click.style("\nGenerated files:", fg='green'))
            for r in results:
                if r['status'] == 'success':
                    for output in r['outputs']:
                        click.echo(f"  - {output}")

    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
def gui():
    """Launch the graphical user interface.

    Example:
        spu-tool gui
    """
    click.echo("Starting SPU Processing Tool GUI...")
    from src.gui import run_app
    run_app()


@cli.command()
@click.option('--show-rru-types', is_flag=True, help='Show available RRU types')
@click.option('--show-earfcn', is_flag=True, help='Show EARFCN mappings')
@click.option('--show-mme', is_flag=True, help='Show MME configurations')
@click.option('--show-amf', is_flag=True, help='Show AMF configurations')
@click.option('--show-baseband', is_flag=True, help='Show baseband configurations')
@click.option('--version', 'config_version', default='V1.70.26',
              help='Config version to show (default: V1.70.26)')
def config(show_rru_types, show_earfcn, show_mme, show_amf, show_baseband, config_version):
    """Show configuration information from config.json.

    Example:
        spu-tool config --show-rru-types
        spu-tool config --show-earfcn
    """
    try:
        with open(get_config_path(), 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        spu_config = config_data.get("SPU", {}).get(config_version, {})

        if show_rru_types:
            click.echo(f"\nRRU Types (hwWorkScence mapping) - {config_version}:")
            hw_mapping = spu_config.get("hwWorkScence_mapping", {})
            for rru_type, tech_map in hw_mapping.items():
                click.echo(f"  {rru_type}:")
                for tech, value in tech_map.items():
                    click.echo(f"    {tech}: {value}")

        if show_earfcn:
            click.echo(f"\nEARFCN Mappings - {config_version}:")
            earfcn_mapping = spu_config.get("earfcn_mapping", {})
            for earfcn, freq in sorted(earfcn_mapping.items(), key=lambda x: int(x[0])):
                click.echo(f"  {earfcn} -> {freq} MHz")

            click.echo(f"\nBand Indicator Mappings:")
            band_mapping = spu_config.get("bandIndicator_mapping", {})
            for earfcn, band in sorted(band_mapping.items(), key=lambda x: int(x[0])):
                click.echo(f"  EARFCN {earfcn} -> Band {band}")

        if show_mme:
            click.echo("\nMME Configurations:")
            mme_config = config_data.get("mme", {})
            for mme_name, ips in sorted(mme_config.items()):
                click.echo(f"  {mme_name}: {', '.join(ips)}")

        if show_amf:
            click.echo("\nAMF Configurations:")
            amf_config = config_data.get("amf", {})
            for amf_name, ips in sorted(amf_config.items()):
                click.echo(f"  {amf_name}: {', '.join(ips)}")

        if show_baseband:
            click.echo(f"\nBaseband Configurations - {config_version}:")
            bb_configs = spu_config.get("baseband_configs", {})
            for config_name in sorted(bb_configs.keys()):
                click.echo(f"  - {config_name}")

        # If no specific option, show summary
        if not any([show_rru_types, show_earfcn, show_mme, show_amf, show_baseband]):
            click.echo(f"Config version: {config_version}")
            click.echo(f"MCC: {config_data.get('mcc', 'N/A')}")
            click.echo(f"MNC: {config_data.get('mnc', 'N/A')}")
            click.echo(f"Available SPU versions: {list(config_data.get('SPU', {}).keys())}")
            click.echo(f"\nUse --show-* options to see specific configurations:")
            click.echo("  --show-rru-types  Show RRU types and hwWorkScence mappings")
            click.echo("  --show-earfcn     Show EARFCN to frequency mappings")
            click.echo("  --show-mme        Show MME IP configurations")
            click.echo("  --show-amf        Show AMF IP configurations")
            click.echo("  --show-baseband   Show baseband configurations")

    except Exception as e:
        click.echo(click.style(f"Error reading config: {e}", fg='red'), err=True)
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
