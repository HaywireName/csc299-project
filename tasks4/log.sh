#!/usr/bin/env bash
# Show git log restricted to tasks4 directory.
git log --oneline --graph --decorate -- tasks4/ "$@"