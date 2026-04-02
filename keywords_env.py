"""
=============================================================================
ENVIRONMENTAL DISCLOSURE CLASSIFICATION SYSTEM
=============================================================================

      1. ENVIRONMENTAL_KEYWORDS  — trigger keywords (Step 1: sentence extraction)
      2. WORD_TYPE_1 (CHANGE_WORDS) — direction-of-movement words (e.g. reduced,
                                       declined, improved). These signal that an
                                       action or effect is being described.
      3. WORD_TYPE_2 (RESULT_WORDS) — outcome/achievement words (e.g. achieved,
                                       resulted, met). These confirm the event is
                                       a completed result, NOT merely a plan.
      4. SYMBOLIC_WORDS            — aspirational / forward-looking / vague words
                                       (e.g. committed, aims to, intends to, plan).
                                       Presence of these WITHOUT result words
                                       signals a symbolic disclosure.

=============================================================================
CLASSIFICATION LOGIC
=============================================================================

STEP 1 — Sentence Extraction
    Extract every sentence that contains ≥1 ENVIRONMENTAL_KEYWORD.
    These are the universe of "environmental disclosure sentences."

STEP 2 — Classify each extracted sentence:

    SUBSTANTIVE disclosure:
        A sentence is SUBSTANTIVE if it contains:
            (a) ≥1 ENVIRONMENTAL_KEYWORD  [topic anchor]
            AND
            (b) ≥1 WORD_TYPE_1 word       [direction of change, e.g. "reduced"]
            AND
            (c) ≥1 WORD_TYPE_2 word       [result confirmation, e.g. "achieved"]

        Rationale (Huq & Carling 2024, p.69):
            "If it is a result from an action, the information presented is
            substantive and thus exhibits accountability."
        Past-participle forms of Word Type 1 alone (e.g. "emissions were reduced")
        also qualify as substantive — they signal a completed action.
        Example SUBSTANTIVE:
            "CO2 emissions were reduced by 15 per cent and we achieved our
            annual reduction target."  → keyword ✓ + change word ✓ + result word ✓

    SYMBOLIC disclosure:
        A sentence is SYMBOLIC if it contains:
            (a) ≥1 ENVIRONMENTAL_KEYWORD  [topic anchor]
            AND
            (b) ≥1 SYMBOLIC_WORD          [aspiration / intention / future plan]
            AND
            (c) does NOT qualify as SUBSTANTIVE

        Rationale (Huq & Carling 2024, p.69):
            "Symbolic CSR reporting can be referred to as 'talks', for example,
            intentions and/or policies."
        Example SYMBOLIC:
            "We are committed to reducing our carbon footprint through sustainable
            practices."  → keyword ✓ + symbolic word ✓ (committed) + no result word

    MIXED (Symbolic + Substantive):
        A sentence contains both aspiration language AND outcome language.
        Example:
            "We are committed to reducing emissions and achieved a 20% reduction."

    NEUTRAL ENVIRONMENTAL:
        Contains ENVIRONMENTAL_KEYWORD but neither symbolic nor substantive
        markers — e.g. a sentence that merely defines scope or reports a raw
        figure with no directional language.

STEP 3 — Scoring per Report
    For each CSR report of firm i in year t:
        ACC_it   = count of SUBSTANTIVE sentences
        SYM_it   = count of SYMBOLIC sentences
        RATIO_it = ACC_it / (ACC_it + SYM_it)   [substantive share]
        DEN_it   = total_ENV_sentences / total_sentences  [GHG density proxy]

STEP 4 — Longitudinal Analysis (2000–2016)
    Aggregate yearly means of ACC, SYM, RATIO to track the shift.
    Sub-period comparisons:
        Pre-GRI G3  : 2000–2005
        GRI G3 era  : 2006–2012
        GRI G4 era  : 2013–2016

=============================================================================
"""

import re

