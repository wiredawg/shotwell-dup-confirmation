# Shotwell Duplication Report Confirmation

Basically, this script is for me to convince myself that when [Shotwell](https://wiki.gnome.org/Apps/Shotwell/) reports
that it found duplicates, that it actually found a duplicate. I just do not want to miss any images while importing
from a library of over 40K images. 

The input to this script is a path to a directory with some text logs from Shotwell which are saved after dragging 
images into Shotwell. The output is a set of HTML pages with a two column table with the duplicate images set side
by side for quick review.

  1. Note that only 50 rows are placed in each page because full images are linked by the browser and loading can
     be slow if large images are in the set.

  2. Paths can be all over the place so my path resolution to create image paths that are relative to an HTTP server
     root may not work for you.


# Conclusion

After reviewing a couple hundred images I have not yet found a problem with the duplication reporting of Shotwell. 
Though, I do not consider this an exhaustive claim.
