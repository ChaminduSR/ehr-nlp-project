"""
Medical Dictionaries for Enhanced Regex Extraction (V2.1)

Comprehensive rheumatology terminology for improved entity extraction.
Supports 50+ medications, 50+ symptoms, 20+ diseases, and 30+ lab tests.

Version: 2.1
Accuracy Target: 85% F1 (up from 65% baseline)
"""

# ==============================================================================
# RHEUMATOLOGY MEDICATIONS (50+ drugs with brand names and abbreviations)
# ==============================================================================

DRUG_DICTIONARY = {
    # Disease-Modifying Antirheumatic Drugs (DMARDs)
    'methotrexate': ['methotrexate', 'MTX', 'rheumatrex', 'trexall', 'otrexup', 'rasuvo'],
    'sulfasalazine': ['sulfasalazine', 'azulfidine', 'SSZ', 'salazopyrin'],
    'leflunomide': ['leflunomide', 'arava', 'LEF'],
    'hydroxychloroquine': ['hydroxychloroquine', 'plaquenil', 'HCQ', 'quensyl'],
    'azathioprine': ['azathioprine', 'imuran', 'AZA', 'azasan'],
    'cyclosporine': ['cyclosporine', 'neoral', 'sandimmune', 'gengraf', 'CSA'],
    'mycophenolate': ['mycophenolate', 'cellcept', 'myfortic', 'MMF'],
    'cyclophosphamide': ['cyclophosphamide', 'cytoxan', 'CTX'],

    # Biologics - TNF Inhibitors
    'adalimumab': ['adalimumab', 'humira', 'ADA', 'amjevita', 'cyltezo'],
    'etanercept': ['etanercept', 'enbrel', 'ETN', 'erelzi', 'eticovo'],
    'infliximab': ['infliximab', 'remicade', 'IFX', 'inflectra', 'renflexis'],
    'certolizumab': ['certolizumab', 'cimzia', 'CZP'],
    'golimumab': ['golimumab', 'simponi', 'GLM'],

    # Biologics - Other Mechanisms
    'rituximab': ['rituximab', 'rituxan', 'RTX', 'truxima', 'ruxience'],
    'abatacept': ['abatacept', 'orencia', 'ABA'],
    'tocilizumab': ['tocilizumab', 'actemra', 'TCZ'],
    'sarilumab': ['sarilumab', 'kevzara', 'SAR'],
    'anakinra': ['anakinra', 'kineret', 'ANK'],
    'secukinumab': ['secukinumab', 'cosentyx', 'SEC'],
    'ixekizumab': ['ixekizumab', 'taltz', 'IXE'],
    'ustekinumab': ['ustekinumab', 'stelara', 'UST'],
    'guselkumab': ['guselkumab', 'tremfya', 'GUS'],

    # JAK Inhibitors
    'tofacitinib': ['tofacitinib', 'xeljanz', 'TOFA'],
    'baricitinib': ['baricitinib', 'olumiant', 'BARI'],
    'upadacitinib': ['upadacitinib', 'rinvoq', 'UPA'],

    # NSAIDs
    'ibuprofen': ['ibuprofen', 'advil', 'motrin', 'brufen', 'IBU', 'nurofen'],
    'naproxen': ['naproxen', 'aleve', 'naprosyn', 'NPX', 'anaprox'],
    'celecoxib': ['celecoxib', 'celebrex', 'CEL'],
    'indomethacin': ['indomethacin', 'indocin', 'INDO'],
    'diclofenac': ['diclofenac', 'voltaren', 'cataflam', 'DIC'],
    'meloxicam': ['meloxicam', 'mobic', 'MEL'],
    'piroxicam': ['piroxicam', 'feldene', 'PIR'],
    'ketorolac': ['ketorolac', 'toradol', 'KET'],
    'aspirin': ['aspirin', 'ASA', 'acetylsalicylic acid', 'ecotrin'],

    # Corticosteroids
    'prednisone': ['prednisone', 'pred', 'deltasone', 'rayos'],
    'prednisolone': ['prednisolone', 'prelone', 'orapred'],
    'methylprednisolone': ['methylprednisolone', 'medrol', 'solu-medrol', 'depo-medrol'],
    'dexamethasone': ['dexamethasone', 'decadron', 'dex'],
    'triamcinolone': ['triamcinolone', 'kenalog', 'aristocort'],
    'hydrocortisone': ['hydrocortisone', 'cortef', 'solu-cortef'],
    'betamethasone': ['betamethasone', 'celestone'],

    # Gout Medications
    'allopurinol': ['allopurinol', 'zyloprim', 'aloprim', 'ALLO'],
    'febuxostat': ['febuxostat', 'uloric', 'FEB'],
    'colchicine': ['colchicine', 'colcrys', 'mitigare', 'COL'],
    'probenecid': ['probenecid', 'probalan', 'PROB'],
    'pegloticase': ['pegloticase', 'krystexxa', 'PEG'],

    # Osteoporosis Medications (common in rheumatology)
    'alendronate': ['alendronate', 'fosamax', 'ALN'],
    'risedronate': ['risedronate', 'actonel', 'RIS'],
    'denosumab': ['denosumab', 'prolia', 'xgeva', 'DEN'],
}

