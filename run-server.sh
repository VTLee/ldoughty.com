#!/usr/bin/env bash
echo ${PWD}
hugo server --baseURL=$(hostname) --themesDir $(pwd)/../ -t silhouette-hugo --bind=0.0.0.0 -EFD -t silhouette-hugo
#hugo config
