# -*- coding: utf-8 -*-
"""FancyPythonThings

This module contains various useful functions.
"""
import collections
import sys
from dateutil import parser
from functools import wraps
from typing import Callable, Dict, Sequence
import matplotlib.pyplot as plt


def parse_date(func: Callable = None,
               date_fields: Sequence[str] = ('date')) -> Callable:
    """
    Cast str date into datetime format.

    This decorator casts string arguments of a function to datetime.datetime
    type. This allows to specify either string of datetime format for a
    function argument. The name of the parameters to cast must be specified in
    the `date_fields`.

    The cast is done using the `parse` function from the
    `dateutil <https://dateutil.readthedocs.io/en/stable/parser.html>`_
    package. All supported format are those from the library and may evolve.

    In order to use the decorator both with or without parenthesis when calling
    it without parameter, the `date_fields` argument is keyword only. This
    allows checking if the parameter was given or not.

    Parameters
    ----------
    func: Callable
        Function with the arguments to parse.
    date_fields: Sequence of str, default 'date'
        Sequence containing the fields with dates.

    Returns
    -------
    Callable
        Function with the date fields cast to datetime.datetime type.

    Examples
    --------
    >>> @parse_date
    ... def dummy_function(**kwargs):
    ...     print(f'Args {kwargs}')
    ...
    >>> dummy_function(date='20190325')
    Args {'date': datetime.datetime(2019, 3, 25, 0, 0)}
    >>> dummy_function(date='Mon, 21 March, 2015')
    Args {'date': datetime.datetime(2015, 3, 21, 0, 0)}
    >>> dummy_function(date='2019-03-09 08:03:00')
    Args {'date': datetime.datetime(2019, 3, 9, 8, 3)}
    >>> dummy_function(date='March 27 2019')
    Args {'date': datetime.datetime(2019, 3, 27, 0, 0)}
    >>> dummy_function(date='wrong string')
    Value `wrong string` for field `date` is not convertible to a date format.
    Args {'date': 'wrong string'}
    """
    def _parse_date(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Parse the arguments of the function, if the date field is present
            # and is str, cast to datetime format.
            for key, value in kwargs.items():
                if key in date_fields and isinstance(value, str):
                    try:
                        kwargs[key] = parser.parse(value)
                    except ValueError:
                        print(f'Value `{value}` for field `{key}` is not '
                              'convertible to a date format.', file=sys.stderr)
            return func(*args, **kwargs)
        return wrapper
    return _parse_date(func) if func else _parse_date


def plot_history(history, style: str = 'default') -> None:
    """
    Plot the history of the model trained using Keras.

    Parameters
    ----------
    history : tensorflow.keras.callbask.History
        History of the training.
    style: str, default 'default'
        Style to use for matplotlib.pyplot.
        The style is use only in this context and not applied globally.
    """
    with plt.style.context(style):
        fig, (ax_acc, ax_loss) = plt.subplots(1, 2, figsize=(17, 7))

        # Summarize history for accuracy
        ax_acc.plot(history.history['acc'],
                    label=f"Train ({history.history['acc'][-1]:.4f})")
        ax_acc.plot(history.history['val_acc'],
                    label=f"Validation ({history.history['val_acc'][-1]:.4f})")
        ax_acc.set_title('Model accuracy')
        ax_acc.set_ylabel('Accuracy')
        ax_acc.set_xlabel('Epochs')
        ax_acc.legend(loc='upper left')

        # Summarize history for loss
        ax_loss.plot(history.history['loss'],
                     label=f"Train ({history.history['loss'][-1]:.4f})")
        ax_loss.plot(history.history['val_loss'],
                     label=f"Validation ({history.history['val_loss'][-1]:.4f})")
        ax_loss.set_title('Model loss')
        ax_loss.set_ylabel('Loss')
        ax_loss.set_xlabel('Epochs')
        ax_loss.legend(loc='upper left')

        fig.suptitle('Model history')
        plt.show()


def sliding_window(sequence: Sequence, window_size: int, step: int):
    """
    Apply a sliding window over the sequence.

    Each window is yielded. If there is a remainder, the remainder is yielded
    last, and will be smaller than the other windows.

    Parameters
    ----------
    sequence: Sequence
        Sequence to apply the sliding window on
        (can be str, list, numpy.array, etc.).
    window_size: int
        Size of the window to apply on the sequence.
    step: int
        Step for each sliding window.

    Yields
    ------
    Sequence
        Sequence generated.

    Examples
    --------
    >>> list(sliding_window('abcdef', 2, 1))
    ['ab', 'bc', 'cd', 'de', 'ef']
    >>> list(sliding_window(np.array([1, 2, 3, 4, 5, 6]), 5, 5))
    [array([1, 2, 3, 4, 5]), array([6])]
    """
    # Check for types.
    try:
        __ = iter(sequence)
    except TypeError:
        raise TypeError('Sequence must by iterable.')

    if not isinstance(step, int):
        raise TypeError('Step must be an integer.')
    if not isinstance(window_size, int):
        raise TypeError('Window size must be an integer.')
    # Check for values.
    if window_size < step or window_size <= 0:
        raise ValueError('Window_size must be larger or equal '
                         'than step and higher than 0.')
    if step <= 0:
        raise ValueError('Step must be higher than 0.')
    if len(sequence) < window_size:
        raise ValueError('Length of sequence must be larger '
                         'or equal than window_size.')

    nb_chunks = int(((len(sequence) - window_size) / step) + 1)
    mod = len(sequence) % window_size
    for i in range(0, nb_chunks * step, step):
        yield sequence[i:i+window_size]
    if mod:
        start = len(sequence) - (window_size - step) - mod
        yield sequence[start:]


def value_2_list(**kwargs) -> Dict[str, Sequence]:
    """
    Convert single values into list.

    For each argument provided, if the type is not a sequence,
    convert the single value into a list.
    Strings are not considered as a sequence in this scenario.

    Parameters
    ----------
    **kwargs
        Parameters passed to the function.

    Returns
    -------
    dict
        Dictionary with the single values put into a list.

    Raises
    ------
    TypeError
        If a non-keyword argument is passed to the function.

    Examples
    --------
    >>> value_2_list(name='John Doe', age=42, children=('Jane Doe', 14))
    {'name': ['John Doe'], 'age': [42], 'children': ('Jane Doe', 14)}
    >>> value_2_list(countries=['Swiss', 'Spain'])
    {'countries': ['Swiss', 'Spain']}
    """
    for k, v in kwargs.items():
        if not isinstance(v, collections.abc.Sequence) or isinstance(v, str):
            kwargs[k] = [v]
    return kwargs