# ==============================================================================
# RHEUMATOLOGY SYMPTOMS (50+ symptoms)
# ==============================================================================

SYMPTOM_PATTERNS = [
    # Pain
    'pain', 'ache', 'aching', 'tenderness', 'tender',
    'joint pain', 'arthralgia', 'myalgia', 'muscle pain',
    'back pain', 'neck pain', 'shoulder pain', 'hip pain', 'knee pain',
    'chest pain', 'abdominal pain',

    # Stiffness
    'stiffness', 'stiff', 'morning stiffness',
    'joint stiffness', 'spine stiffness',

    # Swelling and Inflammation
    'swelling', 'swollen', 'inflammation', 'inflamed',
    'joint swelling', 'synovitis', 'effusion',
    'edema', 'puffiness', 'boggy',

    # Systemic Symptoms
    'fever', 'febrile', 'pyrexia',
    'fatigue', 'tired', 'tiredness', 'exhaustion',
    'weakness', 'weak', 'malaise',
    'weight loss', 'cachexia',
    'night sweats',

    # Skin and Mucosal
    'rash', 'erythema', 'eruption',
    'malar rash', 'butterfly rash',
    'nodules', 'rheumatoid nodules', 'tophi',
    'ulcers', 'oral ulcers', 'mouth sores',
    'photosensitivity', 'sun sensitivity',
    'alopecia', 'hair loss',
    'purpura', 'petechiae',
    'livedo reticularis',

    # Raynaud's and Vascular
    'raynaud', 'raynauds', 'color changes',
    'digital ischemia', 'fingertip ulcers',

    # Sicca Symptoms
    'dry eyes', 'xerophthalmia', 'ocular dryness',
    'dry mouth', 'xerostomia', 'mouth dryness',
    'sicca symptoms', 'sicca syndrome',

    # Joint-Specific
    'deformity', 'deformed', 'subluxation',
    'ankylosis', 'fusion', 'bony fusion',
    'crepitus', 'creaking', 'grating',
    'limited range of motion', 'ROM limitation', 'decreased ROM',

    # Neurological
    'numbness', 'tingling', 'paresthesia',
    'headache', 'migraine',
]

# ==============================================================================
# RHEUMATIC DISEASES (20+ diseases and conditions)
# ==============================================================================

DISEASE_PATTERNS = [
    # Inflammatory Arthritis
    'rheumatoid arthritis', 'RA',
    'psoriatic arthritis', 'PsA', 'psoriatic', 'psoriasis',
    'ankylosing spondylitis', 'AS', 'axial spondyloarthritis', 'axSpA',
    'reactive arthritis', 'Reiter syndrome', 'reiters',
    'enteropathic arthritis',

    # Degenerative
    'osteoarthritis', 'OA', 'degenerative joint disease', 'DJD',
    'spondylosis', 'degenerative disc disease', 'DDD',

    # Connective Tissue Diseases
    'systemic lupus erythematosus', 'SLE', 'lupus',
    'scleroderma', 'systemic sclerosis', 'SSc',
    'sjogren syndrome', 'sjogrens', 'sicca syndrome',
    'mixed connective tissue disease', 'MCTD',
    'polymyositis', 'dermatomyositis', 'myositis',

    # Crystal Arthropathies
    'gout', 'gouty arthritis', 'tophaceous gout',
    'pseudogout', 'CPPD', 'calcium pyrophosphate',
    'chondrocalcinosis',

    # Vasculitis
    'vasculitis', 'arteritis',
    'giant cell arteritis', 'GCA', 'temporal arteritis',
    'polymyalgia rheumatica', 'PMR',
    'Takayasu arteritis', 'takayasus',
    'granulomatosis with polyangiitis', 'GPA', 'Wegeners', 'wegener',
    'microscopic polyangiitis', 'MPA',
    'eosinophilic granulomatosis with polyangiitis', 'EGPA', 'Churg-Strauss',
    'Henoch-Schonlein purpura', 'HSP', 'IgA vasculitis',
    'polyarteritis nodosa', 'PAN',

    # Other
    'fibromyalgia', 'fibro',
    'Still disease', 'adult-onset Still disease', 'AOSD',
    'Behcet disease', 'behcets',
    'sarcoidosis',
    'palindromic rheumatism',
]

# ==============================================================================
# LAB TESTS (30+ rheumatology-specific tests)
# ==============================================================================

