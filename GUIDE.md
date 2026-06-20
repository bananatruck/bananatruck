# GitHub Profile README - Compact Photo Layout

This version keeps only the main profile photo, removes the six-photo collage,
and tightens the spacing to look closer to the Andrew6rant reference layout.

## Files

```text
README.md
light_mode.svg
dark_mode.svg
config.json
assets/profile.jpg
scripts/build_readme.py
.github/workflows/build.yaml
requirements.txt
```

## Edit your info

Update `config.json`, then rebuild:

```bash
python scripts/build_readme.py
```

## Push to your profile repo

Your GitHub profile README repo must be named exactly like your username:

```text
bananatruck/bananatruck
```

From this folder:

```bash
git init
git branch -M main
git remote add origin https://github.com/bananatruck/bananatruck.git 2>/dev/null || git remote set-url origin https://github.com/bananatruck/bananatruck.git

git add .
git commit -m "Update compact profile README"
git fetch origin main
git push -u origin main --force-with-lease
```

If Git still says `stale info` after fetching and this repo has nothing you need
to preserve, use:

```bash
git push -u origin main --force
```

## Notes

- The README image links to `https://bananatruck.site`.
- The SVG defaults to `light_mode.svg`.
- The dark SVG is included only as an optional generated asset.
- No GitHub token is required.
