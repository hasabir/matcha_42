/**
 * Common passwords and dictionary words checker for frontend
 * Provides immediate feedback to users about password strength
 */

// Top common passwords
const COMMON_PASSWORDS = new Set([
  // Most common passwords
  "password", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
  "letmein", "trustno1", "dragon", "baseball", "111111", "iloveyou", "master",
  "sunshine", "ashley", "bailey", "passw0rd", "shadow", "123123", "654321",
  "superman", "qazwsx", "michael", "football", "welcome", "jesus", "ninja",
  "mustang", "password1", "123456789", "adobe123", "admin", "1234567890",
  
  // Common English words
  "hello", "world", "love", "secret", "happy", "friend", "summer", "winter",
  "spring", "autumn", "flower", "garden", "computer", "internet", "freedom",
  "princess", "starwars", "batman", "spiderman", "pokemon", "hello123",
  "welcome1", "admin123", "root", "user", "test", "guest", "demo",
  
  // Common patterns
  "qwertyuiop", "asdfghjkl", "zxcvbnm", "1q2w3e4r", "1qaz2wsx",
  "123qwe", "qwe123", "pass", "login", "changeme", "default",
]);

// Common dictionary words (subset)
const COMMON_WORDS = new Set([
  "about", "above", "accept", "account", "action", "active", "actually", "address",
  "after", "again", "against", "agent", "agree", "ahead", "allow", "almost",
  "alone", "along", "already", "also", "always", "amount", "analysis", "animal",
  "another", "answer", "anyone", "anything", "appear", "apply", "approach", "area",
  "argue", "around", "arrive", "article", "artist", "assume", "attack", "attention",
  "attorney", "audience", "author", "authority", "available", "avoid", "away", "baby",
  "back", "ball", "bank", "base", "beautiful", "because", "become", "before",
  "begin", "behavior", "behind", "believe", "benefit", "best", "better", "between",
  "beyond", "billion", "black", "blood", "blue", "board", "body", "book",
  "born", "both", "break", "bring", "brother", "budget", "build", "building",
  "business", "call", "camera", "campaign", "cancer", "candidate", "capital", "card",
  "care", "career", "carry", "case", "catch", "cause", "cell", "center",
  "central", "century", "certain", "certainly", "chair", "challenge", "chance", "change",
  "character", "charge", "check", "child", "choice", "choose", "church", "citizen",
  "city", "civil", "claim", "class", "clear", "clearly", "close", "coach",
  "cold", "collection", "college", "color", "come", "commercial", "common", "community",
  "company", "compare", "computer", "concern", "condition", "conference", "congress", "consider",
  "consumer", "contain", "continue", "control", "cost", "could", "country", "couple",
  "course", "court", "cover", "create", "crime", "cultural", "culture", "current",
  "customer", "dark", "data", "daughter", "dead", "deal", "death", "debate",
  "decade", "decide", "decision", "deep", "defense", "degree", "democratic", "describe",
  "design", "despite", "detail", "determine", "develop", "development", "difference", "different",
  "difficult", "dinner", "direction", "director", "discover", "discuss", "discussion", "disease",
  "doctor", "door", "down", "draw", "dream", "drive", "drop", "during",
  "each", "early", "east", "easy", "economic", "economy", "edge", "education",
  "effect", "effort", "eight", "either", "election", "else", "employee", "energy",
  "enjoy", "enough", "enter", "entire", "environment", "environmental", "especially", "establish",
  "even", "evening", "event", "ever", "every", "everybody", "everyone", "everything",
  "evidence", "exactly", "example", "executive", "exist", "expect", "experience", "expert",
  "explain", "face", "fact", "factor", "fail", "fall", "family", "famous",
  "father", "fear", "federal", "feel", "feeling", "field", "fight", "figure",
  "fill", "film", "final", "finally", "financial", "find", "fine", "finger",
  "finish", "fire", "firm", "first", "fish", "five", "floor", "focus",
  "follow", "food", "foot", "force", "foreign", "forget", "form", "former",
  "forward", "four", "free", "friend", "from", "front", "full", "fund",
  "future", "game", "garden", "general", "generation", "girl", "give", "glass",
  "goal", "good", "government", "great", "green", "ground", "group", "grow",
  "growth", "guess", "half", "hand", "hang", "happen", "happy", "hard",
  "have", "head", "health", "hear", "heart", "heat", "heavy", "help",
  "here", "herself", "high", "himself", "history", "hold", "home", "hope",
  "hospital", "hotel", "hour", "house", "however", "huge", "human", "hundred",
  "husband", "idea", "identify", "image", "imagine", "impact", "important", "improve",
  "include", "including", "increase", "indeed", "indicate", "individual", "industry", "information",
  "inside", "instead", "institution", "interest", "interesting", "international", "interview", "into",
  "investment", "involve", "issue", "item", "itself", "join", "just", "keep",
  "key", "kill", "kind", "kitchen", "know", "knowledge", "land", "language",
  "large", "last", "late", "later", "laugh", "lawyer", "lead", "leader",
  "learn", "least", "leave", "left", "legal", "less", "letter", "level",
  "life", "light", "like", "likely", "line", "list", "listen", "little",
  "live", "local", "long", "look", "lose", "loss", "love", "machine",
  "magazine", "main", "maintain", "major", "majority", "make", "management", "manager",
  "many", "market", "marriage", "material", "matter", "maybe", "mean", "measure",
  "media", "medical", "meet", "meeting", "member", "memory", "mention", "message",
  "method", "middle", "might", "military", "million", "mind", "minute", "miss",
  "mission", "model", "modern", "moment", "money", "month", "more", "morning",
  "most", "mother", "mouth", "move", "movement", "movie", "much", "music",
  "must", "myself", "name", "nation", "national", "natural", "nature", "near",
  "nearly", "necessary", "need", "network", "never", "news", "newspaper", "next",
  "nice", "night", "none", "north", "note", "nothing", "notice", "number",
  "occur", "offer", "office", "officer", "official", "often", "once", "only",
  "onto", "open", "operation", "opportunity", "option", "order", "organization", "other",
  "others", "outside", "over", "owner", "page", "pain", "painting", "paper",
  "parent", "part", "participant", "particular", "particularly", "partner", "party", "pass",
  "past", "patient", "pattern", "peace", "people", "perform", "performance", "perhaps",
  "period", "person", "personal", "phone", "physical", "pick", "picture", "piece",
  "place", "plan", "plant", "play", "player", "point", "police", "policy",
  "political", "politics", "poor", "popular", "population", "position", "positive", "possible",
  "power", "practice", "prepare", "present", "president", "pressure", "pretty", "prevent",
  "price", "private", "probably", "problem", "process", "produce", "product", "production",
  "professional", "professor", "program", "project", "property", "protect", "prove", "provide",
  "public", "pull", "purpose", "push", "quality", "question", "quickly", "quite",
  "race", "radio", "raise", "range", "rate", "rather", "reach", "read",
  "ready", "real", "reality", "realize", "really", "reason", "receive", "recent",
  "recently", "recognize", "record", "reduce", "reflect", "region", "relate", "relationship",
  "religious", "remain", "remember", "remove", "report", "represent", "Republican", "require",
  "research", "resource", "respond", "response", "responsibility", "rest", "result", "return",
  "reveal", "rich", "right", "rise", "risk", "road", "rock", "role",
  "room", "rule", "safe", "same", "save", "scene", "school", "science",
  "scientist", "score", "season", "seat", "second", "section", "security", "seek",
  "seem", "sell", "send", "senior", "sense", "series", "serious", "serve",
  "service", "seven", "several", "sexual", "shake", "share", "shoot", "short",
  "shot", "should", "shoulder", "show", "side", "sign", "significant", "similar",
  "simple", "simply", "since", "sing", "single", "sister", "site", "situation",
  "size", "skill", "skin", "small", "smile", "social", "society", "soldier",
  "some", "somebody", "someone", "something", "sometimes", "song", "soon", "sort",
  "sound", "source", "south", "southern", "space", "speak", "special", "specific",
  "speech", "spend", "sport", "spring", "staff", "stage", "stand", "standard",
  "star", "start", "state", "statement", "station", "stay", "step", "still",
  "stock", "stop", "store", "story", "strategy", "street", "strong", "structure",
  "student", "study", "stuff", "style", "subject", "success", "successful", "such",
  "suddenly", "suffer", "suggest", "summer", "support", "sure", "surface", "system",
  "table", "take", "talk", "task", "teach", "teacher", "team", "technology",
  "television", "tell", "tend", "term", "test", "than", "thank", "that",
  "their", "them", "themselves", "then", "theory", "there", "these", "they",
  "thing", "think", "third", "this", "those", "though", "thought", "thousand",
  "threat", "three", "through", "throughout", "throw", "thus", "time", "today",
  "together", "tonight", "total", "tough", "toward", "town", "trade", "traditional",
  "training", "travel", "treat", "treatment", "tree", "trial", "trip", "trouble",
  "true", "truth", "turn", "twelve", "twenty", "twice", "type", "under",
  "understand", "unit", "until", "upon", "usually", "value", "various", "very",
  "victim", "view", "violence", "visit", "voice", "vote", "wait", "walk",
  "wall", "want", "war", "watch", "water", "weapon", "wear", "week",
  "weight", "well", "west", "western", "what", "whatever", "when", "where",
  "whether", "which", "while", "white", "whole", "whom", "whose", "wide",
  "wife", "will", "wind", "window", "wish", "with", "within", "without",
  "woman", "wonder", "word", "work", "worker", "world", "worry", "would",
  "write", "writer", "wrong", "yard", "yeah", "year", "young", "your",
  "yourself", "zone"
]);

