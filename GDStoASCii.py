# -*- coding: utf-8 -*-
"""
Created on Thu May 30 22:26:44 2019

Parse GDSii format to ASCII file, final output will be records


@author: actwind
"""
import struct
import functools
# GDS file is consist of records, each record is one object... Finally, the whole GDS file is from 
# Record, basic record can be named tuple, but here We wanted to do
# Do we need to do something for the special typesw
RECTYPEdict={0x00 : 'HEADER',
                0x01 : 'BGNLIB',
                0x02 : 'LIBNAME',
                0x03 : 'UNITS',
                0x04 : 'ENDLIB',
                0x05 : 'BGNSTR',
                0x06 : 'STRNAME',
                0x07 : 'ENDSTR',
                0x08 : 'BOUNDARY',
                0x09 : 'PATH',
                0x0A : 'SERF',
                0x0B : 'AREF',
                0x0C : 'TEXT',
                0x0D : 'LAYER',
                0x0E : 'DATATYPE',
                0x0F : 'WIDTH',
                0x10 : 'XY',
                0x11 : 'ENDEL',
                0x12 : 'SNAME',
                0x13 : 'COLROW',
                0x15 : 'NODE',
                0x16 : 'TEXTTYPE', 
                0x17 : 'PRESENTATION', 
                0x19 : 'STRING', 
                0x1A : 'STRANS', 
                0x1B : 'MAG', 
                0x1C : 'ANGLE', 
                0x1F : 'REFLIBS', 
                0x20 : 'FONTS', 
                0x21 : 'PATHTYPE', 
                0x22 : 'GENERATIONS', 
                0x23 : 'ATTRATABLE', 
                0x26 : 'ELFLAGS', 
                0x2A : 'NODETYPE', 
                0x2B : 'PROPATTR', 
                0x2C : 'PROPVALUE', 
                0x2D : 'BOX', 
                0x2E : 'BOXTYPE', 
                0x2F : 'PLEX', 
                0x32 : 'TAPENUM', 
                0x33 : 'TAPECODE', 
                0x36 : 'FORMAT', 
                0x37 : 'MASK', 
                0x38 : 'ENDMASKS',
                0x39 : 'LIBDIRSIZE',
                0x40 : 'SRFNAME',
                0x41 : 'LIBSECUR'}
DATASIZEdict={0x00: 1, 0x01: 1, 0x02: 2, 0x03: 4, 0x04: 4, 0x05: 8, 0x06: 1}
DATACODEdict={0x02:'>h',0x03:'>l',0x04:'>f',0x05:'>d',0x06:'>c'}
def ReadOnly(storage_name):
    def propGetter(instance):
        return instance.__dict__[storage_name]
    return property(fget=propGetter)
def decode(coding):
    return functools.partial(struct.unpack,coding)

DATADECODERdict={key:decode(value) for key,value in DATACODEdict.items()}
DATADECODERdict[0x01]=lambda x:x

class record(object):
    # General Record class
    # Server most important Record is a little different
    #size=ReadOnly('_size')
    rectype=ReadOnly('_type')
    datatype=ReadOnly('_datatype')
    data=ReadOnly('_data')
    def __init__(self,Type,DataType,data):
        #self._size=Size
        self._type=Type
        self._datatype=DataType
        self._data=data
    # Make the property class to let all the ReadOnly data easily
    @classmethod
    def StrRecord(cls,Size,Type,DataType,string):
        pass
    @classmethod
    def CreateRecord(cls,_bytes):
        # bytes works as sequence, but its bytes[i] return int, while bytes[i:i+1] return bytes
        _bytes=bytes(_bytes)        # Copy of muttable obj to aviod side effect
        rectype=RECTYPEdict[struct.unpack('>b',_bytes[0:1])[0]]
        datatype=struct.unpack('>b',_bytes[1:2])[0]
        datasize=DATASIZEdict[datatype]
        if len(_bytes)==2 and datatype==0:  #Empty Data
            data=None
        else:
            data=[_bytes[i:i+datasize] for i in range(2,len(_bytes),datasize)]
            data=[val[0] for val in map(DATADECODERdict[datatype],data)]
  #          data=[DATADECODERdict[datatype](_bytes[i:i+datasize]) for i in range(2,len(_bytes),datasize)]
        if datatype == 6: # string
            data="".join([byte.decode("utf-8") for byte in data])
        return cls(rectype,datatype,data)
        # if it's empty
    def validation(self):
        '''Try to validate the rectype, datatype
        '''
        pass
    
    def __repr__(self):
        return "record('{}',{},{})".format(self.rectype,self.datatype,self.data)
    

# Read File And Split it into small byts, top level object, represent the 
class gds(object):
    file=ReadOnly('_file')
    records=ReadOnly('_records')
    def __init__(self,file,records):
        self._file=file
        self._records=records
    @classmethod
    def open(cls,file):
        records=[]
        with open(file,'rb') as f:
            while True:
                recsize=struct.unpack('>h',f.read(2))[0]
                rec=record.CreateRecord(f.read(recsize-2))
                records.append(rec)
                if rec.rectype== 'ENDLIB':
                    break
        return cls(file,records)
    # GDS is sequence of reocrd, and also iterable
    def __iter__(self):
        return iter(self.records)
    def __getitem__(self,slice):
        return self.records[slice]
        
        