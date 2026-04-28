# Encapsarduino    Encapsulage programme Arduino
# Version 2.3  YLC le 28/04/26 (intégration de l'appel du script de déverrouillage)
# Source python compatible Windows et Linux
# compilable avec Docker

import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from pathlib import Path
import shutil
import json
import sys
import base64
import yaml
import subprocess
import time
import ctypes
import webbrowser
import locale

# Détection PyInstaller / interprété
if getattr(sys, 'frozen', False):
    # Programme compilé
    loc_actu = Path(sys._MEIPASS)
else:
    # Mode interprété
    loc_actu = Path(os.path.dirname(os.path.abspath(__file__)))

# Chercher l'icône
if sys.platform.startswith("win"):
    icon_name = "Encapsule.ico"
    fallback_icon = Path(os.environ.get("APPDATA", "")) / "Encapsule" / icon_name
else:
    icon_name = "Encapsule.png"
    fallback_icon = Path.home() / ".local/share/icons" / icon_name

# Recherche de l’icône
icon_path = loc_actu / icon_name
if not icon_path.exists():
    fallback_dir = Path.home() / ".local/share/icons" if not sys.platform.startswith("win") else Path.home()
    icon_path = fallback_dir / icon_name

from datetime import datetime                     #recup date du jour
Datjour=(datetime.today().strftime("%d/%m/%Y"))   #sous forme jj/mm/aa
LocActu=os.path.abspath(os.getcwd())              # recup du repertoire courant
#print("LocActu = " + LocActu)
Nomprog = ""
RepertApplis = ""
VersionCarte = "" 
CartesPath = ""
YamlFile = ""  
ErrMsg = ""  
AppliPath = ""
YamlPath = ""
YamlName = ""
YamlLocal = ""
CarteSelPath = ""
ProgPath = ""
InoPath = ""
ArduiName = ""
StartIde = True
CreaCarte = False
RazParam = False
CreParam = False 
ModParam = False
LockLang = False
LockCart = False
ListCartes = []
ListProgs = []
NomCarte = ""
PathExe = ""
TEXTES = {}
titrelisprog = ""
titreliscart = ""
titrelislang = ""
ListLang = []
LANGUES = {}
fichlang = ""
messalert = ""
THEMES = []
indtheme = 0     # = clair     1 =sombre

def memo_theme():
    global LocActu
    global indtheme
    global CreParam
    if CreParam == False :
        FiParam=os.path.join(LocActu,"EncapsParam/Fiparam.json").replace("\\","/")
        with open(FiParam, "r", encoding="utf-8") as f:    
            params = json.load(f)
        params["Theme"] = indtheme  # Modifier uniquement le thème
        with open(FiParam, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=2, ensure_ascii=False)  # Réécrire le fichier avec les autres paramètres inchangés   
    
def appliquer_style(widget, type):
    global THEMES, indtheme
    bg_color = THEMES[indtheme][type][0]
    fg_color = THEMES[indtheme][type][1]
    try:
        widget.config(bg=bg_color, fg=fg_color)
        if isinstance(widget, tk.Entry):
            widget.config(disabledbackground=THEMES[indtheme]["chemin"][0],  # couleur du fond dans Entry disable
                          disabledforeground=fg_color
            )
    except:
        pass       # Évite les erreurs si un widget ne supporte pas bg/fg

def set_clair():
    global indtheme
    indtheme = 0
    memo_theme()
    set_style()

def set_sombre():
    global indtheme
    indtheme = 1
    memo_theme()
    set_style()

def set_style():
    global indtheme
    FormMain.config(bg=THEMES[indtheme]["titre"][0])
    appliquer_style(menubar, "menu")
    appliquer_style(LabExArdui, "menu")
    appliquer_style(LabExeArd1, "titre")
    appliquer_style(LabExeArd2, "chemin")
    appliquer_style(TBExeArd, "saisie")
    appliquer_style(ButtonOK9, "bouton")
    appliquer_style(ButtonSelect, "bouton")
    appliquer_style(Label0, "titre")
    appliquer_style(BoutYaml, "bouton")
    appliquer_style(LabYaml1, "titre")
    appliquer_style(LabYaml2, "chemin")
    appliquer_style(BoutRepCart, "bouton")
    appliquer_style(Labela, "titre")
    appliquer_style(Labelb, "chemin")
    appliquer_style(Labelc, "titre")
    appliquer_style(Label1, "chemin")
    appliquer_style(ButtonOK0, "bouton")
    appliquer_style(Label2, "titre")
    appliquer_style(TextBox1, "saisie")
    appliquer_style(ButtonOK1, "bouton")
    appliquer_style(Label3, "titre")
    appliquer_style(MesCrePro, "titre")
    appliquer_style(RadioBout1, "radbout")
    appliquer_style(RadioBout2, "radbout")
    appliquer_style(Label4, "titre")
    appliquer_style(TextBox, "saisie")
    appliquer_style(Boutonvalid, "bouton")
    appliquer_style(BoutDeverr, "bouton1")
    appliquer_style(Label5, "titre")
    appliquer_style(Messereur, "alerte")
    Label6.lift()
    Label7.lift()

