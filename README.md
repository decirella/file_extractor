# File Extractor for Raw Disk Images  
The program automates the processing and extraction of files, from raw disk images, using the ```fiwalk``` and ```icat``` tools.  

```
usage: file_extractor.py [-h] [-r] [-d] [--version] arg

Process raw disk images to create dfxml and extract files

positional arguments:
  arg              Provide path to directory holding a image or directory of

optional arguments:
  -h, --help       show this help message and exit
  -r, --recursive  Recursive allows processing directories/subdirectories of
                   images
  -d, --dfxml      Specifiy location of dfxml file if it already exisits
  --version        show program's version number and exit
```

### Usage example
Basic usage with path to directory holding a disk image
```
$ python3 file_extractor.py /home/test/

```

If dfxml has been previously generated, us the ```-d``` option to specify it's location.
```
$ python3 file_extractor.py -d /home/test/39002125897281/39002125897281.xml
```

Process mulitple images held in child directories using the ```-r``` option with the parent directory path as argument
```
$ python3 file_extractor.py -r /home/test/
```
