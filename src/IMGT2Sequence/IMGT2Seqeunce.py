# -*- coding: utf-8 -*-

import os, sys, re
import pandas as pd
import argparse, textwrap
from glob import glob
import multiprocessing as mp

########## < Core Global Variables > ##########

### Module name && Std template
std_MAIN_PROCESS_NAME = "\n[%s]: " % (os.path.basename(__file__))
std_ERROR_MAIN_PROCESS_NAME = "\n[%s::ERROR]: " % (os.path.basename(__file__))



def HATK_IMGT2Sequence(_HG, _OUTPUT, _IMGT, _no_Indel=False, _no_MultiP = False,
                       _save_intermediates = False, _imgt_dir = None):

    """

    The wrapping function in interface with "HATK.py".
    Necessary argument checking will be conducted here.

    """


    ### Argument(HATK.py) checking.

    # "-hg"
    if not bool(_HG):
        print(std_ERROR_MAIN_PROCESS_NAME + 'The argument "{0}" has not given. Please check it again.\n'.format("-hg"))
        sys.exit()

    # "-imgt"
    if not bool(_IMGT):
        print(
            std_ERROR_MAIN_PROCESS_NAME + 'The argument "{0}" has not given. Please check it again.\n'.format("-imgt"))
        sys.exit()


    RETURN_dict_AA, RETURN_dict_SNPS, RETURN_IAT = \
        IMGT2Sequence(_HG=_HG, _OUTPUT=_OUTPUT, _IMGT=_IMGT, _no_Indel=_no_Indel,
                      _no_MultiP=_no_MultiP, _save_intermediates=_save_intermediates,
                      _imgt_dir=_imgt_dir)


    # # Summary
    # print(std_MAIN_PROCESS_NAME + "Output from IMGT2Sequence.\n")
    # print("1. dict_AA : {0}\n".format(RETURN_dict_AA))
    # print("2. dict_SNPS : {0}\n".format(RETURN_dict_SNPS))
    # print("3. IAT : {0}\n".format(RETURN_IAT))

    return [RETURN_dict_AA, RETURN_dict_SNPS, RETURN_IAT]




