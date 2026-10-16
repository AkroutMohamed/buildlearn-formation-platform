"""Bounded technical fact alignment. Reads only validated claims/selected evidence."""
from dataclasses import asdict, dataclass
import re

from app.ai.rag.answer_validation_v2 import canonical, support_id
from app.ai.rag.semantic_safety_v2 import SemanticSafetyError, resolve_targets, document_key

ATTRIBUTES = {
    'dimensions': r'\b(dimensions?|encombrement)\b',
    'pressure': r'\b(pression|pressure)\b',
    'voltage': r'\b(tension|voltage)\b',
    'power': r'\b(puissance|power)\b',
    'torque': r'\b(couple|torque)\b',
    'speed': r'\b(vitesse|speed|tours par minute)\b',
    'capacity': r'\b(capacite|capacity|contenance)\b',
    'consumption': r'\b(consommation|consumption|dosage)\b',
    'thickness': r'\b(epaisseur|thickness|thick)\b',
    'diameter': r'\b(diametre|diameter|alesage|bore)\b',
    'length': r'\b(longueur|length)\b',
    'width': r'\b(largeur|width)\b',
    'height': r'\b(hauteur|height)\b',
    'depth': r'\b(profondeur|depth)\b',
    'weight': r'\b(poids|weight|masse|mass)\b',
    'water_quantity': r'\b(eau|water)\b',
    'standards': r'\b(normes?|standards?|classification|classe|classement)\b',
    'compatibility': r'\b(supports?.{0,25}(?:admissibles?|interdits?|autorises?|prohibes?)|allowed|prohibited|compatible|convient|admissible|interdit|autorise|ne pas appliquer|not suitable|peut.{0,50}(?:appliquer|utiliser)|can.{0,50}(?:use|used|apply))\b',
}
NUMERIC = set(ATTRIBUTES) - {'standards','compatibility'}
UNITS = {'bar':r'\bbars?\b','psi':r'\bpsi\b','v':r'\b(?:v|volts?)\b','w':r'\b(?:w|watts?)\b',
    'nm':r'\b(?:nm|n[ .-]*m)\b','mm':r'\b(?:mm|millimetres?|millimeters?)\b',
    'cm':r'\b(?:cm|centimetres?|centimeters?)\b','m':r'\b(?:m|metres?|meters?)\b',
    'kg':r'\b(?:kg|kilogrammes?|kilograms?)\b','g':r'\b(?:g|grammes?|grams?)\b',
    'l':r"\b(?:l(?!')|litres?|liters?)\b",'ah':r'\b(?:ah|ampere.heures?)\b',
    'rpm':r'\b(?:rpm|tr\s*/\s*min|tours par minute)\b'}
UNITS.update({'kg/m2':r'\bkg\s*/\s*m(?:2|²)\b','g/m2':r'\bg\s*/\s*m(?:2|²)\b','l/m2':r'\bl\s*/\s*m(?:2|²)\b'})
UNITS['m2']=r'\bm(?:2|²)\b'
# Units may touch their numeric value (18V, 75Nm); letters in an ordinary
# word must not license a unit. No conversion or rounding is performed.
UNITS={u:p.replace(r'\b',r'(?<![a-z])',1) for u,p in UNITS.items()}
ATTRIBUTE_UNITS={'pressure':{'bar','psi'},'voltage':{'v'},'power':{'w'},'torque':{'nm'},
    'speed':{'rpm'},'capacity':{'l','ah'},'dimensions':{'mm','cm','m'},'thickness':{'mm','cm','m'},
    'diameter':{'mm','cm','m'},'length':{'mm','cm','m'},'weight':{'kg','g'},'water_quantity':{'l'},
    'consumption':{'kg','g','l','m','m2','kg/m2','g/m2','l/m2'}}
MINIMUM=r'\b(minimum|minimale?s?|mini|min|au moins|at least)\b|[≥>]'
MAXIMUM=r'\b(maximum|maximale?s?|maxi|max|au plus|at most|jusqu.a|up to)\b|[≤<]'
ATTRIBUTE_UNITS.update({a:{'mm','cm','m'} for a in ('width','height','depth')})
RANGE=r'\b\d+(?:[.,]\d+)?\s*(?:a|to|[-–])\s*\d+(?:[.,]\d+)?\b|\b(?:range|plage|fourchette|entre|between)\b|±|\+\s*/\s*-'
NUMBER=r'\d+(?:[.,]\d+)?'
RANGE_VALUE=(r'(?<![a-z0-9])'+NUMBER+r'\s*(?:a|to|[-–]|±|\+\s*/\s*-)\s*'+NUMBER+r'(?![\d.,])'
    +r'|\b(?:entre|between)\s+'+NUMBER+r'\s*(?:et|and)\s*'+NUMBER+r'(?![\d.,])')
FIRST=r'\b(premiere passe|premiere couche|first[ -]pass|first coat|1ere passe)\b'
TOTAL=r'\b(totale?|total|globale?|overall)\b'


