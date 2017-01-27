Shenzhen solitaire solver
=================

A backtracking solver for the solitaire minigame in the incredible [Shenzhen I/O](http://www.zachtronics.com/shenzhen-io/).

Terminology and notation
--------

Following [Wikipedia's glossary of patience terms](https://en.wikipedia.org/wiki/Glossary_of_patience_terms), I refer to any stack of cards as a pile. In the Shenzhen solitaire game, the cards start in 8 tableau piles of height 5. To win the game, the numbered cards must be collected in the 4 foundation piles. Finally, there are 3 cells where any card can be moved freely.

The notation `r8` describes the red card rank 8. `RR` is a red dragon. `f1` is the lone flower card.

    Move cards [b3 g2] from pile 0 move to pile 3

    RR -- GG    f1 -- -- b1

    g4 r9 BB g9 g6 g1 b5 GG
       g8    r8 GG b2 r1 r3
       r7    b7    b9 GG BB
             r6    BB    b8
             g5    BB    g7
             r4          b6
             b3          r5
             g2          b4
                         g3
                         r2

Findings
--------

I generated 1000 games and tried to solve them. Around 98% were soluble. On a 2015-spec computer, the median time to solve a game (or prove it insoluble) was 0.1 seconds. The 95th percentile was 6 seconds. A few games took much longer.

Example of an insoluble game
-----------

If it's of interest, I believe the game below is insoluble:

    GG BB b4 g6 BB r7 RR b5
    g1 RR r1 r6 g8 GG r5 GG
    b2 g9 BB b3 g7 r3 BB r8
    r4 g5 b8 b6 r2 b9 b1 g2
    RR r9 f1 g4 g3 b7 GG RR

