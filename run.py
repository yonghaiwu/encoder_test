#!usr/bin/env python
# -*- coding: utf-8 -*-
import os 
import re
import json
import seq_list
import common_cfg

g_enc_frame_num     = 60
g_ENABLE_ENCODE     = True
g_ENABLE_ENC_CHECK  = True # for x265 
g_ENABLE_CALC_SCORE = True
g_ENABLE_CALC_VMAF  = False
g_ENABLE_PARSING    = True

def func_x264_enc (preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, enc_log_file, cmd_log_file):
    if g_ENABLE_ENCODE == True:
        # step 1: encode
        cmd = ".\\binary\\x264.exe --preset {} --fps 30 {}/{} --input-res {}x{} {}".format(preset, root, yuv_name, width, height, gop_param)

        if(g_enc_frame_num != 0 and g_enc_frame_num != -1):
            cmd = cmd + " --frames {}".format(g_enc_frame_num)
        if (rc_mode == 'VBR' or rc_mode == 'ABR'):
            cmd = cmd + " --bitrate {} -o {}".format(point, stream)
        elif(rc_mode == 'CRF'):
            cmd = cmd + " --crf {} -o {}".format(point, stream)
        elif(rc_mode == 'CQP'):
            cmd = cmd + " --qp {} -o {}".format(point, stream)
        else:
            print ("wrong rc mode {}".format(rc_mode))
            exit(0)
        os.system("{} > {} 2>&1 &".format(cmd, enc_log_file))
        cmd_log_file.write(cmd + "\n")

    # step 2: get encoded frame number (for calc score)
    for line in open(enc_log_file, 'r'):
        # encoded 500 frames, 45.20 fps, 10186.47 kb/s
        data = re.search("encoded (.*) frames, (.*) fps, (.*) kb/s", line)
        if data:
            frame_num = data.group(1)
            speed_in_fps = data.group(2)
            actual_bitrate = data.group(3)
            return [frame_num, speed_in_fps, -1, actual_bitrate]
    return [-1, -1, -1, -1]

def func_x265_enc (exe_name, extra_param, preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, log_file, cmd_log_file):
    if g_ENABLE_ENCODE == True:
        # step 1: encode
        cmd = ".\\binary\\{}.exe --preset {} --fps 30 {}/{} --input-res {}x{} {}".format(exe_name, preset, root, yuv_name, width, height, gop_param)
        if g_ENABLE_ENC_CHECK == True:
            cmd = cmd + " --recon rec.yuv"
        if(g_enc_frame_num != 0 and g_enc_frame_num != -1):
            cmd = cmd + " --frames {}".format(g_enc_frame_num)
        if (rc_mode == 'VBR' or rc_mode == 'ABR'):
            cmd = cmd + " --bitrate {} -o {}".format(point, stream)
        elif(rc_mode == 'CRF'):
            cmd = cmd + " --crf {} -o {}".format(point, stream)
        elif(rc_mode == 'CQP'):
            cmd = cmd + " --qp {} -o {}".format(point, stream)
        else:
            print ("wrong rc mode {}".format(rc_mode))
            exit(0)

        # for ultrafast preset, need to adjust lookahead frame number to make sure it's not less than Bframe number
        bframe_num = int(gop_param.split()[1])
        if (preset == 'ultrafast') and (bframe_num > 5):
            cmd = cmd + ' --rc-lookahead {}'.format(bframe_num + 1)
        cmd = cmd + ' ' + extra_param
        os.system("{} > {} 2>&1 &".format(cmd, enc_log_file))
        cmd_log_file.write(cmd + "\n")

    # step 2: get encoded frame number (for calc score)
    for line in open(enc_log_file, 'r'):
        # encoded 60 frames in 0.12s (521.74 fps), 1194.99 kb/s, Avg QP:21.95
        data = re.search("encoded (.*) frames in (.*)s \((.*) fps\), (.*) kb/s, Avg QP:(.*)", line)
        if data:
            frame_num       = data.group(1)
            encoding_time   = data.group(2) 
            speed_in_fps    = data.group(3)
            actual_bitrate  = data.group(4)
            return [frame_num, speed_in_fps, encoding_time, actual_bitrate]
    return [-1, -1, -1, -1]

