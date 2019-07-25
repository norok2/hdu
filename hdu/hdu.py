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
from __future__ import (
    division, absolute_import, print_function, unicode_literals)

# ======================================================================
# :: Python Standard Library Imports
import os  # Miscellaneous operating system interfaces
# import sys  # System-specific parameters and functions
import math  # Mathematical functions
import argparse  # Parser for command-line options, arguments and subcommands
import re  # Regular expression operations
import warnings  # Warning control
import stat  # Interpreting stat() results

# ======================================================================
# :: Version
__version__ = '0.2.3.11.dev16+g9ef230c.d20190527'

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
INFO['author'] = ', '.join(INFO['authors'])

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
def _is_hidden(filepath):
    # if sys.version_info[0] > 2:
    #     filepath = filepath.encode('utf-8')
    # filepath = filepath.decode('utf-8')
    return os.path.basename(filepath).startswith('.')


# ======================================================================
def _is_special(stats_mode):
    is_special = not stat.S_ISREG(stats_mode) and \
                 not stat.S_ISDIR(stats_mode) and \
                 not stat.S_ISLNK(stats_mode)
    return is_special


# ======================================================================
def _or_not_and(flag, check):
    return flag or not flag and check


# ======================================================================
def _or_not_and_not(flag, check):
    return flag or not flag and not check


# ======================================================================
def walk2(
        base,
        follow_links=False,
        follow_mounts=False,
        allow_special=False,
        allow_hidden=True,
        on_error=None):
    """

    Args:
        base (str): directory where to operate
        follow_links (bool): follow links during recursion
        follow_mounts (bool): follow mount points during recursion
        allow_special (bool): include special files
        allow_hidden (bool): include hidden files
        on_error (callable): function to call on error

    Returns:

    """
    try:
        for name in os.listdir(base):
            path = os.path.join(base, name)
            stats = os.stat(path)
            mode = stats.st_mode
            # for some reasons, stat.S_ISLINK and os.path.islink results differ
            allow = \
                _or_not_and_not(follow_links, os.path.islink(path)) and \
                _or_not_and_not(follow_mounts, os.path.ismount(path)) and \
                _or_not_and_not(allow_special, _is_special(mode)) and \
                _or_not_and_not(allow_hidden, _is_hidden(path))
            if allow:
                yield path, stats
                if os.path.isdir(path):
                    next_level = walk2(
                        path, follow_links, follow_mounts,
                        allow_special, allow_hidden, on_error)
                    for next_path, next_stats in next_level:
                        yield next_path, next_stats

    except OSError as error:
        if on_error is not None:
            on_error(error)
        return


