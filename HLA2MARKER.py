# -*- coding: utf-8 -*-

import os, sys, re
import argparse, textwrap
from platform import platform


def HLA2MARKER(_HLA_ped, _OUT,
               _dictionary_AA,
               _dictionary_SNPS,
               _hg="19",
               _p_src="./src", _p_dependency="./dependency"):

    """

    """

    ########## < Core Variables > ##########

    ### Module name

    std_MAIN_PROCESS_NAME = "\n[%s]: " % (os.path.basename(__file__))
    print(std_MAIN_PROCESS_NAME + "Init.\n")


    ### Major Path Variables

    # [1] src (with "_p_src")
    p_src_MakeReferece = os.path.join(_p_src, "MakeReference")


    # [2] dependency (with "_p_dependency")
    _p_plink = os.path.join(_p_dependency, "plink_mac" if not bool(re.search(pattern="Linux", string=platform())) else "plink_linux")
    _p_beagle = os.path.join(_p_dependency, "beagle.jar")
    _p_linkage2beagle = os.path.join(_p_dependency, "linkage2beagle.jar")


    ### Dictionary Files

    _dictionary_AA_seq = _dictionary_AA + ".txt" # From now on, official extension of HLA sequence information dictionary is ".txt". (2018. 9. 25.)
    _dictionary_AA_map = _dictionary_AA + ".map"

    _dictionary_SNPS_seq = _dictionary_SNPS + ".txt"
    _dictionary_SNPS_map = _dictionary_SNPS + ".map"


    ### Intermediate path.

    OUTPUT = _OUT if not _OUT.endswith('/') else _OUT.rstrip('/')
    INTERMEDIATE_PATH = os.path.dirname(OUTPUT)

    print(std_MAIN_PROCESS_NAME + "Intermediate folder path is {0},\nOutput filename prefix is {1}\n\n".format(
        INTERMEDIATE_PATH, os.path.basename(OUTPUT)))

    if not os.path.exists(INTERMEDIATE_PATH):
        os.system(' '.join(["mkdir -p", INTERMEDIATE_PATH]))



    ########## < Checking Dependencies > ##########

    ### Other Software.

    if not os.path.exists(_p_plink):
        print(
            std_MAIN_PROCESS_NAME + "Please Prepare 'PLINK' (http://pngu.mgh.harvard.edu/~purcell/plink/download.shtml) in '{0}'\n".format(
                os.path.dirname(_p_plink)))
        sys.exit()
    if not os.path.exists(_p_beagle):
        print(
            std_MAIN_PROCESS_NAME + "Please Prepare 'Beagle 3' (http://faculty.washington.edu/browning/beagle/beagle.html#download) in '{0}'\n".format(
                os.path.dirname(_p_beagle)))
        sys.exit()
    if not os.path.exists(_p_linkage2beagle):
        print(
            std_MAIN_PROCESS_NAME + "Please Prepare 'linkage2beagle.jar' (http://faculty.washington.edu/browning/beagle_utilities/utilities.html) (beagle.3.0.4/utility/linkage2beagle.jar) in '{0}'\n".format(
                os.path.dirname(_p_linkage2beagle)))
        sys.exit()


    ### Dictionary Information for HLA sequence

    if not os.path.exists(_dictionary_AA_map):
        print(
            std_MAIN_PROCESS_NAME + "Please Prepare 'HLA_DICTIONARY_AA.map' (included with this package) in '{0}'\n".format(
                os.path.dirname(_dictionary_AA_map)))
        sys.exit()

    if not os.path.exists(_dictionary_AA_seq):
        print(std_MAIN_PROCESS_NAME + "Please Prepare 'HLA_DICTIONARY_AA.txt' (included with this package) in '{0}'\n".format(
                os.path.dirname(_dictionary_AA_seq)))
        sys.exit()

    if not os.path.exists(_dictionary_SNPS_map):
        print(std_MAIN_PROCESS_NAME + "Please Prepare 'HLA_DICTIONARY_SNPS.map' (included with this package) in '{0}'\n".format(
                os.path.dirname(_dictionary_SNPS_map)))
        sys.exit()

    if not os.path.exists(_dictionary_SNPS_seq):
        print(std_MAIN_PROCESS_NAME + "Please Prepare 'HLA_DICTIONARY_SNPS.txt' (included with this package) in '{0}'\n".format(
                os.path.dirname(_dictionary_SNPS_seq)))
        sys.exit()


    ### Source Code Scripts

    # New version with Python.

    if not os.path.exists(os.path.join(p_src_MakeReferece, "HLAtoSequences.py")):
        print(std_MAIN_PROCESS_NAME + "Error. 'HLAtoSequences.py' not found in '{0}'".format(p_src_MakeReferece))
        sys.exit()
    else:
        from src.HLA2MARKER.HLAtoSequences import HLAtoSequences

    if not os.path.exists(os.path.join(p_src_MakeReferece, "encodeVariants.py")):
        print(std_MAIN_PROCESS_NAME + "Error. 'encodeVariants.py' not found in '{0}'".format(p_src_MakeReferece))
        sys.exit()
    else:
        from src.HLA2MARKER.encodeVariants import encodeVariants

    if not os.path.exists(os.path.join(p_src_MakeReferece, "encodeHLA.py")):
        print(std_MAIN_PROCESS_NAME + "Error. 'encodeHLA.py' not found in '{0}'".format(p_src_MakeReferece))
        sys.exit()
    else:
        from src.HLA2MARKER.encodeHLA import encodeHLA




    ########## < Core Variables 2 > ##########

    HLA_DATA = _HLA_ped

    AA_CODED = OUTPUT + '.AA.CODED'
    HLA_CODED = OUTPUT + ".HLA"
    SNPS_CODED = OUTPUT + '.SNPS.CODED'

    plink = ' '.join([_p_plink, "--noweb", "--silent"])
    beagle = ' '.join(["java", "-Xmx2000m", "-jar", _p_beagle])
    linkage2beagle = ' '.join(["java", "-Xmx2000m", "-jar", _p_linkage2beagle])




    ########## <Flags for Code Block> ##########

    ENCODE_AA = 1
    ENCODE_HLA = 1
    ENCODE_SNPS = 1

    MERGE = 1
    PREPARE = 1
    PHASE = 1
    CLEANUP = 1




    ########## <Making Reference Panel> ##########

    print(std_MAIN_PROCESS_NAME + "Making Reference Panel for \"{0}\"".format(OUTPUT))

    if ENCODE_AA:

        '''
        echo "[$i] Generating amino acid sequences from HLA types.";  @ i++
        ./HLAtoSequences.pl $HLA_DATA HLA_DICTIONARY_AA.txt AA > $OUTPUT.AA.ped
        cp HLA_DICTIONARY_AA_hg19.map $OUTPUT.AA.map # hg19
        # cp HLA_DICTIONARY_AA.map $OUTPUT.AA.map

        echo "[$i] Encoding amino acids positions." ;  @ i++
        ./encodeVariants.pl $OUTPUT.AA.ped $OUTPUT.AA.map $OUTPUT.AA.CODED

        plink --file $OUTPUT.AA.CODED --missing-genotype 0 --make-bed --out $OUTPUT.AA.TMP
        awk '{if ($5 == "0" || $5 == "x" || $6 == "x"){print $2}}' $OUTPUT.AA.TMP.bim | grep -v INS | cut -f2 > to_remove
        plink --bfile $OUTPUT.AA.TMP --exclude to_remove --make-bed --out $OUTPUT.AA.CODED

        # rm $OUTPUT.AA.TMP*; rm to_remove
        # rm $OUTPUT.AA.???
        '''

        print("\n[1] Generating amino acid sequences from HLA types.")

        HLAtoSequences(HLA_DATA, _dictionary_AA_seq, "AA", _out=OUTPUT)

        os.system(' '.join(["cp", _dictionary_AA_map, OUTPUT + '.AA.map']))



        print("\n[2] Encoding amino acids positions.")

        encodeVariants(OUTPUT + '.AA.ped', OUTPUT + '.AA.map', OUTPUT + '.AA.CODED')  # previously "enCODED".

        # command for checking output from encodeVariant.py(.pl)
        command = ' '.join(
            [plink, "--file", OUTPUT + '.AA.CODED', "--missing-genotype 0", "--make-bed", "--out", OUTPUT + '.AA.TMP'])
        print(command)
        os.system(command)

        # MakeReference
        # command = ' '.join(
        #     ["awk", '\'{if ($5 == "0" || $5 == "x" || $6 == "x"){print $2}}\'', OUTPUT + '.AA.TMP.bim', "|",
        #      "grep -v {0}".format("INDEL"), "|", "cut -f2", ">",
        #      os.path.join(INTERMEDIATE_PATH, "to_remove")])

        # HLA2MARKER
        command = ' '.join(
            ["awk", '\'{if ($5 == "0" || $5 == "x" || $6 == "x"){print $2}}\'', OUTPUT + '.AA.TMP.bim', "|",
             "cut -f2", ">",
             os.path.join(INTERMEDIATE_PATH, "to_remove")])

        """
        In previous framework originally created by Sherman Jia, Only insertions were dealt with as a marker "INS".
        In the new version of Framework, marker label is "INDEL".
        """

        print(command)
        os.system(command)

        command = ' '.join(
            [plink, "--bfile", OUTPUT + '.AA.TMP',
             "--exclude", os.path.join(INTERMEDIATE_PATH, "to_remove"),
             "--make-bed",
             "--out", OUTPUT + '.AA.CODED'])
        print(command)
        os.system(command)

        rm_tlist = (OUTPUT + '.AA.TMP*', os.path.join(INTERMEDIATE_PATH, "to_remove"), OUTPUT + '.AA.???')

        for i in rm_tlist:
            print(i)
            os.system("rm " + i)




    if ENCODE_HLA:

        print("\n[3] Encoding HLA alleles.")

        encodeHLA(HLA_DATA, OUTPUT, _hg)

        command = ' '.join([plink, "--file", OUTPUT + '.HLA', "--make-bed", "--out", OUTPUT + '.HLA'])
        print(command)
        os.system(command)




    if ENCODE_SNPS:

        print("\n[4] Generating DNA sequences from HLA types.")

        HLAtoSequences(HLA_DATA, _dictionary_SNPS_seq, "SNPS", OUTPUT)

        command = ' '.join(["cp", _dictionary_SNPS_map, OUTPUT + '.SNPS.map'])
        print(command)
        os.system(command)



        print("\n[5] Encoding SNP positions.")

        encodeVariants(OUTPUT + '.SNPS.ped', OUTPUT + '.SNPS.map', OUTPUT + '.SNPS.CODED')

        command = ' '.join([plink, "--file", OUTPUT + '.SNPS.CODED', "--missing-genotype 0", "--make-bed", "--out",
                            OUTPUT + '.SNPS.TMP'])
        print(command)
        os.system(command)


        # # MakeReference
        # command = ' '.join(
        #     ["awk", '\'{if ($5 == "0" || $5 == "x" || $6 == "x"){print $2}}\'', OUTPUT + '.SNPS.TMP.bim', "|",
        #      "grep -v {0}".format("INDEL"), "|", "cut -f2", ">",
        #      os.path.join(INTERMEDIATE_PATH, "to_remove")])

        # HLA2MARKER
        command = ' '.join(
            ["awk", '\'{if ($5 == "0" || $5 == "x" || $6 == "x"){print $2}}\'', OUTPUT + '.SNPS.TMP.bim', "|", "cut -f2", ">",
             os.path.join(INTERMEDIATE_PATH, "to_remove")])
        print(command)
        os.system(command)

        command = ' '.join(
            [plink, "--bfile", OUTPUT + '.SNPS.TMP',
             "--exclude", os.path.join(INTERMEDIATE_PATH, "to_remove"),
             "--make-bed",
             "--out", OUTPUT + '.SNPS.CODED'])
        print(command)
        os.system(command)

        rm_tlist = (OUTPUT + '.SNPS.TMP*', os.path.join(INTERMEDIATE_PATH, 'to_remove'), OUTPUT + '.SNPS.???')

        for i in rm_tlist:
            print(i)
            os.system("rm " + i)








    if MERGE:

        print("\n[6] Merging SNP, HLA, and amino acid datasets.")

        """
        echo "[$i] Merging SNP, HLA, and amino acid datasets.";  @ i++
        echo "$OUTPUT.HLA.FOUNDERS.bed $OUTPUT.HLA.FOUNDERS.bim $OUTPUT.HLA.FOUNDERS.fam" > merge_list
        echo "$OUTPUT.AA.FOUNDERS.bed $OUTPUT.AA.FOUNDERS.bim $OUTPUT.AA.FOUNDERS.fam" >> merge_list
        echo "$OUTPUT.SNPS.FOUNDERS.bed $OUTPUT.SNPS.FOUNDERS.bim $OUTPUT.SNPS.FOUNDERS.fam" >> merge_list
        plink --bfile $SNP_DATA.FOUNDERS.QC --merge-list merge_list --make-bed --out $OUTPUT.MERGED.FOUNDERS
        rm $OUTPUT.HLA.???
        rm $OUTPUT.AA.CODED.???
        rm $OUTPUT.SNPS.CODED.???
        rm merge_list
        
        
        (2018. 9. 25.)
        
        Modified to work for HLA2MARKER.
        
        Conventional SNP variant marker(outside of MHC complex region) won't be included anymore.

        """

        TMP_merged_list = os.path.join(INTERMEDIATE_PATH, "merge_list")

        command = ' '.join(["echo", AA_CODED+'.bed', AA_CODED+'.bim', AA_CODED+'.fam', ">", TMP_merged_list])
        print(command)
        os.system(command)

        command = ' '.join(["echo", HLA_CODED+'.bed', HLA_CODED+'.bim', HLA_CODED+'.fam', ">>", TMP_merged_list])
        print(command)
        os.system(command)

        command = ' '.join(["echo", SNPS_CODED+'.bed', SNPS_CODED+'.bim', SNPS_CODED+'.fam', ">>", TMP_merged_list])
        print(command)
        os.system(command)


        command = ' '.join([plink, "--merge-list", TMP_merged_list, "--make-bed", "--out", OUTPUT+'.MERGED.TMP'])
        print(command)
        os.system(command)


        # Setting allele order

        """
        This part is originally done in "QC" code block in MakeReferene.
        """

        TMP_allele_order = os.path.join(INTERMEDIATE_PATH, OUTPUT+".MERGED.refallele")

        command = ' '.join(["awk", '\'{if (NR > 1){if (($5 == "a" && $6 == "p") || ($6 == "a" && $5 == "p")){print $2 "\tp"}}}\'', OUTPUT+'.MERGED.TMP.bim', ">", TMP_allele_order])
        print(command)
        os.system(command)


        command = ' '.join([plink, "--make-bed", "--bfile", OUTPUT+'.MERGED.TMP', "--reference-allele", TMP_allele_order, "--out", OUTPUT+'.MERGED'])
        print(command)
        os.system(command)



        rm_tlist = [OUTPUT+'.MERGED.TMP.*', TMP_merged_list]

        for i in rm_tlist:
            print(i)
            os.system("rm "+i)




    if PREPARE:

        """
        [Source from Buhm Han.]

        awk '{print $2 " " $4 " " $5 " " $6}' $OUTPUT.bim > $OUTPUT.markers
        plink --bfile $OUTPUT --keep-allele-order --recode --alleleACGT --out $OUTPUT
        awk '{print "M " $2}' $OUTPUT.map > $OUTPUT.dat
        cut -d ' ' -f1-5,7- $OUTPUT.ped > $OUTPUT.nopheno.ped

        echo "[$i] Converting to beagle format.";  @ i++
        linkage2beagle pedigree=$OUTPUT.nopheno.ped data=$OUTPUT.dat beagle=$OUTPUT.bgl standard=true > $OUTPUT.bgl.log


        [Source from Yang.]

        awk '{print $2 " " $4 " " $5 " " $6}' $OUTPUT.bim > $OUTPUT.markers
        plink --bfile $OUTPUT --keep-allele-order --recode --alleleACGT --out $OUTPUT
        plink --bfile $OUTPUT --recode --transpose --out $OUTPUT
        # awk '{print "M " $2}' $OUTPUT.map > $OUTPUT.dat
        # cut -d ' ' -f1-5,7- $OUTPUT.ped > $OUTPUT.nopheno.ped

        echo "[$i] Converting to beagle format.";  @ i++
        beagle2vcf -fnmarker $OUTPUT.markers -fnfam $OUTPUT.fam -fngtype $OUTPUT.tped -fnout $OUTPUT.vcf

        I will make this code block based on source given by Yang. for now.

        """

        print("\n[7] Preparing files for Beagle.")

        # *.markers
        command = ' '.join(["awk", '\'{print $2 " " $4 " " $5 " " $6}\'', OUTPUT + '.MERGED.bim', ">", OUTPUT + '.MERGED.markers'])
        print(command)
        os.system(command)

        command = ' '.join([plink, "--bfile", OUTPUT+".MERGED", "--keep-allele-order", "--recode", "--alleleACGT", "--out", OUTPUT+".MERGED"])
        print(command)
        os.system(command)

        # *.dat
        command = ' '.join(["awk", '\'{print "M " $2}\'', OUTPUT + '.MERGED.map', ">", OUTPUT + '.MERGED.dat'])
        print(command)
        os.system(command)

        # *.nopheno.ped
        command = ' '.join(["cut -d ' ' -f1-5,7-", OUTPUT + '.MERGED.ped', ">", OUTPUT + '.MERGED.nopheno.ped'])
        print(command)
        os.system(command)


        print("\n[8] Converting to beagle format.")

        command = ' '.join([linkage2beagle, "pedigree=" + OUTPUT + '.MERGED.nopheno.ped', "data=" + OUTPUT + '.MERGED.dat',
                            "beagle=" + OUTPUT + '.MERGED.bgl', "standard=true", ">", OUTPUT + '.MERGED.bgl.log'])
        print(command)
        os.system(command)




    if PHASE:

        # Put this part postponed. (2017.11.29. by B. Han.)
        # Anyway introduced phasing by beagle. (2018. 7. 16.)

        '''
        beagle unphased=$OUTPUT.bgl nsamples=4 niterations=10 missing=0 verbose=true maxwindow=1000 log=$OUTPUT.phasing >> $OUTPUT.bgl.log

        '''
        print("\n[9] Phasing reference using Beagle (see progress in $OUTPUT.bgl.log).")

        command = ' '.join(
            [beagle, "unphased=" + OUTPUT + '.MERGED.bgl', "nsamples=4 niterations=10 missing=0 verbose=true maxwindow=1000",
             "log=" + OUTPUT + '.MERGED.phasing', ">>", OUTPUT + '.MERGED.bgl.log'])
        print(command)
        os.system(command)




    if CLEANUP:

        print("\n[10] Removing unnecessary files.")

        rm_tlist = ('.nopheno.ped', '.bgl.gprobs', '.bgl.r2', '.bgl', '.ped', '.map', '.dat')

        for i in rm_tlist:
            print("rm " + OUTPUT+".MERGED" + i)
            os.system("rm " + OUTPUT+".MERGED" + i)

    print("\n[11] Done!")

    return 0


