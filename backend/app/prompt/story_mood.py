


"""
Story Genre Narrative Plugins for 50-Second Webtoon Format

These plugins define the NARRATIVE CONTEXT (what exists, how characters speak, what happens)
NOT the visual rendering (colors, lighting, art style) - that's handled separately.

Each plugin contains:
1. CHRONO-LOCK: Time/tech constraints and forbidden anachronisms
2. SOCIOLINGUISTIC LAYER: Dialogue patterns and speech style
3. PROP DATABASE: Allowed physical objects and scene assets
4. TROPE ENGINE: Plot beats for 8-10 scene short-form structure
"""

STORY_GENRE_PROMPTS = {
    "NO_GENRE": """EMPTY - No narrative constraints applied.""",

    "MODERN_ROMANCE_DRAMA": """
=== NARRATIVE PLUGIN: Modern Romance Drama ===

[CHRONO-LOCK: 2020s Urban Setting]
ALLOWED TECH: Smartphones, laptops, coffee machines, cars, public transit, LED screens
ALLOWED LOCATIONS: Coffee shops, corporate offices, apartments, rooftops, parks, subway stations, convenience stores
FORBIDDEN: Historical clothing, fantasy elements, sci-fi technology, rural settings without modern infrastructure
ERA: Present day (2020-2026)

[SOCIOLINGUISTIC LAYER: Contemporary Korean-to-English]
DIALOGUE STYLE:
- Naturalistic, emotionally restrained
- Subtext-heavy (characters avoid saying what they really mean)
- Modern contractions and casual speech in comfortable moments
- Formal politeness when emotionally distant
- Sentence fragments during emotional peaks
EXAMPLES:
✓ "I'm fine." [clearly not fine]
✓ "We should talk." [dreading the conversation]
✓ "It's nothing." [voice breaking]
✗ "I harbor deep affection for thee" [too formal]
✗ "Yo dude, I'm totally into you" [too casual/Western]

[PROP DATABASE: Modern Urban Romance]
DRINKS: Coffee cups, wine glasses, beer cans, bottled water, tea mugs
TECH: Phones (checking messages, calls, notifications), earbuds, laptops
CLOTHING: Business attire, casual streetwear, coats, scarves, umbrellas
FURNITURE: Office desks, cafe tables, apartment couches, bar stools
WEATHER PROPS: Rain, umbrellas, winter breath visible in air, falling leaves
EMOTIONAL PROPS: Crumpled tissues, half-empty glasses, phone screens with unsent messages

[TROPE ENGINE: 50-Second Romance Arc]
SCENE 1-2: EMOTIONAL HOOK
- Start mid-argument, mid-confession, or mid-breakup
- Physical proximity with emotional distance (sitting together but not looking at each other)
- One character clearly hurt, other defensive or regretful

SCENE 3-5: CONTEXT REVEAL
- Quick flashback or dialogue revealing what led here
- Show the good times briefly (shared moment, laughter) then back to present tension
- Misunderstanding or hidden truth surfaces

SCENE 6-7: EMOTIONAL CLIMAX
- Confession or confrontation
- Physical gesture: hand reaching but not touching, turning away, finally making eye contact
- Raw vulnerability: tears, voice breaking, desperate honesty

SCENE 8-10: RESOLUTION/CLIFFHANGER
- Choice made: walking away, choosing to stay, reaching out
- Final beat: hopeful (embrace, small smile) OR heartbreaking (door closing, unanswered call)
- Leave emotional resonance, not necessarily closure

MANDATORY BEATS: Longing, miscommunication, moment of truth, genuine emotion
FORBIDDEN: Love triangles in 50 sec (too complex), magical solutions, easy fixes
""",

    "FANTASY_ROMANCE": """
=== NARRATIVE PLUGIN: Fantasy Romance ===

[CHRONO-LOCK: Medieval-Fantasy Fusion]
ALLOWED TECH: Magic crystals, enchanted items, flying creatures, teleportation circles, potion vials
ALLOWED LOCATIONS: Magical academies, enchanted forests, crystal towers, mystical gardens, throne rooms, ancient libraries
FORBIDDEN: Modern technology, guns, computers, cars, contemporary slang
ERA: Timeless fantasy realm (medieval aesthetic + magic)

[SOCIOLINGUISTIC LAYER: Fantasy-Modern Hybrid]
DIALOGUE STYLE:
- Slightly elevated but not archaic
- Fantasy terms used naturally (mana, spells, royal titles)
- Emotional directness (fantasy allows big declarations)
- Formal titles when appropriate (Your Highness, Master, Lady)
- Modern emotional vulnerability mixed with fantasy formality
EXAMPLES:
✓ "My magic responds to you. It's never done that before."
✓ "You're the heir to the Shadow Throne. I'm nobody."
✓ "Your Highness... don't make me choose between you and my kingdom."
✗ "Verily, I doth love thee" [too archaic]
✗ "Bro, that spell was sick" [too modern]

[PROP DATABASE: Fantasy Romance]
MAGIC ITEMS: Glowing crystals, spell books, enchanted jewelry, magical weapons, potion vials
CLOTHING: Flowing robes, cloaks, royal garments, academy uniforms, leather armor
CREATURES: Dragons (small/large), phoenixes, magical familiars, butterflies of light
ARCHITECTURE: Stone towers, marble halls, vine-covered ruins, floating islands
NATURE: Magical plants, glowing flowers, ancient trees, star-filled skies, ethereal mist
EMOTIONAL PROPS: Broken enchantments, fading spell marks, magical bonds (visible/invisible)

[TROPE ENGINE: 50-Second Fantasy Romance]
SCENE 1-2: MAGICAL HOOK
- Start during magical crisis or forbidden encounter
- Power imbalance visible (royal/commoner, master/student, rival houses)
- Magic itself showing the connection (spells reacting, powers resonating)

SCENE 3-5: FORBIDDEN REVEAL
- Why they can't be together (prophecy, duty, magical law, rival factions)
- Moment where magic betrays their feelings (accidental spell, visible energy)
- Stolen moment of impossible intimacy

SCENE 6-7: MAGICAL-EMOTIONAL CLIMAX
- Powers awakening or failing due to emotion
- Sacrifice offered or choice between love and duty
- Magic visualizing emotional state (barrier breaking, energy surging)

SCENE 8-10: FANTASY RESOLUTION
- Magical consequence of choice
- Final beat: Breaking rules together, tragic separation with promise, or defying fate
- Visual: Magic sealing their bond or tearing them apart

MANDATORY BEATS: Forbidden connection, magic tied to emotion, impossible choice, destiny vs love
FORBIDDEN: Overly complicated magic systems, too many magical creatures, info-dumping
""",

    "HISTORICAL_PERIOD_ROMANCE": """
=== NARRATIVE PLUGIN: Historical Period Romance ===

[CHRONO-LOCK: Joseon Dynasty / Historical Asia]
ALLOWED TECH: Paper, ink, fans, traditional weapons (swords, bows), candles, oil lamps, carriages
ALLOWED LOCATIONS: Royal palaces, noble estates, traditional villages, gardens, throne halls, servants' quarters
FORBIDDEN: Modern items, fantasy magic, casual physical contact, modern speech patterns
ERA: Pre-industrial historical Asia (Joseon-inspired, 1500-1800s aesthetic)

[SOCIOLINGUISTIC LAYER: Historical Formality]
DIALOGUE STYLE:
- Formal address with titles (My Lord, Your Highness, Master, Lady)
- Emotionally restrained in public, intense in private
- Indirect declarations (poetry, metaphor, loaded silences)
- Proper/improper speech indicating class
- Subtext is EVERYTHING (direct emotion is scandalous)
EXAMPLES:
✓ "I should not be here, My Lord."
✓ "Your Highness... this humble servant begs your mercy."
✓ "If I could... just this once..." [trailing off]
✗ "I love you" [too direct for first confession]
✗ "Let's meet up later" [too casual]

[PROP DATABASE: Historical Period]
CLOTHING: Hanbok, royal robes, servant clothes, hair ornaments, veils, formal headwear
OBJECTS: Fans, scrolls, ink stones, silk fabric, traditional furniture, screens
WEAPONS: Swords (ceremonial/battle), daggers, bows
ARCHITECTURE: Wooden pavilions, sliding doors, courtyards, traditional gates
NATURE: Cherry blossoms, pine trees, lotus ponds, moonlight, snow on tile roofs
EMOTIONAL PROPS: Hidden letters, exchanged tokens (hairpin, ribbon), clenched fabric

[TROPE ENGINE: 50-Second Historical Romance]
SCENE 1-2: FORBIDDEN ENCOUNTER
- Stolen moment in hidden location or chance meeting
- Class/status divide immediately visible (clothing, posture, address)
- One character risks everything by being there

SCENE 3-5: DUTY VS DESIRE
- Political arrangement or social pressure revealed
- Brief memory of connection or kindness
- Cannot touch but yearning is palpable

SCENE 6-7: DESPERATE CLIMAX
- Forbidden confession or final meeting
- Physical restraint (reaching but not touching, separated by screen/distance)
- Breaking protocol in moment of emotion (dropping title, physical proximity)

SCENE 8-10: TRAGIC RESOLUTION
- Sacrifice made for duty, honor, or family
- Final exchange: returned token, last look, promise that can't be kept
- Historical weight: choice echoes through court/society

MANDATORY BEATS: Social barrier, restrained longing, protocol breaking, sacrifice, duty wins or love defies
FORBIDDEN: Happy easy endings (not historically fitting), modern emotional directness, casual touch
""",

    "SCHOOL_YOUTH_ROMANCE": """
=== NARRATIVE PLUGIN: School/Youth Romance ===

[CHRONO-LOCK: Modern High School/University]
ALLOWED TECH: Smartphones, headphones, school computers, vending machines, bikes
ALLOWED LOCATIONS: Classrooms, hallways, rooftops, cafeterias, libraries, school gates, convenience stores, parks, karaoke rooms
FORBIDDEN: Adult settings (bars, offices), explicit adult themes, fantasy elements
ERA: Present day (2020s school environment)

[SOCIOLINGUISTIC LAYER: Youthful Contemporary]
DIALOGUE STYLE:
- Natural teenage/young adult speech
- Awkward and earnest, not polished
- Texting language, casual contractions
- Nervous rambling when emotional
- Playful teasing between friends
EXAMPLES:
✓ "I-I just wanted to say... never mind."
✓ "You're such an idiot." [affectionate]
✓ "Wait for me after class?"
✓ "I can't stop thinking about you. Is that weird?"
✗ "My feelings for you are profound" [too formal for teens]
✗ Heavy sexual innuendo [keep it innocent/sweet]

[PROP DATABASE: School Life]
SCHOOL ITEMS: Textbooks, notebooks, pencil cases, uniforms, backpacks, lunch boxes
TECH: Phones (texting, music), earbuds, portable chargers
FOOD/DRINK: Convenience store snacks, vending machine drinks, shared food, ice cream
WEATHER: Shared umbrellas, winter scarves, spring blossoms, summer heat
ACTIVITIES: Sports equipment, musical instruments, art supplies, study materials
EMOTIONAL PROPS: Love letters, shared earbuds, matching items, handwritten notes

[TROPE ENGINE: 50-Second Youth Romance]
SCENE 1-2: INNOCENT HOOK
- Start mid-confession, seeing crush with someone else, or caught staring
- School setting immediately clear
- Youthful awkwardness visible (blushing, stammering, avoiding eye contact)

SCENE 3-5: SWEET TENSION
- Shared moment: walking together, study session, festival preparation
- Friend encouraging or teasing
- Small gesture: sharing food, lending item, protective moment

SCENE 6-7: HEARTFELT CLIMAX
- Rooftop/quiet place confession
- Awkward but genuine emotional honesty
- Physical: holding hands for first time, almost-kiss, or protective gesture

SCENE 8-10: SWEET RESOLUTION
- Reciprocation or gentle rejection with hope
- Final beat: Walking together, shared smile, promise of tomorrow
- Wholesome ending: Beginning of relationship or treasured memory

MANDATORY BEATS: Innocence, awkward sincerity, sweet gestures, youthful hope
FORBIDDEN: Cynicism, adult complications, dark themes, explicit content
""",

    "REINCARNATION_FANTASY": """
=== NARRATIVE PLUGIN: Reincarnation/Isekai Fantasy ===

[CHRONO-LOCK: Fantasy World with Game/Novel Awareness]
ALLOWED TECH: Medieval-fantasy + modern protagonist's knowledge, status windows, magic systems, game-like interfaces
ALLOWED LOCATIONS: Fantasy palaces, noble estates, magical academies, medieval towns, enchanted forests
FORBIDDEN: Modern technology actually working (no phones/computers), Earth locations
ERA: Fantasy medieval world with isekai/otome game mechanics

[SOCIOLINGUISTIC LAYER: Modern Mind in Fantasy Speech]
DIALOGUE STYLE:
- Internal monologue: Modern, snarky, self-aware
- External speech: Adapts to fantasy formality
- Occasional modern slang slip-ups for comedy
- Breaking fourth wall in thoughts about "plot" and "flags"
- Genuine emotion cuts through meta-awareness
EXAMPLES:
✓ [Internal: "Oh no, this is the death flag scene!"] [External: "Your Highness, I must decline."]
✓ "Wait, that wasn't in the original story..."
✓ [Internal: "The capture target is actually kind of..."] *blushes*
✗ Full modern speak to nobles without comment
✗ Over-explaining game mechanics out loud

[PROP DATABASE: Isekai Fantasy]
GAME ELEMENTS: Visible status windows, floating text, level-up effects, quest markers
MAGIC ITEMS: Enchanted jewelry, spell books, magical contracts, transformation items
NOBILITY: Royal regalia, fancy gowns, carriages, family crests, formal invitations
MODERN KNOWLEDGE: Recipes, inventions, strategies (shown, not just told)
FANTASY STANDARD: Swords, magic circles, potions, magical beasts
EMOTIONAL PROPS: Flags being avoided, relationship meters, original vs new timeline evidence

[TROPE ENGINE: 50-Second Isekai Romance]
SCENE 1-2: REINCARNATION REALIZATION
- Start as protagonist realizes they're in the novel/game
- See the "love interest" and internal panic about plot
- Trying to avoid death flags or bad ending

SCENE 3-5: PLOT SUBVERSION
- Original scene playing out differently due to protagonist's choices
- Love interest confused by changed behavior
- Modern knowledge creating unexpected chemistry

SCENE 6-7: REAL FEELINGS EMERGE
- Beyond game mechanics, genuine emotion develops
- Protagonist caught between "this is just a story" and real feelings
- Love interest proving they're a real person, not just a character

SCENE 8-10: NEW FATE
- Choosing connection over "correct route"
- Breaking free from original plot
- Final beat: New timeline established or heartfelt defiance of destiny

MANDATORY BEATS: Meta-awareness, fate defiance, game logic vs real emotion, choosing authenticity
FORBIDDEN: Info-dumping game mechanics, too many capture targets in 50 sec, confusing timeline jumps
""",

    "DARK_OBSESSIVE_ROMANCE": """
=== NARRATIVE PLUGIN: Dark Obsessive Romance ===

[CHRONO-LOCK: Flexible - Historical or Modern Dark Setting]
ALLOWED TECH: Depends on era choice - but always includes: restraints, locked doors, isolated locations
ALLOWED LOCATIONS: Opulent but isolated estates, dark palaces, penthouse prisons, remote manors, underground spaces
FORBIDDEN: Public happy spaces, bright cheerful settings, healthy support systems easily accessible
ERA: Any, but setting must feel inescapable

[SOCIOLINGUISTIC LAYER: Possessive Intensity]
DIALOGUE STYLE:
- Possessive declarations ("mine," "belong to me")
- Threats mixed with tenderness
- Obsessive questioning ("Who were you with?" "Why did you...")
- Vulnerable confessions buried in dominance
- Power imbalance clear in speech patterns
EXAMPLES:
✓ "You can't leave. I won't let you."
✓ "I'll destroy anyone who touches you."
✓ "Don't look at anyone else. Only me."
✓ "I know I'm broken, but you're the only thing that makes sense."
✗ Healthy communication
✗ Respectful boundaries (this is toxic by design)

[PROP DATABASE: Dark Romance]
RESTRAINT: Locked doors, grabbed wrists, caging against walls, chains (metaphorical or literal)
LUXURY: Expensive clothing, jewels, lavish rooms (gilded cage aesthetic)
POWER SYMBOLS: Contracts, family crests, weapons, ownership papers, branding/marking
EMOTIONAL OBJECTS: Broken items, blood (small amounts), tears, rain, shattered glass
INTIMATE: Bed scenes (non-explicit but clearly implied), close physical proximity, predatory spacing
DANGER: Shadows, isolation, no escape routes visible

[TROPE ENGINE: 50-Second Dark Romance]
SCENE 1-2: POWER DYNAMIC ESTABLISHED
- Protagonist trapped (physically or situationally)
- Possessive character's obsession immediately clear
- Dangerous attraction visible despite fear/resistance

SCENE 3-5: TWISTED INTIMACY
- Forced proximity revealing vulnerability
- Captor showing broken humanity beneath cruelty
- Protagonist's resistance warring with unwanted attraction

SCENE 6-7: BREAKING POINT
- Emotional or physical climax (intense but not explicit)
- Confession of twisted devotion
- Protagonist's submission, defiance, or complex acceptance

SCENE 8-10: DARK RESOLUTION
- Neither fully escapes the dynamic
- Final beat: Embracing toxicity, tragic separation, or complicated mutual obsession
- Ambiguous ending - uneasy, intense, unresolved

MANDATORY BEATS: Obsession, possession, dark devotion, moral ambiguity, intensity over health
FORBIDDEN: Healthy resolution, easy escape, pure villainy without complexity
CONTENT WARNING: Toxic dynamics, psychological intensity, dubious consent themes
""",

    "WORKPLACE_ROMANCE": """
=== NARRATIVE PLUGIN: Workplace Romance ===

[CHRONO-LOCK: Modern Corporate/Professional Setting]
ALLOWED TECH: Office computers, smartphones, coffee machines, printers, email, video calls
ALLOWED LOCATIONS: Office buildings, meeting rooms, break rooms, corporate cafes, business hotels, client sites, after-work bars
FORBIDDEN: Fantasy elements, school settings, historical tech
ERA: Present day (2020s professional environment)

[SOCIOLINGUISTIC LAYER: Professional-to-Personal Shift]
DIALOGUE STYLE:
- Formal/professional in work contexts
- Gradually warming to casual/intimate
- Office jargon mixed with personal care
- Struggle between professional boundaries and attraction
- Code-switching between colleague and romantic interest
EXAMPLES:
✓ "We need to discuss the report." [longing look]
✓ "You worked late again. Have you eaten?"
✓ "This is inappropriate. I'm your supervisor."
✓ "Forget the company. What do YOU want?"
✗ Immediate unprofessional behavior
✗ No acknowledgment of workplace complications

[PROP DATABASE: Workplace Romance]
OFFICE: Desks, computers, stacked files, coffee cups, office phones, conference tables
CLOTHING: Business suits, ties, heels, professional attire, loosened tie (classic move)
WORK ITEMS: Reports, presentations, contracts, business cards, name plates
AFTER-HOURS: Alcohol, dinner meetings, late-night office (empty building), rain-soaked suits
EMOTIONAL: Shared documents, working late together, office gossip in background
POWER SYMBOLS: Corner office vs cubicle, name on door, title differences

[TROPE ENGINE: 50-Second Workplace Romance]
SCENE 1-2: PROFESSIONAL TENSION
- Working late together or intense meeting
- Attraction fighting against professionalism
- Power dynamic visible (boss/subordinate, rivals, mentor/mentee)

SCENE 3-5: BOUNDARY BLUR
- Personal care breaking through professional facade
- Overtime moment turning intimate
- Realization of feelings beyond work

SCENE 6-7: CONFESSION/CRISIS
- Can't hide feelings anymore
- Risk to career/reputation acknowledged
- Choosing between professional safety and personal desire

SCENE 8-10: RISKY RESOLUTION
- Decision to pursue or walk away
- Final beat: Secret relationship beginning, public acknowledgment risk, or bittersweet separation
- Career vs love tension remains

MANDATORY BEATS: Professional tension, boundary conflict, career stakes, restrained desire
FORBIDDEN: Easy solutions, no consequences, unprofessional behavior without weight
""",

    "CHILDHOOD_FRIENDS_TO_LOVERS": """
=== NARRATIVE PLUGIN: Childhood Friends to Lovers ===

[CHRONO-LOCK: Modern or Flexible Timeline]
ALLOWED TECH: Depends on time period, but includes: old photos, childhood mementos, shared history markers
ALLOWED LOCATIONS: Hometown settings, childhood spots (park, school, old hangout), returning home scenarios
FORBIDDEN: Instant romance (undermines "friends first"), no shared history shown
ERA: Can span time - flashbacks to childhood, present-day reunion

[SOCIOLINGUISTIC LAYER: Familiar Comfort Shifting]
DIALOGUE STYLE:
- Casual, comfortable speech (no formality)
- Inside jokes and shared references
- Nicknames from childhood
- "When did you become..." realizations
- Fear of ruining friendship in confessions
EXAMPLES:
✓ "You still do that thing when you're nervous."
✓ "When did you get so... I mean, you look different."
✓ "We've been friends forever. I can't lose you."
✓ "It's always been you, hasn't it?"
✗ Formal speech between childhood friends
✗ No evidence of long history

[PROP DATABASE: Childhood Friends Romance]
NOSTALGIA: Old photos, childhood toys, yearbooks, shared mementos, familiar locations changed
COMFORT: Shared food habits, inside jokes visible in actions, worn comfortable clothes together
TIMELINE: Flashback indicators, "then vs now" parallels, growth markers
REALIZATION: Looking at them differently, noticing details, jealousy of others
FRIENDSHIP: Easy physical proximity, casual touch becoming charged, familiar routines disrupted
EMOTIONAL: Fear visible in risk-taking, comfort vs new tension

[TROPE ENGINE: 50-Second Friends-to-Lovers]
SCENE 1-2: SHIFT REALIZATION
- Start at moment of seeing friend "differently"
- Or jealousy scene (friend with someone else)
- Comfortable routine now charged with tension

SCENE 3-5: HISTORY WEIGHT
- Brief flashback showing long friendship
- "I can't risk this" internal conflict
- Small gestures now carrying new meaning

SCENE 6-7: CROSSING LINE
- Accidental intimate moment or deliberate confession
- "We can't go back after this"
- Fear vs desire, friendship vs more

SCENE 8-10: NEW CHAPTER
- Choosing to risk friendship for love
- Final beat: First kiss with history's weight, or pulling back in fear
- Either way, relationship forever changed

MANDATORY BEATS: Established history, comfort-to-tension shift, fear of losing friendship, deep knowledge
FORBIDDEN: Insta-love, no evidence of friendship, easy decision
"""
}

