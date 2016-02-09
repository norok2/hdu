#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Human-friendly summary of estimated disk space usage for files and directories.

Offers a similar information as the standard UNIX program 'du', but in a more
human-friendly format. This program is loosely based on an earlier shell script
by Roberto Metere and has been improved suggestions from Stefania Grasso.
"""

# ======================================================================
# :: Future Imports (for Python 2)
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# ======================================================================
# :: Python Standard Library Imports
import os  # Miscellaneous operating system interfaces
import sys  # System-specific parameters and functions
import math  # Mathematical functions
import argparse  # Parser for command-line options, arguments and subcommands
import re  # Regular expression operations
import warnings  # Warning control

# ======================================================================
# :: Version
__version__ = '0.2.2.5'

# ======================================================================
# :: Project Details
INFO = {
    'authors': (
        'Riccardo Metere <rick@metere.it>',
    ),
    'copyright': 'Copyright (C) 2016',
    'license': 'License: GNU General Public License version 3 (GPLv3)',
    'notice':
        """
This program is free software and it comes with ABSOLUTELY NO WARRANTY.
It is covered by the GNU General Public License version 3 (GPLv3).
You are welcome to redistribute it under its terms and conditions.
        """,
    'version': __version__
}

# ======================================================================
# :: supported verbosity levels (level 4 skipped on purpose)
VERB_LVL = {'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'debug': 5}
D_VERB_LVL = VERB_LVL['low']

# ======================================================================
# magnitude prefix for the units
# except for the case, it is the same for SI, IEC and UNIX
UNITS_PREFIX = ('k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')

# by the definition of units, the length of the size str cannot exceed 4
MAX_CHAR_SIZE = 4


# ======================================================================
def _is_hidden(filename):
    return filename[0] == '.'


# ======================================================================
def disk_usage(
        base_path=os.getcwd(),
        only_dirs=False,
        show_hidden=True,
        max_depth=1,
        followlinks=False,
        verbose=D_VERB_LVL):
    """
    Display a human-friendly summary of disk usage.

    Args:
        base_path (str): directory where to operate
        only_dirs (bool): show only directories and not files
        show_hidden (bool): allow display of hidden files and directories
        max_depth (int): max recursion depth (negative for unlimited)
        followlinks (bool): recursively follow links
        verbose (int): set the level of verbosity

    Returns:
        contents (dict): dictionary where the key is the subfolder, relative
        total_size (int): total size of sub-files and sub-directories in bytes
    """
    if base_path.endswith(os.path.sep):
        base_path = base_path[:-len(os.path.sep)]
    contents = {}
    total_size, num_files, num_dirs = 0, 0, 0

    for root, dirs, files in os.walk(base_path, followlinks=followlinks):
        basename = root[len(base_path):]
        depth = basename.count(os.path.sep)
        for name in dirs + files:
            path = os.path.join(root, name)
            try:
                size = os.path.getsize(path)
            except os.error:
                if verbose >= VERB_LVL['high']:
                    warnings.warn(path + ': could not determine size')
                size = 0
            accepted = \
                (not only_dirs or only_dirs and os.path.isdir(path)) and \
                (show_hidden or not show_hidden and not _is_hidden(name))
            if (max_depth < 0 or depth < max_depth) and accepted:
                name = path[len(base_path) + len(os.path.sep):]
                contents[name] = size
            for key in contents.keys():
                if basename[1:].startswith(key):
                    contents[key] += size
            total_size += size
        num_files += len(files)
        num_dirs += len(dirs)
    return contents, total_size, num_files, num_dirs


# ======================================================================
def progress_bar(
        factor,
        size=16,
        fill='=',
        empty=' ',
        pre='[',
        post=']'):
    """
    Generate a text progress bar.

    Args:
        factor (float): Fill factor. Must be in the [0, 1] range
        size (int): Size of the bar in characters (without pre/post decorators)
        fill (str): String used for filled bar (repeated)
        empty (str): String used for empty bar (repeated)
        pre (str): String prefix of the fill bar
        post (str): String postfix of the fill bar

    Returns:
        text (str): The fill bar.
    """
    fill_size = int(round(factor * size))
    # empty_size = int(round((1.0 - factor) * size))
    text = (fill * (size // len(fill) + 1))[0:fill_size] + \
           (empty * (size // len(empty) + 1))[fill_size:size]
    text = (pre if pre else '') + text + (post if post else '')
    return text


# ======================================================================
def _adjust_format(value, order, num_chars=MAX_CHAR_SIZE):
    len_integral_part = len(str(int(value)))
    if len_integral_part + 1 > num_chars or order == 0:
        precision = 0
    else:
        precision = num_chars - len_integral_part - 1
    return '{:3.{precision}f}'.format(value, precision=precision)


# ======================================================================
def _fix_size(size, base, exp):
    order = int(round(math.log(size, base) // exp)) if size > 0 else 0
    new_size = size / (base ** exp) ** order
    return new_size, order


# ======================================================================
def _to_units(o, units_prefix=UNITS_PREFIX):
    prefix_str = ''.join(units_prefix)
    return prefix_str[o - 1] if o > 0 else 'B'


# ======================================================================
def humanize(
        size,
        units='iec'):
    """
    Human-readable file size.

    Args:
        size (int): Size in bites.
        units (str): Units to be used.
            Implicit options:
                - 'iec': Use IEC units, multiples of 2^10=1024 (e.g. KiB, MiB)
                - 'si': Use SI units, multiples of 10^3=1000 (e.g. kB, MB)
                - 'unix': IEC units with short names (e.g. K instead of KiB)
            Explicit options: any SI, IEC or UNIX units (case sensitive!).
            If invalid string, falls back to none.

    Returns:
        size_str (str): Size in the new units
        units_str (str): Units of the new size
    """
    prefix_str = ''.join(UNITS_PREFIX)

    # explicit units
    if re.match('[{}]B'.format(prefix_str), units) or \
            re.match('[{}](iB)?'.format(prefix_str.upper()), units):
        order = prefix_str.upper().index(units[0].upper()) + 1
        units_str = units
        iec_units = len(units) == 1 or 3 >= len(units) > 1 and units[1] == 'i'
        base, exp = (2, 10) if iec_units else (10, 3)
        size_str = _adjust_format(size / (base ** exp) ** order, order)
    # set units class
    else:
        if units.lower() in 'unix':
            new_size, order = _fix_size(size, 2, 10)
            size_str = _adjust_format(new_size, order)
            units_str = _to_units(order).upper()
        elif units.lower() == 'iec':
            new_size, order = _fix_size(size, 2, 10)
            size_str = _adjust_format(new_size, order)
            units_str = _to_units(order).upper() + ('iB' if order > 0 else '')
        elif units.lower() == 'si':
            new_size, order = _fix_size(size, 10, 3)
            size_str = _adjust_format(new_size, order)
            units_str = _to_units(order) + ('B' if order > 0 else '')
        else:
            size_str = str(size)
            units_str = 'B'

    return size_str, units_str


# ======================================================================
def disk_usage_to_str(
        contents,
        total_size,
        num_files,
        num_dirs,
        base_path,
        sort_by='name',
        units='unix',
        percent_precision=2,
        bar_size=24,
        line_sep='\n',
        verbose=D_VERB_LVL):
    """
    Convert to human-readable text the previously calculate disk usage info.

    Args:
        contents (dict): dictionary where the key is the subfolder, relative
        total_size (int): total size of sub-files and sub-directories in bytes
        num_files (int): total number of files
        num_dirs (int): total number of dirs
        base_path (str): directory where to operate
        units (str): units to use ['iec'|'si'|'unix'|<exact>] (e.g. 'KiB').
            See 'humanize' for more details
        sort_by (str): specify how to sort the results
            ['name'|'name_r'|'size'|'size_r']
        percent_precision (int): Number of decimal digits for percentage
        bar_size (int): number of characters of the progress bar
        line_sep (str): line separator
        verbose (int): set the level of verbosity

    Returns:
        text (str): String containing the disk usage information
    """
    tot_size_str, tot_units_str = humanize(total_size, units)
    # assuming the length of the units str is monotonically increasing
    len_units = len(tot_units_str) + 1
    lines = []
    if verbose >= D_VERB_LVL:
        if sort_by.startswith('name'):
            index = 0
        elif sort_by.startswith('size'):
            index = 1
        else:
            index = 0
            msg = '{}: unknown sorting. Fall back to: name'.format(sort_by)
            warnings.warn(msg)
        reversed = sort_by.endswith('_r')
        sorted_items = sorted(
            list(contents.items()), key=lambda x: x[index], reverse=reversed)
        for (name, size) in sorted_items:
            percent = size / total_size if total_size != 0.0 else 0.0
            size_str, units_str = humanize(size, units)
            lines.append(
                ' '.join((
                    progress_bar(percent, bar_size) if bar_size > 0 else '',
                    '{:>{len_size}.{len_precision}%}'.format(
                        percent, len_size=4 + percent_precision,
                        len_precision=percent_precision),
                    '{:>{len_size}}{:<{len_units}}'.format(
                        size_str, units_str,
                        len_size=MAX_CHAR_SIZE, len_units=len_units),
                    name)))
    lines.append(os.path.realpath(base_path))
    lines.append(
        '{}{} ({}B), {} file(s), {} dir(s)'.format(
            tot_size_str, tot_units_str, total_size, num_files, num_dirs))
    text = line_sep.join(lines)
    return text


# ======================================================================
def hdu(
        base_paths,
        only_dirs,
        show_hidden,
        max_depth,
        followlinks,
        sort_by,
        units,
        percent_precision,
        bar_size,
        eof_line_sep,
        verbose):
    """
    Human-friendly summary of disk usage.

    Args:
        base_paths (str): list of paths where to operate
        only_dirs (bool): show only directories and not files
        show_hidden (bool): allow display of hidden files and directories
        max_depth (int): max recursion depth (negative for unlimited)
        followlinks (bool): recursively follow links
        sort_by (str): specify how to sort the results
            ['name'|'name_r'|'size'|'size_r']
        units (str): units to use ['iec'|'si'|'unix'|<exact>] (e.g. 'KiB').
            See 'humanize' for more details
        percent_precision (int): number of decimal digits for percentage
        bar_size (int): number of characters of the progress bar
        eof_line_sep (bool): use '\0' instead of '\n' as line separator
        verbose (int): set the level of verbosity

    Returns:
        None
    """
    for i, base_path in enumerate(base_paths):
        if os.path.isdir(base_path):
            contents, total, num_files, num_dirs = disk_usage(
                base_path, only_dirs, show_hidden, max_depth, followlinks,
                verbose)
            line_sep = '\0' if eof_line_sep else '\n'
            text = disk_usage_to_str(
                contents, total, num_files, num_dirs, base_path, units,
                sort_by, percent_precision, bar_size, line_sep, verbose)
            if i > 0:
                print()
            print(text)
        elif os.path.isfile(base_path):
            size = os.path.getsize(base_path)
            contents = {base_path: size}
            line_sep = '\0' if eof_line_sep else '\n'
            text = disk_usage_to_str(
                contents, size, 1, 0, base_path, units, sort_by,
                percent_precision, bar_size, line_sep, verbose)
            print(text)
        else:
            if verbose >= VERB_LVL['low']:
                print('W: file not found: {}'.format(base_path))


# ======================================================================
def handle_arg():
    """
    Handle command-line application arguments.
    """
    # :: Create Argument Parser
    arg_parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='v.{} - {}\n{}'.format(
            INFO['version'], ', '.join(INFO['authors']),
            INFO['license']),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # :: Add POSIX standard arguments
    arg_parser.add_argument(
        '--ver', '--version',
        version='%(prog)s - ver. {}\n{}\n{} {}\n{}'.format(
            INFO['version'],
            next(line for line in __doc__.splitlines() if line),
            INFO['copyright'], ', '.join(INFO['authors']),
            INFO['notice']),
        action='version')
    arg_parser.add_argument(
        '-v', '--verbose',
        action='count', default=D_VERB_LVL,
        help='increase the level of verbosity [%(default)s]')
    # :: Positional arguments
    arg_parser.add_argument(
        'TARGET',
        nargs='*', default=(os.getcwd(),),
        help='directory where to estimate disk usage [%(default)s]')
    # :: Add additional arguments
    arg_parser.add_argument(
        '-s', '--only_dirs',
        action='store_true',
        help='show only directories and not files [%(default)s]')
    arg_parser.add_argument(
        '-a', '--no_hidden',
        action='store_false',
        help='do not show hidden files [%(default)s]')
    arg_parser.add_argument(
        '-d', '--max_depth', metavar='N',
        type=int, default=1,
        help='max recursion depth (negative for unlimited) [%(default)s]')
    arg_parser.add_argument(
        '-l', '--followlinks',
        action='store_true',
        help='recursively follow links [%(default)s]')
    arg_parser.add_argument(
        '-u', '--units', metavar='iec|si|unix|<exact>',
        default='unix',
        help='display results in the specified units [%(default)s]')
    arg_parser.add_argument(
        '-o', '--sort_by', metavar='name|name_r|size|size_r',
        default='size',
        help='display results in the specified units [%(default)s]')
    arg_parser.add_argument(
        '-p', '--percent_precision', metavar='N',
        type=int, default=2,
        help='number of decimal digits in the percent field [%(default)s]')
    arg_parser.add_argument(
        '-b', '--bar_size', metavar='N',
        type=int, default=20,
        help='size of the text progress bar [%(default)s]')
    arg_parser.add_argument(
        '-0', '--eof_line_sep',
        action='store_true',
        help='use \0 instead of \n as line separator [%(default)s]')
    return arg_parser


# ======================================================================
def main(argv=None):
    """The main routine."""
    if argv is None:
        argv = sys.argv[1:]

    # :: handle program parameters
    arg_parser = handle_arg()
    args = arg_parser.parse_args()
    # :: print debug info
    if args.verbose == VERB_LVL['debug']:
        arg_parser.print_help()
        print()
        print('II:', 'Parsed Arguments:', args)

    hdu(
        args.TARGET,
        args.only_dirs, args.no_hidden, args.max_depth, args.followlinks,
        args.units, args.sort_by, args.percent_precision, args.bar_size,
        args.eof_line_sep, args.verbose)


# ======================================================================
if __name__ == "__main__":
    main()
