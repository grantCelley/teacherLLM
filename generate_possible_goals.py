from guidance import models, assistant, user, system, select, gen

MODEL = "dolphin-mistral:7b-v2.8-q2_K"

CPP_MODEL = "./dolphin-2.8-mistral-7b-v02.Q3_K_M.gguf"

gpt = models.LlamaCppChat(CPP_MODEL, compute_log_probs=True, n_ctx=6000)


def generate_topics(course_name: str, summary: str):
    """
    This will generate topics for a course
    :param course_name: Name of the course to generate the topics for
    :param summary: Summary from wikipedia about the overall topic
    :returns: List[str] List of the topics
    """

    system_prompt = f"You are a professor creating a course for {course_name}. I will give you a wikipedia summary. Generate a the topics for a 14 week schedule."
    user_prompt = summary

    response = ""

    with system():
        lm = gpt + system_prompt
    with user():
        lm += user_prompt
    with assistant():
         lm += gen("response", max_tokens=2000, temperature=0.7)

    content = lm["response"]
    content = content[content.find("**"):]
    topics = []
    weeks = content.split('\n\n')
    for week in weeks:
        first_line = week[:week.find('\n')]
        begain = first_line.rfind('**')
        topic=first_line[begain + 3:]
        topics.append(topic)
        

    return topics

def is_section_Important(course_name: str, section:str, topic_list: list[str]):
    """
    This will check if the course is important based on the given course name and the given topic list
    :param course_name: Name of the course to generate the topics for
    :param summary: Summary from wikipedia about the overall topic
    :returns: List[str] List of the topics
    """

    topic_list.append("None")
    topic_str = '\n* '.join(topic_list)
    topic_str = '\n* ' + topic_str

    system_prompt = f"You are a professor creating a course for {course_name}. I will give you a wikipedia section and a list of topics. Tell me if the section would be part of any of the topics. If the section does not fall into any of the topics just type 'None'. The topics are:\n{topic_str}"

    user_prompt = f"Wikipedia Section:\n{section}\n\n Topics:{topic_str}\nWhat topic is would the selection be part of? Just classify it."

    answer = ""
    with system():
        lm = gpt + system_prompt
    with user():
        lm += user_prompt
    with assistant():
        lm += select(topic_list, name=answer)

    if answer == "None":
        return False
    else:
        return True
    

topic_list = ['Introduction to Microbiology', 'Bacteria', 'Archaea and Eukaryotes', 'Viruses', 'Protists', 'Fungi', 'Immunology and Parasitology', 'Microbial Genomics', 'Bacterial Pathogens', 'Viral Pathogens', 'Fungal Pathogens', 'Parasitic Pathogens', 'Microbial Ecology', 'Review and Final Exam']

