#!/usr/bin/env bash
# Show git log restricted to tasks2 directory.
git log --oneline --graph --decorate -- tasks2/ "$@"