# ======================================================================
def disk_usage(
        base=os.getcwd(),
        follow_links=True,
        follow_mounts=False,
        allow_special=True,
        allow_hidden=True,
        only_dir=False,
        max_depth=1,
        verbose=D_VERB_LVL):
    """
    Display a human-friendly summary of disk usage.

    Args:
        base (str): directory where to operate
        follow_links (bool): follow links during recursion
        follow_mounts (bool): follow mount points during recursion
        allow_special (bool): include special files
        allow_hidden (bool): include hidden files
        only_dir (bool): show only directories and not files
        max_depth (int): max recursion depth (negative for unlimited)
        verbose (int): set the level of verbosity

    Returns:
        items (dict): dictionary where the key is the subfolder, relative
        total_size (int): total size of sub-files and sub-directories in bytes
    """
    items = {}
    dir_items = {}
    total_size = os.path.getsize(base)
    num_files, num_dirs = 0, 1
    paths = walk2(
        base, follow_links, follow_mounts, allow_special, allow_hidden)
    if base.endswith(os.path.sep):
        base = base[:-len(os.path.sep)]
    base_depth = base.count(os.path.sep)
    for path, stats in paths:
        size = stats.st_size
        if verbose >= VERB_LVL['debug']:
            print(size, path)
        subpath = path[len(base) + len(os.path.sep):]
        depth = path.count(os.path.sep) - base_depth - 1
        is_dir = os.path.isdir(path)
        is_displayed = \
            ((not only_dir) or only_dir and is_dir)
        if (max_depth < 0 or depth < max_depth) and is_displayed:
            name = path[len(base) + len(os.path.sep):]
            if is_dir:
                dir_items[name] = size
            else:
                items[name] = size
        else:
            for key in dir_items.keys():
                if key.endswith(os.path.sep):
                    key_str = key[:-len(os.path.sep)]
                else:
                    key_str = key
                if subpath.startswith(key_str):
                    dir_items[key] += size
                    break
        total_size += size
        if is_dir:
            num_dirs += 1
        else:
            num_files += 1
    items.update({k + os.path.sep: v for k, v in dir_items.items()})
    return items, total_size, num_files, num_dirs


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
    if factor > 1.0:
        factor = 1.0
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
        sort_by (str): specify how to sort the results
            ['name'|'name_r'|'size'|'size_r']
        units (str): units to use ['iec'|'si'|'unix'|<exact>] (e.g. 'KiB').
            See 'humanize' for more details
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
        reverse = sort_by.endswith('_r')
        sorted_items = sorted(
            list(contents.items()), key=lambda x: x[index], reverse=reverse)
        for (name, size) in sorted_items:
            percent = size / total_size if total_size != 0.0 else 0.0
            size_str, units_str = humanize(size, units)
            lines.append(
                ' '.join((
                    progress_bar(percent, bar_size) if bar_size > 0 else '',
                    '{:>{len_size}.{len_precision}%}'.format(
                        percent, len_size=3 + 1 + 1 + percent_precision,
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
        follow_links,
        follow_mounts,
        allow_special,
        allow_hidden,
        only_dir,
        max_depth,
        sort_by,
        units,
        percent_precision,
        bar_size,
        eof_line_sep,
        verbose):
    """
    Human-friendly summary of disk usage.

    Args:
        base_paths (list[str]): List of paths to analyze
        follow_links (bool): follow links during recursion
        follow_mounts (bool): follow mount points during recursion
        allow_special (bool): include special files
        allow_hidden (bool): include hidden files
        only_dir (bool): show only directories and not files
        max_depth (int): max recursion depth (negative for unlimited)
        sort_by (str): specify how to sort the results.
            Allowed values: ['name'|'name_r'|'size'|'size_r']
        units (str): units to use ['iec'|'si'|'unix'|<exact>] (e.g. 'KiB').
            See 'humanize' for more details
        percent_precision (int): number of decimal digits for percentage
        bar_size (int): number of characters of the progress bar
        eof_line_sep (bool): use '\0' instead of '\n' as line separator
        verbose (int): set the level of verbosity

    Returns:
        None
    """
    for i, base in enumerate(base_paths):
        # deal with unicode input
        try:
            base = base.encode('utf-8')
        except UnicodeDecodeError:
            pass
        finally:
            base = base.decode('utf-8')

        if os.path.isdir(base):
            contents, total, num_files, num_dirs = disk_usage(
                base, follow_links, follow_mounts, allow_special, allow_hidden,
                only_dir, max_depth, verbose)
            line_sep = '\0' if eof_line_sep else '\n'
            text = disk_usage_to_str(
                contents, total, num_files, num_dirs, base, sort_by, units,
                percent_precision, bar_size, line_sep, verbose)
            if i > 0:
                print()
            print(text)
        elif os.path.isfile(base):
            size = os.path.getsize(base)
            contents = {base: size}
            line_sep = '\0' if eof_line_sep else '\n'
            text = disk_usage_to_str(
                contents, size, 1, 0, base, sort_by, units,
                percent_precision, bar_size, line_sep, verbose)
            print(text)
        else:
            if verbose >= VERB_LVL['low']:
                print('W: file not found: {}'.format(base))


# ======================================================================
def handle_arg():
    """
    Handle command-line application arguments.
    """
    # :: Create Argument Parser
    arg_parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='v.{version} - {author}\n{license}'.format_map(INFO),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # :: Add POSIX standard arguments
    arg_parser.add_argument(
        '--ver', '--version',
        version= \
            '%(prog)s - ver. {version}\n{}\n{copyright} {author}\n{notice}' \
                .format(next(l for l in __doc__.splitlines() if l), **INFO),
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
        '-l', '--follow_links',
        action='store_true',
        help='follow links during recursion [%(default)s]')
    arg_parser.add_argument(
        '-m', '--follow_mounts',
        action='store_true',
        help='follow mount points during recursion [%(default)s]')
    arg_parser.add_argument(
        '-e', '--allow_special',
        action='store_true',
        help='include special files [%(default)s]')
    arg_parser.add_argument(
        '-i', '--allow_hidden',
        action='store_true',
        help='include hidden files [%(default)s]')
    arg_parser.add_argument(
        '-s', '--only_dirs',
        action='store_true',
        help='show only directories and not files [%(default)s]')
    arg_parser.add_argument(
        '-d', '--max_depth', metavar='N',
        type=int, default=1,
        help='max recursion depth (negative for unlimited) [%(default)s]')
    arg_parser.add_argument(
        '-o', '--sort_by', metavar='name|name_r|size|size_r',
        default='size',
        help='display results in the specified units [%(default)s]')
    arg_parser.add_argument(
        '-u', '--units', metavar='iec|si|unix|<exact>',
        default='unix',
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
def main():
    """The main routine."""
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
        args.follow_links, args.follow_mounts,
        args.allow_special, args.allow_hidden,
        args.only_dirs, args.max_depth,
        args.sort_by, args.units, args.percent_precision, args.bar_size,
        args.eof_line_sep, args.verbose)


# ======================================================================
if __name__ == "__main__":
    main()
