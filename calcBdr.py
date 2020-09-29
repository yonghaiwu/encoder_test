#! python
# -*- coding: utf-8 -*-

import os
import sys
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

if __name__ == "__main__":
    anchor = sys.argv[1]
    test   = sys.argv[2]
    anchor_lines = open(anchor, 'r').readlines()
    test_lines   = open(test,   'r').readlines()
    print ("Calc bd-rate: anchor={}, test={}".format(anchor, test))
    print ("seq_name, bdrate_psnr_y, bdrate_psnr_a, bdrate_ssim_y, bdrate_ssim_a, bdrate_vmaf, speed improvement in fps")
    seq_num = (len(anchor_lines) - 1) / 4

    seq_idx = 0
    bdrate_psnr_y_acc = 0.0
    bdrate_psnr_a_acc = 0.0
    bdrate_ssim_y_acc = 0.0
    bdrate_ssim_a_acc = 0.0
    bdrate_vmaf_acc = 0.0
    fps_ratio_acc = 0.0

    while (seq_idx < seq_num):
        anchor_br     = np.array([0.0, 0.0, 0.0, 0.0])
        anchor_psnr_y = np.array([0.0, 0.0, 0.0, 0.0])
        anchor_psnr_a = np.array([0.0, 0.0, 0.0, 0.0])
        anchor_ssim_y = np.array([0.0, 0.0, 0.0, 0.0])
        anchor_ssim_a = np.array([0.0, 0.0, 0.0, 0.0])
        anchor_vmaf   = np.array([0.0, 0.0, 0.0, 0.0])
        anchor_fps    = np.array([0.0, 0.0, 0.0, 0.0])
        anchor_data = [
            anchor_lines[4 * seq_idx + 1],
            anchor_lines[4 * seq_idx + 2],
            anchor_lines[4 * seq_idx + 3],
            anchor_lines[4 * seq_idx + 4],
        ]
        get_rate_and_score(anchor_br, anchor_psnr_y, anchor_psnr_a, anchor_ssim_y, anchor_ssim_a, anchor_vmaf, anchor_data, anchor_fps)
        seq_name = anchor_data[0].split(',')[0]

        test_br     = np.array([0.0, 0.0, 0.0, 0.0])
        test_psnr_y = np.array([0.0, 0.0, 0.0, 0.0])
        test_psnr_a = np.array([0.0, 0.0, 0.0, 0.0])
        test_ssim_y = np.array([0.0, 0.0, 0.0, 0.0])
        test_ssim_a = np.array([0.0, 0.0, 0.0, 0.0])
        test_vmaf   = np.array([0.0, 0.0, 0.0, 0.0])
        test_fps    = np.array([0.0, 0.0, 0.0, 0.0])
        test_data = [
            test_lines[4 * seq_idx + 1],
            test_lines[4 * seq_idx + 2],
            test_lines[4 * seq_idx + 3],
            test_lines[4 * seq_idx + 4],
        ]
        get_rate_and_score(test_br, test_psnr_y, test_psnr_a, test_ssim_y, test_ssim_a, test_vmaf, test_data, test_fps)

        bdrate_psnr_y = bjontegaard_metric.BD_RATE(anchor_br, anchor_psnr_y, test_br, test_psnr_y, 1)
        bdrate_psnr_a = bjontegaard_metric.BD_RATE(anchor_br, anchor_psnr_a, test_br, test_psnr_a, 1)
        bdrate_ssim_y = bjontegaard_metric.BD_RATE(anchor_br, anchor_ssim_y, test_br, test_ssim_y, 1)
        bdrate_ssim_a = bjontegaard_metric.BD_RATE(anchor_br, anchor_ssim_a, test_br, test_ssim_a, 1)
        fps_ratio     = calc_fps_avg_ratio(anchor_fps, test_fps)
        if test_vmaf[0] == 0.0:
            bdrate_vmaf = 0.0
        else:
            bdrate_vmaf   = bjontegaard_metric.BD_RATE(anchor_br, anchor_vmaf,   test_br, test_vmaf,   1)
        if(anchor_psnr_y[0] < 25 or test_psnr_a[0] < 25):
            print ("******** Warning ********: {} psnr too low".format(seq_name))
        print ("{:<80}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}%".format(seq_name, bdrate_psnr_y, bdrate_psnr_a, bdrate_ssim_y, bdrate_ssim_a, bdrate_vmaf, fps_ratio * 100))

        bdrate_psnr_y_acc = bdrate_psnr_y_acc + bdrate_psnr_y
        bdrate_psnr_a_acc = bdrate_psnr_a_acc + bdrate_psnr_a
        bdrate_ssim_y_acc = bdrate_ssim_y_acc + bdrate_ssim_y
        bdrate_ssim_a_acc = bdrate_ssim_a_acc + bdrate_ssim_a
        bdrate_vmaf_acc   = bdrate_vmaf_acc   + bdrate_vmaf
        fps_ratio_acc     = fps_ratio_acc     + fps_ratio
        seq_idx = seq_idx + 1

    print ("{:<80}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}%".format("Average", bdrate_psnr_y_acc / seq_num, bdrate_psnr_a_acc / seq_num, bdrate_ssim_y_acc / seq_num, bdrate_ssim_a_acc / seq_num, bdrate_vmaf_acc / seq_num, fps_ratio_acc * 100 / seq_num))
    
