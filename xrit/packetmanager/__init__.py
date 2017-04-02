#!/usr/bin/env python
import os, struct, datetime
from PIL import Image

'''
  Known product / subproducts IDs from NOAA
'''
NOAA_PRODUCT_ID = {
  1: {
    "name": "NOAA Text",
    "sub": {
      0: "None"
    }
  },
  4: {
    "name": "Other Satellite",
    "sub": {
      0: "None",
      1: "Infrared Full Disk",
      3: "Visible Full Disk"
    }
  },
  3: {
    "name": "Other Satellite",
    "sub": {
      1: "Infrared Full Disk",
      3: "Visible Full Disk"
    }
  },
  6: {
    "name": "Weather Data",
    "sub": {
      0: "None"
    }
  },
  8: {
    "name": "DCS",
    "sub": {
      0: "None"
    }
  },
  9: {
    "name": "HRIT EMWIN TEXT (?)",
    "sub": {
      0: "None"
    }
  },
  13: {
    "name": "GOES 13 ABI",
    "sub": {
       1: "Infrared Full Disk",
       2: "Infrared Northern Hemisphere",
       3: "Infrared Southern Hemisphere",
       4: "Infrared United States",
       5: "Infrared Area of Interest",
      11: "Visible Full Disk",
      12: "Visible Northern Hemisphere",
      13: "Visible Southern Hemisphere",
      14: "Visible United States",
      15: "Visible Area of Interest",
      21: "Water Vapour Full Disk",
      22: "Water Vapour Northern Hemisphere",
      23: "Water Vapour Southern Hemisphere",
      24: "Water Vapour United States",
      25: "Water Vapour Area of Interest"
    }
  },
  15: {
    "name": "GOES 15 ABI",
    "sub": {
       1: "Infrared Full Disk",
       2: "Infrared Northern Hemisphere",
       3: "Infrared Southern Hemisphere",
       4: "Infrared United States",
       5: "Infrared Area of Interest",
      11: "Visible Full Disk",
      12: "Visible Northern Hemisphere",
      13: "Visible Southern Hemisphere",
      14: "Visible United States",
      15: "Visible Area of Interest",
      21: "Water Vapour Full Disk",
      22: "Water Vapour Northern Hemisphere",
      23: "Water Vapour Southern Hemisphere",
      24: "Water Vapour United States",
      25: "Water Vapour Area of Interest"
    }
  },
  16: {
    "name": "GOES 16 ABI",
    "sub": {
      0: "None",
      1: "Channel 1",
      2: "Channel 2",
      3: "Channel 3",
      4: "Channel 4",
      5: "Channel 5",
      6: "Channel 6",
      7: "Channel 7",
      8: "Channel 8",
      9: "Channel 9",
      10: "Channel 10",
      11: "Channel 11",
      12: "Channel 12",
      13: "Channel 13",
      14: "Channel 14",
      15: "Channel 15",
      16: "Channel 16",
    }
  },
  42: {
    "name": "EMWIN",
    "sub": {
      0: "None"
    }
  },
  43: {
    "name": "HIMAWARI8 ABI",
    "sub": {
      0: "None",
      1: "Channel 1",
      2: "Channel 2",
      3: "Channel 3",
      4: "Channel 4",
      5: "Channel 5",
      6: "Channel 6",
      7: "Channel 7",
      8: "Channel 8",
      9: "Channel 9",
      10: "Channel 10",
      11: "Channel 11",
      12: "Channel 12",
      13: "Channel 13",
      14: "Channel 14",
      15: "Channel 15",
      16: "Channel 16",
    }
  }
}

'''
  Known File Type Codes
'''

FILE_TYPE_CODE_NAME = {
  0: "Image",
  1: "Messages",
  2: "Text",
  3: "Encryption Key",
  4: "Reserved (4)",

  128: "Meteorological Data",
  130: "DCS",
  214: "EMWIN"
}

'''
  Known Compression Types
'''
COMPRESSION_TYPE_NAME = {
  0: "Not Compressed",
  1: "LRIT Rice",
  2: "JPEG",
  5: "GIF",
  10: "ZIP"
}

'''
  Base date for calcuting timestamps
'''
baseDate = datetime.datetime(1958, 1, 1)

def binary(num, length=8):
  return format(num, '#0{}b'.format(length + 2))

def parseFile(filename, showStructuredHeader=False, showImageDataRecord=False):
  '''
    Parses a lrit/hrit file and prints the human readable headers
  '''
  f = open(filename, "rb")

  try:
    k = readHeader(f)
    type, filetypecode, headerlength, datalength = k
  except:
    print("   Header 0 is corrupted for file %s" %filename)
    return
  f.seek(0, 0)
  data = f.read(headerlength)
  headers = getHeaderData(data)
  printHeaders(headers, showStructuredHeader, showImageDataRecord)
  f.close()

