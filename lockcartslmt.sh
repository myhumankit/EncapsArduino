#!/bin/bash
# =============================================================================
# lockcartslmt.sh
# Script de verrouillage/déverrouillage du dossier des cartes Arduino
# Protège les cartes contre les mises à jour involontaires
# Script appelé par EncapsArduino 
# =============================================================================


# -----------------------------------------------------------------------------
# VÉRIFICATION DES DROITS ADMINISTRATEUR
# -----------------------------------------------------------------------------
# Modifier les permissions de fichiers nécessite des droits root (administrateur).
# "$EUID" contient l'identifiant de l'utilisateur courant (0 = root).
# Si on n'est pas root, on relance ce même script ($0) via pkexec,
# qui affiche une fenêtre graphique de demande de mot de passe.
if [ "$EUID" -ne 0 ]; then
    pkexec "$0"
    exit 0
fi


# -----------------------------------------------------------------------------
# IDENTIFICATION DYNAMIQUE DE L'UTILISATEUR RÉEL
# -----------------------------------------------------------------------------
# Quand pkexec élève les privilèges, il remplit automatiquement la variable
# PKEXEC_UID avec l'UID (numéro) de l'utilisateur qui a lancé le script.
# On s'en sert pour retrouver son nom (REAL_USER) et son dossier home (HOME_DIR),
# sans jamais avoir à écrire un nom d'utilisateur en dur dans le script.
#
# "getent passwd" interroge la base des utilisateurs du système.
# "cut -d: -f1" extrait le 1er champ (le nom) séparé par des ":"
# "cut -d: -f6" extrait le 6ème champ (le dossier home)
REAL_USER=$(getent passwd "$PKEXEC_UID" | cut -d: -f1)
HOME_DIR=$(getent passwd "$PKEXEC_UID"  | cut -d: -f6)

# Sécurité : si on n'a pas pu identifier l'utilisateur, on quitte immédiatement
if [ -z "$REAL_USER" ] || [ -z "$HOME_DIR" ]; then
    echo "Erreur : impossible d'identifier l'utilisateur réel (PKEXEC_UID=$PKEXEC_UID)"
    exit 1
fi


# -----------------------------------------------------------------------------
# FONCTION : ENVOYER UNE NOTIFICATION VISUELLE À L'UTILISATEUR
# -----------------------------------------------------------------------------
# Comme le script tourne en root, il n'a pas accès au bureau de l'utilisateur.
# On doit donc "emprunter" la session graphique de l'utilisateur réel pour
# afficher une notification dans sa barre système.
#
# Paramètres :
#   $1 = titre de la notification
#   $2 = message de la notification
notify_user() {
    # PKEXEC_UID contient déjà l'UID de l'utilisateur réel — on l'utilise
    # directement pour trouver le bus de communication de son bureau.
    # su -c "commande" $REAL_USER → exécute la commande en tant que l'utilisateur réel
    su -c "DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/${PKEXEC_UID}/bus \
           notify-send '$1' '$2'" "$REAL_USER"
}


# -----------------------------------------------------------------------------
# LECTURE DU FICHIER DE CONFIGURATION arduino-cli.yaml
# -----------------------------------------------------------------------------

# Le chemin du fichier yaml est construit à partir du home de l'utilisateur réel,
# détecté dynamiquement — plus aucun nom d'utilisateur codé en dur.
YAML="${HOME_DIR}/.arduinoIDE/arduino-cli.yaml"

# awk '/data:/ {print $2}' : cherche la ligne contenant "data:" et extrait
# le 2ème mot (le chemin du dossier de la carte)
# tr -d '\r' : supprime les éventuels retours chariot Windows (\r)
RAW_DATA_PATH=$(awk '/data:/ {print $2}' "$YAML" | tr -d '\r')

# Sécurité : si le chemin est vide (ligne "data:" absente ou mal formatée),
# on avertit et on quitte proprement
if [ -z "$RAW_DATA_PATH" ]; then
    notify_user "Erreur" "lockcartslmt.sh : Chemin YAML introuvable"
    exit 1
fi

# dirname extrait le dossier parent d'un chemin.
# Ex: /home/alice/VERSIONS_CARTES/ESP32.3.1.3 → /home/alice/VERSIONS_CARTES
# On protège ainsi TOUT le dossier des versions de cartes, pas juste une carte.
CARDS_DIR=$(dirname "$RAW_DATA_PATH")

# On extrait le chemin "user:" du yaml (dossier du projet en cours)
USER_DIR=$(awk '/user:/ {print $2}' "$YAML" | tr -d '\r')

# -----------------------------------------------------------------------------
# FONCTION : VERROUILLER (passer en lecture seule)
# -----------------------------------------------------------------------------
lock() {
	touch "$CARDS_DIR/.locked"   # crée fich. marqueur de verrouillage
    # chmod = change mode (modifie les permissions d'un fichier ou dossier)
    # -R    = Récursif : applique le changement à tous les sous-dossiers et fichiers
    # a-w   = "all minus write" : retire le droit d'écriture (w) à TOUS
    #         (a = all : utilisateur + groupe + autres)
    chmod -R a-w "$CARDS_DIR"

    notify_user "Arduino" "🔒 Dossier cartes verrouillé"
}


# -----------------------------------------------------------------------------
# FONCTION : DÉVERROUILLER (remettre en mode écriture)
# -----------------------------------------------------------------------------
unlock() {
	rm -f "$CARDS_DIR/.locked"  # efface le marqueur de verrouillage
    # u+w = "user plus write" : redonne le droit d'écriture (w) uniquement
    #       au propriétaire (u = user), pas au groupe ni aux autres.
    #       C'est plus sûr que de tout réouvrir avec "a+w".
    chmod -R u+w "$CARDS_DIR"

    notify_user "Arduino" "🔓 Dossier cartes déverrouillé"
}


# -----------------------------------------------------------------------------
# LOGIQUE PRINCIPALE : BASCULE (TOGGLE)
# -----------------------------------------------------------------------------
# Le script fonctionne comme un interrupteur :
# - Si le dossier est actuellement accessible en écriture → on verrouille
# - Si le dossier est déjà verrouillé → on déverrouille
#
# ATTENTION : on ne peut pas utiliser [ -w "$CARDS_DIR" ] directement ici,
# car le script tourne en root, et root peut TOUJOURS écrire partout,
# même sur un dossier verrouillé en a-w. Le test retournerait donc
# toujours "vrai" et le script verrouillerait à chaque exécution.
#
# Solution : on effectue le test en tant que l'utilisateur RÉEL (REAL_USER)
# via "su -c", qui lui voit les vraies permissions appliquées.
# La commande "test -w" retourne 0 (succès) si accessible en écriture.
if su -c "test -w '$CARDS_DIR'" "$REAL_USER"; then
    lock    # Dossier accessible en écriture pour l'utilisateur → on verrouille
else
    unlock  # Dossier verrouillé pour l'utilisateur → on déverrouille
fi
