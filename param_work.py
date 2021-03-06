__author__ = 'ali'
__email__ = 'alidanish@outlook.de'
'''
param work is part of A2l generator framework developed to XCP server, for 
XCP-MAVLINK bridge.
'''

from lxml import etree as et
import logging
import sys
import re

logging.basicConfig(filename='exception_param.log', filemode='w', format=('%(levelname)s:%(asctime)s:%(message)s'), level=logging.DEBUG)


def arg_parse():

    valid_prm = False

    if(len(sys.argv[1:]) != 1):
        print("need only one xml either APMrover2 or ArduCopter generated after\n"
              "ardupilot/Tools/autotest/param_metadata$ python param_parse.py --vehicle <APMrover2/Arducopter>")
        sys.exit(1)
    else:
        parse_xml = sys.argv[1]
        tree = et.parse(parse_xml)
        root = tree.getroot()
        for elck in root:
            prm_att = elck[0].attrib
            prm_typ = prm_att.get('name', 'parameters name attribute NA')
            if (prm_typ == 'APMrover2' or prm_typ == 'ArduCopter'):
                valid_prm = True
            else:
                pass
    if(valid_prm == True):

        prm_ds = param_parse(parse_xml)
        a2l_render_param(prm_ds)
        print("Done rendering Mavlink_characteristics.a2l")


