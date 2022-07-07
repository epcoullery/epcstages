from datetime import date


def school_year(date, as_tuple=False):
    """
    Return the school year of 'date'. Example:
      * as_tuple = False: "2013 — 2014"
      * as_tuple = True: [2013, 2014]
    """
    if date.month < 7:
        start_year = date.year - 1
    else:
        start_year = date.year
    if as_tuple:
        return (start_year, start_year + 1)
    else:
        return "%d — %d" % (start_year, start_year + 1)


def school_year_start():
    """ Return first official day of current school year """
    current_year = date.today().year
    if date(current_year, 8, 1) > date.today():
        return date(current_year-1, 8, 1)
    else:
        return date(current_year, 8, 1)


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