# ============================================================
# 1. ENVIRONMENTAL TRIGGER KEYWORDS
#    Sentence must contain ≥1 of these to be included.
#    Scope: GHG/climate, energy, water, waste, biodiversity,
#           pollution — all environmental dimensions.
# ============================================================

ENVIRONMENTAL_KEYWORDS = [

    # --- GHG & Climate (core, from Huq & Carling 2024) ---
    'ghg', 'greenhouse gas', 'greenhouse gases',
    'carbon', 'co2', 'co₂', 'carbon dioxide',
    'emission', 'emissions', 'carbon emission', 'carbon emissions',
    'scope 1', 'scope 2', 'scope 3',
    'methane', 'ch4', 'nitrous oxide', 'n2o',
    'hydrofluorocarbon', 'hfc', 'hfcs',
    'perfluorocarbon', 'pfc', 'pfcs',
    'sulfur hexafluoride', 'sf6',
    'nitrogen trifluoride', 'nf3',
    'carbon footprint', 'carbon intensity',
    'tco2', 'tco2e', 'co2e', 'co2eq',
    'climate change', 'global warming', 'climate risk',
    'net zero', 'net-zero', 'carbon neutral', 'carbon neutrality',
    'decarbonisation', 'decarbonization', 'low carbon', 'low-carbon',
    'paris agreement', 'paris accord', 'kyoto protocol',
    'science based target', 'science-based target', 'sbti',
    'carbon offset', 'carbon offsets', 'carbon credit', 'carbon credits',
    'carbon trading', 'carbon market', 'carbon price', 'carbon pricing',
    'carbon capture', 'carbon sequestration', 'carbon sink',
    'climate target', 'climate goal', 'climate strategy',
    'climate resilience', 'climate adaptation', 'climate mitigation',
    'greenhouse effect', 'global temperature',

    # --- Energy ---
    'energy consumption', 'energy use', 'energy usage',
    'energy efficiency', 'energy intensity',
    'renewable energy', 'clean energy', 'green energy',
    'solar', 'solar energy', 'solar power', 'photovoltaic',
    'wind energy', 'wind power', 'wind turbine',
    'hydropower', 'hydroelectric',
    'geothermal',
    'biomass', 'biofuel', 'bioenergy',
    'fossil fuel', 'fossil fuels', 'coal consumption', 'natural gas consumption',
    'electricity consumption', 'electricity generation',
    'energy mix', 'energy transition',
    'power purchase agreement', 'ppa',
    'energy audit', 'energy management',
    'kwh', 'mwh', 'gwh', 'twh', 'gj', 'tj',

    # --- Water ---
    'water consumption', 'water use', 'water usage',
    'water withdrawal', 'water discharge', 'water recycling',
    'water efficiency', 'water intensity', 'water footprint',
    'water scarcity', 'water stress', 'water risk',
    'wastewater', 'effluent', 'water treatment',
    'freshwater', 'groundwater', 'surface water',
    'water stewardship', 'water management',
    'water pollution', 'water quality',
    'water target', 'water reduction',

    # --- Waste & Circular Economy ---
    'waste generation', 'waste produced', 'waste output',
    'waste reduction', 'waste diversion', 'waste management',
    'landfill', 'landfill diversion',
    'recycling rate', 'recycled material', 'recycled content',
    'hazardous waste', 'non-hazardous waste', 'toxic waste',
    'e-waste', 'electronic waste',
    'circular economy', 'circularity',
    'zero waste', 'zero-waste',
    'packaging waste', 'single-use plastic',
    'plastic waste', 'plastic reduction',
    'waste to energy', 'waste-to-energy',
    'tonnes of waste', 'tons of waste',

    # --- Biodiversity & Land Use ---
    'biodiversity', 'biodiversity loss', 'biodiversity impact',
    'ecosystem', 'ecosystems', 'ecosystem services',
    'deforestation', 'reforestation', 'afforestation',
    'habitat destruction', 'habitat restoration',
    'land use', 'land degradation', 'land restoration',
    'endangered species', 'protected species',
    'wetland', 'wetlands',
    'nature-based solution', 'nature-based solutions',
    'no net loss', 'net positive impact',

    # --- Air Pollution ---
    'air pollution', 'air quality',
    'nox', 'sox', 'particulate matter', 'pm2.5', 'pm10',
    'volatile organic compound', 'voc', 'vocs',
    'pollutant', 'pollutants',
    'spill', 'spills', 'oil spill',
    'soil contamination', 'soil pollution',

    # --- Environmental Performance / Reporting General ---
    'environmental performance', 'environmental impact',
    'environmental target', 'environmental goal', 'environmental objective',
    'environmental management', 'environmental strategy',
    'environmental report', 'environmental reporting',
    'environmental programme', 'environmental program',
    'lca', 'life cycle assessment', 'life-cycle assessment',
    'environmental footprint', 'ecological footprint',
    'ems', 'iso 14001', 'environmental management system',
    'sustainability report', 'csr report',
    'gri', 'global reporting initiative',
    'tcfd', 'task force on climate',
]


