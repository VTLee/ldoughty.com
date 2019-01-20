#!/usr/bin/env bash
echo ${PWD}
hugo server --baseURL=desktop-pi --bind=0.0.0.0 -EFD --themesDir ~/gitwork/ -t silhouette-hugo
#hugo config