# Additional quick-format genre suggestions for 50-second webtoons:

ADDITIONAL_SHORT_FORM_GENRES = """
PERFECT FOR 50-SECOND FORMAT:

1. MISSED CONNECTION ROMANCE
   - Two people almost connecting, kept apart by timing/circumstance
   - High emotion, simple conflict, visual poetry

2. CONFESSION MOMENT
   - Pure confession scene with buildup and response
   - Intense emotion, clear stakes, satisfying beat

3. BREAKUP/MAKEUP
   - Relationship crisis to resolution
   - Dramatic tension, cathartic release

4. LOVE TRIANGLE CLIMAX
   - Choice moment between two people
   - Clear conflict, emotional weight, decisive moment

5. SECRET RELATIONSHIP REVEAL
   - Hidden relationship exposed or nearly exposed
   - Tension, risk, emotional stakes

6. REVENGE ENCOUNTER
   - Confrontation between betrayed and betrayer
   - Intense dialogue, power dynamics, catharsis

7. TIME-SKIP REUNION
   - Childhood friends/lovers meet after years
   - Nostalgia, changed dynamics, unresolved feelings

8. SOULMATE RECOGNITION
   - Moment of realizing "it's you"
   - Destiny feeling, emotional revelation, certainty

NOT RECOMMENDED FOR 50 SECONDS:
- Complex fantasy worldbuilding (too much setup)
- Multiple plotlines (confusing)
- Slow-burn anything (no time)
- Mystery with many clues (too rushed)
- Political intrigue (too complex)
"""