# ============================================================
# 2. WORD TYPE 1 — CHANGE / DIRECTION WORDS
#    These describe the effect (or expected effect) of an action.
#    Maps to Huq & Carling (2024) "word-type 1":
#    reduc*, cut*, declin*, drop*, lessen*, lower*,
#    increas*, ris*, improv*, etc.
#    Both SUBSTANTIVE and SYMBOLIC sentences may contain these.
# ============================================================

WORD_TYPE_1 = [
    # reduce / reduction
    'reduce', 'reduced', 'reducing', 'reduction', 'reductions',
    # decrease
    'decrease', 'decreased', 'decreasing',
    # lower
    'lower', 'lowered', 'lowering',
    # cut
    'cut', 'cutting', 'cuts',
    # drop
    'drop', 'dropped', 'dropping',
    # decline
    'decline', 'declined', 'declining',
    # lessen
    'lessen', 'lessened', 'lessening',
    # shrink
    'shrink', 'shrunk', 'shrinking',
    # increase (e.g. renewable energy increased)
    'increase', 'increased', 'increasing',
    # rise (e.g. recycling rate has risen)
    'rise', 'risen', 'rising',
    # improve
    'improve', 'improved', 'improving', 'improvement', 'improvements',
    # mitigate
    'mitigate', 'mitigated', 'mitigating', 'mitigation',
    # abate
    'abate', 'abated', 'abatement',
    # minimise / minimize
    'minimise', 'minimize', 'minimised', 'minimized', 'minimising', 'minimizing',
    # eliminate
    'eliminate', 'eliminated', 'eliminating', 'elimination',
    # phase out
    'phase out', 'phased out', 'phasing out',
    # divert (waste)
    'divert', 'diverted', 'diverting', 'diversion',
    # conserve
    'conserve', 'conserved', 'conserving', 'conservation',
    # save / saving (energy, water)
    'save', 'saved', 'saving', 'savings',
    # avoid (avoided emissions)
    'avoid', 'avoided', 'avoiding', 'avoidance',
    # prevent
    'prevent', 'prevented', 'preventing', 'prevention',
    # curb
    'curb', 'curbed', 'curbing',
    # limit
    'limit', 'limited', 'limiting',
    # offset
    'offset', 'offsetting', 'offsets',
    # transition (e.g. transitioned to renewable)
    'transition', 'transitioned', 'transitioning',
    # replace (fossil fuels replaced by renewables)
    'replace', 'replaced', 'replacing', 'replacement',
    # upgrade (energy upgrade)
    'upgrade', 'upgraded', 'upgrading',
    # retrofit
    'retrofit', 'retrofitted', 'retrofitting',
    # deploy (solar deployed)
    'deploy', 'deployed', 'deploying', 'deployment',
    # install (solar panels installed)
    'install', 'installed', 'installing', 'installation',
    # implement
    'implement', 'implemented', 'implementing', 'implementation',
    # adopt (adopted cleaner technology)
    'adopt', 'adopted', 'adopting', 'adoption',
    # scale up (renewable scaled up)
    'scale up', 'scaled up', 'scaling up',
    # expand (renewable energy expanded)
    'expand', 'expanded', 'expanding', 'expansion',
    # grow (renewable capacity grew)
    'grow', 'grew', 'growing',
    # embed
    'embed', 'embedded', 'embedding',
    # integrate
    'integrate', 'integrated', 'integrating', 'integration',
]