def open_path(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    else:
        subprocess.Popen(["xdg-open", path])
 
def set_folder_icon_windows():
    # AppliPath : dossier cible (string)
    # icon_path : chemin de Encapsule.ico (Path)
    # loc_actu   : déjà calculé en amont
    if sys.platform != "win32":
        return

    try:
        # ─────────────────────────────────────────────
        # 1. Copier l’icône dans un emplacement permanent
        # ─────────────────────────────────────────────
        icon_install_dir = Path(os.environ["LOCALAPPDATA"]) / "Encapsule"
        icon_install_dir.mkdir(parents=True, exist_ok=True)

        icon_final = icon_install_dir / icon_path.name

        if not icon_final.exists():
            shutil.copy(icon_path, icon_final)

        icon_final = icon_final.resolve()

        # ─────────────────────────────────────────────
        # 2. Créer desktop.ini SANS indentation
        # ─────────────────────────────────────────────
        desktop_ini_content = (
            "[.ShellClassInfo]\r\n"
            f"IconResource={icon_final},0\r\n"
        )

        ini_path = Path(AppliPath) / "desktop.ini"

        with open(ini_path, "w", encoding="utf-16le") as f:
            f.write(desktop_ini_content)

        # ─────────────────────────────────────────────
        # 3. Attributs Windows
        # ─────────────────────────────────────────────
        os.system(f'attrib +h +s "{ini_path}"')
        os.system(f'attrib +s "{AppliPath}"')

        # ─────────────────────────────────────────────
        # 4. Rafraîchir Explorer
        # ─────────────────────────────────────────────
        ctypes.windll.shell32.SHChangeNotify(
            0x08000000, 0, None, None
        )

    except Exception as e:
        print("Erreur icône dossier :", e)

def set_folder_icon_linux(DocuPath, iconPath):
    folder = Path(DocuPath)
    icon_src = Path(iconPath)

    if not folder.is_dir():
        print("Dossier invalide :", folder)
        return
    if not icon_src.is_file():
        print("Icône introuvable :", icon_src)
        return

    # ─────────────────────────────────────────────
    # 1. Copier l’icône vers un emplacement PERMANENT
    # ─────────────────────────────────────────────
    icon_install_dir = Path.home() / ".local/share/icons"
    icon_install_dir.mkdir(parents=True, exist_ok=True)

    icon_dst = icon_install_dir / icon_src.name

    if not icon_dst.exists():
        shutil.copy(icon_src, icon_dst)

    icon_dst = icon_dst.resolve()

    # ─────────────────────────────────────────────
    # 2. Appliquer l’icône via gio (chemin PERMANENT)
    # ─────────────────────────────────────────────
    subprocess.run([
        "gio", "set", "-t", "string",
        str(folder),
        "metadata::custom-icon",
        f"file://{icon_dst}"
    ], check=False)

    # ─────────────────────────────────────────────
    # 3. Rafraîchir Nemo
    # ─────────────────────────────────────────────
    subprocess.run(["nemo", "-q"], check=False)

def Quitter():
    FormMain.quit()
    FormMain.destroy()

FormMain = tk.Tk()                                
FormMain.geometry("1000x600+400+200")
FormMain.resizable(width=True, height=False)
FormMain.configure(bg='lightcyan') 
FormMain.title("EncapsArduino v.2.3")
FormMain.option_add('*font', ('Arial', 11))
FormMain.protocol("WM_DELETE_WINDOW", Quitter)

def show_alerte1(cartename) :
    messagebox.title(TEXTES.get("Titrealert","missing key: Titrealert"))
    Messalert['text']=TEXTES.get("Alertcart","missing key: Alertcart")+cartename
    messagebox.deiconify()
    
def show_alerte2(nomdossier) :
    messagebox.title(TEXTES.get("Titrealert","missing key: Titrealert"))
    Messalert['text']=TEXTES.get("Alertyaml","missing key: Alertyaml")+nomdossier
    messagebox.deiconify()

def show_alerte3(messalert) :
    Messalert['text']=messalert
    messagebox.deiconify()
    
def clear_titrelislang(event):
    if ComboLang.get() == titrelislang:
        ComboLang.set("")

def code_from_name(name):
    for lang in LANGUES:
        if lang["name"] == name:
            return lang["code"]

def name_from_code(code):
    for lang in LANGUES:
        if lang["code"] == code:
            return lang["name"]
        
def file_from_name(name):
    for lang in LANGUES:
        if lang["name"] == name:
            return lang["file"]
        
def on_select_lang(event) :       # récup de la liste des langues
    global LocActu
    global fichlang
    global langue
    global codlang
    global LockLang
    langue = ComboLang.get()
    ComboLang.invisible()
    fichlang = file_from_name(langue)
    menubar.entryconfig(IDX_MENU_LANG, label=f"🌐 {langue}")
    codlang = code_from_name(langue)
    if LockLang == False :
        FiParam=os.path.join(LocActu,"EncapsParam/Fiparam.json").replace("\\","/")
        with open(FiParam, "r", encoding="utf-8") as f:    
            params = json.load(f)
        params["Langue"] = codlang  # Modifier uniquement la langue
        with open(FiParam, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=2, ensure_ascii=False)  # Réécrire le fichier avec les autres paramètres inchangés
    load_language(fichlang)
    #print("Langue choisie :", langue)
    #print("Fichier JSON :", fichlang)

def ChoixLangue():
    global codlang
    global LockCart
    if LockCart == False :
        langue = name_from_code(codlang)
        #print("langueX",langue)
        ComboLang.visible()
        ComboLang.set(langue)
        #print("LANGUES",LANGUES)
    
def load_language(langue):
    global TEXTES
    global Locactu
    global fichlang
    global codlang
    #print("codlang:",codlang)
    langue = name_from_code(codlang)
    fichlang = file_from_name(langue)
    #print("fichlang:",fichlang)
    locparam=os.path.join(LocActu,"EncapsParam").replace("\\","/")
    filename=os.path.join(locparam,fichlang).replace("\\","/")
    #print("filename:",filename)
    try:
        with open(filename, "r", encoding="utf-8") as f:
            TEXTES = json.load(f)
    except IOError:
        messalert = "missing file: "+fichlang
        show_alerte3(messalert)
        Quitter()
    else :            
        LabExArdui['text']=TEXTES.get("QexeArduino","missing key: QexeArduino")
        Label0['text']=TEXTES.get("AideQexeArduino","missing key: AideQexeArduino")
        LabExeArd1['text']=TEXTES.get("ExeArduino","missing key: ExeArduino")
        BoutYaml['text']=TEXTES.get("Qyaml","missing key: Qyaml")
        LabYaml1['text']=TEXTES.get("Yaml","missing key: Yaml")
        BoutRepCart['text']=TEXTES.get("Qrepcart","missing key: Qrepcart")
        Labela['text']=TEXTES.get("Repcart","missing key: Repcart")
        if CreParam :
            Labelc['text']=TEXTES.get("Finquestions","missing key: Finquestions")
        else :
            Labelc['text'] = TEXTES.get("Origparam","missing key: Origparam  ")+ FiParam +")"
        ButtonSelect['text']=TEXTES.get("Qrepappli","missing key: Qrepappli")
        Label2['text']=TEXTES.get("Qnomprog","missing key: Qnomprog")
        Label3['text']=TEXTES.get("Qvercart","missing key: Qvercart")
        ListCartes.append(TEXTES.get("Autrecarte","missing key: Autrecarte"))
        MesCrePro['text']=TEXTES.get("Qcreprog","missing key: Qcreprog")
        RadioBout1['text']=TEXTES.get("Oui","missing key: Oui")
        RadioBout2['text']=TEXTES.get("Non","missing key: Non")
        Label4['text']=TEXTES.get("QnouvCart","missing key: QnouvCart")
        Boutonvalid['text']=TEXTES.get("Valider","missing key: Valider")
        BoutDeverr['text']=TEXTES.get("Deverrouiller","missing key: Déverrouiller")
        Label5['text']=TEXTES.get("Qprogmodif","missing key: Qprogmodif")
        menubar.entryconfig(IDX_MENU_FICHIER, label=TEXTES.get("Fichier","missing key: Fichier"))
        menu1.entryconfig(IDX_QUITTER, label=TEXTES.get("Quitter","missing key: Quitter"))
        menu2.entryconfig(IDX_EFFACE, label=TEXTES.get("Effparam","missing key: Effparam"))
        menu3.entryconfig(IDX_APROPOS, label=TEXTES.get("Apropos","missing key: Apropos"))
        menubar.entryconfig(IDX_MENU_AIDE, label=TEXTES.get("Aide","missing key: Aide"))
        menubar.entryconfig(IDX_STYLE, label=TEXTES.get("Thème","missing key: Thème"))
        menustyle.entryconfig(IDX_CLAIR, label=TEXTES.get("Clair","missing key: Clair"))
        menustyle.entryconfig(IDX_SOMBRE, label=TEXTES.get("Sombre","missing key: Sombre"))
        
messagebox = tk.Tk()
messagebox.title("")
messagebox.geometry("800x400")
messagebox.configure(bg = "Red")
messagebox.withdraw()

Messalert = Label(messagebox, text=" ",bg='White',fg='Red')
Messalert.configure(font= ('Arial', 20, 'bold'))
Messalert.pack(pady=80)

def ouvrir_lien_MHK(event):      # lien vers MHK si on clique sur le logo du bas de la fenêtre
    safe_open_path("https://myhumankit.org/")
    
def AffInfo():
    FormInfo = Toplevel(FormMain)
    FormInfo.transient(FormMain)
    FormInfo.grab_set()
    FormInfo.geometry("750x630+535+200")
    FormInfo.resizable(width=False, height=False)
    FormInfo.title("Encapsarduino v.2")
    bg_c = THEMES[indtheme]["info"][0]
    fg_c = THEMES[indtheme]["info"][1]
    FormInfo.config(bg=bg_c)
    LabInfo=Label(FormInfo,text=TEXTES.get("Infotext","missing key: Infotext"),width=650,
                  bg=bg_c, fg=fg_c,
                  anchor='w',justify='left',padx=10,pady=10)
    LabInfo.pack(fill="both", expand=True)

def AffAbout():
    FormAbout = Toplevel(FormMain)
    FormAbout.transient(FormMain)
    FormAbout.grab_set()
    FormAbout.geometry("350x220+700+400")
    FormAbout.resizable(width=False, height=False)
    FormAbout.title(TEXTES.get("Apropos","missing key: Apropos"))
    bg_t = THEMES[indtheme]["about"][0]
    fg_t = THEMES[indtheme]["about"][1]
    FormAbout.config(bg=bg_t)
    LabAbout=Label(FormAbout,text=TEXTES.get("Aproptext","missing key: Aproptext"),width=350,
                   bg=bg_t, fg=fg_t,)
    LabAbout.pack(fill="both", expand=True)

def RazParam():                    # effacement du fichier paramètres json 
    global RazParam
    FiParam=os.path.join(LocActu,"EncapsParam/Fiparam.json").replace("\\","/")
    if os.path.exists(FiParam) :
        os.remove(FiParam)
        #print("Fichier '{FiParam}' supprimé")
        RazParam = True
    sys.exit()                 # on sort du programme en cas de suppression du fichier paramètres 
    
def ClicButtonOk9():           # validation du chemin du fichier exe de l'IDE arduino
    global PathExe
    nomprov = PathExe_var.get().replace('\"',"")
    if len(nomprov) > 10 :
        PathExe=nomprov.replace("\\","/")
        #print("PathExe = " + PathExe)
        LabExArdui.invisible()
        LabExeArd2['text']=PathExe
        LabExeArd1.visible()
        LabExeArd2.visible()
        TBExeArd.invisible()
        Label0.invisible()
        ButtonOK9.invisible()
        BoutYaml.visible()
    
def ClicBoutYaml():             # saisie du chemin du fichier .Yaml de l'IDE arduino
    global YamlPath
    global YamlFile
    global YamlName
    FolderDialog=filedialog.askopenfilename()
    if len(FolderDialog) > 0 :
        YamlPath=os.path.dirname(FolderDialog)
        #print("- YamlPath = " + YamlPath)
        YamlFile=os.path.abspath(FolderDialog).replace("\\","/")
        #print("- YamlFile = " + YamlFile)
        YamlName = os.path.basename(YamlFile)
        #print("- YamlName = " + YamlName)
        LabYaml2['text']=FolderDialog
        BoutYaml.invisible()
        LabYaml1.visible()
        LabYaml2.visible()
        BoutRepCart.visible()

def ClicBoutRepCart():            # saisie du chemin du repertoire des versions de cartes
    global CartesPath
    FolderParam=filedialog.askdirectory()
    #print("- FolderParam = " + FolderParam)
    if len(FolderParam) > 0 :
        CartesPath=FolderParam
        Labelb['text']=CartesPath
        BoutRepCart.invisible()
        Labela.visible()
        Labelb.visible()
        ButtonSelect.visible()

def ClicButtonSelect():        # saisie du répertoire des applications
    global ModParam
    global RepertApplis
    FolderSelect=filedialog.askdirectory()
    if len(FolderSelect) > 0 :
        ModParam=True
        RepertApplis=FolderSelect
        Label1['text']=RepertApplis
        Label1.visible()
        ButtonOK0.visible()
        
def ClicButtonOk0():           # validation du répertoire des applications
    global CreParam
    global ModParam
    global YamlPath
    global YamlFile
    global PathExe
    global RepertApplis
    global codlang
    global indtheme
    MesCrePro.visible()
    RadioBout1.visible()
    RadioBout2.visible()
    TextBox1.invisible()
    TextBox1.focus_set()
    ButtonOK1.invisible()
    Label5.invisible()
    ComboProg.invisible()
    Label2.invisible()
    Label3.invisible()
    Label4.invisible()
    TextBox.invisible()
    ComboCart.invisible()
    Boutonvalid.invisible()
    BoutDeverr.invisible()
    Messereur['text']=""
    RadioBout1.deselect()
    RadioBout2.deselect()
    if CreParam or ModParam :
        #print("FiParam = " + FiParam)
        #print("CartesPath = " + CartesPath)
        #print("YamlPath = " + YamlPath)
        #print("YamlFile = " + YamlFile)
        #print("RepertApplis = " + RepertApplis) 
        # enregistrement du fichier paramètres avec mémo du repertoire des applications et de la langue
        param = {"PathExe" : PathExe,"CartesPath" : CartesPath,"YamlPath" : YamlPath,"YamlFile" : YamlFile,
                 "RepertApplis" : RepertApplis,"Langue" : codlang, "Theme" : indtheme}
        with open(FiParam, 'w', encoding='utf-8') as fichier:
                json.dump(param, fichier, indent=2, ensure_ascii=False)
        Labelc['text']=TEXTES.get("Mesenrparam","missing key: Mesenrparam") + FiParam 
        Labelc.visible()
        LockLang = False

def BoutRad_sel():          # saisie de la réponse si modification ou non d'un programme existant
    global YamlLocal
    global YamlPath
    global AppliPath
    global ProgPath
    global ListProgs
    global RepertApplis
    Messereur['text']=""
    Label4.invisible()
    TextBox.invisible()
    Boutonvalid.invisible()
    BoutDeverr.invisible()
    selection = varbout.get()
    Label3.invisible()
    ComboCart.invisible()
    if selection == "O" :             # réponse = OUI, => création d'un nouveau programme
        TextBox1.visible()
        TextBox1.focus_set()
        ButtonOK1.visible()
        Label2.visible()
        Label5.invisible()
        ComboProg.invisible()
        TextBox1.config(state='normal')
        TextBox1.delete(0, END)
        
    else :                           # réponse = NON, => modification d'un programme existant
        TextBox1.invisible()
        ButtonOK1.invisible()
        Label2.invisible()
        ListProgs = [ d for d in os.listdir(RepertApplis)   # lister les prog. encapsulés seulement
                    if os.path.isdir(os.path.join(RepertApplis, d)) 
                    and os.path.exists(os.path.join(RepertApplis, d, 'arduino-cli.yaml')) ]
        Label5.visible()
        ComboProg.visible()
        ComboProg['values'] = ListProgs
        ComboProg.config(state="normal")
        ComboProg.set(TEXTES.get("Clichoixprog","missing key: Clichoixprog"))

        
def ClicButtonOk1() :        # validation de la saisie du nom du programme
    global ListCartes
    global AppliPath
    global YamlLocal
    global YamlName
    global ProgPath
    global InoPath
    global ArduiName
    global NomProg
    global CartesPath
    global YamlName
    nomprov = progname_var.get()
    NomProg=nomprov. replace(" ", "")
    MesCrePro.visible()
    Messereur['text']=""
    if len(NomProg) > 3  :         # nom programme doit faire plus de 3 caractères
        AppliPath=os.path.join(RepertApplis,NomProg).replace("\\","/")
        YamlLocal=os.path.join(AppliPath,YamlName).replace("\\","/")
        ProgPath=os.path.join(AppliPath,"Docs").replace("\\","/")
        InoPath=os.path.join(ProgPath,NomProg+"_v1").replace("\\","/")
        ArduiName=os.path.join(InoPath,NomProg+"_v1.ino").replace("\\","/")
        #print("YamlLocal = " + YamlLocal)
        #print("YamlPath = " + YamlPath)
        #print("ProgPath = " + ProgPath)
        #print("AppliPath = " + AppliPath)
        #print("CartesPath = " + CartesPath)
        #print("InoPath = " + InoPath)
        #print("ArduiName = " + ArduiName)
        if os.path.exists(AppliPath) :
            Messereur['text']=TEXTES.get("Errprogexist","missing key: Errprogexist")
        else :
            TextBox1.config(state='disabled')
            # recup des versions de cartes déjà connues 
            chemin=CartesPath
            ListCartes=[d for d in os.listdir(chemin) if os.path.isdir(os.path.join(chemin, d))]
            ListCartes.append(TEXTES.get("Autrecarte","missing key: Autrecarte"))
            Label3.visible()
            ComboCart.visible()
            ComboCart.config(state="normal")
            ComboCart['values'] = ListCartes
            ComboCart.set(TEXTES.get("Clichoixcart","missing key: Clichoixcart"))
            Label4.invisible()
            TextBox.invisible()
            TextBox.config(state="normal")
            TextBox.delete(0, END)
    else :
        Messereur['text']=TEXTES.get("Errlongnom","missing key: Errlongnom")

def clear_titrelisprog(event):
    if ComboProg.get() == titrelisprog:
        ComboProg.set("")

def safe_open_path(path):     # ouverture de dossier indépendant du compilateur
    # A utiliser si compilation avec Docker pour appel proces ou lien url
    # Lance une commande ou ouvre un chemin en nettoyant l'environnement.
    # 'commande' peut être un simple chemin (string) ou une liste [prog, arg]
    new_env = os.environ.copy()    # préparation d'un environnement propre
    if sys.platform.startswith('linux'):
        for var in ['LD_LIBRARY_PATH', 'PYTHONPATH', 'PYTHONHOME']:
            new_env.pop(var, None)
    try:
        if sys.platform == "win32":
            if isinstance(path, list):
                # Cas d'un script (ex: PowerShell)
                # On construit la commande pour forcer l'exécution du .ps1
                commande = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File"] + path
                return subprocess.Popen(commande)
            else:
                # Cas d'un dossier ou URL
                os.startfile(path)
        else:
            # --- LOGIQUE LINUX ---
            if isinstance(path, str):
                # Dossier ou URL
                return subprocess.Popen(['xdg-open', path], env=new_env)
            else:
                # Script .sh ou binaire
                return subprocess.Popen(path, env=new_env)
    except Exception as e:
        print(f"Erreur avec {path} : {e}")

def on_select_prog(event) :       # saisie du programme à modifier dans la liste des programmes
    global selection
    global YamlLocal
    global YamlPath
    global RepertApplis
    global ProgPath
    global PathExe
    TextBox.focus_set()
    selection = ComboProg.get()
    ProgPath=os.path.join(RepertApplis,selection).replace("\\","/")
    AppliPath=os.path.join(RepertApplis,"").replace("\\","/")
    YamlLocal=os.path.join(ProgPath,YamlName).replace("\\","/")
    DocsPath=os.path.join(ProgPath,"Docs").replace("\\","/")
    Boutonvalid.visible()
    #print("selection"+selection)
    #print("YamlLocal = " + YamlLocal)
    #print("YamlPath = " + YamlPath)
    #print("RepertApplis = " + RepertApplis)
    #print("AppliPath = " + AppliPath)
    #print("ProgPath = " + ProgPath)
    #print("PathExe = " + PathExe)
    if os.path.exists(YamlLocal) :
           filePath = shutil.copy(YamlLocal, YamlPath)
           safe_open_path(DocsPath)    # Ouvre l'explorateur sur le dossier programme
           FormMain.destroy()     # ferme le fenetre
           sys.exit()
    else :                	      # Ne doit pas arriver puisqu'on n'affiche que les prog avec ce fichier
           open_path(ProgPath)    # Ouvre l'explorateur sur le dossier applications 
           FormMain.destroy()     # ferme le fenetre
           show_alerte2(selection)  # Affichage d'alerte  Fichier yaml absent

def dossier_inscriptible(path):    # pour tester si le dossier cartes est verrouillé 
    try:
        test_file = os.path.join(path, "lock_test.tmp")
        with open(test_file, "w") as f:
            f.write("x")
        os.remove(test_file)
        return False  # pas verrouillé
    except PermissionError:
        return True   # verrouillé
    except Exception:
        return True   # on considère verrouillé par sécurité
  
def clear_titreliscart(event):
    if ComboCart.get() == titreliscart:
        ComboCart.set("")
    
def on_select_carte(event) :       # saisie du nom/version de carte choisie
    global selection
    global VersionCarte
    global CarteSelPath
    Messereur['text']=""
    selection = ComboCart.get()
    #print(selection)
    VersionCarte=selection
    Boutonvalid.visible()
    if selection == TEXTES.get("Autrecarte","missing key: Autrecarte") :
        Label4.visible()
        TextBox.visible()
        TextBox['text']=""
        TextBox.focus_set()
        if os.path.exists(os.path.join(CartesPath,".locked")) :   # test si dossier cartes verrouillé  
            BoutDeverr.visible()
            Messereur['text']=TEXTES.get("Mesunlock","missing key: Mesunlock")
    else :
        CarteSelPath=os.path.join(CartesPath,selection).replace("\\","/")
        Label4.invisible()
        TextBox.invisible()
        #print ("CarteSelPath= "+CarteSelPath)
          
def Appel_verrouillage():
    # Définition des chemins avec le tilde ~
    if sys.platform == "win32":
        fich = os.path.join(LocActu,"lockcartslmt.ps1")
    else:
        fich = os.path.join(LocActu,"Applications/lockcartslmt.sh").replace("\\","/")

    # Transformation du ~ en chemin absolu réel
    fich_absolu = os.path.expanduser(fich)

    # Contrôle de présence avec le chemin résolu
    if os.path.exists(fich_absolu):
        # On passe le chemin résolu dans une LISTE
        safe_open_path([fich_absolu])
        Messereur['text']=""
        BoutDeverr.invisible()
    else:
        # On affiche le chemin résolu pour que l'utilisateur comprenne où le script est attendu
        print(f"Script de verrouillage non trouvé : {fich_absolu}")

def ClicButtonValid():          # validation de création de programme (avec nouvelle carte ou non)
    global selection, NomProg, CarteSelPath, VersionCarte, NomCarte, ErrMsg, LockCart
    CreaCarte = False
    LockCart = False
    ErrMsg = ""
    Messereur['text'] = ""
    TextBox.config(state="disable")
    ComboCart.config(state="disable")

    # Gestion de la sélection de carte
    if selection == TEXTES.get("Autrecarte","missing key: Autrecarte") :
        newFolderName = TextBox.get().replace(" ", "")
        if not newFolderName:
            ErrMsg = TEXTES.get("Errnomcart","missing key: Errnomcart")
        else:
            newCartePath = Path(CartesPath) / newFolderName
            #print("newCartePath : ",newCartePath)
            VersionCarte = str(newCartePath)
            if newCartePath.exists() :
                ErrMsg = TEXTES.get("Errcartexis1","missing key: Errcartexis1")+newFolderName+TEXTES.get("Errcartexis2","missing key: Errcartexis2")
            else:
                CreaCarte = True
                CarteSelPath = str(newCartePath)
                try:
                    newCartePath.mkdir(parents=True, exist_ok=True) 
                except (PermissionError, OSError):
                    Messereur['text']=TEXTES.get("Mesunlock","missing key: Mesunlock")
                    LockCart = True # blocage changement de langue pendant validation nouvelle carte
                    return          # on ne valide pas tant que le répertoire est protégé en écriture
    else:
        VersionCarte = selection
        CarteSelPath = str(Path(CartesPath) / selection)

    # Détection des erreurs rencontrées et affichage
    if not RepertApplis:
        ErrMsg = TEXTES.get("Errrepappli","missing key: Errrepappli")
    if not NomProg:
        ErrMsg = TEXTES.get("Errnomprog","missing key: Errnomprog")
    if not VersionCarte:
        ErrMsg = TEXTES.get("Errnouvcart","missing key: Errnouvcart")

    if ErrMsg:
        Messereur['text'] = ErrMsg
        TextBox.config(state="normal")
        ComboCart.config(state="normal")
        ComboCart.update_idletasks()
        ComboCart.config(state="readonly")
        return

    # Création des dossiers du programme
    NomCarte=os.path.basename(VersionCarte)
    appli_path = Path(RepertApplis) / NomProg
    prog_docs_path = appli_path / "Docs"
    ino_path = prog_docs_path / f"{NomProg}_v1"
    ino_file = ino_path / f"{NomProg}_v1.ino"

    for p in [appli_path, prog_docs_path, ino_path]:
        p.mkdir(parents=True, exist_ok=True)

    # Création du fichier .ino
    with open(ino_file, "w") as file:
                file.write("//"+ino_file.name+"\n//"+TEXTES.get("Ecritle","written on ")+Datjour+TEXTES.get("Pourcart","for board ")+NomCarte+"\n\n\nvoid setup() {\n\n\n}\n\n\nvoid loop(){\n\n\n}")

    if sys.platform == "win32":
        set_folder_icon_windows()
    else:
        # Détection du chemin de l'icône
        if getattr(sys, 'frozen', False):
            loc_actu = Path(sys._MEIPASS)
        else:
            loc_actu = Path(os.path.dirname(os.path.abspath(__file__)))
        icon_path = loc_actu / "Encapsule.png"
        set_folder_icon_linux(str(AppliPath), str(icon_path))

    # Copie et modification du fichier Arduino-cli.yaml
    shutil.copy(YamlFile, appli_path)
    YamlLocalPath = appli_path / YamlName
    with open(YamlLocalPath, "r") as file:
        config = yaml.safe_load(file)

    config["directories"]["data"] = CarteSelPath
    config["directories"]["user"] = str(appli_path)

    with open(YamlLocalPath, "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, default_flow_style=False, allow_unicode=True)

    shutil.copy(YamlLocalPath, YamlPath)

    safe_open_path([PathExe, str(ino_path)])
    FormMain.destroy()

    if CreaCarte:
        time.sleep(4)
        show_alerte1(NomCarte)                
        
#====================================================================
              

menubar = Menu(FormMain, background='cyan4', fg='white')
menu1 = Menu(menubar, tearoff=0)
menu1.add_command(label="Q", command=Quitter)
IDX_QUITTER = menu1.index("end")
menubar.add_cascade(label="F", menu=menu1)
IDX_MENU_FICHIER = menubar.index("end")
menu2 = Menu(menubar, tearoff=0)
menu2.add_command(label="Effacer fichier paramètres", command=RazParam)
IDX_EFFACE = menu2.index("end")
menubar.add_cascade(label="Param", menu=menu2)
IDX_MENU_PARAM = menubar.index("end")
menu3 = Menu(menubar, tearoff=0)
menu3.add_command(label="A propos", command=AffAbout)
IDX_APROPOS = menu3.index("end")
menu3.add_separator()
menu3.add_command(label="Info", command=AffInfo)
IDX_INFOS = menu3.index("end")
menubar.add_cascade(label="Aide", menu=menu3)
IDX_MENU_AIDE = menubar.index("end")
menustyle = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Thème", menu=menustyle)
IDX_STYLE = menubar.index("end")
menustyle.add_command(label="Clair", command=set_clair)
IDX_CLAIR = menustyle.index("end")
menustyle.add_command(label="Sombre", command=set_sombre)
IDX_SOMBRE = menustyle.index("end")
menubar.add_cascade(label=" "*10)
menu4 = tk.Menu(menubar, tearoff=0, background='gold')
menu4.add_command(label="Language ?", command=ChoixLangue)
menubar.add_cascade(label="Lang.", menu=menu4)
IDX_MENU_LANG = menubar.index("end")
FormMain.config(menu=menubar)

LabExArdui=Label(FormMain, text="")                           # demande du chemin de l'exe Arduino
LabExArdui.visible = lambda: LabExArdui.place(x=12, y=11)
LabExArdui.invisible = lambda: LabExArdui.place_forget()

LabExeArd1 = Label(FormMain, text="")                           # libelle devant le chemin de l'exe Arduino
LabExeArd1.visible = lambda: LabExeArd1.place(x=15, y=15)
LabExeArd1.invisible = lambda: LabExeArd1.place_forget()

LabExeArd2 = Label(FormMain, text="")                            # affiche le chemin de l'exe Arduino
LabExeArd2.visible = lambda: LabExeArd2.place(x=280, y=15)
LabExeArd2.invisible = lambda: LabExeArd2.place_forget()

PathExe_var = StringVar()

TBExeArd=Entry(FormMain, width=65, textvariable = PathExe_var)    # champ de saisie du chemin de l'exe Arduio
TBExeArd.visible = lambda: TBExeArd.place(x=290, y=10)
TBExeArd.invisible = lambda: TBExeArd.place_forget()

ButtonOK9=Button(FormMain, text="OK", command = ClicButtonOk9) # Bouton OK chemin de l'EXE Arduino
ButtonOK9.visible = lambda: ButtonOK9.place(x=900, y=8)
ButtonOK9.invisible = lambda: ButtonOK9.place_forget()

Label0 = Label(FormMain, text="")                            # message aide pour trouver l'Exe IDE Arduino
Label0.visible = lambda: Label0.place(x=80, y=36)
Label0.invisible = lambda: Label0.place_forget()

BoutYaml=Button(FormMain, text="", command = ClicBoutYaml)  # bouton sélection du chemin du fichier yaml
BoutYaml.visible = lambda: BoutYaml.place(x=15, y=65)
BoutYaml.invisible = lambda: BoutYaml.place_forget()

LabYaml1 = Label(FormMain, text="")                        # libellé devant le chemin du fichier yaml
LabYaml1.visible = lambda: LabYaml1.place(x=15, y=68)
LabYaml1.invisible = lambda: LabYaml1.place_forget()

LabYaml2 = Label(FormMain, text="",bg='lightcyan',fg='Blue')     # chemin du fichier yaml
LabYaml2.visible = lambda: LabYaml2.place(x=280, y=68)
LabYaml2.invisible = lambda: LabYaml2.place_forget()
 
BoutRepCart=Button(FormMain, text="", command = ClicBoutRepCart)  # bouton sélection du répertoire des cartes
BoutRepCart.visible = lambda: BoutRepCart.place(x=10, y=110)
BoutRepCart.invisible = lambda: BoutRepCart.place_forget()

Labela = Label(FormMain, text="")                     # libellé devant le chemin du répertoire des versions de cartes
Labela.visible = lambda: Labela.place(x=15, y=115)
Labela.invisible = lambda: Labela.place_forget()

Labelb = Label(FormMain, text="")                                        # chemin du répertoire des cartes
Labelb.visible = lambda: Labelb.place(x=280, y=115)
Labelb.invisible = lambda: Labelb.place_forget()

Labelc = Label(FormMain, text="")                                  # message au sujet des questions initiales
Labelc.configure(font= ('Arial', 10, 'italic'))
Labelc.visible = lambda: Labelc.place(x=25, y=145)
Labelc.invisible = lambda: Labelc.place_forget()

ButtonSelect=Button(FormMain, text="", command = ClicButtonSelect)   # bouton sélection du répertoire des applications
ButtonSelect.visible = lambda: ButtonSelect.place(x=10, y=180)
ButtonSelect.invisible = lambda: ButtonSelect.place_forget()

Label1 = Label(FormMain, text="")                             # libellé devant le répertoire des applications
Label1.visible = lambda: Label1.place(x=255, y=185)
Label1.invisible = lambda: Label1.place_forget()

ButtonOK0=Button(FormMain, text="OK", command = ClicButtonOk0)   # bouton OK pour répertoire des applications
ButtonOK0.visible = lambda: ButtonOK0.place(x=900, y=180)
ButtonOK0.invisible = lambda: ButtonOK0.place_forget()

Label2= Label(FormMain, text="")                                # demande du nom du nouveau programme
Label2.visible = lambda: Label2.place(x=145, y=270)
Label2.invisible = lambda: Label2.place_forget()

progname_var = StringVar()

TextBox1=Entry(FormMain,textvariable = progname_var)         # champ de saisie du nom du nouveau programme 
TextBox1.visible = lambda: TextBox1.place(x=490, y=270)
TextBox1.invisible = lambda: TextBox1.place_forget()

ButtonOK1=Button(FormMain, text="OK", command = ClicButtonOk1)   # bouton OK pour nom du nouveau programme
ButtonOK1.visible = lambda: ButtonOK1.place(x=700, y=268)
ButtonOK1.invisible = lambda: ButtonOK1.place_forget()

Label3= Label(FormMain, text="")                                  # demande du choix de la version de carte
Label3.visible = lambda: Label3.place(x=145, y=330)
Label3.invisible = lambda: Label3.place_forget()


ComboCart = ttk.Combobox(FormMain, values= ListCartes, state="readonly",    # liste déroulante des versions de cartes
                        width=31,height=10)
ComboCart.bind("<Button-1>", clear_titreliscart)
ComboCart.bind("<<ComboboxSelected>>", on_select_carte)
ComboCart.visible = lambda: ComboCart.place(x=490, y=330)
ComboCart.invisible = lambda: ComboCart.place_forget()

ComboProg = ttk.Combobox(FormMain, values= ListProgs, state="readonly",     # Liste déroulante des prog à modifier
                        width=40,height=14)
ComboProg.config(background="red", foreground="blue")
ComboProg.bind("<Button-1>", clear_titrelisprog)
ComboProg.bind("<<ComboboxSelected>>", on_select_prog)
ComboProg.visible = lambda: ComboProg.place(x=490, y=270)
ComboProg.invisible = lambda: ComboProg.place_forget()

ComboLang = ttk.Combobox(FormMain, values= ListLang, state="readonly",     # Liste déroulante des langues disponibles
                        width=12,height=10)
ComboLang.bind("<Button-1>", clear_titrelislang)
ComboLang.bind("<<ComboboxSelected>>", on_select_lang)
ComboLang.visible = lambda: ComboLang.place(x=300, y=0)
ComboLang.invisible = lambda: ComboLang.place_forget()

MesCrePro= Label(FormMain, text="")                                     # demande si creation d'un nouveau programme
MesCrePro.visible = lambda: MesCrePro.place(x=110, y=230)
MesCrePro.invisible = lambda: MesCrePro.place_forget()

varbout = StringVar()
varbout.set("-1")

RadioBout1 = Radiobutton(FormMain, text="", variable=varbout, value="O",      # réponse nouveau prog ? = OUI
                        command=BoutRad_sel, indicatoron=0,
                        selectcolor="white", padx=20, pady=5)
RadioBout1.visible = lambda: RadioBout1.place(x=490, y=225)
RadioBout1.invisible = lambda: RadioBout1.place_forget()

RadioBout2= Radiobutton(FormMain, text="", variable=varbout, value="N",      # réponse nouveau prog ? = NON
                        command=BoutRad_sel, indicatoron=0,
                        selectcolor="white", padx=20, pady=5)
RadioBout2.visible = lambda: RadioBout2.place(x=580, y=225)
RadioBout2.invisible = lambda: RadioBout2.place_forget()

Label4= Label(FormMain, text="")                                         # demande du nom de nouvelle carte
Label4.visible = lambda: Label4.place(x=170, y=380)
Label4.invisible = lambda: Label4.place_forget()

noucarte_var = StringVar()

TextBox=Entry(FormMain,textvariable = noucarte_var)                # champ de saisie de la nouvelle carte
TextBox.visible = lambda: TextBox.place(x=490, y=380)
TextBox.invisible = lambda: TextBox.place_forget()

BoutDeverr=Button(FormMain, text="", command = Appel_verrouillage)      # validation finale
BoutDeverr.visible = lambda: BoutDeverr.place(x=250, y=430)
BoutDeverr.invisible = lambda: BoutDeverr.place_forget()

Boutonvalid=Button(FormMain, text="", command = ClicButtonValid)      # validation finale
Boutonvalid.visible = lambda: Boutonvalid.place(x=700, y=430)
Boutonvalid.invisible = lambda: Boutonvalid.place_forget()

Label5=Label(FormMain, text="")                              # Question : Choix du programme à modifier
Label5.visible = lambda: Label5.place(x=200, y=270)
Label5.invisible = lambda: Label5.place_forget()

Messereur= Label(FormMain, text="")                             # Messages d'erreur en bas de fenêtre
Messereur.configure(font= ('Arial', 14, 'bold'))
Messereur.visible = lambda: Messereur.place(x=161, y=500)
Messereur.invisible = lambda: Messereur.place_forget()
Messereur.visible()

def MHKMouseOver(self):
    Label6.config(bg='White')
    Label7.config(bg='White')
def MHKMouseLeave(self):
    Label6.config(bg='Gray70')
    Label7.config(bg='Gray70')
    
Label6=Label(FormMain, text=" "*4+"MHK"+" "*10,bg='Gray70',fg='tomato')    # LOGO MHK
Label6.bind("<Button-1>", ouvrir_lien_MHK)
Label6.bind("<Enter>", MHKMouseOver)
Label6.bind("<Leave>", MHKMouseLeave)
Label6.configure(font= ('Arial black', 15))
Label6.place(x=889, y=550)

Label7=Label(FormMain, text="My Human Kit"+" "*10,bg='Gray70',fg='skyblue4')    # My Human Kit
Label7.bind("<Button-1>", ouvrir_lien_MHK)
Label7.place(x=889, y=578)

#-----------------------------------------------------------------------
# chargement des dictionnaires de langues et de thémes (Fichier langthem.json)
#print("test1",LocActu)
locparam=os.path.join(LocActu,"EncapsParam").replace("\\","/")
filename=os.path.join(locparam,"langthem.json").replace("\\","/")
try:
    with open(filename, "r", encoding="utf-8") as f:
        datlath = json.load(f)
except IOError:
    messalert = "missing file: langthem.json"
    show_alerte3(messalert)
    Quitter()
else :    
    LANGUES = datlath["langages"]    
    ListLang = [lang["name"] for lang in LANGUES]
    ComboLang["values"] = ListLang
    #print("LANGUES",LANGUES)
    #print("Liste langues",ListLang)
    THEMES = [datlath["themes"]["clair"], datlath["themes"]["sombre"]]
    
# Test présence du fichier parametres Fiparam.json
FiParam=os.path.join(LocActu,"EncapsParam/Fiparam.json").replace("\\","/")
try:
    with open(FiParam, 'r', encoding='utf-8') as fichier:
        Param = json.load(fichier)
except IOError:
    CreParam = True
    LabExArdui.visible()
    Label0.visible()
    TBExeArd.visible()
    ButtonOK9.visible()
    BoutRepCart.invisible()
    BoutYaml.invisible()
    Labelc.visible()
    TBExeArd.focus_set()
    codlang = "EN"                # anglais par défaut
    codes_connus = [lang["code"] for lang in LANGUES]  # liste des codes langues connues
    loc = locale.getlocale()[0]   # récup de la localisation de l'ordi (ex: fr_FR)
    if loc:                       # fr_FR se compose de :  fr = langue, FR = pays      
        elements = loc.split('_') # transforme "fr_FR" en une liste ["fr", "FR"]
        langue_loc = elements[0].upper() # premier élément (langue) mis en majuscule
        if langue_loc in codes_connus:    
            codlang = langue_loc  
        else: 
            if len(elements) > 1:              # vérifier qu'il y a un 2e élément (le pays)
                pays_loc = elements[1].upper() # on le convertit en majuscule
                if pays_loc in codes_connus:
                    codlang = pays_loc         # on prend le pays comme code langue
    #print("Langue par défaut: ", codlang)
    LockLang = True
    indtheme = 0
else :
    #print(Param)
    CartesPath = Param["CartesPath"]
    LabExeArd1.visible()
    PathExe=Param["PathExe"]
    LabExeArd2['text']=PathExe
    LabExeArd2.visible()
    Labela.visible()
    Labelb['text'] = CartesPath
    Labelb.visible()
    RepertApplis = Param["RepertApplis"]
    ButtonSelect.visible()
    Label1['text'] = RepertApplis
    Label1.visible()
    YamlPath = Param["YamlPath"]
    LabYaml1.visible()
    LabYaml2['text'] = Param["YamlFile"]
    LabYaml2.visible()
    YamlFile = Param["YamlFile"]
    YamlName = os.path.basename(YamlFile)
    #print ("YamlName= "+YamlName)
    Labelc.visible()
    ButtonOK0.visible()
    codlang = Param["Langue"]
    indtheme = Param["Theme"]

set_style()
langue = name_from_code(codlang)
fichlang = f"lang_{codlang}.json"
menubar.entryconfig(IDX_MENU_LANG, label=f"🌐 {langue}")
#print("codlang ",codlang)
load_language(codlang)

FormMain.mainloop()

#=======================================================================
