from binaryninja import (binaryview, Architecture, core, SegmentFlag,
                         SectionSemantics, Symbol, SymbolType, log)
import struct
import traceback


class GenesisView(binaryview.BinaryView):
    name = 'SG/SMD'
    long_name = 'SEGA Genesis/Megadrive ROM'

    def __init__(self, data):
        binaryview.BinaryView.__init__(self, parent_view=data,
                                       file_metadata=data.file)
        self.platform = Architecture['M68000'].standalone_platform
        self.raw = data

    @classmethod
    def is_valid_for_data(self, data):

        console_name = data[0x100:0x110].decode('utf-8')
        if ('SEGA MEGA DRIVE' not in console_name.upper()) and ('SEGA GENESIS' not in console_name.upper()):
            # print("No magic SEGA word found in data")
            return False

        rom_start = struct.unpack('>I', data[0x1a0:0x1a4])[0]
        if rom_start != 0:
            # print("rom_start is invalid for Genesis")
            return False

        # Previous versions looked at rom_start address (0x1a0).  Didn't work for the first Genesis
        # ROM I tried (Michael Jackson's Moonwalker).  So I've removed that check...

        software_type = data[0x180:0x182].decode('utf-8')
        if (software_type != "GM"):
            # print("Software type not GM for Genesis Game")
            return False

        return True

    @classmethod
    def get_load_settings_for_data(self, data):
        load_settings_id = core.BNGetUniqueIdentifierString()
        return core.BNAllocString(load_settings_id)

    def create_segments(self):
        self.add_auto_segment(
            0, len(self.raw), 0, len(self.raw),
            SegmentFlag.SegmentReadable | SegmentFlag.SegmentExecutable
        )

        # RAM Segment
        self.add_auto_segment(
            0xff0000, 0xffff, 0, 0,
            SegmentFlag.SegmentReadable | SegmentFlag.SegmentWritable
        )

        # Z80 Segment
        self.add_auto_segment(
            0xa00000, 0xffff, 0, 0,
            SegmentFlag.SegmentReadable | SegmentFlag.SegmentWritable
        )

        # System IO
        self.add_auto_segment(
            0xa10000, 0xfff, 0, 0,
            SegmentFlag.SegmentReadable | SegmentFlag.SegmentWritable
        )

        # IO Control
        self.add_auto_segment(
            0xa11000, 0xffff, 0, 0,
            SegmentFlag.SegmentReadable | SegmentFlag.SegmentWritable
        )
 
        # Copy-protection register Segment
        self.add_auto_segment(
            0xa14000, 0x10, 0, 0,
            SegmentFlag.SegmentReadable | SegmentFlag.SegmentWritable
        )

        # VDP Segment
        self.add_auto_segment(
            0xc00000, 0x20, 0, 0,
            SegmentFlag.SegmentReadable | SegmentFlag.SegmentWritable
        )


    def create_sections(self):
        self.add_auto_section(
            "header", 0, 8,
            SectionSemantics.ReadOnlyDataSectionSemantics)
        self.add_auto_section(
            "ivt", 8, 248,
            SectionSemantics.ReadOnlyDataSectionSemantics)
        self.add_auto_section(
            "info", 256, 256,
            SectionSemantics.ReadOnlyDataSectionSemantics)
        self.add_auto_section(
            "code", 512, len(self.raw)-512,
            SectionSemantics.ReadOnlyCodeSectionSemantics)
        self.add_auto_section(
            "ram", 0xff0000, 0xffff,
            SectionSemantics.ReadWriteDataSectionSemantics)
        self.add_auto_section(
            "z80", 0xa00000, 0xffff,
            SectionSemantics.ReadWriteDataSectionSemantics)
        self.add_auto_section(
            "sys_io", 0xa10000, 0xfff,
            SectionSemantics.ReadWriteDataSectionSemantics)
        self.add_auto_section(
            "io_control", 0xa11000, 0xfff,
            SectionSemantics.ReadWriteDataSectionSemantics)
        self.add_auto_section(
            "vdp", 0xc00000, 0x20,
            SectionSemantics.ReadWriteDataSectionSemantics)

    def create_functions(self):
        for idx in range(4, 252, 4):
            addr = struct.unpack('>I', self.raw[idx:idx+4])[0]
            self.add_function(addr)
            if idx == 4:
                self.add_entry_point(addr)
                self.define_auto_symbol(
                    Symbol(SymbolType.FunctionSymbol, addr, "_start")
                )
            elif idx == 112:
                self.define_auto_symbol(
                    Symbol(SymbolType.FunctionSymbol, addr, "hblank")
                )
            elif idx == 120:
                self.define_auto_symbol(
                    Symbol(SymbolType.FunctionSymbol, addr, "vblank")
                )

    def create_datatype_and_name(self, addr, name, _type):
        self.define_user_data_var(addr, _type)
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, addr, name))

    def create_vector_table(self):
        uint32 = self.parse_type_string("uint32_t")[0]
        self.create_datatype_and_name(8, 'VectOffBusError', uint32)
        self.create_datatype_and_name(12, 'VectOffAddressError', uint32)
        self.create_datatype_and_name(16, 'VectOffIllegalInstruction', uint32)
        self.create_datatype_and_name(20, 'VectOffDivisionByZero', uint32)
        self.create_datatype_and_name(24, 'VectOffChkException', uint32)
        self.create_datatype_and_name(28, 'VectOffTrapVException', uint32)
        self.create_datatype_and_name(32, 'VectOffPrivilegeViolation', uint32)
        self.create_datatype_and_name(36, 'VectOffTraceException', uint32)
        self.create_datatype_and_name(40, 'VectOffLineAEmulator', uint32)
        self.create_datatype_and_name(44, 'VectOffLineFEmulator', uint32)
        self.create_datatype_and_name(48, 'VectUnused00', uint32)
        self.create_datatype_and_name(52, 'VectUnused01', uint32)
        self.create_datatype_and_name(56, 'VectUnused02', uint32)
        self.create_datatype_and_name(60, 'VectUnused03', uint32)
        self.create_datatype_and_name(64, 'VectUnused04', uint32)
        self.create_datatype_and_name(68, 'VectUnused05', uint32)
        self.create_datatype_and_name(72, 'VectUnused06', uint32)
        self.create_datatype_and_name(76, 'VectUnused07', uint32)
        self.create_datatype_and_name(80, 'VectUnused08', uint32)
        self.create_datatype_and_name(84, 'VectUnused09', uint32)
        self.create_datatype_and_name(88, 'VectUnused10', uint32)
        self.create_datatype_and_name(92, 'VectUnused11', uint32)
        self.create_datatype_and_name(96, 'VectOffSpuriousException', uint32)
        self.create_datatype_and_name(100, 'VectOffIrqL1', uint32)
        self.create_datatype_and_name(104, 'VectOffIrqL2', uint32)
        self.create_datatype_and_name(108, 'VectOffIrqL3', uint32)
        self.create_datatype_and_name(112, 'VectOffIrqL4', uint32)
        self.create_datatype_and_name(116, 'VectOffIrqL5', uint32)
        self.create_datatype_and_name(120, 'VectOffIrqL6', uint32)
        self.create_datatype_and_name(124, 'VectOffIrqL7', uint32)
        self.create_datatype_and_name(128, 'VectOffTrap00', uint32)
        self.create_datatype_and_name(132, 'VectOffTrap01', uint32)
        self.create_datatype_and_name(136, 'VectOffTrap02', uint32)
        self.create_datatype_and_name(140, 'VectOffTrap03', uint32)
        self.create_datatype_and_name(144, 'VectOffTrap04', uint32)
        self.create_datatype_and_name(148, 'VectOffTrap05', uint32)
        self.create_datatype_and_name(152, 'VectOffTrap06', uint32)
        self.create_datatype_and_name(156, 'VectOffTrap07', uint32)
        self.create_datatype_and_name(160, 'VectOffTrap08', uint32)
        self.create_datatype_and_name(164, 'VectOffTrap09', uint32)
        self.create_datatype_and_name(168, 'VectOffTrap10', uint32)
        self.create_datatype_and_name(172, 'VectOffTrap11', uint32)
        self.create_datatype_and_name(176, 'VectOffTrap12', uint32)
        self.create_datatype_and_name(180, 'VectOffTrap13', uint32)
        self.create_datatype_and_name(184, 'VectOffTrap14', uint32)
        self.create_datatype_and_name(188, 'VectOffTrap15', uint32)
        self.create_datatype_and_name(192, 'VectUnused12', uint32)
        self.create_datatype_and_name(196, 'VectUnused13', uint32)
        self.create_datatype_and_name(200, 'VectUnused14', uint32)
        self.create_datatype_and_name(204, 'VectUnused15', uint32)
        self.create_datatype_and_name(208, 'VectUnused16', uint32)
        self.create_datatype_and_name(212, 'VectUnused17', uint32)
        self.create_datatype_and_name(216, 'VectUnused18', uint32)
        self.create_datatype_and_name(220, 'VectUnused19', uint32)
        self.create_datatype_and_name(224, 'VectUnused20', uint32)
        self.create_datatype_and_name(228, 'VectUnused21', uint32)
        self.create_datatype_and_name(232, 'VectUnused22', uint32)
        self.create_datatype_and_name(236, 'VectUnused23', uint32)
        self.create_datatype_and_name(240, 'VectUnused24', uint32)
        self.create_datatype_and_name(244, 'VectUnused25', uint32)
        self.create_datatype_and_name(248, 'VectUnused26', uint32)
        self.create_datatype_and_name(252, 'VectUnused27', uint32)

    def create_information(self):
        uint32 = self.parse_type_string('uint32_t')[0]
        uint16 = self.parse_type_string('uint16_t')[0]
        char12 = self.parse_type_string('char foo[12]')[0]
        char14 = self.parse_type_string('char foo[14]')[0]
        char16 = self.parse_type_string('char foo[16]')[0]
        char48 = self.parse_type_string('char foo[48]')[0]
        char52 = self.parse_type_string('char foo[52]')[0]
        self.create_datatype_and_name(256, 'ConsoleName', char16)
        self.create_datatype_and_name(272, 'Copyright', char16)
        self.create_datatype_and_name(288, 'DomesticName', char48)
        self.create_datatype_and_name(336, 'InternationalName', char48)
        self.create_datatype_and_name(384, 'SerialRevision', char14)
        self.create_datatype_and_name(398, 'Checksum', uint16)
        self.create_datatype_and_name(400, 'IoSupport', char16)
        self.create_datatype_and_name(416, 'RomStart', uint32)
        self.create_datatype_and_name(420, 'RomEnd', uint32)
        self.create_datatype_and_name(424, 'RamStart', uint32)
        self.create_datatype_and_name(428, 'RamEnd', uint32)
        self.create_datatype_and_name(432, 'SramInfo', char12)
        self.create_datatype_and_name(444, 'Notes', char52)
        self.create_datatype_and_name(496, 'Region', char16)
        
        # IO registers
        self.create_datatype_and_name(0xa10000, 'VersionRegister', uint16)
        self.create_datatype_and_name(0xa10002, 'Controller1Data', uint16)
        self.create_datatype_and_name(0xa10004, 'Controller2Data', uint16)
        self.create_datatype_and_name(0xa10006, 'ExpansionPortData', uint16)
        self.create_datatype_and_name(0xa10008, 'Controller1Control', uint16)
        self.create_datatype_and_name(0xa1000a, 'Controller2Control', uint16)
        self.create_datatype_and_name(0xa1000c, 'ExpansionPortControl', uint16)
        self.create_datatype_and_name(0xa1000e, 'Controller1SerialTx', uint16)
        self.create_datatype_and_name(0xa10010, 'Controller1SerialRx', uint16)
        self.create_datatype_and_name(0xa10012, 'Controller1SerialControl', uint16)
        self.create_datatype_and_name(0xa10014, 'Controller2SerialTx', uint16)
        self.create_datatype_and_name(0xa10016, 'Controller2SerialRx', uint16)
        self.create_datatype_and_name(0xa10018, 'Controller2SerialControl', uint16)
        self.create_datatype_and_name(0xa1001a, 'ExpansionPortSerialTx', uint16)
        self.create_datatype_and_name(0xa1001c, 'ExpansionPortSerialRx', uint16)
        self.create_datatype_and_name(0xa1001e, 'ExpansionPortSerialControl', uint16)

        self.create_datatype_and_name(0xa11000, 'MemoryModeRegister', uint16)
        self.create_datatype_and_name(0xa11100, 'Z80BusRequest', uint16)
        self.create_datatype_and_name(0xa11200, 'Z80Reset', uint16)
        self.create_datatype_and_name(0xa14000, 'TMSS', uint16)
        
        # VDP registers
        self.create_datatype_and_name(0xc00000, 'VdpData', uint16)
        self.create_datatype_and_name(0xc00002, 'VdpDataMirror', uint16)
        self.create_datatype_and_name(0xc00004, 'VdpControl', uint16)
        self.create_datatype_and_name(0xc00006, 'VdpControlMirror', uint16)
        self.create_datatype_and_name(0xc00008, 'VdpHvCounter0', uint16)
        self.create_datatype_and_name(0xc0000a, 'VdpHvCounter1', uint16)
        self.create_datatype_and_name(0xc0000c, 'VdpHvCounter2', uint16)
        self.create_datatype_and_name(0xc0000e, 'VdpHvCounter3', uint16)
        self.create_datatype_and_name(0xc00011, 'VdpPsg0', uint16)
        self.create_datatype_and_name(0xc00013, 'VdpPsg1', uint16)
        self.create_datatype_and_name(0xc00015, 'VdpPsg2', uint16)
        self.create_datatype_and_name(0xc00017, 'VdpPsg3', uint16)
        self.create_datatype_and_name(0xc0001c, 'VdpDebugReg', uint16)
        self.create_datatype_and_name(0xc0001e, 'VdpDebugRegMirror', uint16)

    def create_header(self):
        uint32 = self.parse_type_string("uint32_t")[0]
        self.create_datatype_and_name(0, 'OffInitialStack', uint32)
        self.create_datatype_and_name(4, 'OffProgramStart', uint32)

    def init(self):
        try:
            self.create_segments()
            self.create_sections()
            self.create_header()
            self.create_vector_table()
            self.create_information()
            self.create_functions()
            return True
        except Exception:
            log.log_error(traceback.format_exc())
            return False

    def perform_is_executable(self):
        return True

    def perform_get_entry_point(self):
        return struct.unpack('>I', self.raw[4:8])[0]
