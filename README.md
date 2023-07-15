# bn-genesis

## Description

Suite of Binary Ninja plugins that assist with SEGA Genesis ROM hacking
* Load SEGA Genesis/Megadrive ROM's
    * Use .bin format roms. These are essentially raw memory dumps, data matches what you see in Genesis debugger
    * The other popular Genesis ROM format is SMD (Super Mega Drive). These have the data interleaved (probably
      some artifact of hardware limitations of the device that dumped the ROMs).  But this format sucks for
      reverse engineering or ROM hacking, so convert them to .bin
* Write m68k assembly and quickly apply a patch at a specified offset
* Fixup ROM checksums
* Enumerate call tables (deprecated)
    * Vector35 addressed issues with its core and now tables are recognized by auto-analysis 

![demo bn-genesis](screencap.gif)

## Dependencies

* Assembler plugin requires `gcc-m68k-linux-gnu` (Ubuntu or Debian)
* Loader requires the third party m68k processor module, which can be found [here](https://github.com/wrigjl/binaryninja-m68k)

## Directions

If you have the dependencies installed, you can just load a Genesis ROM.  If your ROM is successfully loaded you will
have an additional item in the dropdown above the code listing that is normally just RAW (it will say Sega Genesis / Megadrive ROM),
and you should have additional segments and sections that are specific to the Genesis.

