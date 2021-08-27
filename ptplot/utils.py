from typing import Any, Dict


def _union_kwargs(protected_kwargs: Dict[str, Any], *other_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """

    Parameters
    ----------
    protected_kwargs: Any keyword arguments that are non-overrideable
    other_kwargs: Other keyword argument sets. If multiple argument sets have the same
        argument, the argument from the last set will be used. e.g. if there are 5 sets
        in the list of other_kwargs and the same kwarg is used in the 2nd and 4th sets,
        the value from the 4th set will be used.

    Returns
    -------
    A single dictionary of combined keyword arguments, that can be passed into a function
    with **.
    """
    final_kwargs = protected_kwargs
    for other_kwarg_set in other_kwargs:
        protected_kwargs_intersections = set(protected_kwargs.keys()).intersection(set(other_kwarg_set.keys()))
        if len(protected_kwargs_intersections) > 0:
            raise KeyError(
                f"The following keywords are protected and cannot be overridden: {protected_kwargs_intersections}"
            )
        final_kwargs = {**final_kwargs, **other_kwarg_set}

    return final_kwargs
