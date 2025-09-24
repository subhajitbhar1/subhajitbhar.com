---
authors: 
    - subhajit
title: Git 101 – Commands and Workflows Cheat Sheet
description: Practical Git commands for daily use, with the minimal mental model and examples. Copy-paste friendly, organized by task.
slug: git-101-cheat-sheet
date: 
    created: 2025-09-24
categories:
    - Tech
tags:
    - Git
    - Cheat Sheet
    - Version Control
twitter_card: "summary_large_image"
---

A quick, task-oriented Git reference. Pair this with the in-depth guide for concepts and best practices.

<!-- more -->

## Minimal Mental Model

```mermaid
graph LR
  WD[Working Dir] -- add --> ST[Staging]
  ST -- commit --> REPO[Local Repo]
  REPO -- push --> ORI[Origin]
  ORI -- fetch/pull --> REPO
```

## Setup

```bash
git --version
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

## Create or Clone

```bash
git init
git clone <url>
```

## Status and Diffs

```bash
git status
git diff               # unstaged
git diff --staged      # staged vs HEAD
```

## Stage and Commit

```bash
git add <path>
git add -p             # interactive hunks
git commit -m "feat: message"
git commit --amend     # edit last commit
```

## Branching

```bash
git branch
git switch -c feature/x
git switch main
git branch -d feature/x
```

## Sync with Remote

```bash
git remote -v
git fetch
git pull               # merge
git pull --rebase      # rebase
git push -u origin my-branch
```

## Merge vs Rebase

```bash
git switch my-branch && git merge main
git switch my-branch && git rebase main
```

## Resolve Conflicts

```bash
git status
# edit files, remove markers
git add <file>
git commit                 # after merge
git rebase --continue      # during rebase
```

## Stash Work

```bash
git stash push -m "wip"
git stash list
git stash pop
```

## Undo Safely

```bash
git restore --staged <file>   # unstage
git restore <file>            # discard local edits
git revert <sha>              # new commit to undo
git reset --soft HEAD~1       # keep changes, drop last commit
git reflog                    # find lost commits
```

## Tags and Releases

```bash
git tag -a v1.0.0 -m "msg"
git push --tags
```

## Ignore and Clean

```bash
echo "node_modules/" >> .gitignore
git clean -fdx   # dangerous: removes untracked files
```

## Authentication (Quick)

```bash
# HTTPS + PAT
git clone https://github.com/owner/repo.git

# SSH
ssh-keygen -t ed25519 -C "you@example.com"
ssh-add ~/.ssh/id_ed25519
git clone git@github.com:owner/repo.git
```

## Conventional Commits (Optional)

```text
feat(auth): add oauth login
fix(api): handle null pointer in user service
chore(ci): update node to 20
```

## Common One-Liners

```bash
# See last commit summary
git log -1 --stat

# Interactive rebase last 5 commits
git rebase -i HEAD~5

# Squash branch onto main
git switch my-branch && git rebase -i main
```

## Quick PR Flow (GitHub)

```bash
git switch -c feat/x
# edit, add, commit
git push -u origin feat/x
# open PR on GitHub
```

See also: the full guide [“The Definitive Guide to Version Control with Git and GitHub”](/version-control-git-github/).


