def school_year(date, as_tuple=False):
    """
    Return the school year of 'date'. Example:
      * as_tuple = False: "2013 — 2014"
      * as_tuple = True: [2013, 2014]
    """
    if date.month < 8:
        start_year = date.year - 1
    else:
        start_year = date.year
    if as_tuple:
        return (start_year, start_year + 1)
    else:
        return "%d — %d" % (start_year, start_year + 1)
