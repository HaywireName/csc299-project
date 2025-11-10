#!/usr/bin/env bash
# Show git log restricted to tasks1 directory.
git log --oneline --graph --decorate -- tasks1/ "$@"