import json, re, sys, io, urllib.request

# Prose lives here rather than in README.md because the block between the
# markers is fully regenerated; anything typed into it by hand is discarded on
# the next run. A series with no entry here still renders, using its own label.
BLURB = {
    "AWS Architecture Series":
        "One enterprise pattern at a time \u2014 the decision, the trade-offs, "
        "and what it costs when it is made badly.",
    "AWS Weekly Lab":
        "One production-grade capability built end to end each week. Working "
        "Terraform, an architecture diagram, and an honest writeup of what broke.",
    "AWS Daily Intelligence":
        "What AWS shipped, and whether it actually changes anything. Every "
        "claim cited to official AWS documentation.",
}

def build(stats):
    rows = ["| Series | What it is | Published |", "|:---|:---|:---|"]
    for s in stats.get("series", []):
        label = s["label"]
        count = s["count"]
        # stats.json carries "total" only for series with a fixed target
        # length (the 52-week lab). Everything else is open-ended.
        progress = "%d of %d" % (count, s["total"]) if s.get("total") else (
            "%d post%s" % (count, "" if count == 1 else "s"))
        rows.append("| **%s** | %s | %s |" % (
            label, BLURB.get(label, "\u2014"), progress))
    return "\n".join(rows)

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "https://jayanthkatta.com/blog/stats.json"
    if src.startswith("http"):
        stats = json.loads(urllib.request.urlopen(src).read().decode("utf-8"))
    else:
        stats = json.load(io.open(src, encoding="utf-8"))

    block = build(stats)
    readme = io.open("README.md", encoding="utf-8").read()
    updated = re.sub(r"(<!-- SERIES-LIST:START -->)(.*?)(<!-- SERIES-LIST:END -->)",
                     lambda m: m.group(1) + "\n" + block + "\n" + m.group(3),
                     readme, flags=re.DOTALL)
    if updated == readme:
        print("README unchanged")
    else:
        io.open("README.md", "w", encoding="utf-8", newline="\n").write(updated)
        print("README updated")
