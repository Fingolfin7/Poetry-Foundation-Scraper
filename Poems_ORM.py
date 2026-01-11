"""Deprecated module.

This project is now DB/ORM-only and uses `Poems.py` as the single Poems facade.
`Poems_ORM.py` previously existed during migration and retained JSON-era helpers.
It has been intentionally deprecated.

Import `Poems` from `Poems.py` instead.
"""

from Poems import Poems  # re-export for any leftover imports

__all__ = ["Poems"]