# ======================================================================================

# """
# Story Mood Modifiers

# These style modifiers are inserted into the story writer prompt to transform
# the narrative into different webtoon genres. Each mood has specific rules for
# setting translation, character design, visual aesthetic, and tone.
# """

# STORY_GENRE_PROMPTS = {
#     "NO_GENRE": """EMPTY
# """,

#     "MODERN_ROMANCE_DRAMA_MANHWA": """
# Generate a contemporary Korean romance drama story with the following narrative elements:
# - Setting: Modern urban Korea (Seoul cafes, corporate offices, university campuses, apartments)
# - Tone: Emotionally nuanced with bittersweet undertones, tender yet melancholic, slow-burn intimacy
# - Character archetypes: Complex professionals or students with hidden wounds, past traumas, or emotional barriers
# - Themes: Healing through connection, second chances, quiet longing, unspoken feelings, finding comfort in vulnerability
# - Conflict: Emotional distance vs growing attraction, fear of commitment, past relationships haunting present, social or career pressures interfering with love
# - Pacing: Slow, contemplative build-up with intimate everyday moments, gradual emotional revelation
# - Story beats: Chance encounters, shared quiet moments, misunderstandings rooted in fear, tender confessions, emotional breakthroughs
# - Mood: Soft melancholy mixed with hope, realistic relationship struggles, genuine emotional depth
# - Dialogue style: Subtle, layered with subtext, emotionally restrained yet deeply felt
# Create a story that captures the aching beauty of modern love with all its complications and quiet triumphs.
# """,

