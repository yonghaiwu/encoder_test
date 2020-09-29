#!usr/bin/env python
# -*- coding: utf-8 -*-

crf_cqp_points  = [22, 27, 32, 37]

configuration = {
    "x264":
    {
        "rc_mode":      ['ABR', 'CRF', 'CQP'], # ['CQP'] # 
        "preset":       ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium'], # ['ultrafast']
        "gop_param":    
        {
            'ldp': '--bframes 0',
            'ra3':  '--bframes 3',
            'ra8':  '--bframes 7',
        },
        "test_seq": ['hevc_classA', 'hevc_classB', 'hevc_classC', 'hevc_classD', 'hevc_classE', 'hevc_classF'], # ['hevc_classD']
    },
}

'''
    "x265":
    {
        "rc_mode":      ['ABR', 'CRF', 'CQP'], # ['CQP']
        "preset":       ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium'], # ['ultrafast']
        "gop_param":    
        {
            'ldp': '--bframes 0',
            'ra3': '--bframes 3',
            'ra8': '--bframes 7',
        },
        "test_seq": ['hevc_classA', 'hevc_classB', 'hevc_classC', 'hevc_classD', 'hevc_classE', 'hevc_classF'], # ['hevc_classD']
    },

    "kavazaar":
    {
        "rc_mode":      ['ABR', 'CQP'], # ['CQP']
        "preset":       ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium'], # ['ultrafast']
        "gop_param":    
        {
            'ldp': '--gop 0',
            'ra8': '--gop 8', # only support gop 8 and 16
        },
        "test_seq": ['hevc_classA', 'hevc_classB', 'hevc_classC', 'hevc_classD', 'hevc_classE', 'hevc_classF'],  #['hevc_classD']
    },

    "stellar_265":
    {
        "rc_mode":      ['CQP'], # ['CQP']
        "preset":       ['default'],
        "gop_param":    
        {
            'ldp': '-BFrameNum 0',
            #'ra3': '-BFrameNum 3', # only support gop 8 and 16
        },
        "test_seq": ['hevc_classB', 'hevc_classC', 'hevc_classD', 'hevc_classE', 'hevc_classF'], # ['hevc_classD'],
    },

    "stellar_264":
    {
        "rc_mode":      ['CQP'], # ['CQP']
        "preset":       ['default'],
        "gop_param":    
        {
            'ldp': '-BFrameNum 0',
            #'ra3': '-BFrameNum 3', # only support gop 8 and 16
        },
        "test_seq": ['hevc_classD'], #['hevc_classA', 'hevc_classB', 'hevc_classC', 'hevc_classD', 'hevc_classE', 'hevc_classF'],
    },


    "cnm_264":
    {

    },

    "cnm_265":
    {

    },
}
'''