def func_kavazaar_enc (preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, log_file, cmd_log_file):
    if g_ENABLE_ENCODE == True:
        # step 1: encode
        cmd = ".\\binary\\kvazaar.exe --preset {} --period 256 --input-fps 30 --input {}/{} --input-res {}x{} {} --no-psnr --no-info".format(preset, root, yuv_name, width, height, gop_param)
        if(g_enc_frame_num != 0 and g_enc_frame_num != -1):
            cmd = cmd + " --frames {}".format(g_enc_frame_num)
        if (rc_mode == 'VBR' or rc_mode == 'ABR'):
            cmd = cmd + " --bitrate {} -o {}".format(int(point) * 1000, stream) # kvazaar need bitrate in bps unit
        elif(rc_mode == 'CQP'):
            cmd = cmd + " --qp {} -o {}".format(point, stream)
        else:
            print ("wrong rc mode {}".format(rc_mode))
            exit(0)
        os.system("{} > {} 2>&1 &".format(cmd, enc_log_file))
        cmd_log_file.write(cmd + "\n")

    # step 2: get encoded frame number (for calc score)
    frame_num = -1
    encoding_time = -1
    speed_in_fps = -1
    actual_bitrate = -1
    for line in open(enc_log_file, 'r'):
        # Processed 60 frames,    2401952 bits
        # Total CPU time: 0.079 s.
        # Encoding time: 0.078 s.
        # Encoding wall time: 0.078 s.
         # Encoding CPU usage: 100.00%
         # FPS: 771.22
         # Bitrate: 1.145 Mbps
         # AVG QP: 22.0

        data = re.search("Processed (.*) frames", line)
        if data:
            frame_num = data.group(1)
            continue
        
        data = re.search("Encoding time: (.*) s.", line)
        if data:
            encoding_time = data.group(1) 
            continue

        data = re.search("FPS: (.*)", line)
        if data:
            speed_in_fps    = data.group(1)
            continue
        
        data =re.search("Bitrate: (.*) Mbps", line)
        if data:
            actual_bitrate  = float(data.group(1)) * 1000
            continue

        data =re.search("Bitrate: (.*) Kbps", line)
        if data:
            actual_bitrate  = data.group(1) * 1000
            continue
    return [frame_num, speed_in_fps, encoding_time, actual_bitrate]


def func_stellar_264_enc (preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, log_file, cmd_log_file):
    if g_ENABLE_ENCODE == True:
        yuv_total_size = os.path.getsize("{}/{}".format(root, yuv_name))
        one_frame_size = int(width) * int(height) * 3 / 2
        yuv_frame_num = int(yuv_total_size / one_frame_size)
        # step 1: generate script
        cmd = ".\\binary\\GenEncScript.exe -Clip {}/{} -Width {} -Height {} -IntraPeriod 250 -ScpFolderPath ./ -EntropyType 1 -DisDBK 0 -Tr8x8 1 -PicFormat 0 {} -o ".format(root, yuv_name, width, height, gop_param, stream)

        if(g_enc_frame_num != 0 and g_enc_frame_num != -1):
            cmd = cmd + " -EncFrameNum {}".format(g_enc_frame_num)
            frame_num = g_enc_frame_num
        else:
            cmd = cmd + " -EncFrameNum {}".format(yuv_frame_num)
            frame_num = yuv_frame_num
        if(rc_mode == 'CQP'):
            cmd = cmd + " -Qp {}".format(point)
        else:
            cmd = cmd + " -Qp 22"
        os.system("{} 2>&1 &".format(cmd))
        #os.system(cmd)
        cmd_log_file.write(cmd + "\n")    

        # step 2: encode
        # note: -YuvIn parameter must use '\\' for directory, don't use '/'
        cmd = ".\\binary\\S3_Encoder_ref_ZXVD3000.exe -YuvIn .\\PFMT_000000.bin -MeAlgId 0 -Out {} ".format(stream)
        if(rc_mode == 'VBR' or rc_mode == 'ABR'):
            cmd = cmd + " -RcBr {}".format(int(point) * 1000)
        os.system("{} > {} 2>&1 &".format(cmd, enc_log_file))
        #os.system(cmd)
        cmd_log_file.write(cmd + "\n")    
    
    # step 3: get encoded frame number (for calc score)
    #frame_num = -1
    encoding_time = -1
    speed_in_fps = -1
    actual_bitrate = -1
    for line in open(enc_log_file, 'r'):
        # PicIdx:59  FrameType:0  QP:24
        data = re.search("PicIdx:(.*)  FrameType:(.*)  QP:(.*)", line)
        if data:
            frame_num = int(data.group(1)) + 1
    bit_file_size = float(os.path.getsize(stream))
    actual_bitrate = (bit_file_size * 8 * 30 / frame_num) / 1000 # assume fps= 30, and convert to Kbps
    
    # step 4: cleanup, delete bin file and rec YUV
    os.system("del *.bin")
    rec_yuv_file = "{}.yuv".format(os.path.splitext(stream)[0])
    os.system("del {}".format(rec_yuv_file))

    return [frame_num, speed_in_fps, encoding_time, actual_bitrate]

