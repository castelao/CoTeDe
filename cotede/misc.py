import numpy as np

# ============================================================================
# I need to improve this, and include the places where the
#   flags are masked, i.e. only eliminate where the flags
#   could guarantee it was false.


def combined_flag(flags, criteria=None):
    """ Returns the combined flag considering all the criteria

        Input: flags

        Collects all flags in the criteria, and for each measurements, it
          return the maximum flag value among the different criteria.

        If criteria is not defined, considers all the flags,
          i.e. flags.keys()
    """
    assert hasattr(flags, 'keys')

    if criteria is None:
        criteria = list(flags.keys())

    output = np.asanyarray(flags[criteria[0]])
    for c in criteria[1:]:
        assert len(flags[c]) == len(output)
        output = np.max([output, flags[c]], axis=0)

    return output


def make_qc_index(flags, criteria, type="anytrue"):
    ind = flags[criteria[0]].copy()
    if type == "anytrue":
        for c in criteria:
            ind[(ind is True) | (flags[c] is True)] = True
        #ind[np.nonzero((ind == True) | (np.array(flags[c]) == True))[0]] = True
    elif type == "alltrue":
        for c in criteria:
            ind[(ind is True) | (flags[c] is True)] = True
    for c in criteria:
        ind[(ind is False) | (flags[c] is False)] = False
        # ind[np.nonzero((ind == False) | (np.array(flags[c]) == False))[0]] = False
    return ind
