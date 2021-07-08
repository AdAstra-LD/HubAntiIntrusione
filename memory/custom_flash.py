"""
.. module:: flash

*****
Flash
*****

This module contains class definitions to read and write the MCU internal flash


    """

import streams

class FlashFileStream(streams.FileStream):
    """
=========================
The FlashFileStream class
=========================

.. class:: FlashFileStream(start_address,size)

        This class creates an in memory buffer of size *size* bytes that is filled with the content
        of the internal flash starting from address *start_address*
        
        Subsequent operations of read and write are performed on the memory buffer. To actually write the memory buffer
        to the internal flash a call to flush() is needed.

        The memory buffer can also be accessed via bracket notation. The following is valid syntax: ::

            f = flash.FlashFileStream(0x0800000,512)
            f[0] = 1
            x = f[10:20]

    """

    def __init__(self,start_address,size,bb=None):
        streams.FileStream.__init__(self,str(start_address))
        self.size=size
        self.addr = start_address
        if bb is None:
            bb = bytearray(size)
        self.bb = __read_flash(self.addr,self.size, bb)

    def __getitem__(self, key):
        if type(key)==PSLICE:
            if key[2]!=1:
                raise UnsupportedError
            return self.bb[key[0]:key[1]]
        elif type(key)==PSMALLINT:
            return self.bb[key]
        raise IndexError

    def __setitem__(self, key,value):
        if type(key)==PSLICE:
            if key[2]!=1:
                raise UnsupportedError
            self.bb[key[0]:min(key[1],self.size)]=value
        elif type(key)==PSMALLINT:
            self.bb[key]=value
        else:
            raise IndexError

    def _readbuf(self,buf,size=1,ofs=0):
        if self.curpos>=self.size: #eof
            return 0
        size = min(self.size-self.curpos,size)
        bb = self.bb[self.curpos:self.curpos+size]
        buf[ofs:ofs+size]=bb
        self.curpos+=size
        return size

    def __len__(self):
        return self.size
        
    def write(self,buf):
        """
.. method:: write(buf)
        
        Writes the content of *buf* at the current file position, checking for overflow.
        
        """
        if type(buf)==PSMALLINT or type(buf)==PINTEGER:
            n=buf
            buf = bytearray(4)
            buf[0]=n&0xff
            buf[1]=(n>>8)&0xff
            buf[2]=(n>>16)&0xff
            buf[3]=(n>>24)&0xff
            
        ll = min(len(buf),self.size)
        for i in range(ll):
            self.bb[self.curpos]=__byte_get(buf,i)
            self.curpos+=1
        return ll
    
    def read_int(self):
        """
.. method:: read_int()
        
        Read 4 bytes at the current position and return the corresponding 32 bit integer.
        
        """
        if self.size-self.curpos>4:
            n= (self.bb[self.curpos]|(self.bb[self.curpos+1]<<8)|(self.bb[self.curpos+2]<<16)|(self.bb[self.curpos+3]<<24))
            self.curpos+=4
            return n
        raise ValueError

    def flush(self):
        """
.. method:: flush()
        
        Write the memory buffer to flash. It can be VERY slow because the sector(s) of flash interested by the write operation must be erased first.
        
        """
        __write_flash(self.addr,self.bb)

    def close(self):
        """
.. method:: close()

        Free memory buffer

        """
        self.bb=None
        
#------------------------------------------------------------------#
#---------------------- E X T E N S I O N S -----------------------#
#------------------------------------------------------------------#
    
    def __str__(self):
        return self.bb
        
    def read_smallint(self):
        """
.. method:: read_smallint()
        
        Read 2 bytes at the current position and return the corresponding 16 bit integer.
        
        """
        if self.size - self.curpos > 2:
            n = (self.bb[self.curpos] | (self.bb[self.curpos+1]<<8))
            self.curpos += 2
            return n
        raise ValueError
        
    def read_byte(self):
        """
.. method:: read_byte()
        
        Read 1 byte at the current position and return it.
        
        """
        if self.size-self.curpos>1:
            n= (self.bb[self.curpos])
            self.curpos+=1
            return n
        raise ValueError
            
    def read_bytes(self, count):
        """
.. method:: read_bytes()
        
        Read at most *count* bytes starting at the current position and return a list of all the bytes read.
        
        """
        listbytes = []
        #print("size:" + str(self.size))
        #print("curpos:" + str(self.curpos))
        for x in range(min(count, self.size-self.curpos)):
            #print("appending: " + str(self.bb[self.curpos]))
            listbytes.append(self.bb[self.curpos])
            self.curpos += 1
            
        return listbytes
        
    def erase(self, startAddr, endAddr, immediate = False):
        """
.. method:: erase(startAddr, endAddr)
        
        Zero-fill the memory buffer from *startAddr* to *endAddr*.
        
        """
        for i in range(endAddr - startAddr +1):
            self.bb[startAddr] = 0
            self.curpos+=1
            
        if immediate:
            self.flush()
            
    def move_cursor(self, address):
        """
.. method:: move_cursor()
        
        Moves internal memory cursor to the specified *address*.
        
        """
        if address < 0 or address+1 > self.size:
            raise ValueError
        
        self.curpos = address