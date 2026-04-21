Cette application permet de créer un programme arduino encapsulé.
C'est à dire que les cartes et librairies utilisées resteront les mêmes tout au long de
la maintenance de ce programme sous réserve de ne pas les avoir mis à jour.

# Installation d'EncapsArduino sous Linux

## Procédure automatique : 

- [1] Téléchargez le fichier "Release_Github_Linux.tar.gz" dans les [Releases]
  
	 (https://github.com/myhumankit/EncapsArduino/releases/tag/V.2_2).

- [2] Décompressez et lancez `Script_install.sh` (double-clic puis lancer)

                         ==================================

## Compatibilité Linux
Cet exécutable est fourni au format binaire autonome. Il a été compilé sous Docker pour garantir une compatibilité maximale entre les différentes distributions.

    • Systèmes testés et supportés :
        ◦ Ubuntu : 20.04 LTS, 22.04 LTS, 24.04 LTS et versions ultérieures.
        ◦ Linux Mint : 20, 21, 22 et versions ultérieures.
        ◦ Debian : 11 (Bullseye), 12 (Bookworm) et versions ultérieures.
        ◦ Autres : Compatible avec la majorité des distributions utilisant GLIBC 2.31 ou supérieure.

    • Prérequis système : Aucune installation de Python n'est requise. Cependant, si l'interface ne s'affiche pas, assurez-vous que les bibliothèques graphiques de base sont présentes (généralement déjà installées sur les versions "Desktop") : libx11-6, libglib2.0-0.

                       =============================

>Pour en savoir plus sur le fonctionnement et l'usage de ce > programme,
>se reporter au document :  EncapsArduino_v.2_2.pdf

                       =============================

Si vous deviez recompiler le programme sous Linux, voici les procédures de compilations que j'ai utilisées sous Linux Mint 22.3 - Cinnamon 64-bit :

## Compil Linux / PyInstaller :

cd ~/DOCUMENTS/Python/DesktopCreator
python3 -m venv venv
source venv/bin/activate


pip install pyinstaller
pip install customtkinter
pip install pillow
pip install pyyaml


python -m PyInstaller encapsarduino2_2.py \
  --onefile \
  --noconsole \
  --add-data "Encapsule.png:." \
  --hidden-import customtkinter \
  --hidden-import PIL._tkinter_finder \
  --hidden-import yaml

## Compil Linux / Docker :   
(pour être compatible avec anciennes versions Ubuntu, Mint, Debian)

cd ~/DOCUMENTS/Python/EncapsArduino/Compil_Docker

docker run --rm -v "$(pwd):/src" -w /src python:3.10-slim-bullseye /bin/bash -c "apt-get update && apt-get install -y binutils python3-tk && pip install --upgrade pip && pip install -r requirements.txt pyinstaller && pyinstaller --onefile --windowed --icon=Encapsule.png encapsarduino2_2.py"

sudo chown -R $USER:$USER dist build 

                       =============================

# Installation d'EncapsArduino sous Windows

- [1] Téléchargez le fichier `EncapsArduino_Windows.zip` dans les [Releases]
  
	(https://github.com/myhumankit/EncapsArduino/releases/tag/V.2_2).
- [2] Décompressez l'archive.
- [3] Double-cliquez sur `EncapsArduino.exe`.


Si vous deviez recompiler le programme sous windows, voici la procédure de compilation que j'ai exécutée sous Windows 11 :

## Compil Windows / PyInstaller :

Dans une fenêtre terminal : 

	- [1] Se placer dans le dossier où  se trouve le prog (cd C:\.....etc)
	
	- [2] Installer PyInstaller et PyYaml
	
			pip3 install pyinstaller
		
			pip3 install pyyaml	
		
	- [3] Lancer la compilation :
	
			python -m PyInstaller --clean --onefile --noconsole --collect-all customtkinter --collect-all CTkMessagebox --add-data "Encapsule.ico;." --icon="Encapsule.ico" encapsarduino2_2.py
 
		