# ============================================================
# 3. WORD TYPE 2 — RESULT / OUTCOME WORDS
#    These confirm that an event is a COMPLETED RESULT,
#    NOT merely a plan or intention.
#    Maps to Huq & Carling (2024) "word-type 2":
#    resul*, achiev*, lead*, attain*
#    A sentence with WORD_TYPE_1 + WORD_TYPE_2 is SUBSTANTIVE.
# ============================================================

WORD_TYPE_2 = [
    # achieve / achieved
    'achieve', 'achieved', 'achieving', 'achievement', 'achievements',
    # attain
    'attain', 'attained', 'attaining', 'attainment',
    # result / resulted
    'result', 'resulted', 'resulting', 'results',
    # lead to / led to
    'lead', 'led', 'leading',
    # reach / reached
    'reach', 'reached', 'reaching',
    # meet / met (met our target)
    'meet', 'met', 'meeting',
    # fulfil
    'fulfil', 'fulfill', 'fulfilled', 'fulfilling', 'fulfilment', 'fulfillment',
    # accomplish
    'accomplish', 'accomplished', 'accomplishing', 'accomplishment',
    # succeed
    'succeed', 'succeeded', 'succeeding', 'success', 'successful', 'successfully',
    # deliver (delivered our target)
    'deliver', 'delivered', 'delivering', 'delivery',
    # demonstrate (demonstrated a reduction)
    'demonstrate', 'demonstrated', 'demonstrating', 'demonstration',
    # record (recorded a reduction)
    'record', 'recorded', 'recording',
    # verify
    'verify', 'verified', 'verifying', 'verification',
    # measure / measured (measured reduction)
    'measure', 'measured', 'measuring', 'measurement', 'measurements',
    # quantify
    'quantify', 'quantified', 'quantifying', 'quantification',
    # confirm
    'confirm', 'confirmed', 'confirming', 'confirmation',
    # validate
    'validate', 'validated', 'validating', 'validation',
    # certify
    'certify', 'certified', 'certifying', 'certification',
    # show / showed / shown
    'show', 'showed', 'shown', 'showing',
    # exceed (exceeded our target)
    'exceed', 'exceeded', 'exceeding',
    # surpass
    'surpass', 'surpassed', 'surpassing',
    # complete (completed the programme)
    'complete', 'completed', 'completing', 'completion',
    # calculate / calculated
    'calculate', 'calculated', 'calculating', 'calculation',
    # track / tracked
    'track', 'tracked', 'tracking',
    # report / reported (reported reduction)
    'report', 'reported', 'reporting',
    # disclose / disclosed
    'disclose', 'disclosed', 'disclosing', 'disclosure',
    # generate (generated savings)
    'generate', 'generated', 'generating',
    # on track (on track to meet)
    'on track',
    # cut (in past participle use, e.g. "emissions were cut by")
    'was cut', 'were cut',
    # fell / fallen (emissions fell)
    'fell', 'fallen', 'fall',
    # dropped (emissions dropped)
    'dropped',
    # reduced by (direct past-participle construction)
    'reduced by', 'decreased by', 'lowered by', 'cut by',
    'increased by', 'improved by', 'risen by', 'grown by',
]


# ============================================================
# 4. SYMBOLIC WORDS — aspirational / forward-looking / vague
#    Presence of these (with an ENV keyword but WITHOUT result
#    words) signals a SYMBOLIC disclosure.
#    Maps to Huq & Carling (2024): "talks — intentions and/or
#    policies."
# ============================================================

