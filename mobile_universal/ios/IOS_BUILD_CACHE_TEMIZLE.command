#!/bin/bash
set -e
echo "12/D iOS build cache temizlenecek:"
echo "$HOME/.12d_dil_programi_ios"
read -r -p "Devam? (e/H): " answer
case "$answer" in
  e|E|y|Y)
    rm -rf "$HOME/.12d_dil_programi_ios"
    echo "iOS build cache temizlendi."
    ;;
  *)
    echo "Iptal edildi."
    ;;
esac