/**
 * Check if password contains common words or patterns
 * @param {string} password - The password to check
 * @returns {Object} - { isWeak: boolean, reason: string }
 */
export function isCommonPassword(password) {
  if (!password) {
    return { isWeak: false, reason: '' };
  }

  const passwordLower = password.toLowerCase();

  // Check if password is in common passwords list
  if (COMMON_PASSWORDS.has(passwordLower)) {
    return { isWeak: true, reason: 'This password is too common and easily guessed' };
  }

  // Check if password contains common dictionary words (3+ characters)
  for (const word of COMMON_WORDS) {
    if (word.length >= 3 && passwordLower.includes(word)) {
      return { isWeak: true, reason: `Password contains the common word "${word}"` };
    }
  }

  // Check for simple numeric patterns
  if (/^\d+$/.test(password)) {
    return { isWeak: true, reason: 'Password contains only numbers' };
  }

  // Check for simple alphabetic patterns
  if (/^[a-zA-Z]+$/.test(password)) {
    return { isWeak: true, reason: 'Password should contain numbers or special characters' };
  }

  // Check for keyboard patterns
  const keyboardPatterns = [
    'qwerty', 'asdfgh', 'zxcvbn', 'qwertyuiop', 'asdfghjkl',
    'zxcvbnm', '1234567890', '0987654321'
  ];

  for (const pattern of keyboardPatterns) {
    if (passwordLower.includes(pattern)) {
      return { isWeak: true, reason: `Password contains keyboard pattern "${pattern}"` };
    }
  }

  return { isWeak: false, reason: '' };
}

