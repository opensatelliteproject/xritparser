#!/usr/bin/env python

import sys
from xrit.packetmanager import *

def __printDisclaimer():
    print("   * This is part of OpenSatelliteProject and its released under MIT License")
    print("   * For more information about check http://github.com/opensatelliteproject")
    print("")

def parseFileExecutable():
  argc = len(sys.argv) -1
  files = []
  arguments = []
  for i in range(argc):
    if sys.argv[i+1][:1] == "-":
      arg = sys.argv[i+1][1:]
      for i in arg:
        arguments.append(i)
    else:
      files.append(sys.argv[i+1])

  if len(files) == 0:
    print("xRIT File Header Parser")
    print("   * This program reads a HRIT/LRIT Header and prints the known data.")
    __printDisclaimer()
    print("Usage:")
    print("   xritparse file1.lrit [file2.lrit]")
    print("       -h    Print Structured Header Record")
    print("       -i    Print Image Data Record")
  else:
    for i in range(len(files)):
      filename = files[i]
      print("Parsing file %s" % filename)
      try:
        parseFile(filename, "h" in arguments, "i" in arguments)
      except Exception as e:
        print("Error parsing file %s: %s" %(filename, e))

def dumpDataExecutable():
  argc = len(sys.argv) -1
  if argc != 2:
    print("xRIT Data Dumper")
    print("   * This program dumps the data section of a HRIT/LRIT file.")
    __printDisclaimer()
    print("Usage: ")
    print("   xritdump filename.lrit output.bin")
  else:
    filename = sys.argv[1]
    outputname = sys.argv[2]
    dumpData(filename, outputname)

def catExecutable():
  argc = len(sys.argv) -1
  if argc != 1:
    print("xRIT Cat")
    print("   * This program dumps the data section of a HRIT/LRIT file and sends to stdout")
    __printDisclaimer()
    print("Usage: ")
    print("   xritcat filename.lrit")
  else:
    filename = sys.argv[1]
    sys.stdout.write(loadData(filename))