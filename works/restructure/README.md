Scripts used once to build the stored resources of the `restructure` branch
from the files the former code (branch `draconic-transformations`) generated
on a BG2:EE install:

- `extract.py`: copies the kept files, renames their resrefs (NY#K / T / B /
  S / H / C prefixes), turns the install values into placeholders (spell
  states, SPLPROT rows, projectiles), clears the strings, builds Black Dragon
  Breath: Line from the former line form.
- `iemodel.py`: minimal SPL / ITM reader and writer used by extract.py.
- `ie.py`: prints the effects of SPL files (checks).

Not needed to install the mod: the resources are edited in Near Infinity now.
