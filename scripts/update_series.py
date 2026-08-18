import json, re, sys, io, urllib.request

# Prose lives here rather than in README.md because the block between the
# markers is fully regenerated; anything typed into it by hand is discarded on
# the next run. A series with no entry here still renders, using its own label.
#
# That fallback is why five rows sat showing an em dash: the rows and counts come
# from stats.json and appear the moment a series has one post, but the prose does
# not, and nothing reported the gap. Adding a series means adding it HERE too --
# the same one-more-edit that CATEGORY_ORDER, the sidebar feed tabs and the
# per-cloud service catalogues each need on the site side.
BLURB = {
    "AWS Architecture Series":
        "One enterprise pattern at a time \u2014 the decision, the trade-offs, "
        "and what it costs when it is made badly.",
    "Azure Architecture Series":
        "The same treatment on Azure, explained on its own terms rather than as "
        "a translation from AWS \u2014 written for a reader who may never have "
        "opened an AWS console.",
    "GCP Architecture Series":
        "The same treatment on Google Cloud, written while learning the platform "
        "rather than from years of it \u2014 which is exactly why every figure is "
        "checked against Google's own documentation before it ships.",
    "AWS Weekly Lab":
        "One production-grade capability built end to end each week. Working "
        "Terraform, an architecture diagram, and an honest writeup of what broke.",
    "AWS Daily Intelligence":
        "What AWS shipped, and whether it actually changes anything. Every "
        "claim cited to official AWS documentation.",
    "AWS Weekly Intelligence":
        "Everything AWS shipped in one week, ranked, published Saturday once the "
        "week is closed. The inventory is built from AWS's own feeds by script, "
        "because summarising them by hand missed a third of one week.",
    "Azure Weekly Intelligence":
        "The same for Azure \u2014 one week of announcements, ranked, read from "
        "Microsoft's own release feeds rather than from a summary of them.",
    "GCP Weekly Intelligence":
        "The same for Google Cloud, built from the combined release-notes feed "
        "\u2014 which publishes one entry per calendar day rather than per "
        "announcement, so a day has to be taken apart before anything can be "
        "counted.",
}

WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
         7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven",
         12: "Twelve"}


def intro(n):
    """The sentence above the table, generated rather than typed.

    It read "Three ongoing series" while the table listed eight. It was written
    when there were three, sits outside the SERIES-LIST markers, and so was the
    one number on the page that nothing updated -- next to a table whose own
    caption promises the counts are "generated from the blog, not typed by hand".

    Generating it is the fix rather than editing it to eight, which would simply
    be wrong again at nine.
    """
    # "series" is its own plural, so there is nothing to pluralise -- which is
    # why this takes the count and not a count plus a suffix.
    return ("%s ongoing series. Counts below are generated from the blog, not "
            "typed by hand." % WORDS.get(n, str(n)))


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
    # The intro line joins the generated block, so it moves inside the markers
    # and stops being a hand-maintained number.
    return intro(len(stats.get("series", []))) + "\n\n" + "\n".join(rows)

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
