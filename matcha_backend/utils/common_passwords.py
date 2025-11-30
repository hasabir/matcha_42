"""
Common passwords and dictionary words checker
Used to prevent users from using weak, easily guessable passwords
"""

# Top 100 most common passwords and dictionary words
COMMON_PASSWORDS = {
    # Most common passwords
    "password", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
    "letmein", "trustno1", "dragon", "baseball", "111111", "iloveyou", "master",
    "sunshine", "ashley", "bailey", "passw0rd", "shadow", "123123", "654321",
    "superman", "qazwsx", "michael", "football", "welcome", "jesus", "ninja",
    "mustang", "password1", "123456789", "adobe123", "admin", "1234567890",
    
    # Common English words that make weak passwords
    "hello", "world", "love", "secret", "happy", "friend", "summer", "winter",
    "spring", "autumn", "flower", "garden", "computer", "internet", "freedom",
    "princess", "starwars", "batman", "spiderman", "pokemon", "hello123",
    "welcome1", "admin123", "root", "user", "test", "guest", "demo",
    
    # Common patterns
    "qwertyuiop", "asdfghjkl", "zxcvbnm", "1q2w3e4r", "1qaz2wsx",
    "123qwe", "qwe123", "pass", "login", "changeme", "default",
    
    # Common names and words
    "charlie", "thomas", "jordan", "andrew", "daniel", "jennifer", "jessica",
    "matthew", "joshua", "amanda", "austin", "hunter", "william", "chelsea",
    "mother", "father", "sister", "brother", "family", "friends",
    
    # Numbers and simple patterns
    "12345", "123", "1234", "000000", "696969", "666666", "999999"
}

