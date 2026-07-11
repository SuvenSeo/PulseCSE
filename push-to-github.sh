#!/bin/sh
git init
git branch -M main
git add .
git commit -m "Build PulseCSE stock alert dashboard"
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/SuvenSeo/PulseCSE.git
git push -u origin main