SYMBOLIC_WORDS = [
    # commit / commitment
    'commit', 'committed', 'committing', 'commitment', 'commitments',
    # aim / aims
    'aim', 'aims', 'aiming',
    # strive / striving
    'strive', 'striving', 'strives', 'striven',
    # intend / intention
    'intend', 'intends', 'intending', 'intention', 'intentions',
    # plan / planning
    'plan', 'planned', 'planning', 'plans',
    # endeavour
    'endeavour', 'endeavor', 'endeavouring', 'endeavoring',
    # aspire / aspiration
    'aspire', 'aspires', 'aspiring', 'aspiration', 'aspirations',
    # pledge
    'pledge', 'pledged', 'pledging', 'pledges',
    # seek / seeking
    'seek', 'seeks', 'seeking',
    # hope
    'hope', 'hopes', 'hoping',
    # believe / belief
    'believe', 'believes', 'believing', 'belief',
    # promote / promote (aspirational use)
    'promote', 'promotes', 'promoting', 'promotion',
    # encourage
    'encourage', 'encourages', 'encouraging',
    # foster
    'foster', 'fosters', 'fostering',
    # champion
    'champion', 'champions', 'championing',
    # advocate
    'advocate', 'advocates', 'advocating', 'advocacy',
    # prioritise / prioritize
    'prioritise', 'prioritize', 'prioritising', 'prioritizing',
    # focus on (aspirational)
    'focus on', 'focuses on', 'focusing on',
    # dedicated / dedication
    'dedicated to', 'dedication to',
    # vision / mission
    'vision', 'mission statement',
    # strategy (without delivery confirmation)
    'strategy', 'strategic plan',
    # policy / policies
    'policy', 'policies',
    # approach (general approach)
    'approach',
    # will reduce / will lower etc. (future tense)
    'will reduce', 'will decrease', 'will lower', 'will cut',
    'will improve', 'will increase', 'will eliminate',
    'will achieve', 'will reach', 'will meet',
    'will transition', 'will deploy', 'will install',
    'will implement', 'will adopt',
    # aim to / aims to
    'aim to', 'aims to', 'aiming to',
    # committed to (without delivery word)
    'committed to reducing', 'committed to lowering',
    'committed to improving', 'committed to achieving',
    'committed to eliminating', 'committed to cutting',
    # working towards
    'working towards', 'working toward',
    # striving to
    'striving to reduce', 'striving to improve',
    # intend to
    'intend to', 'intends to',
    # plan to
    'plan to', 'plans to', 'planning to',
    # expect to
    'expect to', 'expects to', 'expecting to',
    # hope to
    'hope to', 'hopes to',
    # continue to
    'continue to', 'continues to', 'continuing to',
    # looking to
    'looking to',
    # seeking to
    'seeking to',
    # goal / target / objective (without delivery)
    'goal', 'goals',
    'target', 'targets', 'set a target', 'set targets',
    'objective', 'objectives',
    # ambition
    'ambition', 'ambitions', 'ambitious',
    # milestone (forthcoming)
    'milestone', 'milestones',
    # roadmap
    'roadmap',
    # pathway
    'pathway', 'pathways',
    # recognise importance / recognize importance
    'recognise the importance', 'recognize the importance',
    # aware / awareness
    'aware of', 'awareness of',
    # in line with (policy alignment without delivery)
    'in line with',
    # in accordance with
    'in accordance with',
    # aligned with (aspiration alignment)
    'aligned with', 'alignment with',
    # remain committed
    'remain committed', 'remains committed',
    # on a journey
    'journey', 'on our journey',
    # moving towards
    'moving towards', 'moving toward',
    # work to reduce / work to improve
    'work to reduce', 'work to improve', 'work to lower',
]