LAB_TEST_PATTERNS = [
    # Inflammatory Markers
    'ESR', 'erythrocyte sedimentation rate', 'sed rate', 'sedimentation rate',
    'CRP', 'c-reactive protein', 'C reactive protein',

    # Rheumatoid Factor and Anti-CCP
    'RF', 'rheumatoid factor', 'rheum factor',
    'anti-CCP', 'anti-cyclic citrullinated peptide', 'ACCP', 'CCP antibodies',

    # Antinuclear Antibodies
    'ANA', 'antinuclear antibody', 'antinuclear antibodies',
    'anti-dsDNA', 'anti-double stranded DNA', 'dsDNA',
    'anti-Smith', 'anti-Sm', 'Smith antibody',
    'anti-RNP', 'RNP antibody',
    'anti-SSA', 'anti-Ro', 'Ro antibody', 'SSA',
    'anti-SSB', 'anti-La', 'La antibody', 'SSB',
    'anti-Scl-70', 'anti-topoisomerase', 'Scl-70',
    'anti-centromere', 'ACA', 'centromere antibodies',
    'anti-Jo-1', 'Jo-1 antibody',

    # HLA Typing
    'HLA-B27', 'HLA B27', 'B27',

    # Complement
    'complement', 'C3', 'C4', 'CH50', 'total complement',

    # Uric Acid
    'uric acid', 'UA', 'serum uric acid', 'serum urate',

    # ANCA
    'ANCA', 'antineutrophil cytoplasmic antibody',
    'c-ANCA', 'PR3', 'proteinase 3',
    'p-ANCA', 'MPO', 'myeloperoxidase',

    # Cryoglobulins
    'cryoglobulin', 'cryoglobulins', 'cryo',

    # Muscle Enzymes
    'CK', 'CPK', 'creatine kinase', 'creatine phosphokinase',
    'aldolase',

    # Renal Function (important in rheumatology)
    'creatinine', 'Cr', 'serum creatinine',
    'BUN', 'blood urea nitrogen',
    'GFR', 'eGFR', 'glomerular filtration rate',

    # Liver Function (monitoring DMARDs)
    'ALT', 'AST', 'transaminases', 'liver enzymes',
    'alkaline phosphatase', 'alk phos', 'ALP',

    # Complete Blood Count
    'CBC', 'complete blood count',
    'hemoglobin', 'hgb', 'Hb',
    'WBC', 'white blood cell', 'leukocyte',
    'platelet', 'PLT',
]

# ==============================================================================
# NEGATION MARKERS (Expanded from V2.1 research)
# ==============================================================================

NEGATION_MARKERS = [
    # Direct Negation
    r'\b(no|not|denies|denied|negative for|ruled out|without)\b',

    # Absence/Exclusion
    r'\b(absence of|free of|excludes?|excluding|absent)\b',

    # Clinical Negation
    r'\b(?:unremarkable|normal|negative|within normal limits|WNL)\b',

    # Past Negation (rarely/never had)
    r'(?:never|rarely)\s+(?:had|has|have)',

    # Denial Patterns
    r'denies?\s+(?:any|the)?\s*\b',

    # Rule Out
    r'\b(?:r/o|rule out|ruled out|ruling out)\b',
]

# ==============================================================================
# DOSAGE UNITS
# ==============================================================================

DOSAGE_UNITS = [
    'mg', 'mcg', 'g', 'kg',  # Mass
    'ml', 'l', 'cc',  # Volume
    'units', 'IU', 'international units',  # Units
    'mg/m2', 'mg/kg',  # Body surface area/weight
]

# ==============================================================================
# FREQUENCY PATTERNS
# ==============================================================================

FREQUENCY_PATTERNS = [
    # Times per day
    'once daily', 'twice daily', 'three times daily', 'four times daily',
    'QD', 'BID', 'TID', 'QID',
    'once a day', 'twice a day',

    # Weekly
    'weekly', 'once weekly', 'twice weekly',
    'once a week', 'twice a week',

    # Monthly
    'monthly', 'once monthly',
    'once a month',

    # As needed
    'PRN', 'as needed', 'as required',

    # Every X hours/days
    'every hour', 'every 4 hours', 'every 6 hours', 'every 8 hours', 'every 12 hours',
    'Q4H', 'Q6H', 'Q8H', 'Q12H',
    'every day', 'every other day',
]

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_all_drug_variants():
    """Get flattened list of all drug names and synonyms"""
    all_variants = []
    for canonical, synonyms in DRUG_DICTIONARY.items():
        all_variants.extend(synonyms)
    return all_variants


def get_canonical_drug_name(variant: str) -> str:
    """Get canonical drug name from any variant"""
    variant_lower = variant.lower()
    for canonical, synonyms in DRUG_DICTIONARY.items():
        if variant_lower in [s.lower() for s in synonyms]:
            return canonical
    return variant  # Return original if not found


def get_drug_synonyms(canonical_name: str) -> list:
    """Get all synonyms for a canonical drug name"""
    return DRUG_DICTIONARY.get(canonical_name, [])