@dataclass(frozen=True)
class RequestedFact:
    product_ids: tuple[str,...]
    attribute: str
    comparison_operator: str | None = None
    polarity: str | None = None
    numeric_qualifier: str | None = None
    unit: str | None = None
    application_stage: str | None = None
    condition: str | None = None
    object_substrate: tuple[str,...] = ()


def requested_facts(question, product_ids):
    q=canonical(question)
    q=re.sub(r'\b(?:sans|without|not)\s+(?:(?:a|any|une|de)\s+)?(?:plage|range|maximum|minimum)\b','',q)
    facts=[]
    # Clause-local qualifiers prevent a minimum pressure from becoming a
    # minimum voltage. Shared qualifiers apply only to a single-attribute clause.
    clauses=re.split(r'[;?]|\bet\b|\band\b',q)
    attrs=[a for a,p in ATTRIBUTES.items() if re.search(p,q)]
    if 'water_quantity' in attrs and not re.search(r'quantite|quantity|combien|how much|litres?|liters?|volume|melanger|mix',q): attrs.remove('water_quantity')
    for attr in attrs:
        pattern=ATTRIBUTES[attr]
        for start in [i for i,c in enumerate(clauses) if re.search(pattern,c)]:
            relevant=[clauses[start]]
            if start and not any(re.search(p,clauses[start-1]) for p in ATTRIBUTES.values()) and re.search(MINIMUM+'|'+MAXIMUM+'|'+FIRST+'|'+TOTAL,clauses[start-1]):
                relevant.insert(0,clauses[start-1])
            for continuation in clauses[start+1:]:
                if any(re.search(p,continuation) for p in ATTRIBUTES.values()):break
                relevant.append(continuation)
            facts.extend(_slots(attr,' '.join(relevant),q,product_ids,len(attrs)==1))
    return tuple(dict.fromkeys(facts))


def _slots(attr,clause,q,product_ids,single_attribute):
        qualifier_clause=_qualifier_view(clause)
        qualifiers=[]
        if re.search(MINIMUM,qualifier_clause):qualifiers.append('minimum')
        if re.search(MAXIMUM,qualifier_clause):qualifiers.append('maximum')
        if not qualifiers:
            qualifiers=['range' if re.search(RANGE,clause) else 'exact' if re.search(r'\b(exacte?|exactly|fixe|fixed)\b',clause) else None]
        stages=[]
        if re.search(FIRST,clause):stages.append('first_pass')
        if re.search(TOTAL,clause):stages.append('total')
        condition='no_load' if re.search(r'a vide|no[ -]load',clause) else 'net' if re.search(r'\bnet\b',clause) else None
        if attr=='diameter' and re.search(r'alesage|bore',clause):condition='bore'
        polarity=None
        if attr=='compatibility':
            polarity='prohibited' if re.search(r'interdit|prohib|not allowed|ne pas|non admis',q) else 'allowed' if re.search(r'admissible|autorise|allowed',q) else 'explicit'
        objects=()
        if attr=='compatibility':
            tail=re.search(r'\b(?:sur|on|avec|with)\s+([^?]+)',q)
            if tail:objects=tuple(sorted(set(re.findall(r'[a-z]{3,}',tail[1]))-{'les','des','the','une','and','avec','sur'}))
        units=sorted(u for u,p in UNITS.items() if u in ATTRIBUTE_UNITS.get(attr,set()) and re.search(p,clause))
        # "pressure in bar and psi" uses a shared attribute across unit clauses.
        if single_attribute:units=sorted(u for u,p in UNITS.items() if u in ATTRIBUTE_UNITS.get(attr,set()) and re.search(p,q))
        conditions=[condition]
        if attr=='diameter':
            conditions=[]
            if re.search(r'interieur|inner|internal',clause):conditions.append('inner')
            if re.search(r'exterieur|outer|external',clause):conditions.append('outer')
            if not conditions:conditions=[condition]
        if attr=='standards':
            conditions=[]
            if re.search(r'normes?|standards?',clause):conditions.append('standard')
            if re.search(r'classification|classe|classement',clause):conditions.append('classification')
        facts=[]
        for unit in units or [None]:
            for product in sorted(product_ids):
                for qualifier in qualifiers:
                    for cond in conditions:
                        operator={'minimum':'>=','maximum':'<=','exact':'=','range':'interval'}.get(qualifier)
                        for stage in stages or [None]:
                            facts.append(RequestedFact((product,),attr,operator or ('comparison' if re.search(r'compar|versus|\bvs\b',q) else None),
                                polarity,qualifier,unit,stage,cond,objects))
        return facts


def segments(text):
    lines=[canonical(s) for s in re.split(r'\n|;|(?<!max)(?<!min)(?<!\d)\.(?!\d)',text,flags=re.I) if s.strip()]
    # Only a label without its own value may carry onto the next line, inside
    # the very same validated excerpt. Never borrow from source/context text.
    grouped=[]
    for line in lines:
        if grouped and grouped[-1].endswith(':') and not any(re.search(p,grouped[-1]) for p in UNITS.values()):
            grouped[-1]+=' '+line
        else:grouped.append(line)
    result=[]
    numeric_patterns='|'.join(ATTRIBUTES[a] for a in sorted(NUMERIC))
    for line in grouped:
        markers=list(re.finditer(numeric_patterns,line))
        starts=[0]+[m.start() for m in markers[1:]]
        ends=starts[1:]+[len(line)]
        result.extend(line[start:end] for start,end in zip(starts,ends))
    return result