# ============================================================
# 5. REGEX PATTERN COMPILATION
#    All patterns use lowercase matching.
#    Call .lower() on any sentence before applying.
# ============================================================

ENV_PAT      = re.compile('|'.join([re.escape(k) for k in ENVIRONMENTAL_KEYWORDS]),
                          re.IGNORECASE)

TYPE1_PAT    = re.compile(
    r'\b(?:' + '|'.join([re.escape(w) for w in WORD_TYPE_1]) + r')\b',
    re.IGNORECASE
)

TYPE2_PAT    = re.compile(
    r'\b(?:' + '|'.join([re.escape(w) for w in WORD_TYPE_2]) + r')\b',
    re.IGNORECASE
)

SYMBOLIC_PAT = re.compile(
    r'\b(?:' + '|'.join([re.escape(w) for w in SYMBOLIC_WORDS]) + r')\b',
    re.IGNORECASE
)

# Past-participle construction: e.g. "emissions were reduced", "carbon was cut"
# Catches substantive sentences where result word may be implicit in structure
PAST_PART_PAT = re.compile(
    r'\b(?:' + '|'.join([
        re.escape(w) for w in [
            'reduced', 'decreased', 'lowered', 'cut', 'dropped', 'declined',
            'improved', 'increased', 'risen', 'eliminated', 'diverted',
            'minimised', 'minimized', 'abated', 'avoided', 'offset',
            'phased out', 'replaced', 'installed', 'deployed', 'transitioned',
            'expanded', 'upgraded', 'retrofitted',
        ]
    ]) + r')\b',
    re.IGNORECASE
)


# ============================================================
# 6. CLASSIFICATION FUNCTIONS
# ============================================================

def has_environmental_keyword(sentence: str) -> bool:
    """Step 1: Does the sentence contain at least one environmental keyword?"""
    return bool(ENV_PAT.search(sentence))


def is_substantive(sentence: str) -> bool:
    """
    SUBSTANTIVE disclosure:
        ENV keyword + Word Type 1 (change) + Word Type 2 (result)
        OR
        ENV keyword + past-participle form of Word Type 1
        (e.g. "emissions were reduced by 15%")

    Reflects completed actions / achieved results.
    Huq & Carling (2024): word-type 1 + word-type 2 combinations,
    plus past-participle forms.
    """
    has_env   = bool(ENV_PAT.search(sentence))
    has_t1    = bool(TYPE1_PAT.search(sentence))
    has_t2    = bool(TYPE2_PAT.search(sentence))
    has_pp    = bool(PAST_PART_PAT.search(sentence))

    if not has_env:
        return False
    # Full combination: change word + result word
    if has_t1 and has_t2:
        return True
    # Past-participle alone implies completion (e.g. "emissions were reduced by 20%")
    if has_pp:
        return True
    return False


def is_symbolic(sentence: str) -> bool:
    """
    SYMBOLIC disclosure:
        ENV keyword + Symbolic word
        AND the sentence does NOT qualify as substantive.

    Reflects aspirations, plans, policies, intentions.
    Huq & Carling (2024): "symbolic CSR is ceremonial; mere 'talks'."
    """
    if not bool(ENV_PAT.search(sentence)):
        return False
    if not bool(SYMBOLIC_PAT.search(sentence)):
        return False
    # A sentence can be BOTH; we flag it separately — but pure symbolic
    # means it lacks result confirmation.
    return True