def IMGT2Sequence(_HG, _OUTPUT, _IMGT, _no_Indel=False, _no_MultiP = False,
                  _save_intermediates = False, _imgt_dir = None):

    """
    """

    ########## < Core Variables > ##########


    print(std_MAIN_PROCESS_NAME + "Conducting IMGT2Sequence.")


    # (2018. 8. 28.) This order must be kept.
    raw_HLA_names = ["A", "B", "C", "DPA", "DPB", "DQA", "DQB", "DRB"]
    HLA_names = ["A", "B", "C", "DPA1", "DPB1", "DQA1", "DQB1", "DRB1"]


    ### Dictionaries for Raw files.
    TARGET_prot_files = {}
    TARGET_nuc_files = {}
    TARGET_gen_files = {}


    ### Variables for Paths.
    p_data = "./data/IMGT2Sequence"
    p_src = "./src/IMGT2Sequence"


    ### OUTPUT prefix

    _OUTPUT = _OUTPUT if not _OUTPUT.endswith('/') else _OUTPUT.rstrip('/')
    INTERMEDIATE_PATH = os.path.dirname(_OUTPUT)

    if not os.path.exists(INTERMEDIATE_PATH):
        os.system(' '.join(["mkdir", "-p", INTERMEDIATE_PATH]))


    _OUTPUT_AA_RETURN = os.path.join(INTERMEDIATE_PATH, 'HLA_DICTIONARY_AA.hg{0}.imgt{1}'.format(_HG, _IMGT))
    _OUTPUT_SNPS_RETURN = os.path.join(INTERMEDIATE_PATH, 'HLA_DICTIONARY_SNPS.hg{0}.imgt{1}'.format(_HG, _IMGT))
    _OUTPUT_IAT_RETURN = os.path.join(INTERMEDIATE_PATH, 'HLA_INTEGRATED_ALLELE_TABLE.hg{0}.imgt{1}'.format(_HG, _IMGT))


    ########## < Dependency Checking > ##########

    """
    1. Necessary Python source files.
    2. Necessary Static Data files
    3. Checking each files of "*_nuc.txt", "*_prot.txt", "*_gen.txt".
    """


    ##### < Necessary Python source files > #####

    # ProcessIMGT.py
    if os.path.exists(os.path.join(p_src, "ProcessIMGT.py")):
        from src.IMGT2Sequence.ProcessIMGT import ProcessIMGT
    else:
        print(std_ERROR_MAIN_PROCESS_NAME + "\"src/IMGT2Sequence/ProcessIMGT.py\" doesn't exist!")
        sys.exit()

    # ClassifyGroups.py
    if os.path.exists("src/NomenCleaner/ClassifyGroups.py"):
        from src.NomenCleaner.ClassifyGroups import ClassifyGroups
    else:
        print(std_ERROR_MAIN_PROCESS_NAME + "\"src/NomenCleaner/ClassifyGroups.py\" doesn't exist!")
        sys.exit()



    ##### < Necessary Static Data files > #####

    HLA_INTEGRATED_POSITIONS_filename = os.path.join(p_data, "HLA_INTEGRATED_POSITIONS_hg{0}.txt".format(_HG))
    IMGTHLA_directory = os.path.join(p_data, "IMGTHLA{0}".format(_IMGT)) if not bool(_imgt_dir) else _imgt_dir

    print(HLA_INTEGRATED_POSITIONS_filename)
    print(IMGTHLA_directory)

    if not os.path.exists(HLA_INTEGRATED_POSITIONS_filename):
        print(std_ERROR_MAIN_PROCESS_NAME + "\"{0}\" not found!".format(HLA_INTEGRATED_POSITIONS_filename))
        sys.exit()

    if not os.path.isdir(IMGTHLA_directory):
        print(std_ERROR_MAIN_PROCESS_NAME + "\"{0}\" not found!".format(IMGTHLA_directory))
        sys.exit()


    ##### < "*_nuc.txt", "*_prot.txt", "*_gen.txt" > #####

    files_in_alignments = glob(IMGTHLA_directory + '/alignments/*')

    for i in range(0, len(HLA_names)):

        ### <*_prot.txt, *_nuc.txt>
        found_prot = list(filter(re.compile("/" + raw_HLA_names[i] + "_prot.txt").search, files_in_alignments))
        found_nuc = list(filter(re.compile("/" + raw_HLA_names[i] + "_nuc.txt").search, files_in_alignments))

        if len(found_prot) == 1:
            # When found exactly.
            TARGET_prot_files[HLA_names[i]] = found_prot.pop()
            TARGET_nuc_files[HLA_names[i]] = found_nuc.pop()

        else:
            # If not, then try same job to the names with number "1".
            found_prot = list(filter(re.compile("/" + HLA_names[i] + "_prot.txt").search, files_in_alignments))
            found_nuc = list(filter(re.compile("/" + HLA_names[i] + "_nuc.txt").search, files_in_alignments))

            if len(found_prot) == 1:
                # When found exactly in 2nd trial.
                TARGET_prot_files[HLA_names[i]] = found_prot.pop()
                TARGET_nuc_files[HLA_names[i]] = found_nuc.pop()
            else:
                # Not found finally.
                print(std_ERROR_MAIN_PROCESS_NAME + "\"{0}_prot.txt\" or \"{0}_nuc.txt\" file can't be found.".format(HLA_names[i]))
                sys.exit()

        ### <*_gen.txt>

        found_gen = list(filter(re.compile("/" + raw_HLA_names[i] + "_gen.txt").search, files_in_alignments))

        if len(found_gen) == 1:
            # When found exactly.
            TARGET_gen_files[HLA_names[i]] = found_gen.pop()
        else:
            # If not, then try same job to the names with number "1".
            found_gen = list(filter(re.compile("/" + HLA_names[i] + "_gen.txt").search, files_in_alignments))

            if len(found_gen) == 1:
                # When found exactly in 2nd trial.
                TARGET_gen_files[HLA_names[i]] = found_gen.pop()
            else:
                # Not found finally.
                print(std_ERROR_MAIN_PROCESS_NAME + "\"{0}_gen.txt\" file can't be found.".format(HLA_names[i]))
                sys.exit()

    print("\nTarget prot and gen files : \n")
    print(TARGET_prot_files)
    print(TARGET_gen_files)


    ##### < "Allelelist.txt", "hla_nom_g.txt", "hla_nom_p.txt" > #####

    # (2018. 10. 12.)

    t_allelelist = os.path.join(IMGTHLA_directory, "Allelelist.txt")
    t_p_Group = os.path.join(IMGTHLA_directory, "wmda/hla_nom_g.txt")
    t_p_Proup = os.path.join(IMGTHLA_directory, "wmda/hla_nom_p.txt")

    if not os.path.exists(t_allelelist):
        print(std_ERROR_MAIN_PROCESS_NAME + "\"Allelelist.txt\" file can't be found.\n")
        sys.exit()

    if not os.path.exists(t_p_Group):
        print(std_ERROR_MAIN_PROCESS_NAME + "\"hla_nom_g.txt\" file can't be found.\n")
        sys.exit()

    if not os.path.exists(t_p_Proup):
        print(std_ERROR_MAIN_PROCESS_NAME + "\"hla_nom_p.txt\" file can't be found.\n")
        sys.exit()




    ########## < Control Flags > ##########

    _1_MAKING_DICTIONARY = 1
    _2_CLASSIFY_GROUP = 1
    CLEAN_UP = 0


    if _1_MAKING_DICTIONARY:

        ########## < 1. Making HLA Dictionary. > ##########

        print(std_MAIN_PROCESS_NAME + "[1] Making HLA dictionary file.")

        l_df_Seqs_AA = []
        l_df_forMAP_AA = []

        l_df_Seqs_SNPS = []
        l_df_forMAP_SNPS = []



        if not _no_MultiP:

            pool = mp.Pool(processes=8)

            dict_Pool = {HLA_names[i]: pool.apply_async(ProcessIMGT, (_OUTPUT, HLA_names[i], HLA_INTEGRATED_POSITIONS_filename, _IMGT, TARGET_nuc_files[HLA_names[i]], TARGET_gen_files[HLA_names[i]], TARGET_prot_files[HLA_names[i]]))
                         for i in range(0, len(HLA_names))}

            pool.close()
            pool.join()


        for i in range(0, len(HLA_names)):

            if not _no_MultiP:

                t_df_Seqs_SNPS, t_df_Seqs_AA, t_df_forMAP_SNPS, t_df_forMAP_AA = dict_Pool[HLA_names[i]].get()

            else:
                t_df_Seqs_SNPS, t_df_Seqs_AA, t_df_forMAP_SNPS, t_df_forMAP_AA \
                    = ProcessIMGT(_OUTPUT, HLA_names[i], HLA_INTEGRATED_POSITIONS_filename, _IMGT,
                                  TARGET_nuc_files[HLA_names[i]], TARGET_gen_files[HLA_names[i]], TARGET_prot_files[HLA_names[i]])



            # Dictionary AA.
            l_df_Seqs_AA.append(t_df_Seqs_AA)
            l_df_forMAP_AA.append(MakeMap(HLA_names[i], "AA", t_df_forMAP_AA))

            # Dictionary SNPS.
            l_df_Seqs_SNPS.append(t_df_Seqs_SNPS)
            l_df_forMAP_SNPS.append(MakeMap(HLA_names[i], "SNPS", t_df_forMAP_SNPS))



        HLA_DICTIONARY_AA = pd.concat(l_df_Seqs_AA, axis=0)
        HLA_DICTIONARY_AA_map = pd.concat(l_df_forMAP_AA, axis=0)

        HLA_DICTIONARY_SNPS = pd.concat(l_df_Seqs_SNPS, axis=0)
        HLA_DICTIONARY_SNPS_map = pd.concat(l_df_forMAP_SNPS, axis=0)


        # Exporting AA dictionary.
        HLA_DICTIONARY_AA.to_csv(_OUTPUT_AA_RETURN + ".txt", sep='\t', header=False, index=True)

        HLA_DICTIONARY_AA_map.to_csv(_OUTPUT_AA_RETURN + ".map", sep='\t', header=False, index=False)

        # Exporting SNPS dictionary.
        HLA_DICTIONARY_SNPS.to_csv(_OUTPUT_SNPS_RETURN+".txt", sep='\t', header=False, index=True)

        HLA_DICTIONARY_SNPS_map.to_csv(_OUTPUT_SNPS_RETURN+".map", sep='\t', header=False, index=False)


    if _2_CLASSIFY_GROUP:


        ########## < 2. Making *.iat file. > ##########

        print(std_MAIN_PROCESS_NAME + "[2] Making \"*.iat\" file.")

        t_dict_AA = _OUTPUT_AA_RETURN + ".txt"
        t_dict_SNPS = _OUTPUT_SNPS_RETURN+ ".txt"

        _OUTPUT_IAT_RETURN = ClassifyGroups(t_allelelist, t_p_Group, t_p_Proup, t_dict_AA, t_dict_SNPS, _OUTPUT_IAT_RETURN)




    if CLEAN_UP:

        ########## < 5. Removing unnecessary files. > ##########

        print(std_MAIN_PROCESS_NAME + "[5] Removing unnecessary files")

    print("\n")
    print(std_MAIN_PROCESS_NAME + "Making HLA Dictionary is done.\n")


    return [_OUTPUT_AA_RETURN, _OUTPUT_SNPS_RETURN, _OUTPUT_IAT_RETURN]