def param_parse(pxml):
    # handle empty units, handled in a2l_render_param() here None is places as value
    # exception param should not make it to DS they are only for exception log

    tree = et.parse(pxml)
    root = tree.getroot()
    pr_c = 0


    param_list = []
    param_dict = {}
    fld_dict = {}

    val_list = []
    t_val_dict = {}
    val_dict = {}

    for el in root.iter("param"):
        exp_rsd = False
        t_param_dict = {}
        t_fld_dict = {}
        t_fld_list = []

        value_list = []
        tmp_spdic = {}

        if(type(el.tag) != str):
            raise TypeError("comments found with in param handled can disrupt the parsing..")
        # print(el.tag, pr_c)
        pr_c += 1
        # print("param el attrib::", el.attrib)
        p_name = el.get('name', 'name NA err')
        if(":" in p_name):
            psp_lis = p_name.split(':')
            p_name = psp_lis[1]
        p_des = el.get('humanName', 'humanName NA err') + ', '+ el.get('documentation', 'documentation NA err')

        t_param_dict[p_name] = p_des


        # print("ext name and des", p_name, p_des)
        for cel in el:
            # print("subchilds under param::",cel)
            if(cel.tag == 'field'):

                field_att = cel.attrib
                chk_field = field_att.get('name', 'name tag err')
                print("fields show::", chk_field)
                if('Range' in chk_field):
                    print("Range ext::",cel.text)
                    rng_str = cel.text
                    rng_list = rng_str.split(' ')
                    t_rng_list = rng_list.copy()
                    t_fld_dict ['range'] = t_rng_list
                    tt_fld_dict = t_fld_dict.copy()
                    t_fld_list.append(tt_fld_dict)
                    t_fld_dict.clear()
                    rng_list.clear()
                elif('Units' in chk_field):
                    print("Units ext:: ", cel.text)
                    unt_str = cel.text
                    t_fld_dict ['units'] = unt_str #if no text then None is there
                    tt_fld_dict = t_fld_dict.copy()
                    t_fld_list.append(tt_fld_dict)
                    t_fld_dict.clear()
                elif('Increment' in chk_field):
                    print("Increment ext::", cel.text)
                    inc_str = cel.text
                    t_fld_dict ['Increment'] = inc_str
                    tt_fld_dict = t_fld_dict.copy()
                    t_fld_list.append(tt_fld_dict)
                    t_fld_dict.clear()
                elif('ReadOnly' in chk_field):

                    print("ReadOnly ext::", cel.text)
                    inc_str = cel.text
                    t_fld_dict ['Readonly'] = inc_str
                    tt_fld_dict = t_fld_dict.copy()
                    t_fld_list.append(tt_fld_dict)
                    t_fld_dict.clear()
                elif('Values' in chk_field): #todo wrong pattern spotted in field type please take care of this in future Amilcar
                    print("Values ext::", cel.text)
                    Values_str = cel.text
                    vals_sp = Values_str.split(',')
                    try:
                        tmp_spdic = dict(s.split(':') for s in vals_sp)
                        for k,v in tmp_spdic.items():
                            value_dic = val_dic(k,v)
                            value_list.append(value_dic)
                            t_value_list = value_list.copy()
                        t_fld_dict['values'] = t_value_list
                        tt_fld_dict = t_fld_dict.copy()
                        t_fld_list.append(tt_fld_dict)
                        t_fld_dict.clear()
                        value_list.clear()
                    except ValueError:
                        exp_rsd = True
                        print("update err pattern change detected %s"%(vals_sp))
                        logging.debug("unexpected pattern detected at %s: handle according to range or value routine %s"%(p_name,vals_sp))
                        # rng_str = cel.text
                        # rng_list = rng_str.split(' ')
                        # t_rng_list = rng_list.copy()
                        # t_fld_dict['range'] = t_rng_list
                        # tt_fld_dict = t_fld_dict.copy()
                        # t_fld_list.append(tt_fld_dict)
                        # t_fld_dict.clear()
                        # rng_list.clear()
                else:
                    logging.info("attributes that were not extracted: %s under %s"%(cel.attrib, p_name))


            elif(cel.tag == 'values'):
                # print("values has subchlids::")
                for sub_cel in cel:
                    print("value ext::", sub_cel.tag, sub_cel.attrib, sub_cel.text)
                    val_att = sub_cel.attrib
                    val_val = val_att.get('code', 'tag code NA err') #expects only single value type string put range and any other in exception
                    val_exp = value_excp(val_val)
                    if(val_exp == True):
                        exp_rsd = True
                        print("value patter err. unknown pattern %s"%(val_val))
                        logging.debug("unexpected pattern detected at %s: handle according to range or value routine %s"%(p_name, val_val))
                    val_txt = sub_cel.text
                    t_val_dict[val_val] = val_txt
                    tt_val_dict = t_val_dict.copy()
                    val_list.append(tt_val_dict)
                    t_val_dict.clear()
                t_val_list = val_list.copy()
                val_dict ['values'] = t_val_list
                tmp_val_dict = val_dict.copy()
                t_fld_list.append(tmp_val_dict)
                # t_val_dict.clear()
                val_list.clear()
                val_dict.clear()

        if(exp_rsd == False):
            #add field Ds here
            tmp_fld_list = t_fld_list.copy()
            fld_dict ['fields'] = tmp_fld_list
            tmp_fld_dict = fld_dict.copy()
            param_dict.update(tmp_fld_dict)
            fld_dict.clear()

            tmp_param_dict = t_param_dict.copy()
            param_dict.update(tmp_param_dict)
            t_param_dict.clear()

            upd_param_dict = param_dict.copy()
            param_list.append(upd_param_dict)


            # print("param_ds created....flusing temp ds....")
            t_fld_list.clear()
            param_dict.clear()

    # print("param ds list::", param_list)
    return param_list
def val_dic(key, val):
       val_dc = {}
       val_dc[key] = val
       return val_dc

def value_excp(value):
    value_splis = value.split('-')
    if(len(value_splis) == 2):
        vlck = value_splis[0]
        vlck_sp = vlck.split(' ')
        if(len(vlck_sp) == 2): #handle ' 55'
            return True
        elif(len(value_splis[0]) == 0):
            return False
    elif(len(value_splis) == 1):
        valsp = value_splis[0].split(' ') #for err like 55 60
        if(len(valsp) == 2 and valsp[0].isdigit()):
            raise TypeError("range type pattern is detected in value %s"%(value_splis))



