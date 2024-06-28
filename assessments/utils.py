ASSESSMENT_DOMAINS: dict[str, dict[int, list[str]]] = {
    "Financiën": {
        1: ["groeiende complexe schulden"],
        2: [
            "beschikt niet over vrij besteedbaar inkomen of groeiende schulden door spontaan of ongepast uitgeven"
        ],
        3: [
            "beschikt over vrij besteedbaar inkomen van ouders zonder verantwoordelijkheid voor noodzakelijke behoeften (zak geld)",
            "eventuele schulden zijn stabiel of zijn onder beheer",
        ],
        4: [
            "beschikt over vrij besteedbaar inkomen van ouders met enige verantwoordelijkheid voor noodzakelijke behoeften (zakgeld, en kleed-/lunchgeld)",
            "gepast uitgeven",
            "eventuele schulden verminderen",
        ],
        5: [
            "beschikt over vrij besteedbaar inkomen (uit klusjes of (bij)baan) met enige verantwoordelijkheid voor noodzakelijke behoeften",
            "aan het eind van de maand is geld over",
            "geen schulden",
        ],
    },
    "Werk & Opleiding": {
        1: [
            "geen (traject naar) opleiding/werk of werk zonder adequate toerusting/verzekering",
            "geen zoekactiviteiten naar opleiding/werk",
        ],
        2: [
            "geen (traject naar) opleiding/werk",
            "wel zoekactiviteiten gericht op opleiding/werk of ‘papieren’ opleiding (ingeschreven maar niet volgend) of veel schoolverzuim/dreigend ontslag of dreigende dropout",
        ],
        3: [
            "volgt opleiding maar loopt achter of geregeld verzuim van opleiding/werk of volgt traject naar opleiding (trajectbegeleiding, coaching voor schoolverlaters)"
        ],
        4: [
            "op schema met opleiding of heeft startkwalificatie met tijdelijke baan/traject naar opleiding/traject naar werk",
            "zelden ongeoorloofd verzuim",
        ],
        5: [
            "presteert zeer goed op opleiding of heeft startkwalificatie met vaste baan",
            "geen ongeoorloofd verzuim",
        ],
    },
    "Tijdsbesteding": {
        1: [
            "afwezigheid van activiteiten die plezierig/nuttig zijn",
            "of geen structuur in de dag",
            "onregelmatig dag-nacht ritme",
        ],
        2: [
            "nauwelijks activiteiten die plezierig/nuttig zijn",
            "nauwelijks structuur in de dag",
            "afwijkend dag-nacht ritme",
        ],
        3: [
            "onvoldoende activiteiten die plezierig/nuttig zijn maar voldoende structuur in de dag of enige afwijkingen in het dag-nacht ritme"
        ],
        4: [
            "voldoende activiteiten die plezierig/nuttig zijn",
            "dag-nacht ritme heeft geen negatieve invloed op het dagelijks functioneren",
        ],
        5: [
            "tijd is overwegend gevuld met plezierige/nuttige activiteiten",
            "gezond dag-nacht ritme",
        ],
    },
    "Huisvesting": {
        1: ["dakloos of in crisisopvang"],
        2: ["voor wonen ongeschikte huisvesting of dreigende huisuitzetting"],
        3: [
            "veilige, stabiele huisvesting maar slechts marginaal toereikend of verblijft in niet-autonome huisvesting (instelling)"
        ],
        4: [
            "veilige, stabiele en toereikende huisvesting",
            "gedeeltelijk autonome huisvesting (begeleid wonen)",
        ],
        5: [
            "veilige, stabiele en toereikende huisvesting",
            "autonome huisvesting (zelfstandig wonen)",
            "woont bij ouders/verzorgers",
        ],
    },
    "Huiselijke relaties": {
        1: ["geweld in huiselijke kring / kindermishandeling / misbruik / verwaarlozing"],
        2: [
            "relationele problemen met leden van het huishouden of dreigend geweld in huiselijke kring / kindermishandeling / misbruik / verwaarlozing"
        ],
        3: [
            "spanningen in relatie(s) met leden van het huishouden",
            "probeert eigen negatief relationeel gedrag te veranderen",
        ],
        4: [
            "relationele problemen met leden van het huishouden of spanningen tussen leden van het huishouden zijn niet (meer) aanwezig"
        ],
        5: [
            "wordt gesteund en steunt binnen het huishouden",
            "communicatie met leden van het huishouden is consistent open",
        ],
    },
    "Geestelijke gezondheid": {
        1: ["geestelijke noodsituatie", "een gevaar voor zichzelf/anderen"],
        2: [
            "(chronische) geestelijke aandoening maar geen gevaar voor zichzelf/anderen",
            "functioneren is ernstig beperkt door geestelijk gezondheidsprobleem (incl. gedrags- ontwikkelingsproblematiek)",
            "geen behandeling",
        ],
        3: [
            "geestelijke aandoening",
            "functioneren is beperkt door geestelijk gezondheidsprobleem (incl. gedrags- en ontwikkelingsproblematiek)",
            "behandeltrouw is minimaal of beperking bestaat ondanks goede behandeltrouw",
        ],
        4: [
            "minimale tekenen van geestelijke onrust die voorspelbare reactie zijn op stressoren in het leven (ook puberteit)",
            "functioneren is marginaal beperkt door geestelijke onrust",
            "goede behandeltrouw of geen behandeling nodig",
        ],
        5: ["geestelijk gezond", "niet meer dan de dagelijkse beslommeringen/zorgen"],
    },
    "Lichamelijke gezondheid": {
        1: ["een noodgeval/kritieke situatie", "direct medische aandacht nodig"],
        2: [
            "(chronische) lichamelijke aandoening die medische behandeling vereist",
            "functioneren is ernstig beperkt door lichamelijk gezondheidsprobleem",
            "geen behandeling",
        ],
        3: [
            "lichamelijke aandoening",
            "functioneren is beperkt door lichamelijk gezondheidsprobleem",
            "behandeltrouw is minimaal of beperking bestaat ondanks goede behandeltrouw",
        ],
        4: [
            "minimaal lichamelijk ongemak dat samenhangt met dagelijkse activiteiten",
            "functioneren is marginaal beperkt door lichamelijk ongemak",
            "goede behandeltrouw of geen behandeling nodig",
        ],
        5: ["lichamelijk gezond", "gezonde leefstijl (gezonde voeding en voldoende bewegen)"],
    },
    "Middelengebruik": {
        1: [
            "(gedrags-) stoornis/afhankelijk van het gebruik van middelen of van games/gokken/seks/internet",
            "gebruik veroorzaakt/verergert lichamelijke/geestelijke problemen die behandeling vereisen",
        ],
        2: [
            "gebruik van middelen of problematisch ‘gebruik’ van games/gokken/seks/internet",
            "aan gebruik gerelateerde lichamelijke/geestelijke problemen of problemen thuis/op school/op het werk",
            "geen behandeling",
        ],
        3: [
            "gebruik van middelen",
            "geen aan middelengebruik gerelateerde problemen",
            "behandeltrouw is minimaal of beperking bestaat ondanks goede behandeltrouw",
        ],
        4: [
            "geen middelengebruik ondanks sterke drang of behandeling met potentieel verslavende middelen zonder bijgebruik",
            "goede behandeltrouw of geen behandeling nodig",
        ],
        5: ["geen middelengebruik", "geen sterke drang naar gebruik van middelen"],
    },
    "Basale ADL": {
        1: [
            "een gebied van de basale ADL wordt niet uitgevoerd",
            "verhongering of uitdroging of bevuiling/vervuiling",
        ],
        2: ["meerdere gebieden van de basale ADL worden beperkt uitgevoerd"],
        3: [
            "alle gebieden van de basale ADL worden uitgevoerd maar een enkel gebied van de basale ADL wordt beperkt uitgevoerd"
        ],
        4: [
            "geen beperkingen in de uitvoering van de basale ADL",
            "krijgt hulp of gebruikt hulpmiddel",
        ],
        5: [
            "geen beperkingen in de uitvoering van de basale ADL, zoals eten, wassen en aankleden",
            "geen gebruik van hulp(middelen)",
        ],
    },
    "Instrumentele ADL": {
        1: [
            "meerdere gebieden van de instrumentele ADL worden niet uitgevoerd",
            "woningvervuiling of onder-/over-medicatie of geen administratie of voedselvergiftiging",
        ],
        2: [
            "een enkel gebied van de instrumentele ADL wordt niet uitgevoerd of uitvoering op meerdere gebieden is beperkt",
            "weet gezien de leeftijd te weinig van welke instanties er zijn, wat je er mee moet doen en hoe ze te benaderen",
        ],
        3: [
            "alle gebieden van de instrumentele ADL worden uitgevoerd",
            "uitvoering van een enkel gebied van de instrumentele ADL is beperkt",
            "weet beperkt van instanties af en krijgt gezien de leeftijd veel hulp bij het contact met instanties",
        ],
        4: [
            "geen beperkingen in de uitvoering van de instrumentele ADL",
            "krijgt hulp van buiten het huishouden of gebruikt hulpmiddel",
            "weet van instanties af, maar krijgt gezien de leeftijd enige hulp bij het contact leggen",
        ],
        5: [
            "geen beperkingen in de uitvoering van de instrumentele ADL",
            "voert alle gebieden zelfstandig uit",
            "weet welke instanties er zijn, wat je ermee moet doen en hoe ze te benaderen",
        ],
    },
    "Sociaal netwerk": {
        1: [
            "ernstig sociaal isolement",
            "geen steunend contact met familie of met volwassen steunfiguur buiten gezin",
            "geen steunend contact met leeftijdgenoten",
        ],
        2: [
            "geen steunend contact met familie of met volwassen steunfiguur buiten gezin",
            "weinig steunend contact met leeftijdgenoten",
            "veel belemmerend contact",
        ],
        3: [
            "enig steunend contact met familie of met één volwassen steunfiguur buiten het huishouden",
            "enig steunend contact met leeftijdgenoten",
            "weinig belemmerend contact",
        ],
        4: [
            "voldoende steunend contact met familie of met volwassen steunfiguren buiten het huishouden",
            "voldoende steunend contact met leeftijdgenoten",
            "nauwelijks belemmerend contact",
        ],
        5: [
            "gezond sociaal netwerk",
            "veel steunend contact met familie of met volwassen steunfiguur buiten het huishouden",
            "veel steunend contact met leeftijdgenoten",
            "geen belemmerend contact",
        ],
    },
    "Maatschappelijke participatie": {
        1: [
            "niet van toepassing door crisissituatie of in ‘overlevingsmodus’ of veroorzaakt ernstige overlast"
        ],
        2: ["geen maatschappelijke participatie of veroorzaakt overlast"],
        3: [
            "nauwelijks participerend in maatschappij",
            "logistieke, financiële of sociaal-maatschappelijke hindernissen om meer te participeren",
        ],
        4: [
            "enige maatschappelijke participatie (meedoen)",
            "persoonlijke hindernis (motivatie) om meer te participeren",
        ],
        5: ["actief participerend in de maatschappij (bijdragen)"],
    },
    "Justitie": {
        1: ["zeer regelmatig (maandelijks) contact met politie of openstaande zaken bij justitie"],
        2: [
            "regelmatig (meerdere keren per jaar) contact met politie of lopende zaken bij justitie"
        ],
        3: [
            "incidenteel (eens per jaar) contact met politie of voorwaardelijke straf/voorwaardelijke invrijheidstelling"
        ],
        4: ["zelden (minder dan eens per jaar) contact met politie of strafblad"],
        5: ["geen contact met politie", "geen strafblad"],
    },
}

# # For dubugging purposes
# for domain, levels in ASSESSMENT_DOMAINS.items():
#     print(f"Domain: {domain}")
#     for level_number, level in levels.items():
#         print(f"Level: {level_number} ({len(level)})")


# for domain, levels in ASSESSMENT_DOMAINS.items():
#     assessment_domain = AssessmentDomain.objects.create(name=domain)
#     for level_number, level in levels.items():
#         Assessment.objects.create(domain=assessment_domain, level=level_number, content=str(level
# ))
