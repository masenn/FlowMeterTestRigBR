export AS_BUILD_MODE := Build
export AS_SYSTEM_PATH := C:/Program\ Files/BRAutomation4/AS/System
export AS_BIN_PATH := C:/Program Files/BRAutomation4/AS412/bin-en
export AS_INSTALL_PATH := C:/Program\ Files/BRAutomation4/AS412
export AS_PATH := C:/Program Files/BRAutomation4/AS412
export AS_VC_PATH := C:/Program\ Files/BRAutomation4/AS412/AS/VC
export AS_GNU_INST_PATH := C:/Program\ Files/BRAutomation4/AS412/AS/gnuinst/V4.1.2
export AS_STATIC_ARCHIVES_PATH := C:/Users/sennm/Downloads/FlowMeterTestRigBR/FLowMeterTestRig/Temp/Archives/PPC2200/5PPC2200_AL18_000
export AS_CPU_PATH := C:/Users/sennm/Downloads/FlowMeterTestRigBR/FLowMeterTestRig/Temp/Objects/PPC2200/5PPC2200_AL18_000
export AS_CPU_PATH_2 := C:/Users/sennm/Downloads/FlowMeterTestRigBR/FLowMeterTestRig/Temp/Objects/PPC2200/5PPC2200_AL18_000
export AS_TEMP_PATH := C:/Users/sennm/Downloads/FlowMeterTestRigBR/FLowMeterTestRig/Temp
export AS_BINARIES_PATH := C:/Users/sennm/Downloads/FlowMeterTestRigBR/FLowMeterTestRig/Binaries
export AS_PROJECT_CPU_PATH := C:/Users/sennm/Downloads/FlowMeterTestRigBR/FLowMeterTestRig/Physical/PPC2200/5PPC2200_AL18_000
export AS_PROJECT_CONFIG_PATH := C:/Users/sennm/Downloads/FlowMeterTestRigBR/FLowMeterTestRig/Physical/PPC2200
export AS_PROJECT_PATH := C:/Users/sennm/Downloads/FlowMeterTestRigBR/FLowMeterTestRig
export AS_PROJECT_NAME := FLowMeterTestRig
export AS_PLC := 5PPC2200_AL18_000
export AS_TEMP_PLC := 5PPC2200_AL18_000
export AS_USER_NAME := sennm
export AS_CONFIGURATION := PPC2200
export AS_COMPANY_NAME := \ 
export AS_VERSION := 4.12.6.106
export AS_WORKINGVERSION := 4.12


default: \
	$(AS_CPU_PATH)/Visu.br \
	vcPostBuild_Visu \



include $(AS_CPU_PATH)/Visu/Visu.mak