def a2l_render_param(ds_param):
    #readonly messges are measurments in characteristics a2l
    #handle empty fields [] as simple characteristics

    lim_dic = {'Scalar_FLOAT32_IEEE': ['-3.40282e+38', '3.40282e+38']}

    calib_str = ''
    compu_str = ''
    var_hx = 907018240 #for calibration initialized int ecu addr for hex ecu adder
    c = 0 #for addr reset

    param_cnt = 0
    meas_cnt = 0
    vtab_cnt = 0
    lower_lim = 0
    upper_lim = 0

    set_readonly = False
    set_vls = False
    set_rng = False
    set_emty = False
    set_units = False
    conv_m = ''
    conv_m_pr = ''

    chr_str = ''
    param_cnt = len(ds_param)
    des_list = []
    upper_limit_list = []
    lower_limit_list = []
    param_list = []

    for pe in ds_param:
        fld_ls = pe.get('fields', 'fields key missing err')
        for pr, ds in pe.items():
            if(pr.isupper()):
                des = ds #full des
                dslis = ds.split(',') #separate here by , to the short description in compu vtab and method
                des_short = dslis[0]
                # des_long = dslis[1]
                param = pr

        for flds in fld_ls:

            if('Readonly' in flds):
                set_readonly = True
                chr_str = 'MEASUREMENT'
                meas_cnt += 1
            elif('values' in flds):
                set_vls = True
                vls_list = flds.get('values', 'value list err')
                cnt_vls = len(vls_list) #to render TAB_VERB (count)
                compu_str = a2l_render_compu(cnt_vls, vls_list, des_short, des, param)
                low_lim, up_lim = lim_val(vls_list)
                conv_m_pr = 'CM_{0}'.format(param)
                vtab_cnt += 1

            elif('range' in flds):
                set_rng = True
                rng_ls = flds.get('range', 'range list err')
                lw_lm, up_lm = lim_rng(rng_ls)

            elif('units' in flds):
                set_units = True
                try:
                    conv_m_pass = flds.get('units', 'units err') #to matched for a2l
                    conv_m = convm_units(conv_m_pass)

                    if(conv_m == None): #if we dont find the matched pattern
                        conv_m = "IDENTICAL" #log the cases bcz these are cases that has not been included yet
                        logging.info(
                            "Parameter units that will get %s for being None.... str %s under param %s..." %(conv_m, conv_m_pass, param) )
                except TypeError:
                    print("Failed to recognize str %s ....try to handle"%(conv_m_pass))
                    conv_m = 'IDENTICAL'
                    logging.debug("Failed to recognize unit under param %s....try to handle.. given %s"%(param, conv_m_pass))


            elif(len(flds) == 0):
                set_emty = True

        if (set_rng == True and set_vls == True):
            lower_lim = lw_lm
            upper_lim = up_lm
        elif (set_vls == True):
            lower_lim = low_lim
            upper_lim = up_lim
        elif (set_rng == True):

            lower_lim = lw_lm
            upper_lim = up_lm

        elif(set_rng == False and set_vls == False or set_emty == True):
            for k,v in lim_dic.items():
                lower_lim = v[0]
                upper_lim = v[1]


        if(set_readonly == False):
            chr_str = 'CHARACTERISTIC'
        if(set_units == False):
            conv_m = "IDENTICAL"

        if(set_vls == True):
            conv_m = conv_m_pr
        if(set_emty == True):
            conv_m = "IDENTICAL"

        if(c == 0):
            var_hx = var_hx + 0
        else:
            var_hx = var_hx + 4
        var_hx_str_int = '{:#010x}'.format(var_hx)
        ecu_str = str(var_hx_str_int)

        if(set_vls == False):
            compu_str = '\n'
        else:
            compu_str = compu_str

        if(set_readonly == False):

            chrc_str = "    /begin {0}\n" \
                         "        /* Name               */    {1}\n" \
                         "        /* Long Identifier    */    \"{2}\"\n" \
                         "        /* Type               */    VALUE\n" \
                         "        /* ECU Address        */    {3}\n" \
                         "        /* Record Layout      */    Scalar_FLOAT32_IEEE\n" \
                         "        /* Maximum Difference */    0\n" \
                         "        /* Conversion Method  */    {4}\n" \
                         "        /* Lower Limit        */    {5}\n" \
                         "        /* Upper Limit        */    {6}\n" \
                         "    /end {0}\n".format(chr_str, param, des, ecu_str, conv_m, lower_lim, upper_lim)
            # calib_str += compu_str + chrc_str
        elif(set_readonly == True):
            chrc_str =   "    /begin {0}\n" \
                         "        /* Name               */    {1}\n" \
                         "        /* Long Identifier    */    \"{2}\"\n" \
                         "        /* Record Layout      */    FLOAT32_IEEE\n" \
                         "        /* Conversion Method  */    {4}\n" \
                         "        /* Integer resolution */    0\n" \
                         "        /* float accuracy     */    0\n" \
                         "        /* Lower Limit        */    {5}\n" \
                         "        /* Upper Limit        */    {6}\n" \
                         "        ECU_ADDRESS {3}\n" \
                         "    /end {0}\n".format(chr_str, param, des, ecu_str, conv_m, lower_lim, upper_lim)


        des_list.append(des)
        upper_limit_list.append(upper_lim)
        lower_limit_list.append(lower_lim)
        param_list.append(param)

        calib_str += compu_str + chrc_str
        set_readonly = False
        set_vls = False
        set_rng = False
        set_units = False
        set_emty =False
        conv_m = ''
        conv_m_pr = ''



    with open('Mavlink_characteristics.a2l', 'w') as fcalib:
        fcalib.write(calib_str)

    param_cnt = param_cnt - meas_cnt
    param_stats = "//Rendered {0} CHARACTERISTIC(s), {1} MEASUREMENT(s), {2} VTAB(s)".format(param_cnt, meas_cnt, vtab_cnt)
    with open('Mavlink_characteristics.a2l', 'a') as cnt:
        cnt.write('\n')
        cnt.write(param_stats)

    c_header_render(param_list, lower_limit_list, upper_limit_list, param_cnt, des_list)

