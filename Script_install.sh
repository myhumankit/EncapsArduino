#!/bin/bash
# Installation de l'appli EncapsArduino v.2_3
# --- Gestion du terminal ---
if [[ ! -t 1 ]]; then
  for term in x-terminal-emulator gnome-terminal konsole xterm; do
    if command -v "$term" >/dev/null 2>&1; then
      exec "$term" -e "$0"
      exit
    fi
  done
fi

# --- On se place là où est le script ---
# C'est la clé : maintenant "." désigne le dossier d'installation, peu importe où il est.
cd "$(dirname "$0")"

# --- Chemins SOURCES (Relatifs au script) ---
# On assume que ces fichiers sont dans le même dossier que ce script d'installation
FICHEXE="./encapsarduino2_3" 
PARAM="./EncapsParam"
ICONE="./Encapsule.png"
SVCART="./lockcartslmt.sh"
SVCARLIB="./lockcartlib.sh"
ICOVERR="./arduino_verrouillage.png"

# --- Chemins DESTINATIONS (Toujours absolus car dans le système) ---
DESTEXE="$HOME/Applications"
DESTPARAM="$HOME/"
DESTICONE="$HOME/.local/share/icons"
DESTLANCEUR="$HOME/.local/share/applications"
DESTSCRIPT="$HOME/Scripts"

# === Couleurs ===
GREEN="\e[32m"
YELLOW="\e[33m"
NC="\e[0m"

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}   Installation de EncapsArduino v2.3 ${NC}"
echo -e "${YELLOW}==============================================${NC}"

# === Création des dossiers de destination ===
mkdir -p "$DESTEXE"
mkdir -p "$DESTICONE"
mkdir -p "$DESTLANCEUR"

# === Copie des fichiers ===
# On vérifie si le source existe avant de copier pour éviter un messages d'erreur
if [ -f "$FICHEXE" ]; then
    cp -f "$FICHEXE" "$DESTEXE/"
    # On rend l'exécutable... exécutable !
    chmod +x "$DESTEXE/$(basename "$FICHEXE")"
    echo -e "Exécutable : ${GREEN}Installé${NC}"
else
    echo -e "Exécutable : ${RED}Source introuvable !${NC}"
fi
# copie du script de verrouillage des cartes (appelé par le programme)
if [ -f "$SVCART" ]; then 
    cp -f "$SVCART" "$DESTEXE/"
    # On rend le script de verrouillage des cartes exécutable !
    chmod +x "$DESTEXE/$(basename "$SVCART")"
    echo -e "Script verrouillage cartes : ${GREEN}Installé${NC}"
else
    echo -e "Script verrouillage cartes : ${RED}Source introuvable !${NC}"
fi
# copie du script de verrouillage des cartes et librairies (appelé par l'utilisateur)
if [ -f "$SVCARLIB" ]; then 
    cp -f "$SVCARLIB" "$DESTSCRIPT/"
    # On rend le script de verrouillage des cartes et librairies exécutable !
    chmod +x "$DESTSCRIPT/$(basename "$SVCARLIB")"
    echo -e "Script verrouillage cartes et libs : ${GREEN}Installé${NC}"
else
    echo -e "Script verrouillage cartes et libs : ${RED}Source introuvable !${NC}"
fi

[ -d "$PARAM" ] && cp -r "$PARAM" "$DESTPARAM" && echo -e "Paramètres : ${GREEN}Installés${NC}"
[ -f "$ICONE" ] && cp -f "$ICONE" "$DESTICONE/" && echo -e "Icône application : ${GREEN}Installée${NC}"
[ -f "$ICOVERR" ] && cp -f "$ICOVERR" "$DESTICONE/" && echo -e "Icône verrouillage: ${GREEN}Installée${NC}"

## === Création du lanceur de l'exécutable' ===
cat <<EOF > "$DESTLANCEUR/encapsarduino.desktop"
[Desktop Entry]
Type=Application
Name=EncapsArduino
Comment=Lanceur créé par l'installateur
Exec=$HOME/Applications/encapsarduino2_3
Icon=$HOME/.local/share/icons/Encapsule.png
Terminal=false
Categories=Utility;Development;
EOF

## === Création du lanceur du script de verrouillage cartes & libs ===
cat <<EOF > "$DESTLANCEUR/arduino_verrouillage.desktop"
[Desktop Entry]
Type=Application
Name=Verrouillage cartes & libs
Comment=Verrouille ou déverrouille l'environnement Arduino
Exec=$HOME/Scripts/lockcartlib.sh
Icon=$HOME/.local/share/icons/arduino_verrouillage.png
Terminal=false
Categories=Utility;
EOF

# === Finalisation des droits et rafraîchissement ===
# 1. On rend l'exécutable bien... exécutable
chmod +x "$DESTEXE/encapsarduino2_3"
# 2. On donne les droits au lanceur .desktop
chmod +x "$DESTLANCEUR/encapsarduino.desktop"
# 3. On force le système à voir la nouvelle application immédiatement
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESTLANCEUR" >/dev/null 2>&1
fi

echo -e "\n${GREEN}  Installation terminée ${NC}"
echo ""
read -p "Appuyez sur Entrée pour quitter..."