def classify_sentence(sentence: str) -> str:
    """
    Returns one of:
        'SUBSTANTIVE'  — completed action / result
        'SYMBOLIC'     — aspiration / intention / policy
        'MIXED'        — contains both substantive and symbolic markers
        'NEUTRAL_ENV'  — has ENV keyword but no classifying markers
        'NON_ENV'      — no environmental keyword found

    Priority rule:
        A sentence is MIXED only when it contains BOTH a strong symbolic
        marker (commitment / intention / future plan word) AND a confirmed
        result. Sentences where the only "symbolic" word is also used in
        substantive contexts (e.g. "target" used after "achieved") are
        classified as SUBSTANTIVE to avoid over-inflation of MIXED.
    """
    has_env = has_environmental_keyword(sentence)
    if not has_env:
        return 'NON_ENV'

    sub = is_substantive(sentence)

    # Only trigger MIXED / SYMBOLIC if a strong forward-looking word is present.
    # These are unambiguous intention markers — they cannot appear in a purely
    # substantive sentence.
    strong_symbolic = re.compile(
        r'\b(?:commit(?:ted|ment|ments)?|aim(?:s|ing)?|strive|striving|'
        r'intend(?:s|ing|ion|ions)?|plan(?:ned|ning|s)?|pledge(?:d|s)?|'
        r'endeavour|aspir(?:e|es|ing|ation|ations)?|seek(?:s|ing)?|'
        r'will\s+reduce|will\s+lower|will\s+cut|will\s+improve|'
        r'will\s+achieve|will\s+implement|working\s+towards?|'
        r'aim\s+to|aims\s+to|intend\s+to|plan\s+to|hope\s+to|'
        r'remain\s+committed|committed\s+to\s+\w+ing|'
        r'moving\s+towards?|on\s+our\s+journey|ambition|aspiration)\b',
        re.IGNORECASE
    )
    has_strong_sym = bool(strong_symbolic.search(sentence))

    if sub and has_strong_sym:
        return 'MIXED'
    if sub:
        return 'SUBSTANTIVE'
    if has_strong_sym or is_symbolic(sentence):
        return 'SYMBOLIC'
    return 'NEUTRAL_ENV'


