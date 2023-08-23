import os
import xml.etree.ElementTree as ETXML

def generate_odt_map(measurement_list):
    odt_map = []
    max_odt = 50
    for i in range(max_odt):
        odt_map.append([[],7,''])
    
    # 4Byte
    for m in measurement_list:
        if m[1] in ('SLONG','ULONG'):
            for i in range(max_odt):
                if odt_map[i][1] >= 4:
                    odt_map[i][0].append(m[0])
                    odt_map[i][1] -= 4
                    odt_map[i][2]+='L'
                    break
                else:
                    pass
    # 2Byte
    for m in measurement_list:
        if m[1] in ('SWORD','UWORD'):
            for i in range(max_odt):
                if odt_map[i][1] >= 2:
                    odt_map[i][0].append(m[0])
                    odt_map[i][1] -= 2
                    odt_map[i][2]+='H'
                    break
                else:
                    pass
    # 1Byte
    for m in measurement_list:
        if m[1] == 'UBYTE':
            for i in range(max_odt):
                if odt_map[i][1] >= 1:
                    odt_map[i][0].append(m[0])
                    odt_map[i][1] -= 1
                    odt_map[i][2]+='B'
                    break
                else:
                    pass
    # 남은공간은 Byte로 채움(Python unpack 처리 시 편의를 위해)
    for i in range(len(odt_map)):
        for j in range(odt_map[i][1]):
            odt_map[i][2]+='B'
    return odt_map

def get_odt_map(evt_file):
    tree = ETXML.parse(evt_file)
    root=tree.getroot()
    measurements = root.findall('.//Measurement')
    measurement_list = []
    for measurement in measurements:
        measurement_list.append([measurement.findall('identName')[0].text,measurement.findall('Datatype')[0].text])

    return generate_odt_map(measurement_list)    


EVT_DATAS = {}
COMMAND = command
EVT_FILE_PATH = evtFolder
updated_evts = ''
evt_files = []

if COMMAND.upper() == 'LOAD' or COMMAND.upper() == 'RELOAD':
    evtList = os.listdir(EVT_FILE_PATH)
    for evt in evtList:
        filename = os.path.splitext(evt)[0]
        EVT_DATAS[filename] = get_odt_map(EVT_FILE_PATH + '/' + filename + '.evt')
        evt_files.append(filename)

if evt_files is not None:
    updated_evt = ','.join(evt_files)
