
# bitrate setting for each resolution
# 4k:       12000,  8000,   4000,   2000
# 1080p:    8000,   4000,   2000,   1000
# 720p:     4000,   2000,   1000,   500
# 832x480:  2000,   1000,   500,    300
# 416x240:  1000,   500,    300,    100

seq_list = {
    'hevc_classA': 
    {
        'dir': 'D:/yuv/HevcConfSeq/yuv/classA',
        'seq':
        [
            # clip name, width, height, fps, bitrate array in kbps
            ["NebutaFestival_2560x1600_60_crop.yuv",            2560, 1600, 60, [12000, 8000, 4000, 2000]],
            ["PeopleOnStreet_2560x1600_30_crop.yuv",            2560, 1600, 30, [12000, 8000, 4000, 2000]],
            ["SteamLocomotiveTrain_2560x1600_60_crop.yuv",      2560, 1600, 60, [12000, 8000, 4000, 2000]],
            ["Traffic_2560x1600_30_crop.yuv",                   2560, 1600, 30, [12000, 8000, 4000, 2000]]
        ]
    },

    'hevc_classB':
    {
        'dir': 'D:/yuv/HevcConfSeq/yuv/classB',
        'seq':
        [
            # clip name, width, height, fps, bitrate array in kbps
            ["BasketballDrive_1920x1080_50.yuv",    1920, 1080, 50, [8000, 4000, 2000, 1000]],
            ["BQTerrace_1920x1080_60.yuv",          1920, 1080, 60, [8000, 4000, 2000, 1000]],
            ["Cactus_1920x1080_50.yuv",             1920, 1080, 50, [8000, 4000, 2000, 1000]],
            ["Kimono1_1920x1080_24.yuv",            1920, 1080, 24, [8000, 4000, 2000, 1000]],
            ["ParkScene_1920x1080_24.yuv",          1920, 1080, 24, [8000, 4000, 2000, 1000]],
            ["Tennis_1920x1080_24.yuv",             1920, 1080, 24, [8000, 4000, 2000, 1000]],
        ]
    },

    'hevc_classC':
    {
        'dir': 'D:/yuv/HevcConfSeq/yuv/classC',
        'seq':
        [
            # clip name, width, height, fps, bitrate array in kbps
            ["BasketballDrill_832x480_50.yuv",      832, 480, 50, [2000, 1000, 500, 300]],
            ["BQMall_832x480_60.yuv",               832, 480, 60, [2000, 1000, 500, 300]],
            ["PartyScene_832x480_50.yuv",           832, 480, 50, [2000, 1000, 500, 300]],
            ["RaceHorses_832x480_30.yuv",           832, 480, 50, [2000, 1000, 500, 300]],
            ["Mobisode2_832x480_30.yuv",            832, 480, 30, [2000, 1000, 500, 300]],
            ["Flowervase_832x480_30.yuv",           832, 480, 30, [2000, 1000, 500, 300]],
            ["Keiba_832x480_30.yuv",                832, 480, 30, [2000, 1000, 500, 300]],
        ]        
    },
    'hevc_classD':
    {
        'dir': 'D:/yuv/HevcConfSeq/yuv/classD',
        'seq':
        [
            # clip name, width, height, fps, bitrate array in kbps
            ["BasketballPass_416x240_50.yuv",   416, 240, 50, [1000, 500, 300, 100]],
            ["BQSquare_416x240_60.yuv",         416, 240, 60, [1000, 500, 300, 100]],
            ["BlowingBubbles_416x240_50.yuv",   416, 240, 50, [1000, 500, 300, 100]],
            ["RaceHorses_416x240_30.yuv",       416, 240, 30, [1000, 500, 300, 100]],
            ["Flowervase_416x240_30.yuv",       416, 240, 30, [1000, 500, 300, 100]],
            ["Mobisode2_416x240_30.yuv",        416, 240, 30, [1000, 500, 300, 100]],
            ["Keiba_416x240_30.yuv",            416, 240, 30, [1000, 500, 300, 100]],
        ]        
    },
    'hevc_classE':
    {
        'dir': 'D:/yuv/HevcConfSeq/yuv/classE',
        'seq':
        [
            # clip name, width, height, fps, bitrate array in kbps
            ["FourPeople_1280x720_60.yuv",          1280, 720, 60, [4000, 2000, 1000, 500]],
            ["KristenAndSara_1280x720_60.yuv",      1280, 720, 60, [4000, 2000, 1000, 500]],
            ["Johnny_1280x720_60.yuv",              1280, 720, 60, [4000, 2000, 1000, 500]],
            ["vidyo1_720p_60.yuv",                  1280, 720, 60, [4000, 2000, 1000, 500]],
            ["vidyo3_720p_60.yuv",                  1280, 720, 60, [4000, 2000, 1000, 500]],
            ["vidyo4_720p_60.yuv",                  1280, 720, 60, [4000, 2000, 1000, 500]],
        ]        
    },

    'hevc_classF':
    {
        'dir': 'D:/yuv/HevcConfSeq/yuv/classF',
        'seq':
        [
            # clip name, width, height, fps, bitrate array in kbps
            ["BasketballDrillText_832x480_50.yuv",  832,  480, 50, [2000, 1000, 500,  300]],
            ["ChinaSpeed_1024x768_30.yuv",          1024, 768, 30, [4000, 2000, 1000, 500]],
            ["SlideEditing_1280x720_30.yuv",        1280, 720, 30, [4000, 2000, 1000, 500]],
            ["SlideShow_1280x720_20.yuv",           1280, 720, 20, [4000, 2000, 1000, 500]],
        ]
    },
}