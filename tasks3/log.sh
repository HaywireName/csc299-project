#!/usr/bin/env bash
# Show git log restricted to tasks3 directory.
git log --oneline --graph --decorate -- tasks3/ "$@"