# Common dictionary words (subset - in production, use a larger list)
COMMON_WORDS = {
    "about", "above", "abuse", "accept", "accident", "account", "across", "action",
    "active", "actor", "adult", "advice", "affair", "affect", "afford", "afraid",
    "after", "again", "against", "agency", "agent", "agree", "ahead", "alarm",
    "album", "alcohol", "alive", "allow", "almost", "alone", "along", "already",
    "always", "amount", "animal", "annual", "another", "answer", "anyone", "anything",
    "anyway", "appeal", "appear", "apple", "apply", "approach", "argue", "arise",
    "around", "arrive", "artist", "aside", "asser", "asset", "assist", "assume",
    "attack", "attempt", "attend", "attract", "author", "average", "avoid", "award",
    "aware", "badly", "balance", "barely", "battle", "beach", "beauty", "become",
    "before", "begin", "behind", "being", "belief", "believe", "belong", "below",
    "benefit", "better", "between", "beyond", "black", "blame", "blood", "board",
    "bottom", "brain", "branch", "brave", "bread", "break", "breast", "breath",
    "bridge", "brief", "bright", "bring", "broad", "broken", "brother", "brown",
    "budget", "build", "burden", "bureau", "business", "button", "buyer", "camera",
    "campus", "cancer", "canvas", "capable", "capacity", "capital", "captain", "capture",
    "carbon", "career", "careful", "carrier", "carry", "catch", "cause", "ceiling",
    "center", "central", "century", "certain", "chain", "chair", "challenge", "chamber",
    "chance", "change", "channel", "chapter", "character", "charge", "charity", "chart",
    "chase", "cheap", "check", "cheese", "chest", "chicken", "chief", "child",
    "china", "choice", "choose", "church", "circle", "citizen", "claim", "class",
    "classic", "clean", "clear", "client", "climate", "climb", "close", "cloud",
    "coach", "coast", "coffee", "collapse", "collect", "college", "colonial", "color",
    "column", "combine", "comfort", "command", "comment", "commerce", "common", "community",
    "company", "compare", "compete", "complain", "complete", "complex", "computer", "concern",
    "concrete", "conduct", "conflict", "congress", "connect", "consider", "consist", "constant",
    "construct", "consult", "consumer", "contain", "content", "context", "continue", "contract",
    "contrast", "control", "convert", "convince", "cooking", "corner", "correct", "cotton",
    "could", "council", "counter", "country", "county", "couple", "courage", "course",
    "court", "cousin", "cover", "crack", "craft", "crash", "crazy", "cream",
    "create", "creature", "credit", "crime", "crisis", "critic", "cross", "crowd",
    "crucial", "cruise", "culture", "current", "customer", "cycle", "daily", "damage",
    "dance", "danger", "darkness", "database", "daughter", "dealer", "death", "debate",
    "decade", "decide", "decision", "declare", "decline", "defeat", "defend", "define",
    "degree", "delay", "deliver", "demand", "democracy", "demonstrate", "denial", "depend",
    "DepOsit", "depression", "depth", "deputy", "derive", "describe", "desert", "deserve",
    "design", "desire", "destroy", "detail", "detect", "determine", "develop", "device",
    "devote", "dialogue", "differ", "difference", "different", "difficult", "digital", "dimension",
    "dinner", "direct", "director", "disappear", "disaster", "discipline", "discourse", "discover",
    "discuss", "disease", "dismiss", "disorder", "display", "dispute", "distance", "distant",
    "distinct", "distinguish", "distribute", "district", "diverse", "divide", "division", "doctor",
    "document", "domestic", "dominant", "dominate", "double", "doubt", "dozen", "draft",
    "dragon", "drama", "dramatic", "draw", "drawing", "dream", "dress", "drink",
    "drive", "driver", "during", "eager", "early", "earth", "easily", "eastern",
    "economic", "economy", "editor", "educate", "education", "effect", "effective", "efficiency",
    "effort", "eight", "either", "elderly", "elect", "election", "electric", "element",
    "eliminate", "elite", "email", "embrace", "emerge", "emergency", "emotion", "emphasis",
    "empire", "employ", "employee", "employer", "empty", "enable", "encounter", "encourage",
    "enemy", "energy", "enforce", "engage", "engine", "engineer", "enhance", "enjoy",
    "enormous", "enough", "ensure", "enter", "enterprise", "entire", "entrance", "entry",
    "environment", "episode", "equal", "equally", "equipment", "error", "escape", "especially",
    "essay", "essential", "establish", "estate", "estimate", "ethnic", "evaluate", "evening",
    "event", "eventually", "every", "everybody", "everyday", "everyone", "everything", "everywhere",
    "evidence", "evolution", "exact", "exactly", "examine", "example", "exceed", "excellent",
    "except", "exception", "exchange", "exciting", "executive", "exercise", "exhibit", "exist",
    "existence", "existing", "expand", "expansion", "expect", "expense", "expensive", "experience",
    "experiment", "expert", "explain", "explanation", "explode", "explore", "export", "expose",
    "express", "expression", "extend", "extension", "extensive", "extent", "external", "extra",
    "extraordinary", "extreme", "fabric", "facility", "factor", "factory", "faculty", "failure",
    "fairly", "faith", "false", "familiar", "family", "famous", "fantasy", "farmer",
    "fashion", "father", "favor", "favorite", "feature", "federal", "feeling", "fellow",
    "female", "fence", "fewer", "fiber", "fiction", "field", "fifteen", "fifth",
    "fifty", "fight", "fighter", "figure", "finally", "finance", "financial", "finding",
    "finger", "finish", "first", "fishing", "fitness", "flash", "flavor", "fleet",
    "flesh", "flight", "float", "floor", "flower", "focus", "follow", "football",
    "force", "foreign", "forest", "forever", "forget", "formal", "formation", "former",
    "formula", "forth", "fortune", "forward", "found", "foundation", "founder", "fourth",
    "frame", "freedom", "freeze", "French", "frequency", "frequent", "fresh", "friend",
    "front", "fruit", "frustration", "fully", "function", "fundamental", "funding", "funeral",
    "funny", "furniture", "furthermore", "future", "galaxy", "gallery", "garden", "garlic",
    "gather", "gender", "general", "generate", "generation", "genetic", "genius", "genre",
    "gentle", "gentleman", "gently", "ghost", "giant", "given", "glass", "global",
    "golden", "gospel", "govern", "government", "governor", "grace", "grade", "gradually",
    "graduate", "grain", "grand", "grandfather", "grandmother", "grant", "grass", "grave",
    "great", "greatest", "green", "grocery", "ground", "group", "growing", "growth",
    "guarantee", "guard", "guess", "guest", "guide", "guideline", "guilty", "guitar",
    "habit", "handle", "happen", "happy", "harbor", "hardly", "health", "healthy",
    "heart", "heaven", "heavy", "height", "hello", "helpful", "heritage", "herself",
    "hidden", "highlight", "highly", "highway", "himself", "historic", "historical", "history",
    "holder", "holiday", "homeless", "honest", "honor", "horse", "hospital", "hotel",
    "house", "household", "housing", "however", "huge", "human", "humor", "hundred",
    "hungry", "hunter", "hurry", "husband", "hypothesis", "ideal", "identify", "identity",
    "ignore", "illegal", "illness", "illustrate", "image", "imagine", "immediate", "immigrant",
    "impact", "implement", "implication", "imply", "importance", "important", "impose", "impossible",
    "impress", "impression", "improve", "improvement", "incident", "include", "income", "incorporate",
    "increase", "increasingly", "incredible", "indeed", "independence", "independent", "index", "Indian",
    "indicate", "individual", "industrial", "industry", "infant", "infection", "inflation", "influence",
    "inform", "information", "ingredient", "initial", "initially", "initiative", "injury", "inner",
    "innocent", "inquiry", "inside", "insight", "insist", "inspire", "install", "instance",
    "instead", "institution", "institutional", "instruction", "instructor", "instrument", "insurance", "intellectual",
    "intelligence", "intend", "intense", "intention", "interaction", "interest", "interested", "interesting",
    "internal", "international", "internet", "interpret", "interpretation", "intervention", "interview", "introduce",
    "introduction", "invasion", "invest", "investigate", "investigation", "investment", "investor", "invite",
    "involve", "involved", "involvement", "Irish", "island", "isolate", "issue", "Italian",
    "itself", "jacket", "jail", "Japanese", "joint", "journal", "journalist", "journey",
    "judge", "judgment", "juice", "jump", "junior", "jury", "justice", "justify",
    "keeper", "kitchen", "knife", "knock", "knowledge", "label", "labor", "laboratory",
    "labour", "ladder", "lady", "landscape", "language", "large", "largely", "laser",
    "later", "Latin", "latter", "laugh", "launch", "lawyer", "layer", "lead",
    "leader", "leadership", "leading", "league", "learn", "learning", "least", "leather",
    "leave", "lecture", "left", "legacy", "legal", "legend", "legislation", "legislative",
    "legislator", "legitimate", "lemon", "length", "lesson", "letter", "level", "liberal",
    "library", "license", "lifestyle", "lifetime", "light", "likely", "limit", "limitation",
    "limited", "linear", "linguistic", "lipid", "liquid", "listen", "literally", "literary",
    "literature", "little", "living", "lobby", "local", "locate", "location", "logic",
    "lonely", "long", "look", "loose", "lord", "lose", "loss", "lost",
    "lovely", "lover", "lower", "luck", "lucky", "lunch", "luxury", "machine",
    "magazine", "magic", "magnetic", "magnitude", "maintain", "maintenance", "major", "majority",
    "maker", "makeup", "male", "manage", "management", "manager", "manner", "manufacturer",
    "manufacturing", "many", "margin", "marine", "mark", "market", "marketing", "marriage",
    "married", "marry", "mask", "mass", "massive", "master", "match", "mate",
    "material", "math", "matter", "maximum", "maybe", "mayor", "meal", "meaning",
    "means", "meanwhile", "measure", "measurement", "meat", "mechanism", "media", "medical",
    "medication", "medicine", "medium", "meet", "meeting", "member", "membership", "memory",
    "mental", "mention", "menu", "mere", "merely", "mess", "message", "metal",
    "meter", "method", "Mexican", "middle", "might", "mighty", "military", "milk",
    "million", "mind", "mine", "minister", "minor", "minority", "minute", "miracle",
    "mirror", "miss", "missile", "mission", "mistake", "model", "moderate", "modern",
    "modest", "moment", "money", "monitor", "month", "mood", "moon", "moral",
    "more", "moreover", "morning", "mortgage", "most", "mostly", "mother", "motion",
    "motivate", "motivation", "motor", "mount", "mountain", "mouse", "mouth", "move",
    "movement", "movie", "much", "multiple", "murder", "muscle", "museum", "music",
    "musical", "musician", "must", "mutual", "myself", "mystery", "myth", "naked",
    "name", "narrative", "narrow", "nation", "national", "native", "natural", "naturally",
    "nature", "near", "nearby", "nearly", "necessarily", "necessary", "neck", "need",
    "negative", "negotiate", "negotiation", "neighbor", "neighborhood", "neither", "nerve", "nervous",
    "network", "never", "nevertheless", "newly", "news", "newspaper", "next", "nice",
    "night", "nine", "nobody", "noise", "nominate", "none", "nonetheless", "normal",
    "normally", "north", "northern", "nose", "note", "nothing", "notice", "notion",
    "novel", "nowhere", "nuclear", "number", "numerous", "nurse", "object", "objective",
    "obligation", "observation", "observe", "observer", "obtain", "obvious", "obviously", "occasion",
    "occasionally", "occupation", "occupy", "occur", "ocean", "offense", "offensive", "offer",
    "office", "officer", "official", "often", "okay", "once", "ongoing", "onion",
    "online", "only", "onto", "open", "opening", "operate", "operating", "operation",
    "operator", "opinion", "opponent", "opportunity", "oppose", "opposite", "opposition", "option",
    "orange", "order", "ordinary", "organic", "organization", "organize", "orientation", "origin",
    "original", "originally", "other", "others", "otherwise", "ought", "ourselves", "outcome",
    "outside", "oven", "over", "overall", "overcome", "overlook", "owe", "owner",
    "pace", "pack", "package", "page", "pain", "painful", "paint", "painter",
    "painting", "pair", "pale", "palm", "panel", "pant", "paper", "parent",
    "park", "parking", "part", "participant", "participate", "participation", "particular", "particularly",
    "partly", "partner", "partnership", "party", "pass", "passage", "passenger", "passion",
    "past", "patch", "path", "patient", "pattern", "pause", "payment", "peace",
    "peak", "peer", "penalty", "people", "pepper", "perceive", "percent", "percentage",
    "perception", "perfect", "perfectly", "perform", "performance", "perhaps", "period", "permanent",
    "permission", "permit", "person", "personal", "personality", "personally", "personnel", "perspective",
    "persuade", "pet", "phase", "phenomenon", "philosophy", "phone", "photo", "photograph",
    "photographer", "phrase", "physical", "physically", "physician", "piano", "pick", "picture",
    "piece", "pile", "pilot", "pine", "pink", "pipe", "pitch", "place",
    "plan", "plane", "planet", "planning", "plant", "plastic", "plate", "platform",
    "play", "player", "please", "pleasure", "plenty", "plot", "plus", "pocket",
    "poem", "poet", "poetry", "point", "pole", "police", "policy", "political",
    "politically", "politician", "politics", "poll", "pollution", "pool", "poor", "popular",
    "population", "porch", "port", "portion", "portrait", "portray", "pose", "position",
    "positive", "possess", "possibility", "possible", "possibly", "post", "pot", "potato",
    "potential", "potentially", "pound", "pour", "poverty", "powder", "power", "powerful",
    "practical", "practice", "pray", "prayer", "precisely", "predict", "prefer", "preference",
    "pregnancy", "pregnant", "preparation", "prepare", "prescription", "presence", "present", "presentation",
    "preserve", "president", "presidential", "press", "pressure", "pretend", "pretty", "prevent",
    "previous", "previously", "price", "pride", "priest", "primarily", "primary", "prime",
    "principal", "principle", "print", "prior", "priority", "prison", "prisoner", "privacy",
    "private", "probably", "problem", "procedure", "proceed", "process", "produce", "producer",
    "product", "production", "profession", "professional", "professor", "profile", "profit", "program",
    "progress", "project", "prominent", "promise", "promote", "prompt", "proof", "proper",
    "properly", "property", "proportion", "proposal", "propose", "proposed", "prosecutor", "prospect",
    "protect", "protection", "protein", "protest", "proud", "prove", "provide", "provider",
    "province", "provision", "psychological", "psychologist", "psychology", "public", "publication", "publicly",
    "publish", "publisher", "pull", "punishment", "purchase", "pure", "purpose", "pursue",
    "push", "qualify", "quality", "quarter", "quarterback", "queen", "question", "quick",
    "quickly", "quiet", "quietly", "quit", "quite", "quote", "race", "racial",
    "radical", "radio", "rail", "rain", "raise", "range", "rank", "rapid",
    "rapidly", "rare", "rarely", "rate", "rather", "rating", "ratio", "rational",
    "reach", "react", "reaction", "read", "reader", "reading", "ready", "real",
    "reality", "realize", "really", "reason", "reasonable", "recall", "receive", "recent",
    "recently", "recipe", "recognition", "recognize", "recommend", "recommendation", "record", "recording",
    "recover", "recovery", "recruit", "reduce", "reduction", "refer", "reference", "reflect",
    "reflection", "reform", "refugee", "refuse", "regard", "regarding", "regardless", "regime",
    "region", "regional", "register", "regular", "regularly", "regulate", "regulation", "reinforce",
    "reject", "relate", "relation", "relationship", "relative", "relatively", "relax", "release",
    "relevant", "relief", "religion", "religious", "rely", "remain", "remaining", "remarkable",
    "remember", "remind", "remote", "remove", "repeat", "repeatedly", "replace", "reply",
    "report", "reporter", "represent", "representation", "representative", "Republican", "reputation", "request",
    "require", "requirement", "research", "researcher", "resemble", "reservation", "reserve", "resident",
    "resist", "resistance", "resolution", "resolve", "resort", "resource", "respect", "respond",
    "respondent", "response", "responsibility", "responsible", "rest", "restaurant", "restore", "restriction",
    "result", "retain", "retire", "retirement", "return", "reveal", "revenue", "review",
    "revolution", "rhythm", "rice", "rich", "ride", "rifle", "right", "ring",
    "rise", "risk", "river", "road", "rock", "role", "roll", "romantic",
    "roof", "room", "root", "rope", "rose", "rough", "roughly", "round",
    "route", "routine", "royal", "rub", "rule", "running", "rural", "rush",
    "Russian", "sacred", "safe", "safety", "sake", "salad", "salary", "sale",
    "sales", "salt", "same", "sample", "sanction", "sand", "satellite", "satisfaction",
    "satisfy", "sauce", "save", "saving", "scale", "scandal", "scared", "scenario",
    "scene", "schedule", "scheme", "scholar", "scholarship", "school", "science", "scientific",
    "scientist", "scope", "score", "scream", "screen", "script", "sculpture", "search",
    "season", "seat", "second", "secret", "secretary", "section", "sector", "secure",
    "security", "seek", "seem", "segment", "seize", "select", "selection", "self",
    "sell", "seller", "semester", "semi", "senate", "senator", "send", "senior",
    "sense", "sensitive", "sentence", "separate", "sequence", "series", "serious", "seriously",
    "serve", "service", "session", "settle", "settlement", "seven", "several", "severe",
    "sexual", "shade", "shadow", "shake", "shall", "shape", "share", "sharp",
    "shatter", "shed", "sheet", "shelf", "shell", "shelter", "shift", "shine",
    "ship", "shirt", "shock", "shoe", "shoot", "shooting", "shop", "shopping",
    "shore", "short", "shortly", "shot", "should", "shoulder", "shout", "show",
    "shower", "shrug", "shut", "sick", "side", "sigh", "sight", "sign",
    "signal", "significance", "significant", "significantly", "silence", "silent", "silver", "similar",
    "similarly", "simple", "simply", "since", "sing", "singer", "single", "sink",
    "sister", "site", "situation", "sixth", "size", "sketch", "skill", "skin",
    "skirt", "skull", "slightly", "slip", "slow", "slowly", "small", "smart",
    "smell", "smile", "smoke", "smooth", "snap", "snow", "so", "so-called",
    "soccer", "social", "society", "soft", "software", "soil", "solar", "soldier",
    "solid", "solution", "solve", "some", "somebody", "somehow", "someone", "something",
    "sometimes", "somewhat", "somewhere", "song", "soon", "sophisticated", "sorry", "sort",
    "soul", "sound", "soup", "source", "south", "southern", "Soviet", "space",
    "Spanish", "speak", "speaker", "special", "specialist", "species", "specific", "specifically",
    "speech", "speed", "spend", "spending", "spin", "spirit", "spiritual", "split",
    "spokesman", "sport", "spot", "spread", "spring", "square", "squeeze", "stability",
    "stable", "staff", "stage", "stair", "stake", "stand", "standard", "standing",
    "star", "stare", "start", "state", "statement", "station", "statistics", "status",
    "stay", "steady", "steal", "steel", "steep", "steer", "stem", "step",
    "stick", "still", "stir", "stock", "stomach", "stone", "stop", "storage",
    "store", "storm", "story", "straight", "strange", "stranger", "strategic", "strategy",
    "stream", "street", "strength", "strengthen", "stress", "stretch", "strike", "string",
    "strip", "stroke", "strong", "strongly", "structure", "struggle", "student", "studio",
    "study", "stuff", "stupid", "style", "subject", "submit", "subsequent", "substance",
    "substantial", "succeed", "success", "successful", "successfully", "such", "sudden", "suddenly",
    "sue", "suffer", "sufficient", "sugar", "suggest", "suggestion", "suicide", "suit",
    "summer", "summit", "super", "supply", "support", "supporter", "suppose", "supposed",
    "Supreme", "sure", "surely", "surface", "surgery", "surprise", "surprised", "surprising",
    "surprisingly", "surround", "survey", "survival", "survive", "survivor", "suspect", "sustain",
    "swear", "sweep", "sweet", "swim", "swing", "switch", "symbol", "symptom",
    "system", "table", "tablespoon", "tactic", "tail", "take", "tale", "talent",
    "talk", "tall", "tank", "tape", "target", "task", "taste", "teach",
    "teacher", "teaching", "team", "tear", "teaspoon", "technical", "technique", "technology",
    "teen", "teenager", "telephone", "telescope", "television", "tell", "temperature", "temporary",
    "tend", "tendency", "tennis", "tension", "tent", "term", "terms", "terrible",
    "territory", "terror", "terrorism", "terrorist", "test", "testify", "testimony", "testing",
    "text", "than", "thank", "thanks", "that", "theater", "their", "them",
    "theme", "themselves", "then", "theory", "therapy", "there", "therefore", "these",
    "they", "thick", "thin", "thing", "think", "thinking", "third", "thirty",
    "this", "those", "though", "thought", "thousand", "threat", "threaten", "three",
    "throat", "through", "throughout", "throw", "thus", "ticket", "tight", "time",
    "tiny", "tired", "tissue", "title", "tobacco", "today", "together", "tomato",
    "tomorrow", "tone", "tongue", "tonight", "tool", "tooth", "topic", "toss",
    "total", "totally", "touch", "tough", "tour", "tourist", "tournament", "toward",
    "towards", "tower", "town", "trace", "track", "trade", "tradition", "traditional",
    "traffic", "tragedy", "trail", "train", "training", "transfer", "transform", "transformation",
    "transition", "translate", "transmission", "transport", "transportation", "travel", "treat", "treatment",
    "treaty", "tree", "tremendous", "trend", "trial", "tribe", "trick", "trip",
    "troop", "trouble", "truck", "true", "truly", "trust", "truth", "tube",
    "tunnel", "turn", "twelve", "twenty", "twice", "twin", "type", "typical",
    "typically", "ugly", "ultimate", "ultimately", "unable", "uncle", "under", "undergo",
    "understand", "understanding", "unfortunately", "uniform", "union", "unique", "unit", "universal",
    "universe", "university", "unknown", "unless", "unlike", "unlikely", "until", "unusual",
    "upon", "upper", "urban", "urge", "used", "useful", "user", "usual",
    "usually", "utility", "vacation", "valley", "valuable", "value", "variable", "variation",
    "variety", "various", "vary", "vast", "vegetable", "vehicle", "venture", "version",
    "versus", "very", "vessel", "veteran", "victim", "victory", "video", "view",
    "viewer", "village", "violate", "violation", "violence", "violent", "virtually", "virtue",
    "virus", "visible", "vision", "visit", "visitor", "visual", "vital", "voice",
    "volume", "volunteer", "vote", "voter", "wage", "wait", "wake", "walk",
    "wall", "wander", "want", "warm", "warn", "warning", "wash", "waste",
    "watch", "water", "wave", "way", "weak", "wealth", "wealthy", "weapon",
    "wear", "weather", "wedding", "week", "weekend", "weekly", "weigh", "weight",
    "welcome", "welfare", "well", "west", "western", "what", "whatever", "wheel",
    "when", "whenever", "where", "whereas", "whether", "which", "while", "whisper",
    "white", "whole", "whom", "whose", "wide", "widely", "widespread", "wife",
    "wild", "will", "willing", "wind", "window", "wine", "wing", "winner",
    "winter", "wipe", "wire", "wisdom", "wise", "wish", "with", "withdraw",
    "within", "without", "witness", "woman", "wonder", "wonderful", "wood", "wooden",
    "word", "work", "worker", "working", "works", "workshop", "world", "worried",
    "worry", "worse", "worst", "worth", "would", "wound", "wrap", "write",
    "writer", "writing", "wrong", "yard", "yeah", "year", "yell", "yellow",
    "yesterday", "yield", "young", "your", "yours", "yourself", "youth", "zone"
}

