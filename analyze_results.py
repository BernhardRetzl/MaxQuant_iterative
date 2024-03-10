import glob
from Bio import SeqIO
import pandas as pd
import matplotlib.pyplot as plt


file_list = glob.glob(r'.\Data\Run\*')

iteration = 0

for file in file_list:

    ox_list = list()
    ox_dict = dict()
    iteration = iteration + 1
    for sequence in SeqIO.parse(file+r'\uniprot_sprot.fasta', 'fasta'):
        description = sequence.description
        ox = description.split('OX=')[-1].split(' ')[0]
        if ox in ox_dict:
            ox_dict[ox] += 1
        else:
            ox_dict[ox] = 1

    a = pd.DataFrame.from_dict(ox_dict, orient='index')

    values = list(sorted(ox_dict.values(), reverse=True))
    print(len(values))

    values_index = [i for i in range(len(values))]

    plt.bar(values_index, values)
    plt.xlabel('Organism')
    plt.ylabel('log Number of sequences in each organism')

    plt.title('Iteration '+str(iteration))
    plt.yscale('log')
    plt.show()
