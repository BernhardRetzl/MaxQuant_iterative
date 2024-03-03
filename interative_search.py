import subprocess
import os


# subprocess.call(r'C:\Users\retzl\OneDrive\Desktop\ZUW\MaxQuant_v2.4.14.0\MaxQuant_v2.4.14.0\bin\MaxQuantCmd.exe --help', shell=True)
#

path_to_MaxQuant = r''
path_to_mqpar = r'./Data/Start/start.mqpar'

folder_number = 0


while True:
    folder_number += 1
    os.mkdir('./Data/Run/run_'+str(folder_number))
    subprocess.call(path_to_MaxQuant + f'--changeFolder="./Data/Run/run_{str(folder_number)}/mqpar.xml" "./Data/Start/file.fasta" "./Data/Start/file.d" ./Data/Start/mqpar.xml', shell=True)
    break