#     "FANTASY_ROMANCE_MANHWA": """
# Generate a fantasy romance story with magical academy or mystical world elements:
# - Setting: Enchanted academy, magical realm, or supernatural modern world with hidden magic
# - Tone: Whimsical yet emotionally charged, dreamy with underlying danger, romance intertwined with destiny
# - Character archetypes: Magically gifted protagonists with hidden powers or royal bloodlines, mysterious love interests with secrets, rivals-to-lovers dynamics
# - Themes: Forbidden love across magical hierarchies, destiny vs choice, power awakening through emotional bonds, sacrifice for love
# - Conflict: Magical threats requiring partnership, class or species divides, prophecies forcing difficult choices, dark forces threatening loved ones
# - Pacing: Balanced between romantic development and magical plot progression, alternating tender moments with dramatic reveals
# - Story beats: Magical awakening or discovery, forced proximity through quests or academy partnerships, near-death moments sparking confessions, climactic magical battles fueled by love
# - Mood: Enchanting and emotionally intense, sparkles and danger, passionate devotion within fantastical stakes
# - Dialogue style: Emotionally direct during pivotal moments, playful banter mixed with profound declarations
# Create a story where magic and romance are inseparably intertwined, where love itself becomes a power.
# """,

#     "HISTORY_SAGEUK_ROMANCE": """
# Generate a historical Korean period romance (Joseon era or historical dynasty setting):
# - Setting: Royal palaces, noble houses, historical villages, ancient Korea with strict social hierarchies
# - Tone: Deeply dramatic and tragic, passionate yet restrained by social conventions, intense forbidden longing
# - Character archetypes: Noble ladies, princes, royal guards, scholars, courtesans—all bound by duty and honor, star-crossed lovers from different social stations
# - Themes: Forbidden love vs duty, sacrifice for family or kingdom, love that transcends social barriers, tragic devotion, honor and passion in conflict
# - Conflict: Class divides, political intrigue threatening romance, forced marriages, family honor vs personal desire, dangerous court conspiracies
# - Pacing: Slow-burning tension with explosive emotional climaxes, weighted by historical formality and propriety
# - Story beats: Stolen glances during formal ceremonies, secret midnight meetings, politically motivated betrayals, desperate sacrifices, bittersweet or tragic endings with lasting impact
# - Mood: Heavy with longing and tragedy, sensual tension beneath formal restraint, raw emotional intensity within historical constraints
# - Dialogue style: Formal and poetic, heavy with subtext and unspoken emotion, declarations carry enormous weight
# Create a story of passionate, forbidden love set against the rigid beauty and danger of historical Korea.
# """,