def a2l_render_compu(cnt, vls, short_des, full_des, param):
    compu_str = ''
    val_str = ''
    for vl in vls:
        for nm, enum in vl.items():
            val_str += " {0:>14}   \"{1:<}\n".format(nm,enum + '"')

    compu_str = "\n    /begin COMPU_METHOD CM_{0} \"{1}\"\n" \
                "        TAB_VERB\n" \
                "        \"%17.6\"\n" \
                "        \"\"\n"\
                "        COMPU_TAB_REF TAB_{0}\n" \
                "    /end COMPU_METHOD\n" \
                "    /begin COMPU_VTAB TAB_{0} \"{2}\" TAB_VERB {3}\n"  \
                "{4}" \
                "    /end COMPU_VTAB\n".format(param, short_des, full_des, cnt, val_str)

    return compu_str

def lim_rng(rngls):

    num_lis = []
    for r in rngls:
        rng_flt = float(r)
        num_lis.append(rng_flt)
    up_lim = max(num_lis)
    lw_lim = min(num_lis)

    return lw_lim, up_lim

def lim_val(vls):

    num_lis = []
    for vl in vls:
        for k,v in vl.items():
            if("0x" in k):
                nm_int = int(k, 16) #for a2l limits are put in integer format
                num_lis.append(nm_int)
            else:
                nflt = float(k)
                num_lis.append(nflt)


        lim_up = max(num_lis)
        lim_lw = min(num_lis)
    return lim_lw, lim_up

