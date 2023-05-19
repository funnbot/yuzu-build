# SPDX-FileCopyrightText: 2019 yuzu Emulator Project
# SPDX-License-Identifier: GPL-2.0-or-later

# Download all pull requests as patches that match a specific label
# Usage: python apply-patches-by-label.py <Label to Match>

import json, requests, subprocess, sys, traceback

allow_labels = sys.argv[1].split(',') # comma separated list of labels to allow that pr
extra_nums = sys.argv[2].split(',') # comma separated list of pr numbers to also add, even if it doesn't have the right labels 
github_token = None
if len(sys.argv) >= 4: github_token = sys.argv[3]

def check_individual(labels, number):
    for label in labels:
        if label["name"] in allow_labels: return True
    if str(number) in extra_nums: return True
    return False

def do_page(page):
    url = f"https://api.github.com/repos/yuzu-emu/yuzu/pulls?page={page}"
    headers = {}
    if github_token is not None: 
        headers["Authorization"] = f"Bearer {github_token}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    if (response.ok):
        j = json.loads(response.content)
        if j == []:
            return
        for pr in j:
            if (check_individual(pr["labels"], pr["number"])):
                # sanity check
                if (pr["state"] != "open"): continue
                pn = pr["number"]
                title = pr["title"]
                try:
                    print(subprocess.check_output(["git", "fetch", "origin", f"pull/{pn}/head:pr-{pn}", "-f", "--recurse-submodules=no"]))
                    print(subprocess.check_output(["git", "merge", "--squash", f"pr-{pn}"]))
                    print(subprocess.check_output(["git", "commit", "-m", f"Merge PR-{pn} '{title}'"]))
                    print(f"::notice::Merged PR-{pn} '{title}'")
                except:
                    print(f"::error::Error merging PR-{pn} '{title}'")
                    raise

try:
    for i in range(1,10):
        do_page(i)
except:
    traceback.print_exc(file=sys.stdout)
    sys.exit(-1)