#     "ACADEMY_SCHOOL_LIFE": """
# Generate a contemporary high school or university romance story:
# - Setting: Modern Korean school campus, classrooms, cafeterias, after-school clubs, neighborhoods near school
# - Tone: Sweet and wholesome with gentle emotional depth, youthful and hopeful, light-hearted with sincere feelings
# - Character archetypes: Relatable students—popular but kind, quiet and misunderstood, childhood friends, academic rivals, new transfer students
# - Themes: First love and self-discovery, friendship evolving into romance, overcoming insecurities together, finding courage to confess
# - Conflict: Social dynamics and peer pressure, academic competition, misunderstandings from inexperience, fear of ruining friendships, family expectations
# - Pacing: Episodic with gentle progression, everyday school life moments building gradually to emotional milestones
# - Story beats: Shared umbrella in rain, study sessions turning intimate, school festival confessions, protecting each other from bullies, awkward first dates
# - Mood: Innocent and tender, nostalgic warmth, gentle humor mixed with heartfelt sincerity
# - Dialogue style: Youthful and genuine, awkward yet endearing, emotionally honest in key moments
# Create a story capturing the pure, hopeful essence of young love blooming in the everyday magic of school life.
# """,

#     "ISEKAI_OTOME_FANTASY": """
# Generate an isekai otome fantasy romance story (reincarnation/transmigration into fantasy world or otome game):
# - Setting: Fantasy kingdom with nobility, magic, and otome game or novel-like world structure
# - Tone: Whimsical and romantic with comedic moments, self-aware and playful, dreamy wish-fulfillment balanced with genuine stakes
# - Character archetypes: Reincarnated protagonist with modern knowledge, charming princes or duke love interests, scheming villainess rivals, loyal knights, childhood friends with hidden feelings
# - Themes: Changing fate and rewriting destiny, modern wisdom in fantasy setting, earning love through genuine connection not game mechanics, found family and friendship
# - Conflict: Avoiding "bad endings" or original plot death flags, winning over capture targets authentically, rival characters and political schemes, balancing multiple love interests
# - Pacing: Lighthearted episodic adventures with romantic subplot progression, escalating stakes as protagonist changes the story
# - Story beats: Realization of transmigration, clever use of future knowledge, subverting expected plot points, collecting love interests through kindness, dramatic confrontations with original storyline, choosing true love
# - Mood: Playful and romantic, sparkling palace fantasy with comedic self-awareness, sweet multiple romantic routes converging
# - Dialogue style: Modern protagonist's inner monologue contrasting with formal fantasy speech, witty banter, heartfelt emotional confessions breaking through game-like scenarios
# Create a story of a modern soul navigating a fantasy romance world, finding real love while cleverly rewriting their destined fate.
# """,

