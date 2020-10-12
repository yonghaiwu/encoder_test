#! python
# -*- coding: utf-8 -*-

import os
import sys
import copy
import bjontegaard_metric
import numpy as np

def get_rate_and_score(br, psnr_y, psnr_a, ssim_y, ssim_a, vmaf, data, fps):
    i = 0
    while (i < 4):
        # sequence	 resolution	 target bitrate	 actual bitrate	 PSNR Y	 U	 V	 average	 SSIM Y	 U	 V	 average	 VMAF   fps
        line_data = data[i].split(',')
        br[i]     = (line_data[3])
        psnr_y[i] = (line_data[4])
        psnr_a[i] = (line_data[7])
        ssim_y[i] = (line_data[8])
        ssim_a[i] = (line_data[11])
        vmaf[i]   = (line_data[12])
        
        if(len(line_data) >= 14):
            fps[i]    = (line_data[13])
        i = i + 1

def calc_fps_avg_ratio(anchor_fps, test_fps):
    i = 0
    ratio = 0.0
    while (i < 4):
        if(anchor_fps[i] == 0.0):
            return -1
        ratio = ratio + (float(test_fps[i]) / float(anchor_fps[i]))
        i = i + 1
    return (ratio / 4) - 1

def get_bitrate_and_score_data(lines):
    br     = np.array([0.0, 0.0, 0.0, 0.0])
    psnr_y = np.array([0.0, 0.0, 0.0, 0.0])
    psnr_a = np.array([0.0, 0.0, 0.0, 0.0])
    ssim_y = np.array([0.0, 0.0, 0.0, 0.0])
    ssim_a = np.array([0.0, 0.0, 0.0, 0.0])
    vmaf   = np.array([0.0, 0.0, 0.0, 0.0])
    fps    = np.array([0.0, 0.0, 0.0, 0.0])
    
    data_map = {}
    seq_idx = 0
    seq_num = len(lines) / 4
    while (seq_idx < seq_num):
        seq_data = [
            lines[4 * seq_idx],
            lines[4 * seq_idx + 1],
            lines[4 * seq_idx + 2],
            lines[4 * seq_idx + 3],
        ]
        get_rate_and_score(br, psnr_y, psnr_a, ssim_y, ssim_a, vmaf, seq_data, fps)
        key = seq_data[0].split(',')[0]
        val = [br, psnr_y, psnr_a, ssim_y, ssim_a, vmaf, fps]
        data_map[key] = copy.deepcopy(val)
        seq_idx = seq_idx + 1
    return data_map

