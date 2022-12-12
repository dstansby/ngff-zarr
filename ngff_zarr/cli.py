#!/usr/bin/env python3

"""ngff-zarr command line interface."""

import argparse
import sys
from typing import List, Optional
import zarr
from rich.console import Console
from rich.theme import Theme
from rich.style import Style
from rich.highlighter import RegexHighlighter

def open_store(identifier: str, writable: bool=False) -> zarr.storage.StoreLike:
    dimension_separator = None
    mode = 'r'
    if writable:
        dimension_separator = '/'
        mode='w'

    if identifier.endswith('.zip'):
        store = zarr.storage.ZipStore(identifier, mode=mode, dimension_separator=dimension_separator)
        return store

    store = zarr.storage.DirectoryStore(identifier, dimension_separator=dimension_separator)
    return store

def copy(args: argparse.Namespace) -> None:
    """Copy the Zarr store args.source to args.dist"""
    source = open_store(args.source, False)
    dest = open_store(args.dest, True)
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
    parser = argparse.ArgumentParser()

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
        help="Run a dry run that does not actually copy the store")
    parser_copy.set_defaults(func=copy)

    if args is None:
        parsed_args = parser.parse_args(sys.argv[1:])
    else:
        parsed_args = parser.parse_args(args)

    parsed_args.func(parsed_args)

if __name__ == '__main__':
    main()