#     "DARK_ROMANCE_REVENGE_MANHWA": """
# Generate a dark romance manhwa story infused with intense emotional stakes, explicit sexual scenes, and the following narrative elements:

# Setting: Opulent yet oppressive noble estates, decaying royal palaces, shadowy fantasy kingdoms, or modern elite circles tainted by power and secrets; environments that feel luxurious on the surface but suffocating underneath, often serving as backdrops for clandestine and heated intimate encounters
# Tone: Brooding, obsessive, and highly erotically charged with undercurrents of danger, bitterness, vengeance, and reluctant tenderness; raw passion mixed with pain, moral ambiguity, and vivid depictions of physical desire and consummation
# Character archetypes: Jaded protagonists scarred by betrayal, abuse, or loss (abandoned princesses, betrayed spouses, vengeful heirs, possessive anti-heroes); dominant, morally gray male leads who are ruthless yet fiercely protective, often expressing possession through intense sexual dominance; female leads who start broken or scheming but grow into empowered figures through desire, defiance, and exploratory sexual awakening
# Themes: Revenge through seduction or marriage, reclaiming power after humiliation via erotic empowerment, twisted obsession turning into genuine (if unhealthy) devotion, healing trauma through intense physical and emotional possession including BDSM-like dynamics, the blurred line between love and destruction, second chances born from ruin and amplified by passionate sexual bonds
# Conflict: Forced or predatory marriages/arrangements leading to coerced yet mutually addictive sexual encounters, past betrayals fueling vengeance through seductive games, possessive jealousy clashing with independence in bedroom power struggles, power imbalances and dominance/submission dynamics explored explicitly in intimate scenes, fear of vulnerability in toxic bonds revealed during moments of raw physical intimacy, external enemies or societal expectations threatening the fragile connection amid escalating erotic tensions
# Pacing: Deliberate escalation from cold calculation or hatred to consuming passion; slow-burn tension punctuated by explosive confrontations, intimate power plays, graphic sexual sequences, and moments of raw vulnerability
# Story beats: Bitter reunions or chance encounters laced with resentment and immediate sexual tension, revenge plots involving seduction or entrapment with detailed erotic manipulations, possessive claiming and marking (literal or emotional) through intense physical acts like biting or binding, breakdowns revealing hidden wounds during post-coital confessions, obsessive protection manifesting in jealous and dominant sexual reclaiming, multiple steamy yet psychologically charged encounters with explicit descriptions of foreplay, intercourse, and aftercare, eventual twisted redemption or mutual ruin-and-rebuild sealed by climactic passionate unions
# Mood: Heavy sensuality laced with melancholy and danger, intoxicating toxicity that feels addictive through vivid eroticism, moments of tender cruelty in sexual dominance, the thrill of forbidden or destructive desire culminating in cathartic orgasms, cathartic release after suffering via intense physical pleasure
# Dialogue style: Sharp, laced with subtext and taunts, possessive declarations during intimate moments, emotionally raw confessions hidden behind cruelty or whispered during sex, seductive threats promising pleasure and pain, restrained yet intense expressions of longing or rage escalating into explicit dirty talk

# Create a story that captures the intoxicating darkness of obsessive love, vengeful passion, and the destructive beauty of bonds forged in betrayal and desire, with frequent and detailed sexual scenes driving the emotional and narrative progression.
# """


#     "SMUT_FANTASY_ROMANCE": """
#     [NEED YOUR HELP HERE]
#     """

# "ANY EXTRA GENRE GOOD FOR 40 SECONDS WEBTOON"
# }