"""
Functions that anaylyze VDP related functions and provides comments on what the instructions are doing.
"""

import binaryninja

class VdpAnalysis:

    def __init__(self, view):
        self.view = view

    def vdp_reg_name(self, regNum):
        vdp_reg_names = [ "Mode1",
                        "Mode2",
                        "PlaneA_Name_Table_Location",
                        "Window_Name_TableLocation",
                        "PlaneB_Name_Table_Location",
                        "Sprite_Table_Location",
                        "Sprite_Pattern_Gen_Base_Addr",
                        "Background_Color",
                        "Reg8_Unused",
                        "Reg9_Unused",
                        "Horizontal_Interrupt_Control",
                        "Mode3",
                        "Mode4",
                        "Horizontal_Scroll_Data_Location",
                        "Nametable_Pattern_Generator_Base_Addr",
                        "Auto_Increment_Value",
                        "Plane_Size",
                        "Window_Plane_Horizontal_Position",
                        "Window_Plane_Vertical_Position",
                        "DMA_Length_0",
                        "DMA_Length_1",
                        "DMA_Source_0",
                        "DMA_Source_1",
                        "DMA_Source_2",
                        "Status"]
        if (regNum >= len(vdp_reg_names)) or (regNum < 0):
            return "REG_{}_INVALID".format(regNum)
        else:
            return vdp_reg_names[regNum]

    def decode_vdp_register_set(self, regNum, regVal):
        return "{} = {}".format(self.vdp_reg_name(regNum), hex(regVal))

    def comment_vdp_control_register(self, value_written):
        if ( (value_written & 0xe000) == 0x8000):
            registerToWrite = (value_written >> 8) & 0x1f
            dataToWrite = value_written & 0xff
            #c = "This is a single reg write of {} to VDP {}".format(hex(dataToWrite), registerToWrite)
            c = "VDP " + self.decode_vdp_register_set(registerToWrite, dataToWrite)
            return c
        else:
            print("First 3 bits not 100")
            return ""



    def comment_register_set(self, cur_inst, target_addr, value_written, value_size):
        if (target_addr != 0xc00004):
            # print("Not a write to VDP Control!")
            return

        if (value_size == 2):
            c = self.comment_vdp_control_register(value_written)
            self.view.set_comment_at(cur_inst.address, c)
        elif (value_size == 4):
            c1 = self.comment_vdp_control_register(value_written & 0xffff)
            c2 = self.comment_vdp_control_register( (value_written >> 16) & 0xffff)
            self.view.set_comment_at(cur_inst.address, c1 + " and " + c2)
        else:
            print("value_size is not 2 or 4")        

    def comment_vdp_instructions(self, mlilFunc):
        i = 0
        while i < len(mlilFunc):

            cur_inst = mlilFunc[i]
        
            if (cur_inst.operation == binaryninja.MediumLevelILOperation.MLIL_STORE):
                #print("MLIL Instr #{} is a store!: {}".format(i, cur_inst))
                #print(cur_inst.size)
                #print(cur_inst.operands)

                if ( ( type(cur_inst.operands[0]) == binaryninja.mediumlevelil.MediumLevelILConstPtr) and
                    ( type(cur_inst.operands[1]) == binaryninja.mediumlevelil.MediumLevelILConst) ):
                    target_addr = cur_inst.operands[0].constant
                    value_written = cur_inst.operands[1].constant
                    value_size = cur_inst.operands[1].size

                    #print("Const ptr target = {}, size={}, val={}".format(hex(target_addr), value_size, hex(value_written)))
                    self.comment_register_set(cur_inst, target_addr, value_written, value_size)

            i += 1



