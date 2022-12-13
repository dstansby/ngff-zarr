#!/usr/bin/env python3

"""ngff-zarr command line interface."""

import argparse
import sys
from typing import List, Optional, Dict
import zarr
from rich.console import Console
from rich.theme import Theme
from rich.style import Style
from rich.highlighter import RegexHighlighter
from rich import print as rprint
import json

def open_store(identifier: str, storage_options: Dict, writable: bool=False) -> zarr.storage.StoreLike:
    dimension_separator = None
    mode = 'r'
    if writable:
        dimension_separator = '/'
        mode='w'

    protocol = identifier.find('://') != -1
    if protocol:
        try:
            import fsspec
        except ImportError:
            rprint('[italic red]Please install fsspec to access protocols[/italic red]')
            sys.exit(1)
        
        store = zarr.storage.FSStore(identifier, dimension_separator=dimension_separator, normalize_keys=False, mode=mode, **storage_options)
        return store

    if identifier.endswith('.zip'):
        store = zarr.storage.ZipStore(identifier, mode=mode, dimension_separator=dimension_separator)
        return store

    store = zarr.storage.DirectoryStore(identifier, dimension_separator=dimension_separator)
    return store

def copy(args: argparse.Namespace) -> None:
    """Copy the Zarr store args.source to args.dist"""
    storage_options = json.loads(args.storage_options)
    source = open_store(args.source, storage_options, False)
    dest = open_store(args.dest, storage_options, True)
    class CopyHighlighter(RegexHighlighter):
        base_style = 'copy.'
        highlights = [
            r'^(?P<alldone>all done:) (?P<ncopied>\S+) (?P<copied>copied,) (?P<nskipped>\S+) (?P<skipped>skipped,) (?P<nbytes>\S+) (?P<bytes>bytes copied)$',
            r'^(?P<copy>\w+) (?P<path>\S+)$',
        ]
    copy_highlighter = CopyHighlighter()
    theme = Theme(
        {
            "copy.alldone": Style.parse("bold yellow"),
            "copy.ncopied": Style.parse("bold cyan"),
            "copy.copied": Style.parse("cyan"),
            "copy.nskipped": Style.parse("bold blue"),
            "copy.skipped": Style.parse("blue"),
            "copy.nbytes": Style.parse("bold green"),
            "copy.bytes": Style.parse("green"),
            "copy.copy": Style.parse("dim"),
            "copy.path": Style.parse("magenta"),
        }
    )
    console = Console(theme=theme, quiet=args.quiet)
    logcallable = lambda x: console.log(copy_highlighter(x))
    console.log('[i]Starting copy...[/i]')
    with console.status(f"[bold green]Copying {args.source} to {args.dest}...") as status:
        zarr.convenience.copy_store(source, dest, if_exists='replace',
                dry_run=args.dry_run, log=logcallable)
    console.log('[i]Copy finished.[/i]')

def main(args: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Do not output information into the console",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # copy
    parser_copy = subparsers.add_parser("copy")
    parser_copy.add_argument("source")
    parser_copy.add_argument("dest")
    parser_copy.add_argument("--dry-run", action="store_true",
        help="execute a dry run that does not actually copy the store")
    parser_copy.add_argument("--storage-options", default='{}',
        help="string of JSON storage_options to pass to fsspec")
    parser_copy.set_defaults(func=copy)

    if args is None:
        parsed_args = parser.parse_args(sys.argv[1:])
    else:
        parsed_args = parser.parse_args(args)

    parsed_args.func(parsed_args)

if __name__ == '__main__':
    main()
