import subprocess
import os
from Bio import SeqIO
import re
import PySimpleGUI as psg


# https://bioinformatics.stackexchange.com/questions/7212/what-is-the-purpose-of-folder-locations-in-maxquant
# https://www.tutorialspoint.com/pysimplegui/pysimplegui_popup_windows.htm


def correct_mqpar_file(input_file, output_file, folder_number, fasta_file_name, path_to_ms_file, working_directory):
    with open(input_file) as f, open(output_file, 'w') as f_out:
        for line in f:
            if line.strip().startswith('<fastaFilePath>'):
                start = line.split('<')[0]
                f_out.write(start + '<fastaFilePath>' + fr'{working_directory}/Data/Run/run_{folder_number}/{fasta_file_name}' + '</fastaFilePath>\n')
            elif line.strip().startswith('<fixedCombinedFolder>'):
                start = line.split('<')[0]
                f_out.write(start + fr'<fixedCombinedFolder>{working_directory}/Data/Run/run_{folder_number}</fixedCombinedFolder>'+'\n')
            elif line.strip().startswith('<filePaths>'):
                f_out.write(line)
                start = f.readline().split('<')[0]
                f_out.write(start + '<string>' + path_to_ms_file + '</string>\n')
            elif line.strip().startswith('<numThreads>'):
                f_out.write(line)
                num_threads = line.split('<numThreads>')[-1].split('</numThreads>')[0]
            else:
                f_out.write(line)
    return num_threads


def write_new_fasta(protein_group_file, fasta_input_file, fasta_output_file):
    tax_ids = set()
    with open(protein_group_file) as f:
        for line in f:
            info = line.split('\t')[7]
            tax_info = re.findall(r'OX=\d+', info)
            for tax in tax_info:
                tax_ids.add(tax.split('OX=')[-1])
    out_handle = open(fasta_output_file, 'w')
    for sequence in SeqIO.parse(fasta_input_file, "fasta"):
        ox = sequence.description.split('OX=')[-1].split(' ')[0]
        if ox in tax_ids:
            SeqIO.write(sequence, out_handle, "fasta")
    out_handle.close()


def make_folders():
    os.makedirs(f'./Data', exist_ok=True)
    os.makedirs(f'./Data/Run', exist_ok=True)
    os.makedirs(f'./Data/Run/run_1', exist_ok=True)
    os.makedirs(f'./Data/Start', exist_ok=True)


def get_paths_for_run():
    path_to_MaxQuant = psg.popup_get_file(r'Please specify the path to MaxQuantCmd.exe (it´s in MaxQuant\bin\MaxQuantCmd.exe)',  title="File selector")
    path_to_mqpar_file = psg.popup_get_file(r'Please specify the path to the mqpar.xml file',  title="File selector")
    path_to_fasta_file = psg.popup_get_file(r'Please specify the path to the FASTA-file',  title="File selector")
    path_to_ms_file = psg.popup_get_folder(r'Please specify the path to the MS (.d) file',  title="Folder selector")
    fasta_file_name = path_to_fasta_file.split('/')[-1]
    return path_to_MaxQuant, path_to_mqpar_file, path_to_fasta_file, path_to_ms_file, fasta_file_name


make_folders()
path_to_MaxQuant, path_to_mqpar_file, path_to_fasta_file, path_to_ms_file, fasta_file_name = get_paths_for_run()
working_directory = os.getcwd().replace('\\', '/')


threads_in_use = correct_mqpar_file(path_to_mqpar_file,'./Data/Run/run_1/mqpar.xml', folder_number=1, fasta_file_name=fasta_file_name, path_to_ms_file=path_to_ms_file, working_directory=working_directory)
print('Attention ' + threads_in_use + ' threads in use!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
os.replace(path_to_fasta_file, './Data/Run/run_1/' + fasta_file_name)


folder_number = 1
for k in range(5):
    print('Run '+str(k))
    subprocess.call(path_to_MaxQuant + f' ./Data/Run/run_{folder_number}/mqpar.xml', shell=True)
    folder_number += 1
    os.makedirs(f'./Data/Run/run_{folder_number}', exist_ok=True)
    write_new_fasta(protein_group_file=f'./Data/Run/run_{folder_number-1}/combined/txt/proteinGroups.txt',
                    fasta_input_file=f'./Data/Run/run_{folder_number-1}/uniprot_sprot.fasta',
                    fasta_output_file=f'./Data/Run/run_{folder_number}/uniprot_sprot.fasta')
    correct_mqpar_file(f'./Data/Run/run_{folder_number-1}/mqpar.xml', f'./Data/Run/run_{folder_number}/mqpar.xml', folder_number, fasta_file_name)