def dumpData(filename, output):
  '''
    Reads lrit/hrit file "filename" and writes the data section to file "output"
  '''
  f = open(filename, "rb")

  try:
    k = readHeader(f)
    type, filetypecode, headerlength, datalength = k
  except:
    print("   Header 0 is corrupted for file %s" %filename)
    return
  f.seek(0, 2)
  length = f.tell() - headerlength
  f.seek(headerlength, 0)
  o = open(output, "wb")
  c = 0

  while c < length:
    data = f.read(4096)
    if len(data) == 0:
      print("   Error: Premature file end. Expected %s bytes and only read %s bytes" %(length, c))
      break
    o.write(data)
    c += len(data)

  f.close()
  o.close()

def loadData(filename):
  '''
    Reads an lrit/hrit file and returns the data section content
  '''
  f = open(filename, "rb")

  try:
    k = readHeader(f)
    type, filetypecode, headerlength, datalength = k
  except:
    print("   Header 0 is corrupted for file %s" %filename)
    return
  f.seek(headerlength, 0)
  data = f.read()
  f.close()
  return data

def manageFile(filename):
  '''
    Reads a lrit/hrit file and renames itself to the filename specified in the header
  '''
  f = open(filename, "rb")

  try:
    k = readHeader(f)
    type, filetypecode, headerlength, datalength = k
  except:
    print("   Header 0 is corrupted for file %s" %filename)
    return

  newfilename = filename
  while f.tell() < headerlength:
    data = readHeader(f)
    if data[0] == 4:
      newfilename = data[1]
      break
  f.close()
  if filename != newfilename:
    print("   Renaming %s to %s/%s" %(filename, os.path.dirname(filename), newfilename))
    os.rename(filename, "%s/%s" %(os.path.dirname(filename), newfilename))
  else:
    print("   Couldn't find name in %s" %filename)

def getHeaderData(data):
  '''
    Interprets the buffer "data" as a lrit/hrit header chain
  '''
  headers = []
  while len(data) > 0:
    type = data[0] if isinstance(data[0], int) else ord(data[0])
    size = struct.unpack(">H", data[1:3])[0]
    o = data[3:size]
    data = data[size:]
    td = parseHeader(type, o)
    headers.append(td)
    if td["type"] == 0:
      data = data[:td["headerlength"]-size]
  return headers

def parseHeader(type, data):
  '''
    Parses the binary "data" as a header defined by "type" and returns a python object
  '''
  if type == 0:
    filetypecode, headerlength, datalength = struct.unpack(">BIQ", data)
    return {"type":type, "filetypecode":filetypecode, "headerlength":headerlength, "datalength":datalength}
  elif type == 1:
    bitsperpixel, columns, lines, compression = struct.unpack(">BHHB", data)
    return {"type":type, "bitsperpixel":bitsperpixel, "columns":columns, "lines":lines, "compression":compression}

  elif type == 2:
    projname, cfac, lfac, coff, loff = struct.unpack(">32sIIII", data)
    return {"type":type, "projname":projname, "cfac":cfac, "lfac":lfac, "coff":coff, "loff":loff}

  elif type == 3:
    return {"type":type, "data":data}

  elif type == 4:
    return {"type":type, "filename":data}

  elif type == 5:
    days, ms = struct.unpack(">HI", data[1:])
    return {"type":type, "days":days, "ms":ms}

  elif type == 6:
    return {"type":type, "data":data}

  elif type == 7:
    return {"type":type, "data":data}

  elif type == 128:
    imageid, sequence, startcol, startline, maxseg, maxcol, maxrow = struct.unpack(">7H", data)
    return {"type":type, "imageid":imageid, "sequence":sequence, "startcol":startcol, "startline":startline, "maxseg":maxseg, "maxcol":maxcol, "maxrow":maxrow}

  elif type == 129:
    signature, productId, productSubId, parameter, compression = struct.unpack(">4sHHHB", data)
    return {"type":type, "signature":signature, "productId":productId, "productSubId":productSubId, "parameter":parameter, "compression":compression}

  elif type == 130:
    return {"type":type, "data":data}

  elif type == 131:
    flags, pixel, line = struct.unpack(">HBB", data)
    return {"type":type, "flags":flags, "pixel":pixel, "line":line}

  elif type == 132:
    return {"type":type, "data": data}
  else:
    return {"type":type}

