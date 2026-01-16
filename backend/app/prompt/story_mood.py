"""
Story Mood Modifiers

These style modifiers are inserted into the story writer prompt to transform
the narrative into different webtoon genres. Each mood has specific rules for
setting translation, character design, visual aesthetic, and tone.
"""

MOOD_MODIFIERS = {
    "rofan": """
**[NARRATIVE MODIFIER: ROMANCE FANTASY (ROFAN / ISEKAI)]**
**Core Objective:** Completely twist the original Reddit seed into a grand romance fantasy tale filled with destiny, reincarnation, forbidden love, and dramatic reversals of fate. Even if the seed has no romantic or fantastical elements, force in isekai/reincarnation tropes and aristocratic intrigue.

**Key Transformations:**
1. Reposition the protagonist as someone who has been reincarnated/transmigrated into a new identity (villainess, abandoned princess, cursed noble, etc.).
2. Turn everyday conflicts into high-stakes courtly or magical drama: betrayals become prophesied schemes, arguments become duels of honor, misunderstandings become tragic fate-driven obstacles.
3. Introduce a powerful, emotionally unavailable male lead (cold duke, crown prince, grand mage) whose heart slowly thaws due to the protagonist's actions.
4. Build toward destined, sweeping romantic climaxes: soul-bond revelations, life-saving sacrifices, or public declarations that defy social hierarchy.
5. Infuse heavy themes of "fate," "destined love," "imperial grace," "cursed bloodline," and "reincarnation atonement."

**Tone:** Dramatic, poetic, swoon-worthy, emotionally intense with a sense of grand destiny.
""",

    "modern_romance": """
**[NARRATIVE MODIFIER: MODERN ROMANCE (K-DRAMA STYLE)]**
**Core Objective:** Transform the seed into a glossy, emotionally-charged contemporary romance full of slow-burn tension, dramatic coincidences, misunderstandings, and heart-fluttering reconciliations.

**Key Transformations:**
1. Elevate ordinary characters into idealized romantic leads: the protagonist becomes someone attractive yet emotionally guarded or career-focused; the love interest is usually aloof/rich/powerful with a hidden soft side.
2. Turn conflicts into classic K-drama tropes: contract relationships, fake dating, secret identities, childhood connections, family opposition, or workplace rivalry that turns romantic.
3. Create multiple "almost" moments and near-misses before the big emotional confession or kiss.
4. Include external obstacles (jealous second leads, family pressure, past trauma) that make the eventual union feel earned.

**Tone:** Heart-pounding, sophisticated, witty, tender, with lots of sim-kung (heart-fluttering) tension.
""",

    "slice_of_life": """
**[NARRATIVE MODIFIER: HEALING / SLICE OF LIFE]**
**Core Objective:** Soften and slow down the original seed into a gentle, comforting, everyday story focused on small joys, quiet growth, human connection, and emotional healing.

**Key Transformations:**
1. Drastically reduce or remove high-stakes conflict — replace it with personal struggles, small misunderstandings, or everyday inconveniences.
2. Shift focus to warm relationships: friendships, family bonds, budding gentle romance, mentorship, or community support.
3. Emphasize small, meaningful moments: sharing a meal, late-night talks, comforting gestures, rediscovering simple pleasures.
4. End with quiet fulfillment, acceptance, or subtle personal growth rather than explosive drama.

**Tone:** Tender, slow-paced, sentimental, warm, restorative, hopeful.
""",

    "revenge": """
**[NARRATIVE MODIFIER: REVENGE & GLOW-UP]**
**Core Objective:** Turn the seed into a deeply satisfying revenge fantasy where the protagonist is betrayed/humiliated, then transforms into a powerful, confident version of themselves and delivers perfect comeuppance.

**Key Transformations:**
1. Introduce a clear betrayal or injustice early (even if the seed doesn't have one — invent a cruel ex, backstabbing friend/colleague, family abandonment, etc.).
2. Give the protagonist a dramatic "glow-up" arc: emotional, social, financial, or skill-based transformation.
3. Build toward multiple satisfying power moves, public humiliations of the antagonists, and a final devastating reveal/showdown.
4. Make antagonists increasingly desperate, regretful, or pathetic as the protagonist rises.

**Tone:** Cathartic, empowering, fast-paced, aggressive, "cider" (refreshing revenge satisfaction), boss energy.
""",

    "high_teen": """
**[NARRATIVE MODIFIER: HIGH TEEN / ELITE ACADEMY DRAMA]**
**Core Objective:** Repackage the seed as a juicy, hormonal teen drama set in an elite private school/academy full of hierarchy, cliques, crushes, rivalries, and coming-of-age rebellion.

**Key Transformations:**
1. Relocate the entire story into a prestigious school setting with clear social ladder (queens/kings, scholarship students, heirs, etc.).
2. Turn adult relationships into teen versions: bosses become student council presidents/queen bees, colleagues become classmates/rivals/best friends.
3. Introduce classic high-teen tropes: bullying arcs that turn into redemption, secret crushes, love triangles, school festivals, talent shows, or major ranking battles.
4. Layer surface-level bubbly/gossipy energy over deeper tension, insecurity, and desire for acceptance or revenge.

**Tone:** Youthful, gossipy, dramatic, bubbly on the surface but emotionally intense underneath, full of teenage energy and petty/high-stakes school drama.
"""
}