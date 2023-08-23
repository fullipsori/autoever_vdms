import cantools
import pandas as pd

def parsed_dbc(filepath):
    canDB = cantools.db.load_file(filepath)
    
    message_db=[]
    lines = []
    sigs=[]
    sigs_comment=[]
    sigs_spn=[]
    sigs_mtable=[]
    sigs_multi_id=[]
    msgs_id=[]
    msgs=[]
    msg_id=['msg_name','msg_id','msg_is_extended_frame','msg_length','msg_comment']
    sig_id=['sig_name','sig_start','sig_length','sig_byte_order','sig_is_signed','sig_initial','sig_scale','sig_offset','sig_minimum','sig_maximum','sig_unit','sig_is_multiplexer','sig_multiplexer_ids','sig_mtable','sig_spn','sig_comments']
 
    for message in canDB.messages:
        for signal in message.signals:
            sigs.append(str(signal))
            sigs_comment.append(str(signal.comments))
            sigs_spn.append(str(signal.spn))
            sigs_multi_id.append(str(signal.multiplexer_ids))
            sigs_mtable.append(str(signal.choices))
            msgs.append(str(message))
            msgs_id.append(str(message._frame_id))
            
    # print(sigs)
    msg_list=pd.DataFrame(msgs)
    msg_list[1]=msg_list[0].str.split("'").str[1]
    msg_list[2]=msgs_id
    # msg_list[2]=msg_list[0].str.split(",").str[1]
    # msg_list[2]=(msg_list[0].str.split(",").str[1]).str.replace('0x','')
    msg_list[3]=msg_list[0].str.split(",").str[2]
    msg_list[4]=msg_list[0].str.split(",").str[3]
    msg_list[5]=msg_list[0].str.split(",").str[4]
    msg_list[5]=msg_list[5].str.replace(")","")
    msg_list.drop(columns=[0],axis=1,inplace=True)
    msg_list.columns=msg_id
    # signal_list=pd.DataFrame(lines)
    sig_list=pd.DataFrame(sigs)
    # print(lines)
    # signal_list=signal_list[0].str.split(",",expand=True)
    # print(sigs)
    sig_list[1]=sig_list[0].str.split("'").str[1]
    sig_list[2]=sig_list[0].str.split(",").str[1]
    sig_list[3]=sig_list[0].str.split(",").str[2]
    sig_list[4]=sig_list[0].str.split(",").str[3]
    sig_list[4]=sig_list[4].str.replace("'","")
    sig_list[5]=sig_list[0].str.split(",").str[4]
    sig_list[6]=sig_list[0].str.split(",").str[5]
    sig_list[7]=sig_list[0].str.split(",").str[6]
    sig_list[8]=sig_list[0].str.split(",").str[7]
    sig_list[9]=sig_list[0].str.split(",").str[8]
    sig_list[10]=sig_list[0].str.split(",").str[9]
    sig_list[11]=sig_list[0].str.split(",").str[10]
    sig_list[11]=sig_list[11].str.replace("'","")
    sig_list[12]=sig_list[0].str.split(",").str[11]
    # sig_list[13]=sig_list[0].str.split(",").str[12]
    # sig_list[13]=sig_list[13].str.replace("[","")
    # sig_list[13]=sig_list[13].str.replace("]","")

    sig_list[13]=sigs_multi_id
    sig_list[13]=sig_list[13].str.replace("[","")
    sig_list[13]=sig_list[13].str.replace("]","")
    sig_list[14]=sigs_mtable
    sig_list[15]=sigs_spn
    sig_list[16]=sigs_comment
    sig_list.drop(columns=[0],axis=1,inplace=True)
    sig_list.columns=sig_id
    dbc_list=pd.concat([msg_list,sig_list],axis=1)
    # print(sigs_mtable)
    dbc_list=dbc_list.apply(lambda x: x.str.strip(), axis = 1)
    return dbc_list        

# import sys
# sys.stdout.reconfigure(encoding='utf-8')

# pd.set_option('display.max_rows',None)
# pd.set_option('display.max_columns',None)
# pd.set_option('display.width',1000)

#input : vehicleKeyID, signals
# vehicleKeyID = 219054
# signals = ['CF_Clu_Odometer', 'CF_Vcu_GarSelDisp', 'CR_Mcu_VehSpdDec_Kph', 'CR_Mcu_VehSpd_Kph', 'CF_OBC_DCChargingStat', 'CF_Bms_ChgSts']

# pd.set_option('mode.chained_assignment',  None)
#
# dbcFileName = str(vehicleKeyID) + '.dbc'
# dbcfilepath = 'd:/projects/vdms/resources/dbc/' + dbcFileName
# dbc_list = parsed_dbc(dbcfilepath)
#
# sig_data = dbc_list[dbc_list['sig_name'].isin(signals)]
# sig_data['vehicleKeyID'] = vehicleKeyID 
# converted = sig_data.astype({'msg_id':'int', 'msg_is_extended_frame':'str', 'msg_length':'int', 'sig_start':'int', 'sig_length':'int', 'sig_is_signed':'str', 'sig_initial':'int', 'sig_scale':'float', 'sig_offset':'float', 'sig_is_multiplexer':'str'})
#
# dbc_json = f'{{"dbcList": {converted.to_json(orient="records")}}}'

# print(dbc_json)