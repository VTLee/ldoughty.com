#!/usr/bin/env bash
echo ${PWD}
hugo -D server --baseURL=pi3 --bind=0.0.0.0 -E -F --themesDir /share -t silhouette-hugo
#hugo config
