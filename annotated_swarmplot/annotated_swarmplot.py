#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("Config Rule Inventory.csv")


# We're not really interested in anything that is not considered in-scope, and
# we also don't want anything that was pointed 55 because that was John's way
# of noting work that was too big to estimate.

# We only actually care about the values of the estimated points and the risk
# score.
ndf = df.loc[
    ((df["In scope?"] == "Yes") | (df["In scope?"] == "Potential Add"))
    & (df["Pts to Automate Enforcement"] != 55)
]


# Create an x and y to build the plot from. We're going to plot story points by risk score.
x = ndf["Pts to Automate Enforcement"].fillna(0)
y = ndf["Risk"].fillna(0)


# To create the annotations, we'll need to assign a name to each dot. Since
# we're using a swarm plot, we really just have buckets... as many buckets as
# there are unique risk scores. So it doesn't matter which name goes to which
# dot as long as it's in the right bucket.
# So, for each bucket, we can assign the first name that fits the criterion
# (that it belongs to the bucket) and then remove it from the list. We'll take
# the first one by using the head() method and remove it by using drop().
#
sw = sns.swarmplot(x, y)

# We'll call our lookup table, which will be keyed by point coordinate,
# nlookup.
nlookup = {}
df = ndf.fillna(0)
for c in sw.collections:
    for (i, j) in c.get_offsets().astype(np.float16):
        name = df[df["Risk"] == j][["Feature / Rule Name"]].head(1)
        nlookup[(i, j)] = name.values.all()
        df = df.drop(name.index)


# At this point, the DataFrame should be empty.
# The nlookup dict should have an entry for every record that was in df.

# Now we need to define our annotation function to lookup the name for the dot
# being hovered over by the mouse pointer. This code was adapted from the great
# example given by
# [ImportanceOfBeingEarnest](https://stackoverflow.com/users/4124317/importanceofbeingernest),
# who is apparently a member of the matplotlib dev team, in [this Stack
# Overflow
# post](https://stackoverflow.com/questions/7908636/possible-to-make-labels-appear-when-hovering-over-a-point-in-matplotlib).

annot = sw.annotate(
    "",
    xy=(0, 0),
    xytext=(20, 20),
    textcoords="offset points",
    bbox=dict(boxstyle="round", fc="w"),
    arrowprops=dict(arrowstyle="->"),
)
annot.set_visible(False)


def update_annot(pc, ind):
    pos = pc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    i, j = pos.astype(np.float16)
    text = nlookup[(i, j)]
    annot.set_text(text)


def hover(event):
    vis = annot.get_visible()
    for pc in sw.collections:
        (status, ind) = pc.contains(event)
        if status is True:
            update_annot(pc, ind)
            annot.set_visible(True)
            sw.figure.canvas.draw_idle()
            break

    # If we made it through all of our collections and the status is False, we
    # are not in any dots.
    if status is False and vis:
        annot.set_visible(False)
        sw.figure.canvas.draw_idle()


sw.figure.canvas.mpl_connect("motion_notify_event", hover)
plt.show()
