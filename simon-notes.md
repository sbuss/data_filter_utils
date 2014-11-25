# Filtering

* Exclude practice (first 24)
* just correct response filtering.
* Exclude cases where box was in the middle of the screen, we messed up there.

# Summarizing

Accuracy for incongruent and congruent

Congruent if:

    box_img == 'redsquare.bmp' && alignment == 'left'
    box_img == 'bluesquare.bmp' && alignment == 'right'

Reaction time for incog & cog (for both (just accurate responses) and (all responses))

Simon score = incog RT - cog RT (for just accurate reponses)
