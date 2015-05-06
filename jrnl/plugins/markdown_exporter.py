#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals, print_function
from .text_exporter import TextExporter
import re
import sys
from ..util import WARNING_COLOR, ERROR_COLOR, RESET_COLOR


class MarkdownExporter(TextExporter):
    """This Exporter can convert entries and journals into Markdown."""
    names = ["md", "markdown"]
    extension = "md"

    @classmethod
    def export_entry(cls, entry, to_multifile=True):
        """Returns a markdown representation of a single entry."""
        date_str = entry.date.strftime(entry.journal.config['timeformat'])
        body_wrapper = "\n" if entry.body else ""
        body = body_wrapper + entry.body

        if to_multifile is True:
            heading = '#'
        else:
            heading = '###'

        '''Increase heading levels in body text'''
        newbody = ''
        previous_line = ''
        warn_on_heading_level = False
        for line in body.splitlines(True):
            if re.match(r"#+ ", line):
                """ATX style headings"""
                newbody = newbody + previous_line + heading + line
                if re.match(r"#######+ ", heading + line):
                    warn_on_heading_level = True
                line = ''
            elif re.match(r"=+$", line) and not re.match(r"^$", previous_line):
                """Setext style H1"""
                newbody = newbody + heading + "# " + previous_line
                line = ''
            elif re.match(r"-+$", line) and not re.match(r"^$", previous_line):
                """Setext style H2"""
                newbody = newbody + heading + "## " + previous_line
                line = ''
            else:
                newbody = newbody + previous_line
            previous_line = line
        newbody = newbody + previous_line   # add very last line

        if warn_on_heading_level is True:
            print("{}WARNING{}: Headings increased past H6 on export - {} {}".format(WARNING_COLOR, RESET_COLOR, date_str, entry.title), file=sys.stderr)

        return "{md} {date} {title} {body} {space}".format(
            md=heading,
            date=date_str,
            title=entry.title,
            body=newbody,
            space=""
        )

    @classmethod
    def export_journal(cls, journal):
        """Returns a Markdown representation of an entire journal."""
        out = []
        year, month = -1, -1
        for e in journal.entries:
            if not e.date.year == year:
                year = e.date.year
                out.append(str(year))
                out.append("=" * len(str(year)) + "\n")
            if not e.date.month == month:
                month = e.date.month
                out.append(e.date.strftime("%B"))
                out.append('-' * len(e.date.strftime("%B")) + "\n")
            out.append(cls.export_entry(e, False))
        result = "\n".join(out)
        return result
