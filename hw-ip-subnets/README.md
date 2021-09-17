# IP Subnetting

[doctests](https://docs.python.org/3/library/doctest.html), are "pieces
of text that look like interactive python sessions" (i.e., starting with
`>>>`), found in the [docstring](https://www.python.org/dev/peps/pep-0257/) of
a Python file, class, function, or method.  Examine the doctests in `subnet.py`,
and the functions or methods to which they correspond.  Then complete the
following exercises.  Read both exercises before you begin, as it might be easier
for you to do one before the other.

 1. Fill in the appropriate return value for each of the doctests for
    `Subnet.__contains__()` and `ForwardingTable.get_forwarding_entry()` in
    `subnet.py`.  `None` is currently used as a placeholder for each. The
    return value for `Subnet.__contains__()` should be a boolean (`True` or
    `False`) and the return value for `ForwardingTable.get_forwarding_entry()`
    is a string indicating the name of the outgoing interface.  You might also
    choose to create a doc test for `IPAddress.mask()`, to check your work, but
    it is not required.

 2. Fill out the following methods (marked with `FIXME`):

    - `IPAddress.mask()` (approx. 1 - 2 lines of code)
    - `Subnet.__contains__()` (approx. 1 line of code)
    - `ForwardingTable.get_forwarding_entry()` (approx. 10 lines of code)

    The first two methods are small but require a bit more thought than the
    last one.  Remember to use longest prefix match for the last method!

When you have finished your revisions of `subnet.py`:

    - The return values in the doc tests must be correct; and
    - The following should run without error:
      ```
      python3 -m doctest subnet.py
      ```