/**
 * Comprehensive password strength validation
 * @param {string} password - Password to validate
 * @param {string} username - Optional username to check similarity
 * @param {string} email - Optional email to check similarity
 * @returns {Object} - { isValid: boolean, error: string, strength: string }
 */
export function validatePasswordStrength(password, username = '', email = '') {
  if (!password) {
    return { isValid: false, error: 'Password is required', strength: 'none' };
  }

  // Length check
  if (password.length < 8) {
    return { isValid: false, error: 'Password must be at least 8 characters long', strength: 'weak' };
  }

  if (password.length > 128) {
    return { isValid: false, error: 'Password must be less than 128 characters', strength: 'weak' };
  }

  // Check against common passwords
  const { isWeak, reason } = isCommonPassword(password);
  if (isWeak) {
    return { isValid: false, error: reason, strength: 'weak' };
  }

  // Check if password contains username
  if (username && username.length >= 3) {
    if (password.toLowerCase().includes(username.toLowerCase())) {
      return { isValid: false, error: 'Password cannot contain your username', strength: 'weak' };
    }
  }

  // Check if password contains email local part
  if (email && email.includes('@')) {
    const emailLocal = email.split('@')[0];
    if (emailLocal.length >= 3 && password.toLowerCase().includes(emailLocal.toLowerCase())) {
      return { isValid: false, error: 'Password cannot contain your email', strength: 'weak' };
    }
  }

  // Character diversity checks
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password);

  const diversityCount = [hasUpper, hasLower, hasDigit, hasSpecial].filter(Boolean).length;

  if (diversityCount < 3) {
    return { 
      isValid: false, 
      error: 'Password must contain at least 3 of: uppercase, lowercase, numbers, special characters',
      strength: 'weak'
    };
  }

  // Determine strength
  let strength = 'medium';
  if (password.length >= 12 && diversityCount === 4) {
    strength = 'strong';
  } else if (password.length >= 10 && diversityCount >= 3) {
    strength = 'medium';
  }

  return { isValid: true, error: '', strength };
}

/**
 * Get password strength with visual indicator
 * @param {string} password - Password to check
 * @returns {Object} - { strength: string, color: string, message: string }
 */
export function getPasswordStrength(password) {
  if (!password) {
    return { strength: 'none', color: '#ccc', message: '' };
  }

  const { strength } = validatePasswordStrength(password);

  const strengthMap = {
    none: { color: '#ccc', message: '' },
    weak: { color: '#ff4444', message: 'Weak password' },
    medium: { color: '#ffaa00', message: 'Medium strength' },
    strong: { color: '#00cc66', message: 'Strong password' }
  };

  return { strength, ...strengthMap[strength] };
}
