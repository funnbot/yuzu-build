# SPDX-FileCopyrightText: 2019 yuzu Emulator Project
# SPDX-License-Identifier: GPL-2.0-or-later

# Download all pull requests as patches that match a specific label
# Usage: python apply-patches-by-label.py <Label to Match>

import json, requests, subprocess, sys, traceback

tagline = sys.argv[2]

def check_individual(labels):
    ok_to_merge = False
    for label in labels:
        if (label["name"] == "do-not-merge"):
            return False
        if (label["name"] == sys.argv[1]):
            ok_to_merge = True
    return ok_to_merge

def do_page(page):
    url = f"https://api.github.com/repos/yuzu-emu/yuzu/pulls?page={page}"
    response = requests.get(url)
    response.raise_for_status()
    if (response.ok):
        j = json.loads(response.content)
        if j == []:
            return
        for pr in j:
            if (check_individual(pr["labels"])):
                # sanity check
                if (pr["state"] != "open"): continue
                pn = pr["number"]
                print(f"Matched {tagline} PR# {pn}")
                print(subprocess.check_output(["git", "fetch", "origin", f"pull/{pn}/head:pr-{pn}", "-f"]))
                print(subprocess.check_output(["git", "merge", "--squash", f"pr-{pn}"]))
                print(subprocess.check_output(["git", "commit", "--no-verify", "-m", f"Merge {tagline} PR-{pn}"]))

try:
    for i in range(1,10):
        do_page(i)
except:
    traceback.print_exc(file=sys.stdout)
    sys.exit(-1)