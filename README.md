xRIT Parser Toolkit
======================

A toolkit to parse / dump HRIT / LRIT files.

### xritparse

Parses xRIT file Header and print in a human readable format.

```
  Usage:
    xritparse [-hi] filen.lrit [file2.lrit]
         -h    Print Structured Header Record
         -i    Print Image Data Record
```

##### Example:

```
  # xritparse DCSdat363042229684.lrit
  Parsing file DCSdat363042229684.lrit
  Primary Header:
     File Type Code: DCS
     Header Length: 89
     Data Field Length: 1617088

  NOAA Specific Header
     Signature: NOAA
     Product ID: DCS
     Product SubId: None
     Parameter: 11500
     Compression: Not Compressed

  Annotation Record
     Filename: DCSdat363042229684.lrit

  Timestamp Record
     DateTime: 2016-12-28 04:22:00

  DCS Filename:
     Filename: pL-16363042229-A.dcs
```

### xritdump

Dumps the data section of a HRIT/LRIT file.
PS: This does not convert or process anything. It just saves the data section.

```
  Usage:
     xritdump filename.lrit output.bin
```

### xritcat

Reads the data section of a HRIT/LRIT file and prints to stdout.

```
  Usage:
     xritcat filename.lrit
```

## Python Library

This also can be used as a python library by importing `xrit`. The documentation is still WIP. Please us the module executables as a reference.

## Installing

The package is available at `pip`. Just run:

```
  sudo pip install xrit
```