#################### < Core Functions > ####################

def MakeMap(_hla, _type, _df_forMAP):

    if not (_type == "AA" or _type == "SNPS"):
        return -1

    if _type == "AA" and (_df_forMAP.shape[1] != 3):
        return -1

    if _type == "SNPS" and (_df_forMAP.shape[1] != 6):
        return -1

    """
    (1) Chr
    (2) Label
    (3) GD
    (4) Genomic Positions
    """

    _df_forMAP = _df_forMAP.astype(str)

    sr_Chr = pd.Series(["6" for i in range(0, _df_forMAP.shape[0])])
    l_Label = []
    sr_GD = pd.Series(["0" for i in range(0, _df_forMAP.shape[0])])
    sr_GenPos = _df_forMAP.iloc[:, 1]

    # Processing `l_Label`.

    p = re.compile('-?\d+x-?\d+')

    for i in range(0, _df_forMAP.shape[0]):

        t_rel_pos = _df_forMAP.iat[i, 0]
        t_gen_pos = _df_forMAP.iat[i, 1]
        t_type = _df_forMAP.iat[i, 2]

        main_label = '_'.join([("INDEL" if bool(p.match(t_rel_pos)) else "AA" if _type == "AA" else "SNPS"),
                               _hla, t_rel_pos, t_gen_pos, t_type])

        if _type == "SNPS":

            additional_label = ["AA"]

            t_AA_rel_pos = _df_forMAP.iat[i, 3]
            t_AA_gen_pos = _df_forMAP.iat[i, 4]
            #             t_AA_type = _df_forMAP.iat[i, 5]

            if t_AA_rel_pos != "nan" and t_AA_rel_pos != "NaN":
                additional_label.append(t_AA_rel_pos)

            if t_AA_gen_pos != "nan" and t_AA_gen_pos != "NaN":
                additional_label.append(t_AA_gen_pos)


            if len(additional_label) > 1:
                additional_label = '_'.join(additional_label)
                main_label = '_'.join([main_label, additional_label])

        l_Label.append(main_label)

    df_MAP = pd.concat([sr_Chr, pd.Series(l_Label), sr_GD, sr_GenPos], axis=1)


    return df_MAP