if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description=textwrap.dedent('''\
    #################################################################################################

        HLA2MARKER.py

        Generating markers based on HLA sequence information dictionary(generated bt "MakeDictionary").

        (ex.)
        : python3 HLA2MARKER.py  
            -ped ./data/MakeReference/HAPMAP_CEU_HLA.4field.ped 
            -hg 18 
            -o ./Trial_HAPMAP_CEU
            -dict-AA ./data/MakeReference/HLA_DICTIONARY_AA.hg18.imgt370
            -dict-SNPS ./data/MakeReference/HLA_DICTIONARY_SNPS.hg18.imgt370 

        HLA PED file should contain HLA alleles in the following (alphabetical) order:
        HLA-A, B, C, DPA1, DPB1, DQA1, DQB1, DRB1

    #################################################################################################
                                     '''),
                                     # epilog="-*- Recoded to Python script by Wansun Choi in Han lab. at Asan Medical Center -*-",
                                     add_help=False)

    parser._optionals.title = "OPTIONS"

    parser.add_argument("-h", "--help", help="\nShow this help message and exit\n\n", action='help')

    parser.add_argument("-ped", help="\nHLA Type Data(.ped)\n\n", required=True)
    parser.add_argument("-hg", help="\nHuman Genome version(ex. 18, 19)\n\n", choices=["18", "19", "38"], metavar="hg", default="19")
    parser.add_argument("-o", help="\nOutput file prefix\n\n")

    parser.add_argument("-dict-AA", help="\nPrefix of AA HLA Dictionary file(*.txt, *.map).\n\n", default="Not_given")
    parser.add_argument("-dict-SNPS", help="\nPrefix of SNP HLA Dictionary file(*.txt, *.map).\n\n", default="Not_given")



    ##### <for Test> #####

    # HLA2MARKER (2018. 9. 25.) : hg18 / imgt3320
    # args = parser.parse_args(["-ped", "/Users/wansun/Dropbox/_Sync_MyLaptop/from_WansunChoi_to_Professor/20180910_Cancer_fixed/hg18_imgt3320/Cancer_merged.phe_reversed.fam_fixed.imgt3320.4field.ped",
    #                           "-o", "/Users/wansun/Git_Projects/HATK/HLA2MARKER_test/Marker_Panel.hg18.imgt3320",
    #                           "-dict-AA", "/Users/wansun/Dropbox/_Sync_MyLaptop/from_WansunChoi_to_Professor/20180910_Cancer_fixed/hg18_imgt3320/MAKEDICTIONARY_v2_hg18_imgt3320/HLA_DICTIONARY_AA.hg18.imgt3320",
    #                           "-dict-SNPS", "/Users/wansun/Dropbox/_Sync_MyLaptop/from_WansunChoi_to_Professor/20180910_Cancer_fixed/hg18_imgt3320/MAKEDICTIONARY_v2_hg18_imgt3320/HLA_DICTIONARY_SNPS.hg18.imgt3320",
    #                           "-hg", "18"
    #                           ])


    #  HLA2MARKER (2018. 9. 25.) : hg19 / imgt3320
    # args = parser.parse_args(["-ped", "/Users/wansun/Dropbox/_Sync_MyLaptop/from_WansunChoi_to_Professor/20180910_Cancer_fixed/hg18_imgt3320/Cancer_merged.phe_reversed.fam_fixed.imgt3320.4field.ped",
    #                           "-o", "/Users/wansun/Git_Projects/HATK/HLA2MARKER_test_hg19/Marker_Panel.hg19.imgt3320",
    #                           "-dict-AA", "/Users/wansun/Git_Projects/HATK/MAKEDICTIONARY_v2_hg19_imgt3320/HLA_DICTIONARY_AA.hg19.imgt3320",
    #                           "-dict-SNPS", "/Users/wansun/Git_Projects/HATK/MAKEDICTIONARY_v2_hg19_imgt3320/HLA_DICTIONARY_SNPS.hg19.imgt3320",
    #                           "-hg", "19"
    #                           ])

    # #  HLA2MARKER (2018. 9. 25.) : hg38 / imgt3320
    # args = parser.parse_args(["-ped", "/Users/wansun/Dropbox/_Sync_MyLaptop/from_WansunChoi_to_Professor/20180910_Cancer_fixed/hg18_imgt3320/Cancer_merged.phe_reversed.fam_fixed.imgt3320.4field.ped",
    #                           "-o", "/Users/wansun/Git_Projects/HATK/HLA2MARKER_test_hg38/Marker_Panel.hg38.imgt3320",
    #                           "-dict-AA", "",
    #                           "-dict-SNPS", "",
    #                           "-hg", "38"
    #                           ])

    ##### <for Publication> #####

    args = parser.parse_args()
    # print(args)





    ##### Additional Argument processing

    t_dict_AA = ""
    t_dict_SNPS = ""

    if (args.dict_AA != "Not_given" and args.dict_SNPS != "Not_given"):

        # When all HLA DICTIONARY information is given properly,

        t_dict_AA = args.dict_AA
        t_dict_SNPS = args.dict_SNPS


    elif (args.dict_AA == "Not_given" and args.dict_SNPS == "Not_given"):

        # No values are given to HLA DICTIONARY related options.

        # Abort
        print("\n[Error]: None of HLA DICTIONARY files are given. Please check them all again.")
        print('{"-dict-AA", "-dict-SNPS"}\n')
        sys.exit()



    else:
        # Abort
        print("\n[Error]: Not all of HLA DICTIONARY files are given. Please check them all again.")
        print('{"-dict-AA", "-dict-SNPS"}\n')
        sys.exit()



    # Implementing Main Function.
    HLA2MARKER(_HLA_ped=args.ped, _OUT=args.o,
               _dictionary_AA=t_dict_AA,
               _dictionary_SNPS=t_dict_SNPS,
               _hg=args.hg)