def is_common_password(password):
    """
    Check if password is a common password or contains common dictionary words.
    
    Args:
        password: The password string to check
        
    Returns:
        tuple: (is_weak, reason) where is_weak is boolean and reason is explanation
    """
    if not password:
        return False, ""
    
    password_lower = password.lower()
    
    # Check if password is in the common passwords list
    if password_lower in COMMON_PASSWORDS:
        return True, "This password is too common and easily guessed"
    
    # Check if password contains common dictionary words (3+ characters)
    for word in COMMON_WORDS:
        if len(word) >= 3 and word in password_lower:
            return True, f"Password contains the common word '{word}'"
    
    # Check for simple numeric patterns
    if password.isdigit():
        return True, "Password contains only numbers"
    
    # Check for simple alphabetic patterns
    if password.isalpha():
        return True, "Password should contain numbers or special characters"
    
    # Check for keyboard patterns
    keyboard_patterns = [
        "qwerty", "asdfgh", "zxcvbn", "qwertyuiop", "asdfghjkl",
        "zxcvbnm", "1234567890", "0987654321"
    ]
    for pattern in keyboard_patterns:
        if pattern in password_lower:
            return True, f"Password contains keyboard pattern '{pattern}'"
    
    return False, ""


def validate_password_strength(password, username=None, email=None):
    """
    Comprehensive password strength validation.
    
    Args:
        password: Password to validate
        username: Optional username to check similarity
        email: Optional email to check similarity
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    # Length check
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check against common passwords
    is_weak, reason = is_common_password(password)
    if is_weak:
        return False, reason
    
    # Check if password contains username
    if username and len(username) >= 3:
        if username.lower() in password.lower():
            return False, "Password cannot contain your username"
    
    # Check if password contains email local part
    if email and '@' in email:
        email_local = email.split('@')[0]
        if len(email_local) >= 3 and email_local.lower() in password.lower():
            return False, "Password cannot contain your email"
    
    # Character diversity checks
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    
    diversity_count = sum([has_upper, has_lower, has_digit, has_special])
    
    if diversity_count < 3:
        return False, "Password must contain at least 3 of: uppercase, lowercase, numbers, special characters"
    
    return True, "Password is strong"
