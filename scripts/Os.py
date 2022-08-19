import os
import inspect
from colorama import (Fore, Style)
from scripts.Shutil import Shutil


class Os:
    def pasta_atual(self):
        return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def desligar_pc(self):
        os.system('shutdown -s')

    def abrir(self, directory: str):
        archive = directory.split('\\')[-1]
        print('Abrindo "{}".'.format(archive))
        os.startfile(directory)
        print(Fore.GREEN + '"{}" acabou de ser aberto.\n'.format(archive) + Style.RESET_ALL)

    def criar_pastas(self, directory: str):
        os.makedirs(directory)

    def ir_para(self, directory: str):
        os.chdir(directory)
        return os.getcwd()

    def obter_usuario(self):
        return os.getenv('USERNAME')

    def remove(self, archive: str, obrigatory=True):
        if obrigatory:
            os.remove(archive)
        else:
            try:
                os.remove(archive)
            except:
                print("Não foi possível remover o arquivo.\n")

    def rename(self, name_beforce, name_after):
        os.rename(name_beforce, name_after)

    def criar_pasta(self, directory: str):
        archive = directory.split('\\')[-1]
        if archive == "":
            return SyntaxError
        else:
            for letra in archive:
                if letra == " ":
                    return SyntaxError
                else:
                    break
            try:
                os.mkdir(directory)
                print(Fore.GREEN + 'A pasta "{}" acaba de ser criada.'.format(archive) + Style.RESET_ALL)
                return True
            except:
                return FileExistsError

    def obter_arquivos_em(self, directory: str):
        for root, dirs, files in os.walk(directory):
            return files

    def obter_pastas_em(self, directory: str):
        for root, dirs, files in os.walk(directory):
            return dirs

    def obter_caminhos_em(self, directory: str):
        for root, dirs, files in os.walk(directory):
            return root

    def obter_caminhos_e_arquivos_em(self, directory: str):
        roots_and_files = []
        for root, dirs, files in os.walk(directory):
            roots_and_files.append(root)
            roots_and_files.append(files)
        return roots_and_files

    def obter_pastas_escolhidas(self, directory: str, chosen_folders):
        folders_oltputs = self.obter_pastas_em(directory)
        folders_for_select = []
        for folder_oltput in folders_oltputs:
            for folder_input in chosen_folders:
                if folder_oltput.lower().replace(' ', '') == folder_input.lower().replace(' ', ''):
                    folders_for_select.append(folder_oltput)
        return folders_for_select