def extract_environmental_sentences(text: str) -> list:
    """
    Tokenise text into sentences and return those containing
    at least one ENVIRONMENTAL_KEYWORD.
    Standard NLP pre-processing follows Huq & Carling (2024):
        1. Convert to lowercase
        2. Tokenise by sentence boundary
        3. Filter by keyword presence
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for s in sentences:
        for part in re.split(r'\n+', s):
            part = part.strip()
            if len(part) >= 15 and has_environmental_keyword(part):
                result.append(part)
    return result


def score_report(text: str) -> dict:
    """
    Score a single CSR report.
    Returns a dict with:
        total_sentences   : int
        env_sentences     : int
        substantive_count : int   (ACC_it in Huq & Carling 2024)
        symbolic_count    : int   (SYM_it)
        mixed_count       : int
        neutral_env_count : int
        density           : float (env_sentences / total_sentences)
        substantive_ratio : float (ACC / (ACC + SYM)), or None if denom=0
        symbolic_ratio    : float (SYM / (ACC + SYM)), or None if denom=0
    """
    all_sentences = re.split(r'(?<=[.!?])\s+', text)
    total = len(all_sentences)

    env_sents = extract_environmental_sentences(text)
    counts = {'SUBSTANTIVE': 0, 'SYMBOLIC': 0, 'MIXED': 0, 'NEUTRAL_ENV': 0}
    for s in env_sents:
        label = classify_sentence(s)
        if label in counts:
            counts[label] += 1

    acc = counts['SUBSTANTIVE'] + counts['MIXED']   # mixed has substantive element
    sym = counts['SYMBOLIC'] + counts['MIXED']       # mixed has symbolic element
    denom = acc + sym

    return {
        'total_sentences':   total,
        'env_sentences':     len(env_sents),
        'substantive_count': counts['SUBSTANTIVE'],
        'symbolic_count':    counts['SYMBOLIC'],
        'mixed_count':       counts['MIXED'],
        'neutral_env_count': counts['NEUTRAL_ENV'],
        'density':           round(len(env_sents) / total, 4) if total > 0 else 0,
        'substantive_ratio': round(acc / denom, 4) if denom > 0 else None,
        'symbolic_ratio':    round(sym / denom, 4) if denom > 0 else None,
    }


# ============================================================
# 7. QUICK TEST
# ============================================================

if __name__ == '__main__':

    test_cases = [
        
        ("CO2 emissions were reduced by 15% and we achieved our annual reduction target.",
         "SUBSTANTIVE"),
        ("Water consumption decreased by 20%, resulting in attainment of our 2020 goal.",
         "SUBSTANTIVE"),
        ("Waste sent to landfill was cut by 30 tonnes and we successfully delivered our zero-waste target.",
         "SUBSTANTIVE"),
        ("Renewable energy increased to 60% of our mix and we met our science-based target.",
         "SUBSTANTIVE"),
        ("Our energy intensity declined by 12%, confirming the success of our efficiency programme.",
         "SUBSTANTIVE"),
        ("GHG emissions fell by 8% in 2015 compared to the 2010 baseline.",
         "SUBSTANTIVE"),
        ("Carbon emissions were reduced by 28.7 percent since 2005 and we are on track to achieve the 35% reduction.",
         "SUBSTANTIVE"),

        # --- SYMBOLIC (aspirations, plans, intentions) ---
        ("We are committed to reducing our carbon footprint through sustainable practices.",
         "SYMBOLIC"),
        ("The company aims to improve water efficiency and strives for responsible stewardship.",
         "SYMBOLIC"),
        ("We intend to reduce GHG emissions in line with the Kyoto Protocol.",
         "SYMBOLIC"),
        ("Our goal is to achieve net zero carbon by 2050 through a phased transition.",
         "SYMBOLIC"),
        ("We will reduce our energy consumption and plan to install solar panels by 2020.",
         "SYMBOLIC"),
        ("The company is committed to minimising its environmental impact and promoting sustainability.",
         "SYMBOLIC"),
        ("We are working towards a low-carbon economy and remain committed to our climate strategy.",
         "SYMBOLIC"),

        # --- MIXED --- 
        ("We are committed to reducing emissions and achieved a 20% reduction in our carbon footprint.",
         "MIXED"),
        ("The company plans to eliminate waste to landfill and has already diverted 80% in 2015.",
         "MIXED"),
    ]

    print("=" * 90)
    print(f"{'SENTENCE':<60} {'EXPECTED':<14} {'RESULT':<14} {'MATCH'}")
    print("=" * 90)
    correct = 0
    for sentence, expected in test_cases:
        result = classify_sentence(sentence)
        match = "✓" if result == expected else "✗"
        if result == expected:
            correct += 1
        print(f"{sentence[:58]:<60} {expected:<14} {result:<14} {match}")

    print("=" * 90)
    print(f"Accuracy: {correct}/{len(test_cases)} ({100*correct//len(test_cases)}%)")
    print()
    print(f"Total ENVIRONMENTAL keywords : {len(ENVIRONMENTAL_KEYWORDS)}")
    print(f"Total Word Type 1 (change)   : {len(WORD_TYPE_1)}")
    print(f"Total Word Type 2 (result)   : {len(WORD_TYPE_2)}")
    print(f"Total Symbolic words         : {len(SYMBOLIC_WORDS)}")
    print()

    # --- Demo: score a mini-report ---
    sample_report = """
    We are committed to reducing our greenhouse gas emissions and aim to achieve net zero by 2050.
    In 2015, our CO2 emissions were reduced by 12 per cent compared to the 2010 baseline, and we met our annual carbon target.
    Water consumption decreased by 8 per cent and we achieved our water efficiency goal for the year.
    The company plans to install solar panels across all facilities by 2018.
    Waste sent to landfill was cut by 25 tonnes, resulting in attainment of our zero-waste objective.
    We remain committed to our low-carbon strategy and will continue to improve our environmental performance.
    Energy intensity declined by 6 per cent, demonstrating the success of our energy management programme.
    """
    print("--- Sample Report Scoring ---")
    scores = score_report(sample_report)
    for k, v in scores.items():
        print(f"  {k:<25}: {v}")
