# coding = utf8
"""自动post文件"""

import os
import subprocess
import time

POST_PATH = "_posts/"
PREVIEW_LENGTH = 120


def preview(filename):
    """获取文件预览"""
    with open(filename, "r", encoding="utf8") as f:
        yaml = False
        pre = ""
        for l in f.readlines():
            if l == "---\n":
                yaml = not yaml
                continue
            if yaml:
                continue
            if "<!-- " in l:
                if " -->" in l:
                    continue
                yaml = True
            if " -->" in l:
                yaml = False
                continue
            if l.startswith("#"):
                pre += "<br>\n"
                continue
            pre += l
            if "<br>\n\n" in pre:
                pre = pre.split("<br>\n\n")[-1]
            if len(pre) > PREVIEW_LENGTH * 0.8:
                pre = pre.strip()
                break
    for l in pre.split("\n\n"):
        if len(l) > PREVIEW_LENGTH * 0.2:
            pre = l.strip()
            break
    if len(pre) > PREVIEW_LENGTH * 1.2:
        pre = pre[:PREVIEW_LENGTH] + "……"
    if pre.count("*") % 2 == 1:
        pre += "*"
    return pre


def get_title(filename):
    """post标题"""
    with open(filename, "r", encoding="utf8") as f:
        for l in f.readlines():
            l = l.strip()
            if l.startswith("title: "):
                return l.strip("title: ")
    return filename.strip(".md").replace("\\", "/").split("/")[-1]


def post(filename):
    """发布单个文件"""

    title = get_title(filename)

    date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    with subprocess.Popen(
        ["git", "log", "--date=format:'%Y-%m-%d'", filename],
        stdout=subprocess.PIPE,
    ) as pipe:
        output = pipe.communicate()[0].decode("utf8")
        print(output)
    for t in output.split("\n"):
        if t.startswith("Date:"):
            date = t.split()[1][1:-1]
            break

    target = filename.replace(".md", "").replace("\\", "/")
    if target.endswith("."):
        target = target[:-1] + "/html"

    post_name = f"{date}-{title}.md"

    with open(os.path.join(POST_PATH, post_name), "w", encoding="utf8") as f:
        f.write(
            f"""---
target: /{target}
title: {title}
date: {date}
---

{preview(filename)}
"""
        )
    print(f"Posted: {post_name}")


def post_dir(path):
    """post文件夹路径下的内容"""
    for sub in os.listdir(path):
        subdir = os.path.join(path, sub)
        if os.path.isdir(subdir):
            post_dir(subdir)
        elif subdir.endswith(".md"):
            post(subdir)


if __name__ == "__main__":
    if not os.path.exists(POST_PATH):
        os.mkdir(POST_PATH)
    skip_dirs = [".git", "_includes", "_layouts", "_posts"]
    for i in os.listdir("./"):
        if os.path.isdir(i) and i not in skip_dirs:
            post_dir(os.path.join(i))