def convm_units(conv):
    lin_re = re.compile(r'(?<!\w)(?<!\/)(?P<SECONDS_P1>\weconds)'
                        r'|(?P<MS_P1>\williseconds)|(?<!\w)(?P<MS_P2>mse?c?)|(?P<MS_P3>Time since system boot)'
                        r'|(?P<MICROSEC_P1>\wicroseconds)|(?P<MICROSEC_P2>micros)|(?P<MICROSEC_P3>Timestamp \(UNIX\))'
                        r'|(?<!\w )(?P<MICROSEC_P4>Timestamp)(?! \()(?!\w)(?!\s\w)|(?P<MICROSEC_P5>pwm|PWM)'
                        r'|(?<!\w)(?P<METERS_P1>m)(?!\w+)(?!\/)(?!\*)|(?<!\*\s)(?<!\w)(?P<METERS_P2>\wetere?s)(?!\/)(?!,)(?! \*)|(?<=Global\s)(?P<METERS_P3>\w\s\wosition\s)|(?<!\w)(?P<METERS_P4>\w\s\wosition)(?!\sof)(?!\sin\sWGS84)'
                        r'|(?P<CM_P1>\wentimeters)(?!\/)|(?P<CM_P2>cm)(?!\/)'
                        r'|(?P<MM_P1>millimeters)|(?P<MM_P2>meters \* \d+)|(?<!\w)(?P<MM_P3>mm)(?!\w)'
                        r'|(?<!\w)(?P<MPS_P1>meters\/second)|(?P<MPS_P2>meter \/ s)(?!\^)'
                        r'|(?<!\w)(?P<MPS_P3>m\/s)(?!\s\*)(?!\^)(?!\/)|(?<=Global )(?P<MPS_P4>\w \wpeed)'
                        r'|(?<!\w )(?P<MPS_P5>\w Speed)'
                        r'|(?P<CMPS_P1>\wentimeters\/\wecond)|(?P<CMPS_P2>m\/s \* \d\d\d)|(?P<CMPS_P3>cm\/s)(?!\/)'
                        r'|(?P<MPSPS_P1>m\/s\^2)|(?P<MPSPS_P2>meter\s\/\ss\^2)|(?<!\w)(?P<MPSPS_P3>m\/s\/s)'
                        r'|(?P<CMPSPS_P1>cm\/s\/s)'
                        r'|(?<!\d\s)(?<!\-)(?<!\w)(?P<DGR_P1>\wegrees)(?!\/)(?!\s\*)(?!\scelsius)'
                        r'|(?P<CDGR_P1>\wenti-?\wegrees)(?!\s\welsius)|(?P<CDGR_P2>degrees?\s\*\s\d\d\d)|(?P<CDGR_P3>deg\*100)'
                        r'|(?<!-)(?<!\d\s)(?P<DGRC_P1>\wegrees \welsius)|(?P<DGRC_P2>degreesC)'
                        r'|(?P<CDGRC_P1>\wenti-\wegrees\s\welsius)|(?P<CDGRC_P2>\d\D\d\d\s\wegrees\s\welsius)'
                        r'|(?P<DGR107_P1>degrees\s\*\s?\d\d?\^\d)|(?P<DGR107_P2>degr?e?e?s?\s\*\s\dE7)'
                        r'|(?P<DGRPS_P1>degrees\/s)|(?P<DGRPS_P2>deg\/s\w?\w?)'
                        r'|(?P<RAD_P1>\wadians)(?!\sper)|(?P<RAD_P2>rad)(?!\s?\/)(?!\w)'
                        r'|(?P<RADPS_P1>radians per second)|(?<!\w)(?P<RADS_P2>rad\s?\/\s?s\w?\w?)(?!\/)'
                        r'|(?P<RADPSPS_P1>rad\/s\/s)'
                        r'|(?P<MRADPS_P1>millirad\s\/sec)'
                        r'|(?P<HPASCAL_P1>hectopascal)'
                        r'|(?P<AMP_P1>\wmps)(?!\/)'
                        r'|(?P<CAMP_P1>10\*milliamp\w+)'
                        r'|(?P<MAMPH_P1>milliamp\w+\shours)|(?<!\d\s)(?P<MAMPH_P2>mA\w)(?!\s\w)'
                        r'|(?P<VOLT_P1>raw voltage)|(?<!\w)(?P<VOLT_P2>\wolts?)(?!\w)'
                        r'|(?P<MVOLT_P1>millivolts)|(?P<MVOLT_P2>mV)'
                        r'|(?P<MTESLA_P1>milli\stesla)'
                        r'|(?P<MILLIG_P1>mg)'
                        r'|(?P<MILLIBAR_P1>millibar)'
                        r'|(?<!\w)(?P<GAUSS_P1>\wauss)(?!\/)'
                        r'|(?P<MGAUSS_P1>milligauss)'
                        r'|(?P<DECIPIXELS_P1>pixels\s\*\s10)'
                        r'|(?P<HECTOJOULES_P1>100\*Joules)'
                        r'|(?P<WATTS_P1>\watts)'
                        r'|(?<!hecto)(?P<PASCAL_P1>pascals?)'
                        r'|(?P<KM_P1>\wilometers?)'
                        r'|(?<!\w)(?P<MPSPSPS_P1>m\/s\/s\/s)'
                        r'|(?P<CMPSPSPS_P1>cm\/s\/s\/s)'
                        r'|(?P<CDGRPS_P1>\wenti\-?\wegrees\/\wec)(?!\/)'
                        r'|(?P<PC_P1>\wercent\w?\w?\w?)(?!\*)|(?P<PC_P2>%)'
                        r'|(?P<DECIPC_P1>\wercent\*10)'
                        r'|(?P<APV_P1>\wmps\/\wolt)'
                        r'|(?P<MPV_P1>\weters\/\wolt)'
                        r'|(?P<GAUSSPS_P1>gauss\/s)'
                        r'|(?<!\w\s)(?P<HZ_P1>Hz)|(?P<HZ_P2>1\/\w)'
                        r'|(?P<CDGRPSPS_P1>\wenti-?\wegrees\/\wec\/\wec)'
                        r'|(?P<MAV_BATT>Function\sof\sthe\sbattery)'
                        r'|(?P<MAV_RMLOG>log\sdata\sblock\ssequence\snumber)'
                        r'|(?<!\w\s)(?<!\-)(?P<MAV_PIDAXIS>axis)(?!\s\w)'
                        r'|(?P<MAV_ADSBFL>Flags\sto\sindicate)'
                        r'|(?P<MAV_COLLSRC>Collision\sdata)'
                        r'|(?P<MAV_COLLSAC>Action\sthat\sis)'
                        r'|(?P<MAV_COLLSTH>How\sconcerned)'
                        r'|(?P<MAV_ESTTYP>estimate\soriginated)'
                        r'|(?P<MAV_BATTTYP>Type\s\(chemistry\))'
                        r'|(?P<M10E7>1e7\s\*\smeters)')


    srds_linear = {'SECONDS': ['SECONDS_P1'], 'MILLISECONDS': ['MS_P1', 'MS_P2', 'MS_P3'],
               'MICROSECONDS': ['MICROSEC_P1', 'MICROSEC_P2', 'MICROSEC_P3', 'MICROSEC_P4', 'MICROSEC_P5'],
               'METERS': ['METERS_P1', 'METERS_P2', 'METERS_P3', 'METERS_P4'], 'CENTIMETERS': ['CM_P1', 'CM_P2'],
               'MILLIMETERS': ['MM_P1', 'MM_P2', 'MM_P3'],
               'METERS_PER_SECOND': ['MPS_P1', 'MPS_P2', 'MPS_P3', 'MPS_P4', 'MPS_P5'],
               'CENTIMETERS_PER_SECOND': ['CMPS_P1', 'CMPS_P2', 'CMPS_P3'],
               'METERS_PER_SECOND_PER_SECOND': ['MPSPS_P1', 'MPSPS_P2', 'MPSPS_P3'],
               'CENTIMETERS_PER_SECOND_PER_SECOND': ['CMPSPS_P1'], 'DEGREES': ['DGR_P1'],
               'CENTIDEGREES': ['CDGR_P1', 'CDGR_P2', 'CDGR_P3'],
               'DEGREESCELSIUS': ['DGRC_P1', 'DGRC_P2'], 'CENTIDEGREESCELSIUS': ['CDGRC_P1', 'CDGRC_P2'],
               'DEGREES_10E7': ['DGR107_P1', 'DGR107_P2'],
               'DEGREES_PER_SECOND': ['DGRPS_P1', 'DGRPS_P2'], 'DEGREES_PER_SECOND_PER_SECOND': [''],
               'RADIANS': ['RAD_P1', 'RAD_P2'], 'RADIANS_PER_SECOND': ['RADPS_P1', 'RADS_P2'],
               'RADIANS_PER_SECOND_PER_SECOND': ['RADPSPS_P1'], 'MILLIRADIANS_PER_SECOND': ['MRADPS_P1'],
               'HECTOPASCAL': ['HPASCAL_P1'],
               'AMPERE': ['AMP_P1'], 'CENTIAMPERE': ['CAMP_P1'], 'MILLIAMPERE': [''],
               'MILLIAMPERE_HOUR': ['MAMPH_P1', 'MAMPH_P2'], 'VOLT': ['VOLT_P1', 'VOLT_P2'],
               'MILLIVOLT': ['MVOLT_P1', 'MVOLT_P2'],
               'MILLITESLA': ['MTESLA_P1'], 'MILLIG': ['MILLIG_P1'], 'MILLIBAR': ['MILLIBAR_P1'], 'GAUSS': ['GAUSS_P1'],
               'MILLIGAUSS': ['MGAUSS_P1'], 'DECIPIXELS': ['DECIPIXELS_P1'], 'HECTOJOULES': ['HECTOJOULES_P1'],
               'WATT': ['WATTS_P1'],
               'PASCAL': ['PASCAL_P1'], 'KILOMETERS': ['KM_P1'],
               'METERS_PER_SECOND_PER_SECOND_PER_SECOND': ['MPSPSPS_P1'],
               'CENTIMETERS_PER_SECOND_PER_SECOND_PER_SECOND': ['CMPSPSPS_P1'],
               'CENTIDEGREES_PER_SECOND': ['CDGRPS_P1'], 'PERCENT': ['PC_P1', 'PC_P2'],
               'DECIPERCENT': ['DECIPC_P1'], 'AMPERE_PER_VOLT': ['APV_P1'], 'METERS_PER_VOLT': ['MPV_P1'],
               'GAUSS_PER_SECOND': ['GAUSSPS_P1'],
               'HERZ': ['HZ_P1', 'HZ_P2'], 'CENTIDEGREES_PER_SECOND_PER_SECOND': ['CDGRPS_P1'],
               'MAV_BATTERY_FUNCTION': ['MAV_BATT'], 'MAV_REMOTE_LOG_DATA_BLOCK_COMMANDS': ['MAV_RMLOG'],
               'PID_TUNING_AXIS': ['MAV_PIDAXIS'],
               'ADSB_FLAGS': ['MAV_ADSBFL'], 'MAV_COLLISION_SRC': ['MAV_COLLSRC'],
               'MAV_COLLISION_ACTION': ['MAV_COLLSAC'],
               'MAV_COLLISION_THREAT_LEVEL': ['MAV_COLLSTH'], 'MAV_ESTIMATOR_TYPE': ['MAV_ESTTYP'],
               'MAV_BATTERY_TYPE': ['MAV_BATTTYP'],
               'METERS_10E7': ['M10E7']}

    conv_sr = re.search(lin_re, conv)
    # print("found in conv::", conv_sr)
    if(conv_sr):
        lin_dc = conv_sr.groupdict()
        ksr = lin_dc.keys()
        for ks in ksr:
            lin_gets = lin_dc.get(ks, 'NA')
            if (lin_gets != None):
                for k, vlis in srds_linear.items():
                    if (ks in vlis):
                        return k


