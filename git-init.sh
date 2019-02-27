#!/usr/bin/env bash

# Running this file is optional.
# It is intended as a convenience wrapper to initialize yopur git repo and link it to gitlab.
# If you run into problems with this, read what these steps are supposed to do and try to figure out a solution for your case

# define a local git repo
git init || exit

# link this local version to the remote on gitlab
git remote add origin git@git.datasciencelab.nl:intern/boom-chicago.git || exit

# add all the template files
git add . || exit

# since data dir is in the .gitignore, force-add that part
git add -f data/* || exit

# do the first commit annd push
git commit -am "Initial commit" || exit
git push -u origin master || exit

# just checking...
git status