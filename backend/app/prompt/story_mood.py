"""
Story Mood Modifiers

These style modifiers are inserted into the story writer prompt to transform
the narrative into different webtoon genres. Each mood has specific rules for
setting translation, character design, visual aesthetic, and tone.
"""

STORY_GENRE_PROMPTS = {
    "MODERN_ROMANCE_DRAMA_MANHWA": """
Generate a contemporary Korean romance drama story with the following narrative elements:
- Setting: Modern urban Korea (Seoul cafes, corporate offices, university campuses, apartments)
- Tone: Emotionally nuanced with bittersweet undertones, tender yet melancholic, slow-burn intimacy
- Character archetypes: Complex professionals or students with hidden wounds, past traumas, or emotional barriers
- Themes: Healing through connection, second chances, quiet longing, unspoken feelings, finding comfort in vulnerability
- Conflict: Emotional distance vs growing attraction, fear of commitment, past relationships haunting present, social or career pressures interfering with love
- Pacing: Slow, contemplative build-up with intimate everyday moments, gradual emotional revelation
- Story beats: Chance encounters, shared quiet moments, misunderstandings rooted in fear, tender confessions, emotional breakthroughs
- Mood: Soft melancholy mixed with hope, realistic relationship struggles, genuine emotional depth
- Dialogue style: Subtle, layered with subtext, emotionally restrained yet deeply felt
Create a story that captures the aching beauty of modern love with all its complications and quiet triumphs.
""",

    "FANTASY_ROMANCE_MANHWA": """
Generate a fantasy romance story with magical academy or mystical world elements:
- Setting: Enchanted academy, magical realm, or supernatural modern world with hidden magic
- Tone: Whimsical yet emotionally charged, dreamy with underlying danger, romance intertwined with destiny
- Character archetypes: Magically gifted protagonists with hidden powers or royal bloodlines, mysterious love interests with secrets, rivals-to-lovers dynamics
- Themes: Forbidden love across magical hierarchies, destiny vs choice, power awakening through emotional bonds, sacrifice for love
- Conflict: Magical threats requiring partnership, class or species divides, prophecies forcing difficult choices, dark forces threatening loved ones
- Pacing: Balanced between romantic development and magical plot progression, alternating tender moments with dramatic reveals
- Story beats: Magical awakening or discovery, forced proximity through quests or academy partnerships, near-death moments sparking confessions, climactic magical battles fueled by love
- Mood: Enchanting and emotionally intense, sparkles and danger, passionate devotion within fantastical stakes
- Dialogue style: Emotionally direct during pivotal moments, playful banter mixed with profound declarations
Create a story where magic and romance are inseparably intertwined, where love itself becomes a power.
""",

    "HISTORY_SAGEUK_ROMANCE": """
Generate a historical Korean period romance (Joseon era or historical dynasty setting):
- Setting: Royal palaces, noble houses, historical villages, ancient Korea with strict social hierarchies
- Tone: Deeply dramatic and tragic, passionate yet restrained by social conventions, intense forbidden longing
- Character archetypes: Noble ladies, princes, royal guards, scholars, courtesans—all bound by duty and honor, star-crossed lovers from different social stations
- Themes: Forbidden love vs duty, sacrifice for family or kingdom, love that transcends social barriers, tragic devotion, honor and passion in conflict
- Conflict: Class divides, political intrigue threatening romance, forced marriages, family honor vs personal desire, dangerous court conspiracies
- Pacing: Slow-burning tension with explosive emotional climaxes, weighted by historical formality and propriety
- Story beats: Stolen glances during formal ceremonies, secret midnight meetings, politically motivated betrayals, desperate sacrifices, bittersweet or tragic endings with lasting impact
- Mood: Heavy with longing and tragedy, sensual tension beneath formal restraint, raw emotional intensity within historical constraints
- Dialogue style: Formal and poetic, heavy with subtext and unspoken emotion, declarations carry enormous weight
Create a story of passionate, forbidden love set against the rigid beauty and danger of historical Korea.
""",

    "ACADEMY_SCHOOL_LIFE": """
Generate a contemporary high school or university romance story:
- Setting: Modern Korean school campus, classrooms, cafeterias, after-school clubs, neighborhoods near school
- Tone: Sweet and wholesome with gentle emotional depth, youthful and hopeful, light-hearted with sincere feelings
- Character archetypes: Relatable students—popular but kind, quiet and misunderstood, childhood friends, academic rivals, new transfer students
- Themes: First love and self-discovery, friendship evolving into romance, overcoming insecurities together, finding courage to confess
- Conflict: Social dynamics and peer pressure, academic competition, misunderstandings from inexperience, fear of ruining friendships, family expectations
- Pacing: Episodic with gentle progression, everyday school life moments building gradually to emotional milestones
- Story beats: Shared umbrella in rain, study sessions turning intimate, school festival confessions, protecting each other from bullies, awkward first dates
- Mood: Innocent and tender, nostalgic warmth, gentle humor mixed with heartfelt sincerity
- Dialogue style: Youthful and genuine, awkward yet endearing, emotionally honest in key moments
Create a story capturing the pure, hopeful essence of young love blooming in the everyday magic of school life.
""",

    "ISEKAI_OTOME_FANTASY": """
Generate an isekai otome fantasy romance story (reincarnation/transmigration into fantasy world or otome game):
- Setting: Fantasy kingdom with nobility, magic, and otome game or novel-like world structure
- Tone: Whimsical and romantic with comedic moments, self-aware and playful, dreamy wish-fulfillment balanced with genuine stakes
- Character archetypes: Reincarnated protagonist with modern knowledge, charming princes or duke love interests, scheming villainess rivals, loyal knights, childhood friends with hidden feelings
- Themes: Changing fate and rewriting destiny, modern wisdom in fantasy setting, earning love through genuine connection not game mechanics, found family and friendship
- Conflict: Avoiding "bad endings" or original plot death flags, winning over capture targets authentically, rival characters and political schemes, balancing multiple love interests
- Pacing: Lighthearted episodic adventures with romantic subplot progression, escalating stakes as protagonist changes the story
- Story beats: Realization of transmigration, clever use of future knowledge, subverting expected plot points, collecting love interests through kindness, dramatic confrontations with original storyline, choosing true love
- Mood: Playful and romantic, sparkling palace fantasy with comedic self-awareness, sweet multiple romantic routes converging
- Dialogue style: Modern protagonist's inner monologue contrasting with formal fantasy speech, witty banter, heartfelt emotional confessions breaking through game-like scenarios
Create a story of a modern soul navigating a fantasy romance world, finding real love while cleverly rewriting their destined fate.
"""
}