def readHeader(f):
  '''
    Reads a reader from file and returns a tuple with its values
  '''
  global t
  type = ord(f.read(1))
  size = f.read(2)
  size = struct.unpack(">H", size)[0]
  data = f.read(size-3)

  if type == 0:
    filetypecode, headerlength, datalength = struct.unpack(">BIQ", data)
    return type, filetypecode, headerlength, datalength
  elif type == 1:
    bitsperpixel, columns, lines, compression = struct.unpack(">BHHB", data)
    return type, bitsperpixel, columns, lines, compression

  elif type == 2:
    projname, cfac, lfac, coff, loff = struct.unpack(">32sIIII", data)
    return type, projname, cfac, lfac, coff, loff

  elif type == 3:
    return type, data

  elif type == 4:
    return type, data

  elif type == 5:
    days, ms = struct.unpack(">HI", data[1:])
    return type, days, ms

  elif type == 6:
    return type, data

  elif type == 7:
    return type, data

  elif type == 128:
    imageid, sequence, startcol, startline, maxseg, maxcol, maxrow = struct.unpack(">7H", data)
    return type, imageid, sequence, startcol, startline, maxseg, maxcol, maxrow

  elif type == 129:
    signature, productId, productSubId, parameter, compression = struct.unpack(">4sHHHB", data)
    return type, signature, productId, productSubId, parameter, compression

  elif type == 130:
    return type, data

  elif type == 131:
    flags, pixel, line = struct.unpack(">HBB", data)
    return type, flags, pixel, line

  elif type == 132:
    return type, data

  else:
    return type

def printHeaders(headers, showStructuredHeader=False, showImageDataRecord=False):
  '''
    Prints a list of python object parsed headers in a Human Readable Format
  '''
  for head in headers:
    type = head["type"]
    if type == 0:
      print("Primary Header: ")
      if FILE_TYPE_CODE_NAME.has_key(head["filetypecode"]):
        print("   File Type Code: %s" % FILE_TYPE_CODE_NAME[head["filetypecode"]])
      else:
        print("   File Type Code: Unknown(%s)" % head["filetypecode"])
      print("   Header Length: %s" %head["headerlength"])
      print("   Data Field Length: %s" %head["datalength"])
    elif type == 1:
      print("Image Structure Header: ")
      print("   Bits Per Pixel: %s" %head["bitsperpixel"])
      print("   Columns: %s" %head["columns"])
      print("   Lines: %s" %head["lines"])
      if COMPRESSION_TYPE_NAME.has_key(head["compression"]):
        print("   Compression: %s" %COMPRESSION_TYPE_NAME[head["compression"]])
      else:
        print("   Compression: Unknown(%s)" %head["compression"])

    elif type == 2:
      print("Image Navigation Record")
      print("   Projection Name: %s" %head["projname"])
      print("   Column Scaling Factor: %s" %head["cfac"])
      print("   Line Scaling Factor: %s" %head["lfac"])
      print("   Column Offset: %s" %head["coff"])
      print("   Line Offset: %s" %head["loff"])

    elif type == 3:
      print("Image Data Function Record")
      if showImageDataRecord:
        print("   Data: %s" %head["data"])
      else:
        print("   Data: {HIDDEN}")

    elif type == 4:
      print("Annotation Record")
      print("   Filename: %s" %head["filename"])

    elif type == 5:
      print("Timestamp Record")
      print("   DateTime: %s" % (baseDate + datetime.timedelta(days=head["days"], milliseconds=head["ms"])))

    elif type == 6:
      print("Ancillary Text")
      print("   Data: ")
      t = head["data"].split(";")
      for i in t:
        print("     %s" %i)

    elif type == 7:
      print("Key Header")
      print("   Data: %s" %head["data"])

    elif type == 128:
      print("Segment Identification Header")
      print("   Image Id: %s" %head["imageid"])
      print("   Sequence: %s" %head["sequence"])
      print("   Start Column: %s" %head["startcol"])
      print("   Start Line: %s" %head["startline"])
      print("   Number of Segments: %s" %head["maxseg"])
      print("   Width: %s" %head["maxcol"])
      print("   Height: %s" %head["maxrow"])

    elif type == 129:
      print("NOAA Specific Header")
      print("   Signature: %s" %head["signature"])
      if NOAA_PRODUCT_ID.has_key(head["productId"]):
        product = NOAA_PRODUCT_ID[head["productId"]]
        print("   Product ID: %s" %product["name"])
        if product["sub"].has_key(head["productSubId"]):
          print("   Product SubId: %s" %product["sub"][head["productSubId"]])
        else:
          print("   Product SubId: Unknown(%s)" %head["productSubId"])
      else:
        print("   Product ID: Unknown(%s)" %head["productId"])
        print("   Product SubId: Unknown(%s)" %head["productSubId"])
      print("   Parameter: %s" %head["parameter"])
      if COMPRESSION_TYPE_NAME.has_key(head["compression"]):
        print("   Compression: %s" %COMPRESSION_TYPE_NAME[head["compression"]])
      else:
        print("   Compression: Unknown(%s)" %head["compression"])

    elif type == 130:
      print("Header Structured Record")
      if showImageDataRecord:
        t = head["data"].split("UI")
        print("   Data: ")
        for i in t:
          print("     %s" %i)
      else:
        print("   Data: {HIDDEN}")

    elif type == 131:
      print("Rice Compression Record")
      print("   Flags: %s" %head["flags"])
      print("   Pixel: %s" %head["pixel"])
      print("   Line: %s" %head["line"])

    elif type == 132: # Got in DCS Data
      print("DCS Filename: ")
      print("   Filename: %s" %head["data"])

    else:
      print("Type not mapped: %s" % type)
    print("")