def c_header_render(param_list, lower_limit_list, upper_limit_list, param_cnt, des_list):
    #rendering c header file based on the a2l_characteristic file
    #use description list as generator

    low_itr = iter(lower_limit_list)
    up_itr = iter(upper_limit_list)
    des_itr = iter(des_list)

    param_array_cat = ''
    low_array_cat = ''
    up_array_cat = ''

    str_def_hdr = "#ifndef MAVA2L_H\n" \
                  "#define MAVA2L_H\n"

    str_def_end = "#endif"
    str_def_prmno = "#define MAVLINK_XCP_PARAMETERS {0}\n".format(param_cnt)
    param_array_st = "const char* const param_c[MAVLINK_XCP_PARAMETERS] = {0} \n".format('{')
    low_array_st = "const float param_min[MAVLINK_XCP_PARAMETERS] = {0} \n".format('{')
    up_array_st = "const float param_max[MAVLINK_XCP_PARAMETERS] = {0} \n".format('{')
    for prm in param_list:
        des = des_itr.__next__()
        lv = low_itr.__next__()
        up = up_itr.__next__()

        param_array = "{3: >4}{0:16}{2: <2}{4: >2} {1:50}\n".format(prm + '"', des, ',', '"', '//')
        # param_array = "    \"%-16s    %s  //%-50s\n"%(prm + "\"","," ,des)
        low_array = "    {0:>16}, // {1}\n".format(lv, des)
        up_array = "    {0:>16}, // {1}\n".format(up, des)
        param_array_cat += param_array
        low_array_cat += low_array
        up_array_cat += up_array


    arrays_render = str_def_hdr + '\n' + str_def_prmno + '\n' + param_array_st + param_array_cat + '};\n' \
                    + low_array_st + low_array_cat + '};\n' + up_array_st + up_array_cat + '};\n' + str_def_end
    with open('MAVA2L.h', 'w') as chdr:
        chdr.write(arrays_render)
if __name__ == '__main__':
    arg_parse()

