# Data

The scripts read two files from this folder. They are not stored in the repository, because they are large (about 25 MB for the PET file) and may have sharing restrictions.

|File|Columns used|Description|
|-|-|-|
|`OsloData\_5min.txt`|`Precipitation` (column 2), `UnderdrainFlow` (column 4)|Rainfall and underdrain flow at 5-minute resolution, 1 Sep 2009 onwards. Other columns are not used.|
|`Oslo\_PET\_5min.txt`|`minutelyPET` (column 2)|Potential evapotranspiration at 5-minute resolution, from the same start time.|

Both files have 876,672 rows and the same start time. Column numbers above are counted from 1, with the timestamp as column 1.

To run the scripts, place both files in this folder, or pass another folder with `--data-dir`.

**Source and access:** The rainfall and green roof underdrain flow data were obtained by personal communication with colleagues at NTNU (Tone Muthanna).

