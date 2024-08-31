#!/usr/bin/env python
import fileinput, csv, sys

# allow large content
csv.field_size_limit(sys.maxsize)

def is_insert(line):
    return line.startswith('INSERT INTO')

def get_values(line):
    return line.partition(' VALUES ')[2]

# save values from SQL INSERT into a file
def parse_values(values, outfile):
    latest_row = []

    reader = csv.reader([values], delimiter=',',
                        doublequote=False,
                        escapechar='\\',
                        quotechar="'",
                        strict=True
    )

    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
    for reader_row in reader:
        for column in reader_row:
            # current string is empty
            if len(column) == 0 or column == 'NULL':
                latest_row.append(chr(0))
                continue
            # string starts with an open parenthesis
            if column[0] == "(":
                # If we've been filling out a row
                if len(latest_row) > 0:
                    # Check if the previous entry ended in
                    # a close paren. If so, the row we've
                    # been filling out has been COMPLETED
                    # as:
                    #    1) the previous entry ended in a )
                    #    2) the current entry starts with a (
                    if latest_row[-1][-1] == ")":
                        # Remove the close paren.
                        latest_row[-1] = latest_row[-1][:-1]
                        writer.writerow(latest_row)
                        latest_row = []
                # If beginning a new row - eliminate opening parentheses.
                if len(latest_row) == 0:
                    column = column[1:]
            # Add our column to the row we're working on.
            latest_row.append(column)
        # At the end of an INSERT statement, we'll
        # have the semicolon.
        # Make sure to remove the semicolon and
        # the close paren.
        if latest_row[-1][-2:] == ");":
            latest_row[-1] = latest_row[-1][:-2]
            writer.writerow(latest_row)


def main():
    # Iterate over all lines in all files
    # listed in sys.argv[1:]
    # or stdin if no args given.
    try:
        for line in fileinput.input():
            # Look for an INSERT statement and parse it.
            if not is_insert(line):
                continue
            values = get_values(line)
            parse_values(values, sys.stdout)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()