section = "\nWhile some people have [[Mysophobia|fear of microbes]] due to the association of some microbes with various human diseases, many microbes are also responsible for numerous beneficial processes such as [[industrial fermentation]] (e.g. the production of [[Ethanol|alcohol]], [[vinegar]] and [[dairy products]]), [[antibiotic]] production and act as molecular vehicles to transfer DNA to complex organisms such as plants and animals. Scientists have also exploited their knowledge of microbes to produce biotechnologically important [[enzyme]]s such as [[Taq polymerase]],<ref>{{Cite book| vauthors = Gelfand DH |chapter=Taq DNA Polymerase|date=1989|work=PCR Technology: Principles and Applications for DNA Amplification|pages=17\u201322| veditors = Erlich HA |publisher=Palgrave Macmillan UK|language=en|doi=10.1007/978-1-349-20235-5_2|isbn=978-1-349-20235-5|title=PCR Technology|s2cid=100860897 }}</ref> [[reporter gene]]s for use in other genetic systems and novel molecular biology techniques such as the [[two-hybrid screening|yeast two-hybrid system]].<ref>{{Cite journal |last=Uetz |first=Peter |date=December 2012 |title=Editorial for \"The Yeast two-hybrid system\" |url=https://pubmed.ncbi.nlm.nih.gov/23317557/ |journal=Methods |volume=58 |issue=4 |pages=315\u2013316 |doi=10.1016/j.ymeth.2013.01.001 |issn=1095-9130 |pmid=23317557}}</ref>\n\nBacteria can be used for the industrial production of [[amino acid]]s. [[organic acids]], [[vitamin]], [[proteins]], [[antibiotics]] and other commerically used metabolites with are produced by microorganisms. ''[[Corynebacterium glutamicum]]'' is one of the most important bacterial species with an annual production of more than two million tons of amino acids, mainly L-glutamate and L-lysine.<ref name= BurkovskiA>{{cite book | veditors = Burkovski A | title = Corynebacteria: Genomics and Molecular Biology | publisher = Caister Academic Press | year = 2008 | url=http://www.horizonpress.com/cory | isbn =978-1-904455-30-1 | access-date = 2016-03-25}}</ref> Since some bacteria have the ability to synthesize antibiotics, they are used for medicinal purposes, such as ''[[Streptomyces]]'' to make [[aminoglycoside antibiotics]].<ref name= \"Puglisi, Joseph D.\">{{cite journal | vauthors = Fourmy D, Recht MI, Blanchard SC, Puglisi JD | title = Structure of the A site of Escherichia coli 16S ribosomal RNA complexed with an aminoglycoside antibiotic | journal = Science | volume = 274 | issue = 5291 | pages = 1367\u20131371 | date = November 1996 | pmid = 8910275 | doi = 10.1126/science.274.5291.1367 | s2cid = 21602792 | bibcode = 1996Sci...274.1367F }}</ref>\n\n[[File:Cuves de fermentations.jpg|thumb|upright|left|Fermenting tanks with [[yeast]] being used to [[Brewing|brew]] [[beer]] ]]\n\nA variety of [[biopolymer]]s, such as [[polysaccharide]]s, [[polyester]]s, and [[polyamide]]s, are produced by microorganisms. Microorganisms are used for the biotechnological production of biopolymers with tailored properties suitable for high-value medical application such as [[tissue engineering]] and drug delivery. Microorganisms are for example used for the biosynthesis of [[xanthan]], [[alginate]], [[cellulose]], [[cyanophycin]], poly(gamma-glutamic acid), [[levan polysaccharide|levan]], [[hyaluronic acid]], organic acids, [[oligosaccharide]]s [[polysaccharide]] and polyhydroxyalkanoates.<ref name= RehmBHA>{{cite book | veditors = Rehm BH | title = Microbial Production of Biopolymers and Polymer Precursors: Applications and Perspectives | publisher = Caister Academic Press | year = 2008 | url=http://www.horizonpress.com/biopolymers | isbn =978-1-904455-36-3 | access-date = 2016-03-25}}</ref>\n\nMicroorganisms are beneficial for [[microbial biodegradation]] or [[bioremediation]] of domestic, agricultural and industrial wastes and subsurface [[pollution]] in soils, sediments and marine environments. The ability of each microorganism to degrade [[toxic waste]] depends on the nature of each [[contaminant]]. Since sites typically have multiple pollutant types, the most effective approach to [[microbial biodegradation]] is to use a mixture of bacterial and fungal species and strains, each specific to the [[biodegradation]] of one or more types of contaminants.<ref name=Diaz>{{cite book | veditors = Diaz E | title = Microbial Biodegradation: Genomics and Molecular Biology | edition = 1st | publisher = Caister Academic Press | year = 2008 | url = https://archive.org/details/microbialbiodegr0000unse | isbn = 978-1-904455-17-2 | access-date = 2016-03-25 | url-access = registration }}</ref>\n\n[[Mutualism (biology)|Symbiotic]] microbial communities confer benefits to their human and animal hosts health including aiding digestion, producing beneficial vitamins and amino acids, and suppressing pathogenic microbes. Some benefit may be conferred by eating fermented foods, [[probiotics]] (bacteria potentially beneficial to the digestive system) or [[prebiotics]] (substances consumed to promote the growth of probiotic microorganisms).<ref>{{cite journal | vauthors = Macfarlane GT, Cummings JH | title = Probiotics and prebiotics: can regulating the activities of intestinal bacteria benefit health? | journal = BMJ | volume = 318 | issue = 7189 | pages = 999\u20131003 | date = April 1999 | pmid = 10195977 | pmc = 1115424 | doi = 10.1136/bmj.318.7189.999 }}</ref><ref name=Tannockpro3>{{cite book | veditors = Tannock GW | title = Probiotics and Prebiotics: Scientific Aspects | publisher = Caister Academic Press | year = 2005 | url=http://www.horizonpress.com/pro3 | isbn =978-1-904455-01-1 | access-date = 2016-03-25}}</ref> The ways the microbiome influences human and animal health, as well as methods to influence the microbiome are active areas of research.<ref>{{cite magazine|url=http://www.scientificamerican.com/article.cfm?id=strange-but-true-humans-carry-more-bacterial-cells-than-human-ones|title=Humans Carry More Bacterial Cells than Human Ones| vauthors = Wenner M |magazine= Scientific American|date=30 November 2007|access-date=14 April 2017}}</ref>\n\nResearch has suggested that microorganisms could be useful in the treatment of [[cancer]]. Various strains of non-pathogenic [[Clostridium|clostridia]] can infiltrate and replicate within solid [[tumors]]. Clostridial vectors can be safely administered and their potential to deliver therapeutic proteins has been demonstrated in a variety of preclinical models.<ref name= Mengesha>{{cite book | vauthors = Mengesha A, Dubois L, Paesmans K, Wouters B, Lambin P, Theys J |year=2009|chapter=Clostridia in Anti-tumor Therapy | veditors = Br\u00fcggemann H, Gottschalk G |title=Clostridia: Molecular Biology in the Post-genomic Era|publisher=Caister Academic Press|isbn = 978-1-904455-38-7 }}</ref>\n\nSome bacteria are used to study fundamental mechanisms. An example of model bacteria used to study [[motility]]<ref>{{cite journal | vauthors = Zusman DR, Scott AE, Yang Z, Kirby JR | title = Chemosensory pathways, motility and development in Myxococcus xanthus | journal = Nature Reviews. Microbiology | volume = 5 | issue = 11 | pages = 862\u2013872 | date = November 2007 | pmid = 17922045 | doi = 10.1038/nrmicro1770 | s2cid = 2340386 }}</ref> or the production of polysaccharides and development is ''[[Myxococcus xanthus]]''.<ref>{{cite journal | vauthors = Islam ST, Vergara Alvarez I, Sa\u00efdi F, Guiseppi A, Vinogradov E, Sharma G, Espinosa L, Morrone C, Brasseur G, Guillemot JF, Benarouche A, Bridot JL, Ravicoularamin G, Cagna A, Gauthier C, Singer M, Fierobe HP, Mignot T, Mauriello EM | display-authors = 6 | title = Modulation of bacterial multicellularity via spatio-specific polysaccharide secretion | journal = PLOS Biology | volume = 18 | issue = 6 | pages = e3000728 | date = June 2020 | pmid = 32516311 | pmc = 7310880 | doi = 10.1371/journal.pbio.3000728 | doi-access = free }}</ref>\n<!-- These traits allowed Joshua and Esther Lederberg to devise an elegant experiment in 1951 demonstrating that [[adaptive mutation]]s arise from [[preadaptation]] rather than [[directed mutation]]. For this purpose, they invented [[replica plating]], which allowed them to transfer numerous [[colony (biology)|bacterial colonies]] from their specific locations on one [[agar]]-filled [[petri dish]] to analogous locations on several other petri dishes. After replicating a plate of ''E. coli'', they exposed each of the new plates to a [[bacteriophage]]. They observed that phage-resistant colonies were present at analogous locations on each of the plates, allowing them to conclude that the phage resistance trait had existed in the original colony, which had never been exposed to phage, instead of arising after the bacteria had been exposed to the virus.-->\n\n"

print(is_section_Important("Microbiology", section, topic_list))