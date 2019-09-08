#!/usr/bin/env bash
echo ${PWD}
hugo server --baseURL=$(hostname) -t silhouette-hugo --bind=0.0.0.0 -EFD
