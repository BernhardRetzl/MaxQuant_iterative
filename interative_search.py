import subprocess
import os
from Bio import SeqIO
import re
import glob


# https://bioinformatics.stackexchange.com/questions/7212/what-is-the-purpose-of-folder-locations-in-maxquant

def correct_mqpar_file(input_file, output_file, folder_number):
    with open(input_file) as f, open(output_file, 'w') as f_out:
        for line in f:
            if line.strip().startswith('<fastaFilePath>'):
                start = line.split('<')[0]
                f_out.write(start + '<fastaFilePath>' + fr'.\Data\Run\run_{folder_number}\uniprot_sprot.fasta' + '</fastaFilePath>\n')
            elif line.strip().startswith('<fixedCombinedFolder>'):
                start = line.split('<')[0]
                f_out.write(start + fr'<fixedCombinedFolder>.\Data\Run\run_{folder_number}</fixedCombinedFolder>'+'\n')
            else:
                f_out.write(line)


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


os.makedirs(f'./Data', exist_ok=True)
os.makedirs(f'./Data/Run', exist_ok=True)
os.makedirs(f'./Data/Run/run_1', exist_ok=True)
os.makedirs(f'./Data/Start', exist_ok=True)

print('Please place MS-file (.d), FASTA-file (.fasta) and the mqpar (mqpar.xml) in the folder ./Data/Start !')
input('Press any key to continue...')

correct_mqpar_file(f'./Data/Start/mqpar.xml','./Data/Run/run_1/mqpar.xml', folder_number=1)
fasta_file = glob.glob('./Data/Start/*.fasta')[0]
fasta_file = fasta_file.split(os.sep)[-1]
os.replace(f'./Data/Start/' + fasta_file, './Data/Run/run_1/' + fasta_file)


path_to_MaxQuant = r'.\MaxQuant_v2.4.14.0\bin\MaxQuantCmd.exe'
folder_number = 1

for k in range(5):
    print('Run '+str(k))
    subprocess.call(path_to_MaxQuant + f' ./Data/Run/run_{folder_number}/mqpar.xml', shell=True)
    folder_number += 1
    os.makedirs(f'./Data/Run/run_{folder_number}', exist_ok=True)
    write_new_fasta(protein_group_file=f'./Data/Run/run_{folder_number-1}/combined/txt/proteinGroups.txt',
                    fasta_input_file=f'./Data/Run/run_{folder_number-1}/uniprot_sprot.fasta',
                    fasta_output_file=f'./Data/Run/run_{folder_number}/uniprot_sprot.fasta')
    correct_mqpar_file(f'./Data/Run/run_{folder_number-1}/mqpar.xml',f'./Data/Run/run_{folder_number}/mqpar.xml', folder_number)