def func_stellar_265_enc (preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, log_file, cmd_log_file):
    if g_ENABLE_ENCODE == True:
        yuv_total_size = os.path.getsize("{}/{}".format(root, yuv_name))
        one_frame_size = int(width) * int(height) * 3 / 2
        yuv_frame_num = int(yuv_total_size / one_frame_size)
        # step 1: generate script
        cmd = ".\\binary\\GenHEVCEncScript.exe -Clip {}/{} -Width {} -Height {} -IntraPeriod 250 -ScpFolderPath ./ -Dbk 1 -Sao 1 -PicFormat 0 {} -o ".format(root, yuv_name, width, height, gop_param, stream)

        if(g_enc_frame_num != 0 and g_enc_frame_num != -1):
            cmd = cmd + " -EncFrameNum {}".format(g_enc_frame_num)
            frame_num = g_enc_frame_num
        else:
            cmd = cmd + " -EncFrameNum {}".format(yuv_frame_num)
            frame_num = yuv_frame_num
        if(rc_mode == 'CQP'):
            cmd = cmd + " -Qp {}".format(point)
        else:
            cmd = cmd + " -Qp 22"
        os.system("{} 2>&1 &".format(cmd))
        #os.system(cmd)
        cmd_log_file.write(cmd + "\n")    

        # step 2: encode
        # note: -YuvIn parameter must use '\\' for directory, don't use '/'
        cmd = ".\\binary\\S3_Encoder_ref_ZXVD3000.exe -YuvIn .\\PFMT_000000.bin -MeAlgId 0 -Out {} ".format(stream)
        if(rc_mode == 'VBR' or rc_mode == 'ABR'):
            cmd = cmd + " -RcBr {}".format(int(point) * 1000)
        os.system("{} > {} 2>&1 &".format(cmd, enc_log_file))
        #os.system(cmd)
        cmd_log_file.write(cmd + "\n")    
    
    # step 3: get encoded frame number (for calc score)
    # FIXME: log file frame number is wrong
    #frame_num = -1 
    encoding_time = -1 # there is no speed data, may need to use system function to get
    speed_in_fps = -1
    actual_bitrate = -1
    '''
    for line in open(enc_log_file, 'r'):
        # Encoding Frame Idx: 000000, Type: 2, QPY: 22
        data = re.search("Encoding Frame Idx: (.*), Type: (.*), QPY: (.*)", line)
        if data:
            frame_num = int(data.group(1)) + 1
    '''
    bit_file_size = float(os.path.getsize(stream))
    actual_bitrate = (bit_file_size * 8 * 30 / frame_num) / 1000 # assume fps= 30, and convert to Kbps
    
    # step 4: cleanup, delete bin file and rec YUV
    os.system("del *.bin")
    rec_yuv_file = "{}.yuv".format(os.path.splitext(stream)[0])
    os.system("del {}".format(rec_yuv_file))

    return [frame_num, speed_in_fps, encoding_time, actual_bitrate]