if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description=textwrap.dedent('''\
    ###########################################################################################

        IMGT2Sequence.py



    ###########################################################################################
                                     '''),
                                     add_help=False
                                     )

    parser._optionals.title = "OPTIONS"

    parser.add_argument("-h", "--help", help="\nShow this help message and exit\n\n", action='help')
    parser.add_argument("-hg", help="\nHuman Genome version(18, 19 or 38)\n\n", choices=["18", "19", "38"],
                        metavar="hg", required=True)
    parser.add_argument("-o", help="\nOutput File Prefix\n\n", metavar="OUTPUT", required=True)

    parser.add_argument("-imgt", help="\nIMGT-HLA data version(ex. 370, 3300)\n\n", metavar="IMGT_Version",
                        required=True)

    parser.add_argument("--no-indel", help="\nExcluding indel in HLA sequence outputs.\n\n", action='store_true')
    parser.add_argument("--no-multiprocess", help="\nSetting off parallel multiprocessing.\n\n", action='store_true')
    parser.add_argument("--save-intermediates", help="\nDon't remove intermediate files.\n\n", action='store_true')
    parser.add_argument("--imgt-dir", help="\nIn case User just want to specify the directory of IMGT data folder.\n\n")




    ##### < for Test > #####

    # (2018. 9. 17.)

    # Dictionary / hg18 / imgt370
    # args = parser.parse_args(["-hg", "18", "-o", "MAKEDICTIONARY_v2_hg18_imgt370/makedictionary.hg18.imgt370", "-imgt", "370"])

    # Dictionary / hg18 / imgt3320
    # args = parser.parse_args(["-hg", "18", "-o", "MAKEDICTIONARY_v2_hg18_imgt3320/makedictionary.hg18.imgt3320", "-imgt", "3320"])

    # Dictionary / hg19 / imgt3320
    # args = parser.parse_args(["-hg", "19", "-o", "MAKEDICTIONARY_v2_hg19_imgt3320/makedictionary.hg19.imgt3320", "-imgt", "3320"])




    ##### < for Publish > #####

    args = parser.parse_args()
    print(args)


    ##### < Main function Execution. > #####
    IMGT2Sequence(_HG=args.hg, _OUTPUT=args.o, _IMGT=args.imgt, _no_Indel=args._no_indel,
                  _no_MultiP=args.no_mulitprocess, _save_intermediates=args.save_intermediates,
                  _imgt_dir=args.imgt_dir)
