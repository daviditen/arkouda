from __future__ import annotations
from typing import Iterable, Union
from typeguard import typechecked
from arkouda.client import generic_msg
from arkouda.pdarrayclass import pdarray, create_pdarray
from arkouda.pdarraycreation import zeros
from arkouda.strings import Strings
from arkouda.dtypes import *

__all__ = ["argsort", "coargsort", "sort"]

def argsort(pda : Union[pdarray,Strings,'Categorical']) -> pdarray:
    """
    Return the permutation that sorts the array.
    
    Parameters
    ----------
    pda : pdarray or Strings or Categorical
        The array to sort (int64 or float64)

    Returns
    -------
    pdarray, int64
        The indices such that ``pda[indices]`` is sorted
        
    Raises
    ------
    TypeError
        Raised if the parameter is other than a pdarray or Strings

    See Also
    --------
    coargsort

    Notes
    -----
    Uses a least-significant-digit radix sort, which is stable and
    resilinent to non-uniformity in data but communication intensive.

    Examples
    --------
    >>> a = ak.randint(0, 10, 10)
    >>> perm = ak.argsort(a)
    >>> a[perm]
    array([0, 1, 1, 3, 4, 5, 7, 8, 8, 9])
    """
    if hasattr(pda, "argsort"):
        return pda.argsort()
    if pda.size == 0:
        return zeros(0, dtype=int64)
    if isinstance(pda, Strings):
        name = '{}+{}'.format(pda.offsets.name, pda.bytes.name)
    else:
        name = pda.name
    repMsg = generic_msg("argsort {} {}".format(pda.objtype, name))
    return create_pdarray(repMsg)

@typechecked
def coargsort(arrays : Iterable[Union[Strings,pdarray]]) -> pdarray:
    """
    Return the permutation that groups the rows (left-to-right), if the
    input arrays are treated as columns. The permutation sorts numeric
    columns, but not strings -- strings are grouped, but not ordered.
    
    Parameters
    ----------
    arrays : iterable of pdarray or Strings
        The columns (int64, float64, or Strings) to sort by row

    Returns
    -------
    pdarray, int64
        The indices that permute the rows to grouped order
        
    Raises
    ------
    ValueError
        Raised if the pdarrays are not of the same size or if the parameter
        is not an Iterable containing pdarrays or Strings

    See Also
    --------
    argsort

    Notes
    -----
    Uses a least-significant-digit radix sort, which is stable and resilient
    to non-uniformity in data but communication intensive. Starts with the
    last array and moves forward. This sort operates directly on numeric types,
    but for Strings, it operates on a hash. Thus, while grouping of equivalent
    strings is guaranteed, lexicographic ordering of the groups is not.

    Examples
    --------
    >>> a = ak.array([0, 1, 0, 1])
    >>> b = ak.array([1, 1, 0, 0])
    >>> perm = ak.coargsort([a, b])
    >>> perm
    array([2, 0, 3, 1])
    >>> a[perm]
    array([0, 0, 1, 1])
    >>> b[perm]
    array([0, 1, 0, 1])
    """
    size = -1
    anames = []
    atypes = []
    for a in arrays:
        if isinstance(a, Strings):
            anames.append('{}+{}'.format(a.offsets.name, a.bytes.name))
            atypes.append(a.objtype)
        elif isinstance(a, pdarray):
            anames.append(a.name)
            atypes.append('pdarray')
        else:
            raise ValueError("Argument must be an iterable of pdarrays or Strings")
        if size == -1:
            size = a.size
        elif size != a.size:
            raise ValueError("All pdarrays or Strings must be of the same size")
    if size == 0:
        return zeros(0, dtype=int64)
    cmd = "coargsort"
    reqMsg = "{} {:n} {} {}".format(cmd,
                                    len(arrays),
                                    ' '.join(anames),
                                    ' '.join(atypes))
    repMsg = generic_msg(reqMsg)
    return create_pdarray(repMsg)

@typechecked
def sort(pda : pdarray) -> pdarray:
    """
    Return a sorted copy of the array. Only sorts numeric arrays; 
    for Strings, use argsort.
    
    Parameters
    ----------
    pda : pdarray or Categorical
        The array to sort (int64 or float64)

    Returns
    -------
    pdarray, int64 or float64
        The sorted copy of pda

    Raises
    ------
    TypeError
        Raised if the parameter is not a pdarray
    RuntimeError
        Raised if sort attempted on a pdarray with an unsupported dtype

    See Also
    --------
    argsort

    Notes
    -----
    Uses a least-significant-digit radix sort, which is stable and resilient
    to non-uniformity in data but communication intensive.

    Examples
    --------
    >>> a = ak.randint(0, 10, 10)
    >>> sorted = ak.sort(a)
    >>> a
    array([0, 1, 1, 3, 4, 5, 7, 8, 8, 9])
    """
    if pda.size == 0:
        return zeros(0, dtype=int64)
    repMsg = generic_msg("sort {}".format(pda.name))
    return create_pdarray(repMsg)