if __name__ == "__main__":
    if(os.path.exists(".\\bitstream") == False):
        os.system("mkdir bitstream")
    for encoder in common_cfg.configuration:
        encoder_map = common_cfg.configuration[encoder]
        for preset in encoder_map["preset"]:
            for rc_mode in encoder_map["rc_mode"]:
                for gop_name in encoder_map["gop_param"]:
                    gop_param = encoder_map["gop_param"][gop_name]
                    
                    # create directories for each kind of data
                    output_dir = ".\\bitstream\\{}_{}_{}_{}".format(encoder, preset, rc_mode, gop_name)
                    if(os.path.exists(output_dir) == False):
                        os.system("mkdir {}".format(output_dir))
                    psnr_log_dir = "{}\\psnr_log".format(output_dir)
                    if(os.path.exists(psnr_log_dir) == False):
                        os.system("mkdir {}".format(psnr_log_dir))
                    ssim_log_dir = "{}\\ssim_log".format(output_dir)
                    if(os.path.exists(ssim_log_dir) == False):
                        os.system("mkdir {}".format(ssim_log_dir))
                    vmaf_log_dir = "{}\\vmaf_log".format(output_dir)
                    if(os.path.exists(vmaf_log_dir) == False):
                        os.system("mkdir {}".format(vmaf_log_dir))
                    cmd_log_dir = "{}\\cmd_log".format(output_dir)
                    if(os.path.exists(cmd_log_dir) == False):
                        os.system("mkdir {}".format(cmd_log_dir))
                    bit_file_dir = "{}\\bit_file_log".format(output_dir)
                    if(os.path.exists(bit_file_dir) == False):
                        os.system("mkdir {}".format(bit_file_dir))
                    enc_log_dir = "{}\\enc_log".format(output_dir)
                    if(os.path.exists(enc_log_dir) == False):
                        os.system("mkdir {}".format(enc_log_dir))
                    err_log_dir = "{}\\err_log".format(output_dir)
                    if(os.path.exists(err_log_dir) == False):
                        os.system("mkdir {}".format(err_log_dir))
                    dec_log_dir = "{}\\dec_log".format(output_dir)
                    if(os.path.exists(dec_log_dir) == False):
                        os.system("mkdir {}".format(dec_log_dir))

                    # create command log file for current setting
                    if g_ENABLE_ENCODE == True:
                        cmd_log_file = open("{}/{}_{}_{}_{}_cmd.log".format(cmd_log_dir, encoder, preset, rc_mode, gop_name), "w")
                        err_log_file = open("{}/{}_{}_{}_{}_err.log".format(err_log_dir, encoder, preset, rc_mode, gop_name), "w")
                    else:
                        cmd_log_file = False

                    # create csv to record psnr, ssim, etc
                    if g_ENABLE_PARSING == True:
                        score_file = open("{}/{}_{}_{}_{}.csv".format(output_dir, encoder, preset, rc_mode, gop_name), "w")
                        if(rc_mode == 'VBR' or rc_mode == 'ABR'):
                            score_file.write("sequence, resolution, target bitrate, actual bitrate, PSNR Y, U, V, average, SSIM Y, U, V, average, VMAF, fps\n")
                        elif(rc_mode == 'CQP'):
                            score_file.write("sequence, resolution, QP, actual bitrate, PSNR Y, U, V, average, SSIM Y, U, V, average, VMAF, fps\n")
                        else:
                            score_file.write("sequence, resolution, CRF, actual bitrate, PSNR Y, U, V, average, SSIM Y, U, V, average, VMAF, fps\n")
                        
                    for seq_set in encoder_map["test_seq"]:
                        test_seq_list = seq_list.seq_list[seq_set]
                        root = test_seq_list['dir']
                        for seq_params in test_seq_list['seq']:
                            yuv_name = seq_params[0]
                            width = seq_params[1]
                            height = seq_params[2]
                            fps = seq_params[3]
                            br_list = seq_params[4]
                            
                            print ("encoder: {}, preset: {}, rc: {}, gop: {}, seq: {}".format(encoder, preset, rc_mode, gop_name, yuv_name))
                            if(rc_mode == 'VBR' or rc_mode == 'ABR'):
                                test_points = br_list
                            else:
                                test_points = common_cfg.crf_cqp_points
                            for point in test_points:
                                test_name_prefix = "{}_{}_{}_{}_{}_{}".format(encoder, os.path.splitext(yuv_name)[0], preset, gop_name, rc_mode, point)
                                if(encoder.find('264') != -1):
                                    stream = "{}\\{}.264".format(bit_file_dir, test_name_prefix)
                                else:
                                    stream = "{}\\{}.265".format(bit_file_dir, test_name_prefix)
                                enc_log_file = "{}/{}_enc.log".format(enc_log_dir, test_name_prefix)

                                # step 1 encode
                                if (encoder == 'x264'):
                                    [frame_num, speed_in_fps, encoding_time, actual_bitrate] = func_x264_enc(preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, enc_log_file, cmd_log_file)
                                elif (encoder == 'x265'):
                                    extra_param = "--aq-mode 0 --rd 1"
                                    [frame_num, speed_in_fps, encoding_time, actual_bitrate] = func_x265_enc(encoder, extra_param, preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, enc_log_file, cmd_log_file)
                                elif (encoder == 'stellar_x265'):
                                    extra_param = "--aq-mode 0 --rd 1 --no-cu64 --no-intra-nxn --intra-sync-size 32 --no-intra-rdo"
                                    [frame_num, speed_in_fps, encoding_time, actual_bitrate] = func_x265_enc(encoder, extra_param, preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, enc_log_file, cmd_log_file)
                                elif (encoder == 'kavazaar'):
                                    [frame_num, speed_in_fps, encoding_time, actual_bitrate] = func_kavazaar_enc(preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, enc_log_file, cmd_log_file)
                                elif (encoder == 'stellar_264'):
                                    [frame_num, speed_in_fps, encoding_time, actual_bitrate] = func_stellar_264_enc(preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, enc_log_file, cmd_log_file)
                                elif (encoder == 'stellar_265'):
                                    [frame_num, speed_in_fps, encoding_time, actual_bitrate] = func_stellar_265_enc(preset, rc_mode, gop_param, root, yuv_name, width, height, point, stream, enc_log_file, cmd_log_file)
                                else:
                                    print ("encoder type {} is not supported yet".format(encoder))
                                    exit(0)
                                
                                if(frame_num == -1):
                                    err_log_file.write("Encoder error for {}\n".format(stream))
                                    continue
                                
                            
                                if g_ENABLE_CALC_SCORE == True:
                                    # step 2 decode
                                    dec_log_file = "{}/{}_enc.log".format(dec_log_dir, test_name_prefix)
                                    dec_yuv = "{}_dec.yuv".format(test_name_prefix)
                                    if (encoder == 'stellar_264'):
                                        # TODO: using ffmpeg to decode will have error
                                        dec_cmd = ".\\binary\\ldecod.exe -p InputFile=\"{}\" -p OutputFile=\"{}\"".format(stream, dec_yuv)
                                    else:
                                        dec_cmd = "ffmpeg -i {} -vsync 0  -pix_fmt yuv420p -f rawvideo {} -y -loglevel error".format(stream, dec_yuv)
                                    
                                    os.system("{} > {} 2>&1 & ".format(dec_cmd, dec_log_file))
                                    if g_ENABLE_ENCODE == True:
                                        cmd_log_file.write(dec_cmd + "\n")
                                        if g_ENABLE_ENC_CHECK == True:
                                            cmp_result = os.system("cmp rec.yuv {}".format(dec_yuv))
                                            if cmp_result:
                                                print ("enc/dec mismatch found\n")
                                                exit(-1)
                                            #else:
                                            #    os.system("pause")
                                            os.system("rm rec.yuv")

                                    # crop for stellar 264 encoder when height is not 16 aligned
                                    if (encoder == 'stellar_264' and (height % 16) != 0):
                                        height_align = height - (height % 16) + 16
                                        crop_cmd = "ffmpeg -s {}x{} -f rawvideo -pix_fmt yuv420p -i {} -vf crop={}:{}:0:0 dec.yuv -y > nul 2>&1 &".format(width, height_align, dec_yuv, width, height)
                                        os.system(crop_cmd)
                                        os.system("del {}".format(dec_yuv))
                                        os.system("rename dec.yuv {}".format(dec_yuv))
                                        
                                    # step 3 calculate psnr, ssim and VMAF
                                    basic_cmd = "ffmpeg -s {}x{} -pix_fmt yuv420p -f rawvideo -i {}/{} -s {}x{} -pix_fmt yuv420p -f rawvideo -i {} -frames {}".format(width, height, root, yuv_name, width, height, dec_yuv, frame_num)
                                    psnr_file = "{}/psnr_{}.txt".format(psnr_log_dir, test_name_prefix)
                                    psnr_cmd = "{} -lavfi psnr -f null -".format(basic_cmd)
                                    os.system("{} > {} 2>&1 & ".format(psnr_cmd, psnr_file))
                                    if g_ENABLE_ENCODE == True:
                                        cmd_log_file.write(psnr_cmd + "\n")

                                    ssim_file = "{}/ssim_{}.txt".format(ssim_log_dir, test_name_prefix)
                                    ssim_cmd = "{} -lavfi ssim -f null -".format(basic_cmd)
                                    os.system("{} > {} 2>&1 & ".format(ssim_cmd, ssim_file))
                                    if g_ENABLE_ENCODE == True:
                                        cmd_log_file.write(ssim_cmd + "\n")

                                    if g_ENABLE_CALC_VMAF == True:
                                        vmaf_file = "{}/vmaf_{}.txt".format(vmaf_log_dir, test_name_prefix)
                                        vmaf_detail_json_file = "{}/vmaf_detail_{}.json".format(vmaf_log_dir, test_name_prefix)
                                        vmaf_cmd = "{} -lavfi \"libvmaf=model_path=./model/vmaf_v0.6.1.pkl:psnr=1:ssim=1:ms_ssim=1:log_fmt=json:log_path={}\" -f null -".format(basic_cmd, vmaf_detail_json_file)
                                        os.system("{} > {} 2>&1 & ".format(vmaf_cmd, vmaf_file))
                                        if g_ENABLE_ENCODE == True:
                                            cmd_log_file.write(vmaf_cmd + "\n")

                                    # step 4: clean up, delete intermediate files, especially decoded YUV
                                    os.system("del *_dec.yuv")

                                if g_ENABLE_PARSING == True:
                                    # step 5: parse log files, to get psnr, ssim, and vmaf
                                    for line in open("{}/psnr_{}.txt".format(psnr_log_dir, test_name_prefix), 'r'):
                                        # [Parsed_psnr_0 @ 00000217af7be800] PSNR y:28.785715 u:35.178416 v:34.610500 average:30.043795 min:23.428239 max:32.324142
                                        data = re.search("PSNR y:(.*) u:(.*) v:(.*) average:(.*) min:(.*) max:(.*)", line)
                                        if data:
                                            psnr_y = data.group(1)
                                            psnr_u = data.group(2)
                                            psnr_v = data.group(3)
                                            psnr_a = data.group(4)

                                    for line in open("{}/ssim_{}.txt".format(ssim_log_dir, test_name_prefix), 'r'):
                                        # [Parsed_ssim_0 @ 0000020ca1a32e40] SSIM Y:0.831603 (7.736647) U:0.906896 (10.310310) V:0.914640 (10.687450) All:0.857991 (8.476843)
                                        data = re.search("SSIM Y:(.*) \((.*)\) U:(.*) \((.*)\) V:(.*) \((.*)\) All:(.*) \((.*)\)", line)
                                        if data:
                                            ssim_y = data.group(1)
                                            ssim_u = data.group(3)
                                            ssim_v = data.group(5)
                                            ssim_a = data.group(7)
                                            break
                                    vmaf = 0.0
                                    if g_ENABLE_CALC_VMAF == True:
                                        for line in open("{}/vmaf_{}.txt".format(vmaf_log_dir, test_name_prefix), 'r'):
                                            # [libvmaf @ 0000026c97161680] VMAF score: 99.754917
                                            data = re.search("VMAF score: (.*)", line)
                                            if data:
                                                vmaf = data.group(1)
                                                break

                                        #vmaf_detail = json.load(open("{}/vmaf_detail_{}.json".format(vmaf_log_dir, test_name_prefix), 'r'))
                                        #print (vmaf_detail)

                                    # sequence, resolution, target bitrate/QP/CRF, actual bitrate, PSNR Y, U, V, average, SSIM Y, U, V, average, VMAF
                                    # for some encoders, encoding_time may not available and set to -1
                                    score_file.write("{},{}x{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(yuv_name, width, height, point, actual_bitrate, psnr_y, psnr_u, psnr_v, psnr_a, ssim_y, ssim_u, ssim_v, ssim_a, vmaf, speed_in_fps, encoding_time))






