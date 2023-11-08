import random

charatereigenschaften = [
    "abenteuerlustig", "abgehoben", "abgeklärt", "abgestumpft", "absprachefähig", "absprechend", "abwägend", "abwartend", "abweisend", "abwesend", "achtsam", "affektiert", "affig", "aggressiv", "agil", "akkurat", "aktiv", "albern", "altklug", "altruistisch", "ambitioniert", "ambivalent", "amüsant", "anarchisch", "angeberisch", "angepasst", "angriffslustig", "angsteinflößend", "angstvoll", "anhänglich", "anpassungsfähig", "ansprechend", "anspruchslos", "anspruchsvoll", "anziehend", "arglistig", "arglos", "arrogant", "artig", "asketisch", "atemberaubend", "athletisch", "attraktiv", "aufbegehrend", "aufbrausend", "aufdringlich", "aufgedreht", "aufgeregt", "aufgeschlossen", "aufgeweckt", "aufhetzerisch", "aufmerksam", "aufmerksamkeitsbedürftig", "aufmüpfig", "aufrichtig", "aufsässig", "aufschneiderisch", "ausdauernd", "ausdruckslos", "ausfallend", "ausgeflippt", "ausgefuchst", "ausgeglichen", "ausgeklügelt", "ausländerfeindlich", "ausnutzbar", "autark", "authentisch", "autonom", "autoritär ",
    "bärbeißig", "barbarisch", "barmherzig", "bedacht", "bedächtig", "bedrohlich", "bedrückt", "bedürfnislos", "beeinflussbar", "befangen", "befehlerisch", "begabt", "begehrenswert", "begeistert", "begeisterungsfähig", "begierig", "begnügsam", "begriffsstutzig", "behämmert", "behaglich", "beharrlich", "behende", "beherrscht", "beherzt", "behutsam", "beirrbar", "bekloppt", "belastbar", "belebend", "bemüht", "bemutternd", "beneidenswert", "bequem", "berechnend", "beredsam", "bereichernd", "bescheiden", "besessen", "besitzergreifend", "besonnen", "besorgt", "bescheuert", "besserwissend", "besserwisserisch", "beständig", "bestechend", "bestechlich", "bestialisch", "bestimmend", "bestimmerisch", "betörend", "betriebsam", "betrügerisch", "bevormundend", "bewusst", "bezaubernd", "bigott", "bissig", "bizarr", "blasiert", "blass", "blauäugig", "blumig", "blutrünstig", "bockig", "bodenständig", "bösartig", "böse", "böswillig", "borniert", "borstenartig", "boshaft", "brav", "breitspurig", "brisant", "brummig", "brutal ", 
    "chaotisch", "charakterlos", "charakterstark", "charismatisch", "charmant", "chauvinistisch", "chevaleresk", "cholerisch", "clever", "couragiert ", 
    "dämlich", "damenhaft", "dankbar", "defensiv", "dekadent", "demütig", "depressiv", "derb", "despotisch", "destruktiv", "determinativ", "devot", "dezent", "dezidiert", "diabolisch", "dickhäutig", "dickköpfig", "diffus", "diktatorisch", "diplomatisch", "direkt", "diskret", "diskussionsfreudig", "distanziert", "distinguiert", "diszipliniert", "disziplinlos", "divenhaft", "dogmatisch", "doktrinär", "dominant", "doof", "drängend", "dramatisch", "dramatisierend", "draufgängerisch", "dreist", "dubios", "duckmäuserisch", "dünkelhaft", "dünnhäutig", "duldsam", "dumm", "durchblickend", "durcheinander", "durchschaubar", "durchschauend", "durchsetzungsstark", "durchtrieben", "dusslig", "dynamisch ", 
    "echt", "edel", "effizient", "effektiv", "egoistisch", "egoman", "egozentrisch", "ehrenhaft", "ehrenwert", "ehrfürchtig", "ehrgeizig", "ehrlich", "eifersüchtig", "eifrig", "eigen", "eigenbestimmt", "eigenbrödlerisch", "eigenmächtig", "eigennützig", "eigensinnig", "eigenständig", "eigenwillig", "einfach", "einfältig", "einfallslos", "einfallsreich", "einfühlsam", "eingebildet", "eingeschüchtert", "einladend", "einnehmend", "einsam", "einsatzbereit", "einschüchternd", "einseitig", "einsichtig", "eintönig", "einzelgängerisch", "einzigartig", "eisern", "eiskalt", "eitel", "ekelig", "elegant", "elitär", "eloquent", "emotional", "empathisch", "empfindlich", "empfindsam", "empfindungsvoll", "emsig", "energiegeladen", "energievoll", "energisch", "engagiert", "engstirnig", "entgegenkommend", "enthaltsam", "enthusiastisch", "entscheidungsfreudig", "entschieden", "entschlossen", "entspannt", "erbärmlich", "erbarmungslos", "erfahren", "erfinderisch", "erfolgsorientiert", "erfrischend", "ergeben", "erhaben", "ermutigend", "ernst", "ernsthaft", "erwartungsvoll", "exaltiert", "experimentierfreudig", "extravagant", "extrovertiert (extravertiert)", "exzentrisch ", 
    "facettenreich", "fachlich", "fair", "falsch", "familiär", "familienbewusst", "fantasielos", "fantasiereich", "fantasievoll", "fantastisch", "fatalistisch", "faul", "fehlerhaft", "feige", "fein", "feindselig", "feinfühlig", "feinsinnig", "feminin", "fesselnd", "feurig", "fidel", "fies", "flatterhaft", "fleissig", "fleißig", "flexibel", "flink", "folgsam", "fordernd", "forsch", "fotogen", "fragil", "frech", "freidenkend", "freiheitskämfend", "freiheitsliebend", "freimütig", "freizügig", "fremdbestimmend", "fremdbestimmt", "freudvoll", "freundlich", "friedfertig", "friedlich", "friedliebend", "friedlos", "friedselig", "friedvoll", "frigide", "frisch", "frivol", "fröhlich", "frohnatur", "frohsinnig", "fromm", "frostig", "fügsam", "fürsorglich", "furchtlos", "furchtsam", "furios ", 
    "galant", "gallig", "garstig", "gastfreundlich", "gebieterisch", "gebildet", "gebührend", "gedankenlos", "gedankenvoll", "gediegen", "geduldig", "gefährlich", "gefällig", "gefallsüchtig", "gefügig", "gefühllos", "gefühlsbetont", "gefühlsduselig", "gefühlskalt", "gefühlvoll", "gehässig", "geheimnisvoll", "gehemmt", "gehorsam", "geil", "geistreich", "geizig", "geladen", "gelassen", "geldgierig", "geltungssüchtig", "gemein", "gemütvoll", "genauigkeitsliebend", "generös", "genial", "genügsam", "gepflegt", "geradlinig", "gerecht", "gerechtigkeitsliebend", "gerissen", "gescheit", "geschickt", "geschmacklos", "geschmeidig", "geschwätzig", "gesellig", "gesprächig", "gesundheitsbewusst", "gewagt", "gewaltsam", "gewalttätig", "gewieft", "gewissenhaft", "gewissenlos", "gewitzt", "gewöhnlich", "gierig", "giftig", "gläubig", "glaubend", "glaubensstark", "gleichgültig", "gleichmütig", "glücklich", "gnadenlos", "gönnerhaft", "gottergeben", "gottesfürchtig", "gräßlich", "grantig", "grausam", "grazil", "griesgrämig", "grimmig", "grob", "grobschlächtig", "größenwahnsinnig", "großherzig", "großkotzig", "großmäulig", "großmütig", "großspurig", "großzügig", "grübelnd", "gründlich", "gütig", "gutgläubig", "gutherzig", "gutmütig ", 
    "haarspalterisch", "habgierig", "habsüchtig", "hämisch", "häuslich", "halsstarrig", "harmlos", "harmoniebedürftig", "harmoniesüchtig", "hart", "hartherzig", "hartnäckig", "hasenherzig", "hasserfüllt", "hedonistisch", "heimatverbunden", "heimtückisch", "heiß", "heiter", "hektisch", "heldenhaft", "heldenmütig", "hellhörig", "hemmungslos", "herablassend", "herausfordernd", "heroisch", "herrisch", "herrlich", "herrschsüchtig", "herzerfrischend", "herzlich", "herzlos", "hetzerisch", "heuchlerisch", "hibbelig", "hilflos", "hilfsbereit", "hingebungsvoll", "hinterfotzig", "hintergründig", "hinterhältig", "hinterlistig", "hinterwäldlerisch", "hirnrissig", "hitzig", "hitzköpfig", "hochbegabt", "hochfahrend", "hochmütig", "hochnäsig", "hochtrabend", "höflich", "höflichkeitsliebend", "homoist", "humorlos", "humorvoll", "hungrig", "hübsch", "hyperaktiv", "hyperkorrekt", "hypochondrisch", "hysterisch ", 
    "ichbezogen", "idealistisch", "ideenreich", "idiotisch", "ignorant", "impertinent", "impulsiv", "inbrünstig", "individualistisch", "infam", "infantil", "initiativ", "inkonsequent", "innovativ", "innovationsfreudig", "inspirierend", "instinktiv", "integer", "intelektuell", "intelligent", "interessiert", "intolerant", "intrigant", "introvertiert", "intuitiv", "ironisch", "irrational ", 
    "jähzornig", "jämmerlich", "jovial", "jugendlich", "jungfräulich ", 
    "kämpferisch", "kalkulierend", "kalt", "kaltblütig", "kaltherzig", "kaltschnäuzig", "kapriziös", "kasuistisch", "katzig", "kauzig", "keck", "ketzerisch", "keusch", "kinderfeindlich", "kinderlieb", "kindisch", "kindlich", "klar", "kleingeistig", "kleinkariert", "kleinlaut", "kleinlich", "kleinmütig", "kleptomanisch", "klug", "knallhart", "knickrig", "kokett", "kollegial", "kommunikationsfähig", "kommunikativ", "kompetent", "kompliziert", "kompromissbereit", "konfliktfreudig", "konfliktscheu", "konkret", "konsequent", "konservativ", "konsistent", "konstant", "kontaktarm", "kontaktfreudig", "kontraproduktiv", "kontrareligiös", "kontrolliert", "konziliant", "kooperativ", "kopflastig", "kordial", "korrekt", "korrupt", "kosmopolitisch", "kostspielig", "kräftig", "kraftvoll", "krank", "kratzbürstig", "kreativ", "kriecherisch", "kriegstreiberisch", "kriminell", "kritisch", "kritkfähig", "kühl", "kühn", "künstlerisch", "künstlich", "kulant", "kultiviert", "kumpelhaft", "kurios ", 
    "labil", "lachhaft", "lässig", "lahm", "lammfromm", "langmütig", "langsam", "larmoyant", "lasziv", "launisch", "laut", "lebendig", "lebensbejahend", "lebensfroh", "lebenslustig", "lebensmüde", "lebhaft", "leger", "leicht", "leichtfertig", "leichtfüßig", "leichtgläubig", "leichtsinnig", "leidenschaftlich", "leidlich", "leise", "leistungsbereit", "leistungsstark", "lernbereit", "lethargisch", "leutselig", "liberal", "lieb", "liebend", "liebenswert", "liebevoll", "lieblich", "lieblos", "link", "lisanne", "locker", "lösungsorientiert", "loyal", "lüstern", "lustlos", "lustvoll ", 
    "machtbesessen", "machtgierig", "machthaberisch", "machthungrig", "männerfeindlich", "männlich", "mager", "magisch", "manipulativ", "markant", "martialisch", "maskulin", "masochistisch", "maßlos", "materialistisch", "matriachalisch", "melancholisch", "memmenhaft", "menschenscheu", "menschenverachtend", "merkerisch", "merkwürdig", "mies", "mieslich", "mild", "militant", "mimosenhaft", "misanthropisch", "missgünstig", "missmutig", "misstrauisch", "mitfühlend", "mitleiderregend", "mitleidlos", "mitleidslos", "mitteilsam", "modisch", "mondän", "moralisch", "motivierend", "motiviert", "müde", "mürrisch", "mütterlich", "musikalisch", "mutig ", 
    "nachdenklich", "nachgiebig", "nachlässig", "nachsichtig", "nachtragend", "naiv", "narzisstisch", "natürlich", "naturfreudig", "naturverbunden", "negativ", "neiderfüllt", "neidisch", "nervig", "nervtötend", "nervös", "nett", "neugierig", "neurotisch", "neutral", "niedergeschlagen", "niederträchtig", "niedlich", "nihilistisch", "niveaulos", "nonchalant", "normal", "notgeil", "nüchtern ", 
    "oberflächlich", "objektiv", "offen", "offenherzig", "offensiv", "opportunistisch", "optimistisch", "ordentlich", "ordinär", "ordnungsfähig", "ordnungsliebend", "orientierungslos ", 
    "paranoid", "passiv", "patent", "paternalistisch", "patriotisch", "patriarchalisch", "pedantisch", "pejorativ", "penetrant", "penibel", "perfekt", "perfektionistisch", "pervers", "pessimistisch", "pfiffig", "pflegeleicht", "pflichtbewusst", "pflichtversessen", "phantasievoll", "philanthropisch", "phlegmatisch", "phobisch", "pingelig", "planlos", "plump", "poetisch", "polarisierend", "politisch", "positiv", "positiveeigenschaften", "präzise", "pragmatisch", "prinzipientreu", "problembewusst", "produktiv", "profilierungssüchtig", "progressiv", "prollig", "promiskuitiv", "prophetisch", "protektiv", "provokant", "prüde", "psychotisch", "pünktlich", "putzig ", 
    "quälend", "qualifiziert", "querdenkend", "quertreiberisch", "quicklebendig", "quirlig ", 
    "rabiat", "rachsüchtig", "radikal", "raffiniert", "rassistisch", "rastlos", "ratgebend", "rational", "ratlos", "ratsuchend", "rau", "reaktionär", "reaktionsschnell", "realistisch", "realitätsfremd", "rebellisch", "rechthaberisch", "rechtlos", "rechtschaffend", "redegewandt", "redelustig", "reflektiert", "rege", "reif", "reiselustig", "reizbar", "reizend", "reizvoll", "religiös", "renitent", "reserviert", "resigniert", "resolut", "respektlos", "respektvoll", "reudig", "reumütig", "rigoros", "risikofreudig", "robust", "romantisch", "routineorientiert", "rückgratlos", "rücksichtslos", "rücksichtsvoll", "rüde", "ruhelos", "ruhig", "ruppig ", 
    "sachlich", "sadistisch", "salopp", "sanft", "sanftmütig", "sanguinisch", "sardonisch", "sarkastisch", "sauertöpfisch", "saumselig", "schadenfroh", "schäbig", "schamlos", "scheinheilig", "scheu", "schlagfertig", "schlampig", "schlau", "schlussfolgernd", "schmeichelhaft", "schmierig", "schneidig", "schnell", "schnippisch", "schnoddrig", "schön", "schreckhaft", "schrullig", "schüchtern", "schullehrerhaft", "schusselig", "schwach", "schweigsam", "schwungvoll", "seicht", "selbstbeherrscht", "selbstbewusst", "selbstdarstellerisch", "selbstgefällig", "selbstgerecht", "selbstherrlich", "selbstkritisch", "selbstlos", "selbstreflektierend", "selbstsicher", "selbstständig", "selbstsüchtig", "selbstverliebt", "selbstzweifelnd", "seltsam", "senil", "sensationslüstern", "sensibel", "sensitiv", "sentimental", "seriös", "sexistisch", "sexsüchtig", "sicherheitsbedürftig", "sinnlich", "skeptisch", "skrupellos", "skurril", "smart", "solidarisch", "solide", "sonnig", "sorgfältig", "sorglos", "sorgsam", "souverän", "sozial", "sozialkompetent", "sparsam", "spaßig", "spießig", "spirituell", "spitzfindig", "spöttisch", "spontan", "sportlich", "sprachbegabt", "spritzig", "spröde", "sprunghaft", "stabil", "stachelig", "standhaft", "stark", "starr", "starrköpfig", "starrsinnig", "stereotypisch", "stilbewusst", "still", "stillos", "stilsicher", "stilvoll", "störend", "störrisch", "stoisch", "stolz", "strahlend", "strategisch", "streberhaft", "strebsam", "streitsüchtig", "streng", "strikt", "stürmisch", "stumpf", "stur", "sturköpfig", "subjektiv", "subtil", "suchend", "suchtgefährdet", "süchtig ", 
    "taff", "tagträumerisch", "taktisch", "taktlos", "taktvoll", "tatkräftig", "tatlos", "teamfähig", "temperamentlos", "temperamentvoll", "tiefgründig", "tierlieb", "töricht", "tolerant", "tollkühn", "tollpatschig", "tough", "träge", "träumerisch", "transparent", "treu", "treuherzig", "trödelich", "trotzig", "trübsinnig", "tüchtig", "tyrannisch ", 
    "ulkig", "umgänglich", "umsichtig", "umständlich", "umtriebig", "unabhängig", "unanständig", "unantastbar", "unartig", "unaufrichtig", "unausgeglichen", "unausstehlich", "unbedeutend", "unbeherrscht", "unbeirrbar", "unbelehrbar", "unberechenbar", "unbeschreiblich", "unbeschwert", "unbeständig", "unbeugsam", "undankbar", "undiszipliniert", "undurchschaubar", "undurchsichtig", "unehrlich", "uneigennützig", "uneinig", "unentschlossen", "unerbittlich", "unerreichbar", "unerschrocken", "unerschütterlich", "unerträglich", "unfair", "unfein", "unflätig", "unfolgsam", "unfreundlich", "ungeduldig", "ungehörig", "ungehorsam", "ungepflegt", "ungerecht", "ungeschickt", "ungesellig", "ungestüm", "ungewöhnlich", "ungezogen", "ungezügelt", "ungläubig", "unglaubwürdig", "unheimlich", "unhöflich", "unkompliziert", "unkonventionell", "unkonzentriert", "unmenschlich", "unnachgiebig", "unnahbar", "unordentlich", "unparteiisch", "unproblematisch", "unpünktlich", "unrealistisch", "unreflektiert", "unruhig", "unsachlich", "unscheinbar", "unschlüssig", "unschuldig", "unselbständig", "unsensibel", "unseriös", "unsicher", "unsichtbar", "unstet", "unterhaltsam", "unternehmungsfreudig", "unternehmungslustig", "unterstützend", "untertänig", "unterwürfig", "untreu", "unverschämt", "unverzagt", "unzufrieden", "unzuverlässig ", 
    "väterlich", "verachtend", "verärgert", "verantwortungsbewusst", "verantwortungslos", "verantwortungsvoll", "verbindlich", "verbissen", "verbittert", "verbohrt", "verbrecherisch", "verfressen", "verführerisch", "vergebend", "vergesslich", "verharrend", "verkopft", "verlässlich", "verlangend", "verlegen", "verletzbar", "verliebt", "verlogen", "verlustängstlich", "vermittelnd", "vernetzend", "vernünftig", "verräterisch", "verrucht", "verrückt", "versaut", "verschlagen", "verschlossen", "verschmitzt", "verschroben", "verschüchtert", "versessen", "verspielt", "verständnislos", "verständnisvoll", "verstört", "verträumt", "vertrauensvoll", "vertrauenswürdig", "verwahrlost", "verwegen", "verwirrt", "verwöhnt", "verwundert", "verzweifelt", "vielfältig", "vielschichtig", "vielseitig", "vital", "vorausschauend", "voreingenommen", "vorlaut", "vornehm", "vorsichtig", "vorwitzig ", 
    "wählerisch", "wagemutig", "waghalsig", "wahnhaft", "wahnsinnig", "wahnwitzig", "wahrhaftig", "wahrheitsliebend", "wankelmütig", "warm", "warmherzig", "wechselhaft", "wehmütig", "weiblich", "weich", "weinerlich", "weinselig", "weise", "weitsichtig", "weltfremd", "weltoffen", "wendig", "wichtigtuerisch", "widerlich", "widerspenstig", "widersprüchlich", "widerstandsfähig", "wild", "willenlos", "willensschwach", "willensstark", "willig", "willkürlich", "wissbegierig", "wissensdurstig", "witzig", "wohlerzogen", "wohlgesinnt", "wohlwollend", "wortkarg", "würdelos", "würdevoll", "wundervoll ", 
    "zäh", "zärtlich", "zaghaft", "zappelig", "zart", "zartbesaitet", "zartfühlend", "zauberhaft", "zaudernd", "zerbrechlich", "zerdenkend", "zerstörerisch", "zerstreut", "zickig", "zielbewusst", "ziellos", "zielorientiert", "zielstrebig", "zimperlich", "zögerlich", "züchtig", "zufrieden", "zugeknöpft", "zuhörend", "zukunftsgläubig", "zupackend", "zurechnungsfähig", "zurückhaltend", "zuverlässig", "zuversichtlich", "zuvorkommend", "zwanghaft", "zweifelnd", "zwiegespalten", "zwielichtig", "zwingend ", 
    "ängstlich", "ätzend", 
    "ökologisch", "ökonomisch", 
    "überdreht", "überemotional", "überfürsorglich", "übergenau", "überheblich", "überkandidelt", "überkritisch", "überlebensfähig", "überlegen", "überlegt", "übermütig", "überragend", "überraschend", "übersensibel", "überspannt", "überwältigend", "überzeugend"]

def get_random(start =None):
    if start is None:
        return random.choice(charatereigenschaften)
    else:
        return random.choice([eigenschaft for eigenschaft in charatereigenschaften if eigenschaft.startswith(start)])
    