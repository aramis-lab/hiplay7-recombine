% routine thomas samaille
function [sujet]=ouvrir(chemin_fichier)

sujet.header=spm_vol(chemin_fichier);
sujet.image=spm_read_vols(sujet.header);