def _qualifier_view(text):
    # /min and a duration such as 5 min are minute units, not minima.
    text=re.sub(r'/\s*min\b','/minute',text)
    return re.sub(r'('+NUMBER+r'\s*)min\b',r'\1minute',text)


def matches(fact, text):
    body=canonical(text)
    for line in segments(text):
        qualifier_line=_qualifier_view(line)
        attribute=bool(re.search(ATTRIBUTES[fact.attribute],line))
        if fact.attribute=='thickness' and fact.application_stage=='first_pass':
            attribute=attribute or bool(re.search(FIRST,line) and re.search(UNITS['mm'],line))
        # Unambiguous physical units may establish an attribute, but mm alone
        # never distinguishes a thickness from a length or diameter.
        inferred={'pressure':'bar|psi','voltage':'v','power':'w','torque':'nm','speed':'rpm'}
        if fact.attribute in inferred:
            attribute=attribute or (not any(re.search(ATTRIBUTES[a],line) for a in NUMERIC)
                and any(re.search(UNITS[u],line) for u in inferred[fact.attribute].split('|')))
        standard=bool(re.search(r'\b(?:en|nf|iso|dtu|iec|din)\s*\d',line))
        classification=bool(re.search(r'\b(?:classe|class|type)\s+\w',line))
        if fact.attribute=='standards':attribute=attribute or standard or classification
        if not attribute:continue
        if fact.attribute in NUMERIC and not re.search(r'(?<![a-z0-9])\d+(?:[.,]\d+)?',line):continue
        if fact.attribute in NUMERIC and not any(re.search(UNITS[u],line) for u in ATTRIBUTE_UNITS[fact.attribute]):continue
        if fact.unit and not re.search(UNITS[fact.unit],line):continue
        if fact.numeric_qualifier=='minimum' and (not re.search(MINIMUM,qualifier_line) or re.search(MAXIMUM,qualifier_line)):continue
        if fact.numeric_qualifier=='maximum' and (not re.search(MAXIMUM,qualifier_line) or re.search(MINIMUM,qualifier_line)):continue
        if fact.numeric_qualifier=='range' and not re.search(RANGE_VALUE,line):continue
        if fact.numeric_qualifier=='exact' and (re.search(RANGE_VALUE,line) or re.search(MINIMUM,qualifier_line) or re.search(MAXIMUM,qualifier_line) or re.search(r'environ|about|approx',line)):continue
        if fact.application_stage=='first_pass' and not re.search(FIRST,line):continue
        if fact.application_stage=='total' and not re.search(TOTAL,line):continue
        if fact.condition=='no_load' and not re.search(r'a vide|no[ -]load',line):continue
        if fact.condition=='net' and not re.search(r'\bnet\b',line):continue
        if fact.condition=='bore' and not re.search(r'alesage|bore',line):continue
        if fact.condition=='inner' and not re.search(r'interieur|inner|internal',line):continue
        if fact.condition=='outer' and not re.search(r'exterieur|outer|external',line):continue
        if fact.attribute=='standards' and fact.condition=='standard' and not standard:continue
        if fact.attribute=='standards' and fact.condition=='classification' and not classification:continue
        if fact.attribute=='compatibility':
            # An explicit qualifier may precede a list within this same exact
            # validated excerpt; never borrow a heading from another support.
            negative=bool(re.search(r'interdit|prohib|ne pas|not allowed|not suitable|non admis',body))
            positive=bool(re.search(r'admissible|autorise|allowed|convient|suitable',body))
            if fact.polarity=='prohibited' and not negative:continue
            if fact.polarity=='allowed' and (not positive or negative):continue
            if fact.polarity=='explicit' and not (negative or positive):continue
            if fact.object_substrate and not set(fact.object_substrate)&set(re.findall(r'[a-z]{3,}',body)):continue
        return True
    return False


def context_coverage(facts, sources, owners):
    return [asdict(f) for f in facts if not any(set(f.product_ids)&owners[document_key(s)] and matches(f,s.text) for s in sources)]


def validate_fact_alignment(claims, sources, question, resolver=None):
    products,owners=resolve_targets(question,sources,resolver)
    facts=requested_facts(question,products)
    if not facts:return claims # Explicitly outside this bounded fact vocabulary.
    lookup={support_id(s):s for s in sources}
    covered=set()
    for claim in claims:
        source=lookup[claim['support_chunk_ids'][0]]
        found={i for i,f in enumerate(facts) if set(f.product_ids)&owners[document_key(source)] and matches(f,claim['text'])}
        if not found:raise SemanticSafetyError('requested_fact_mismatch')
        covered.update(found)
    if covered!=set(range(len(facts))):raise SemanticSafetyError('incomplete_requested_fact_coverage')
    return claims