def calcBdrate(anchor, test, test_file_name, result_file, detail_file):
    bdrate_psnr_y_acc = 0.0
    bdrate_psnr_a_acc = 0.0
    bdrate_ssim_y_acc = 0.0
    bdrate_ssim_a_acc = 0.0
    bdrate_vmaf_acc = 0.0
    fps_ratio_acc = 0.0
    seq_num = 0
    for key in anchor:
        if key in test.keys():
            anchor_br     = anchor[key][0]
            anchor_psnr_y = anchor[key][1]
            anchor_psnr_a = anchor[key][2]
            anchor_ssim_y = anchor[key][3]
            anchor_ssim_a = anchor[key][4]
            anchor_vmaf   = anchor[key][5]
            anchor_fps    = anchor[key][6]
                        
            test_br     = test[key][0]
            test_psnr_y = test[key][1]
            test_psnr_a = test[key][2]
            test_ssim_y = test[key][3]
            test_ssim_a = test[key][4]
            test_vmaf   = test[key][5]
            test_fps    = test[key][6]

            bdrate_psnr_y = bjontegaard_metric.BD_RATE(anchor_br, anchor_psnr_y, test_br, test_psnr_y, 1)
            bdrate_psnr_a = bjontegaard_metric.BD_RATE(anchor_br, anchor_psnr_a, test_br, test_psnr_a, 1)
            bdrate_ssim_y = bjontegaard_metric.BD_RATE(anchor_br, anchor_ssim_y, test_br, test_ssim_y, 1)
            bdrate_ssim_a = bjontegaard_metric.BD_RATE(anchor_br, anchor_ssim_a, test_br, test_ssim_a, 1)
            fps_ratio     = calc_fps_avg_ratio(anchor_fps, test_fps)

            if test_vmaf[0] == 0.0:
                bdrate_vmaf = 0.0
            else:
                bdrate_vmaf   = bjontegaard_metric.BD_RATE(anchor_br, anchor_vmaf,   test_br, test_vmaf,   1)

            bdrate_psnr_y_acc = bdrate_psnr_y_acc + bdrate_psnr_y
            bdrate_psnr_a_acc = bdrate_psnr_a_acc + bdrate_psnr_a
            bdrate_ssim_y_acc = bdrate_ssim_y_acc + bdrate_ssim_y
            bdrate_ssim_a_acc = bdrate_ssim_a_acc + bdrate_ssim_a
            bdrate_vmaf_acc   = bdrate_vmaf_acc   + bdrate_vmaf
            fps_ratio_acc     = fps_ratio_acc     + fps_ratio
            seq_num = seq_num + 1

            result_file.write ("{:<80}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}%\n".format(key, bdrate_psnr_y, bdrate_psnr_a, bdrate_ssim_y, bdrate_ssim_a, bdrate_vmaf, fps_ratio * 100))
            i = 0
            while(i < 4):
                detail_file.write("{},{},{},{},{},{},{},{},".format(key, anchor_br[i], anchor_psnr_y[i], anchor_psnr_a[i], anchor_ssim_y[i], anchor_ssim_a[i],anchor_vmaf[i], anchor_fps[i]))
                detail_file.write("{},{},{},{},{},{},{},".format(test_br[i], test_psnr_y[i], test_psnr_a[i], test_ssim_y[i], test_ssim_a[i], test_vmaf[i], test_fps[i]))
                if( i == 0):
                    detail_file.write("{},{},{},{},{},{}\n".format(bdrate_psnr_y, bdrate_psnr_a, bdrate_ssim_y, bdrate_ssim_a, bdrate_vmaf, fps_ratio * 100))
                else:
                    detail_file.write("\n")
                i = i + 1
    summary = "{:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}%".format(bdrate_psnr_y_acc / seq_num, bdrate_psnr_a_acc / seq_num, bdrate_ssim_y_acc / seq_num, bdrate_ssim_a_acc / seq_num, bdrate_vmaf_acc / seq_num, fps_ratio_acc * 100 / seq_num)
    print ("{:<80}, {}".format(test_file_name, summary))
    result_file.write("Average, {}\n".format(summary))

if __name__ == "__main__":
    argc = len(sys.argv)
    if(argc < 3):
        print ("Need at least 2 parameters, 1 anchor, and 1 or more test")
        exit(0)

    anchor_file = sys.argv[1]
    test_num = argc - 2
    test_file_list = []
    test_idx = 0
    while (test_idx < test_num):
        test_file_list.append(sys.argv[test_idx + 2])
        test_idx = test_idx + 1
    anchor_lines = open(anchor_file, 'r').readlines()
    seq_num = (len(anchor_lines) - 1) / 4
    anchor_data_map = get_bitrate_and_score_data(anchor_lines[1:])

    result_file = open("result.csv", "w")
    detail_file = open("detail.csv", "w")
    result_file.write ("seq_name, bdrate_psnr_y, bdrate_psnr_a, bdrate_ssim_y, bdrate_ssim_a, bdrate_vmaf, speed improvement in fps\n")
    print ("Calc bd-rate: anchor={}".format(anchor_file))
    for test_file in test_file_list:
        test_lines   = open(test_file, 'r').readlines()
        test_data_map = get_bitrate_and_score_data(test_lines[1:])

        #result_file.write("=====================================================================\n")
        result_file.write("{}\n".format(test_file))
        calcBdrate(anchor_data_map, test_data_map, test_file, result_file, detail_file)
        result_file.write("=====================================================================\n")


