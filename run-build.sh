#!/usr/bin/env bash
hugo -DE --baseURL=$(hostname) --themesDir $(pwd)/../ -t silhouette-hugo --cleanDestinationDir