def parseDCSHeader(header):
  address = header[:8]
  dt = header[9:20]
  status = chr(header[20]) if isinstance(header[20], (int)) else header[20]
  signal = header[21:23]
  frequencyoffset = header[23:25]
  modindexnormal = chr(header[25]) if isinstance(header[25], (int)) else header[20]
  dataqualnominal = chr(header[26]) if isinstance(header[26], (int)) else header[20]
  channel = header[27:31]
  sourcecode = header[31:33]
  return {
    "address": address.decode("utf-8"),
    "datetime": datetime.datetime.strptime(dt.decode("utf-8"), "%y%j%H%M%S"),
    "status": status,
    "signal": signal.decode("utf-8"),
    "frequencyoffset": frequencyoffset.decode("utf-8"),
    "modindexnormal": modindexnormal,
    "dataqualnominal": dataqualnominal,
    "channel": channel.decode("utf-8"),
    "sourcecode": sourcecode.decode("utf-8")
  }

def parseDCS(data):
  baseHeader = data[:64]
  data = data[64:]
  dcs = filter(None, data.split(b"\x02\x02\x18")) # Frame Marker
  d = []
  for i in dcs:
    dh = i[:33]
    dk = parseDCSHeader(dh)
    dk["data"] = i[33:]
    d.append(dk)

  return baseHeader, d

def dumpImage(filename):
  f = open(filename, "rb")
  try:
    k = readHeader(f)
    type, filetypecode, headerlength, datalength = k
  except:
    print("   Header 0 is corrupted for file %s" %filename)
    f.close()
    return

  if filetypecode != 0:
    print("The file %s is not an image container." %filename)
    f.close()
    return

  f.seek(0, 0)

  hdata = f.read(headerlength)
  headers = getHeaderData(hdata)

  data = f.read()

  f.close()

  compression = -1

  for i in headers:
    if i["type"] == 0:
      fileoffset = i["headerlength"]
      datasize = i["datalength"]
    if i["type"] == 1:
      imagedata = i
      if compression < i["compression"]:
        compression = i["compression"]
    elif i["type"] == 2:
      projdata = i
    elif i["type"] == 128:
      posdata = i
    elif i["type"] == 129:
      if compression < i["compression"]:
        compression = i["compression"]

  if compression == 2:
    outfilename = filename.replace(".lrit", ".jpg")
    print("JPEG Image, dumping to %s" %outfilename)
    f = open(outfilename, "wb")
    f.write(data)
    f.close()
  elif compression == 5:
    outfilename = filename.replace(".lrit", ".gif")
    print("GIF Image, dumping to %s" %outfilename)
    f = open(outfilename, "wb")
    f.write(data)
    f.close()
  elif compression == 1 or compression == 0:
    outfilename = filename.replace(".lrit", ".jpg")
    print("Decompressed image. Saving to %s" %outfilename)
    if imagedata["bitsperpixel"] == 8:
      if len(data) < imagedata["columns"] * imagedata["lines"]:
        msbytes = (imagedata["columns"] * imagedata["lines"]) - len(data)
        print("Missing %s bytes on image." %msbytes)
        data += "\x00" * msbytes
      im = Image.frombuffer("L", (imagedata["columns"], imagedata["lines"]), data, 'raw', "L", 0, 1)
      im.save(outfilename)
    elif imagedata["bitsperpixel"] == 1:
      if imagedata["columns"] % 8 != 0:
        im = Image.new("1", (imagedata["columns"], imagedata["lines"]))
        arr = im.load()
        x = 0
        y = 0
        for i in data:
          t = binary(i) if isinstance(i, int) else binary(ord(i))
          for z in range(8):
            arr[x, y] = 1 if t[z] == "1" else 0
            x+=1
            if x == imagedata["columns"]:
              x = 0
              y+= 1
            if y == imagedata["lines"]:
              break
      else:
        im = Image.frombuffer("1", (imagedata["columns"], imagedata["lines"]), data, 'raw', "1", 0, 1)

      im.save(outfilename)
    else:
      print("BPP not supported: %s" %imagedata["bitsperpixel"])