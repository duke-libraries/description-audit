from bs4 import BeautifulSoup
import csv
import pandas as pd
import os
import spacy
from spacy.matcher import PhraseMatcher
from itertools import chain
nlp = spacy.blank("en")


def parse_lexicon(lexicon_csv_path, lexicon_test, hatebase_include):
    """
    Reads in CSV containing lexicon and produces phrase list for matching based on columns
    :param lexicon_csv_path: file path to CSV file containing various phrase lists of potentially harmful or
    otherwise noteworthy terms to identify
    :param lexicon_test: string representing phrase lists to match during process. Multiple lists should be separated
        using underscores. To use all lists present in CSV, argument should be the string "ALL"
    :return: phrase_dict: dictionary with strings keys each representing list of terms to be matched
    """
    if lexicon_test == 'ALL':
        df = pd.read_csv(lexicon_csv_path, header=0)
    else:
        lexicon_test = lexicon_test.split("_")
        df = pd.read_csv(lexicon_csv_path, header=0, usecols=lexicon_test)
    phrase_dict = dict()
    for i in list(df.columns):
        if (i not in ['HateBaseFull', 'HateBaseUnambiguous']) or (hatebase_include == 1):
            phrase_dict[i] = df[i].dropna().to_list()
    return phrase_dict


def file_soup_maker(source_path, file_type):
    """
    Uses os.walk to find and create BS object of each file for parsing/analysis
    :param source_path: relative file path (string) to access directory of EAD entries OR to access single MARCXML file.
     If a single file is passed for EAD analysis, an exception will be raised.
    :param file_type: string representing whether archival structure being searched is EAD or MARCXML
    :return: entries: list of BeautifulSoup objects for each xml file in EAD directory OR of records found in MARCXML
    """
    print("file_soup_maker has been called\n")
    if source_path.endswith(".xml") and file_type == "MARCXML":
        soup = BeautifulSoup(open(source_path, 'r', encoding='utf-8'), features='lxml', from_encoding='utf-8')
        entries = soup.find_all('record')
    else:
        # TODO: This is the last major bottleneck--how to access all of these entries faster?
        entries = [BeautifulSoup(open(os.path.join(path, name), encoding="utf-8"), features="lxml",
                                 from_encoding='utf-8')
                   for path, subdirs, files in os.walk(source_path) for name in files]
    return entries


def structure_builder(file_data, matcher, structure_type):
    """
    Uses list comprehensions to parse and search each archival entry for spaCy matches to provided lexicon
    :param file_data: list of Beautiful Soup objects, either representing full EAD files or MARC records
    :param matcher: spaCy rule-based phrase matcher produced from CSV of terms
    :param structure_type: String indicating the type of archival structure is being parsed, EAD or MARC, to determine
    which information fields must be parsed and accessed for processing
    :return: return_structure: list of dictionaries containing matches and any other pertinent information for any
    archive entries which have matches with the lexicons
    """
    presearch_entries = [entry_parser(entry, structure_type) for entry in file_data]
    searched_entries = [nlp_matcher(matcher, presearch_entry, structure_type) for presearch_entry in presearch_entries]
    return_structure = list(filter(None, searched_entries))
    return return_structure


def entry_parser(entry, structure_type):
    """
    Higher order function to call the appropriate parser for the archive entry given based on the archival structure the
    entry came from--allows for similarities between coding structure for vastly different archival structures
    :param entry: BeautifulSoup object representing an archive entry
    :param structure_type: String representing the archival structure the entry came from
    :return: Appropriate function to parse the given entry
    """
    if structure_type == "EAD":
        return ead_entry_parser(entry)
    else:
        return marc_entry_parser(entry)


def ead_entry_parser(entry):
    """
    Accesses data fields in BeautifulSoup object for EAD entry and adds relevant data to entry dictionary
    :param entry: a BeautifulSoup object made from an XML file for a single entry in the EAD
    :return: entry_data (dictionary): Keyed dictionary containing pertinent information about EAD entry for NLP analysis
    """
    # Get collection info
    eadid = entry.eadid.text
    print(eadid)
    collection_title = entry.archdesc.did.unittitle.text  # might need to remove tabs, newlines
    collection_title = collection_title.split()
    clean_collection_title = ' '.join(collection_title).replace('\\n', '').replace('\\', '')

    # Check for bib number and store
    if entry.find("num", {"type": "aleph"}):
        bib_number = entry.find("num", {"type": "aleph"})
        bib_number = bib_number.text
    else:
        bib_number = 'NULL'
    print(bib_number)

    # Note fields (stuff in <p> tags)
    p_tags = entry.find_all('p')
    p_list = [tag.text for tag in p_tags]
    # Convert giant list object of p text into one big string
    full_note_text = " ".join(p_list)
    # Get rid of extra spaces and clean
    clean_note_text = ' '.join(full_note_text.split()).replace('\\n', '\n').replace("\n", " ")

    # Title fields
    unittitle_tags = entry.find_all('unittitle')
    unittitle_list = [unittitle.text for unittitle in unittitle_tags]
    clean_unittitle_text = ' '.join(unittitle_list).replace('\\n', '\n').replace("\n", " ")
    # print(clean_unittitle_text)

    entry_data = {"eadid": eadid, "bibnumber": bib_number, "collection_title": clean_collection_title,
                  "clean_note_text": clean_note_text, "clean_unittitle_text": clean_unittitle_text}

    return entry_data


def marc_entry_parser(entry):
    """
    Parses relevant information from BeautifulSoup object for a particular MARC archive entry into a dictionary
    :param entry: BeautifulSoup object for a MARC record extracted from XML
    :return: entry_data: Keyed dictionary containing pertinent information about EAD entry for NLP analysis
    """
    entry_data = dict()
    # Get text for certain fields as variables
    if not entry.find('controlfield', {'tag': '001'}):
        entry_data["bib_num"] = "NULL"
    else:
        entry_data["bib_num"] = entry.find('controlfield', {'tag': '001'}).text.strip()
    if not entry.find('datafield', {'tag': '035'}):
        entry_data["oclc_num"] = "NULL"
    elif not entry.find('datafield', {'tag': '035'}).find('subfield', {'code': 'a'}):
        entry_data["oclc_num"] = 'NULL'
    else:
        entry_data["oclc_num"] = entry.find('datafield', {'tag': '035'}).find('subfield', {'code': 'a'}).text.strip()
    if not entry.find('controlfield', {'tag': '005'}):
        entry_data["last_update"] = 'NULL'
    else:
        entry_data["last_update"] = entry.find('controlfield', {'tag': '005'}).text.strip()
    if entry.find('datafield', {'tag': '100'}):
        entry_data["creator"] = "NULL"
        entry_data["creator"] = entry.find('datafield', {'tag': '100'}).text.replace('\n', ' ')
    elif entry.find('datafield', {'tag': '110'}):
        entry_data["creator"] = entry.find('datafield', {'tag': '110'}).text.replace('\n', ' ')
    else:
        entry_data["creator"] = 'NULL'

    title_fields = entry.find_all('datafield', {'tag': '245'})
    title_list = [title.text.strip() for title in title_fields]
    if not title_list:
        entry_data["title"] = 'NULL'
    else:
        entry_data["title"] = ' '.join(title_list).replace('\n', ' ')

    extent_fields = entry.find_all('datafield', {'tag': '300'})
    extent_list = [field.text.strip() for field in extent_fields]
    if not extent_list:
        entry_data["extent"] = 'NULL'
    else:
        entry_data["extent"] = ' '.join(extent_list).replace('\n', ' ')

    # Iterate over multiple 520s and spit out one text string as summary_text
    summary_520_fields = entry.find_all('datafield', {'tag': '520'})
    summary_list = [field.text.strip() for field in summary_520_fields]
    if not summary_list:
        entry_data["summary"] = 'NULL'
    else:
        entry_data["summary"] = ' '.join(summary_list).replace('\n', ' ')

    bionote_545_fields = entry.find_all('datafield', {'tag': '545'})
    bionote_list = [field.text.strip() for field in bionote_545_fields]
    if not bionote_list:
        entry_data["bionote"] = 'NULL'
    else:
        entry_data["bionote"] = ' '.join(bionote_list).replace('\n', ' ')

    print(entry_data["bib_num"])

    return entry_data


def nlp_matcher(matcher, entry_data, structure_type):
    """
    Uses spaCy rule-based phrase matchers to identify presence of terms in specific fields of entry and adds match data
    to entry dictionary
    :param matcher: rule-based phrase matcher created from lexicon CSV. Each CSV column specifies a 'rule' for the
    matcher to use in identifying terms
    :param entry_data: (dictionary) keyed data about a particular library entry, including information which will be
    checked for matches
    :return: entry_data: (dictionary OR None) if any matches are found, they are analyzed and added to dictionary. Else,
    None is returned as there is nothing to report from this item.
    """
    print("nlp_matcher called\n")
    nlp_length_msg = "Text too long to process, please search node manually"
    keys = entry_data.keys()
    matches = dict()
    docs = dict()

    if "clean_note_text" in keys:
        if len(entry_data["clean_note_text"]) > 1000000:  # nlp has max text length of 1000000 chars
            entry_data["nlp_results_notes"] = {"terms": [nlp_length_msg], "context_snippets": [""], "rule_ids": [""],
                                               "type": "note_exception"}
        else:
            notedoc = nlp.make_doc(entry_data["clean_note_text"])
            docs["notes"] = notedoc
            matches["notes"] = matcher(docs["notes"])
        entry_data.pop("clean_note_text")

    if "clean_unittitle_text" in keys:
        if len(entry_data["clean_unittitle_text"]) > 1000000:  # nlp has max text length of 1000000 chars
            entry_data["nlp_results_title"] = {"terms": [nlp_length_msg], "context_snippets": [""], "rule_ids": [""],
                                               "type": "title_exception"}
        else:
            docs["title"] = nlp.make_doc(entry_data["clean_unittitle_text"])
            matches["title"] = matcher(docs["title"])
        entry_data.pop("clean_unittitle_text")

    if "summary" in keys:
        if len(entry_data["summary"]) > 1000000:  # nlp has max text length of 1000000 chars
            entry_data["nlp_results_summary"] = {"terms": [nlp_length_msg], "context_snippets": [""], "rule_ids": [""],
                                                 "type": "summary_exception"}
        else:
            docs["summary"] = nlp.make_doc(entry_data["summary"])
            matches["summary"] = matcher(docs["summary"])
        entry_data.pop("summary")

    if "bionote" in keys:
        if len(entry_data["bionote"]) > 1000000:  # nlp has max text length of 1000000 chars
            entry_data["nlp_results_bionote"] = {"terms": [nlp_length_msg], "context_snippets": [""], "rule_ids": [""],
                                                 "type": "bionote_exception"}
        else:
            docs["bionote"] = nlp.make_doc(entry_data["bionote"])
            matches["bionote"] = matcher(docs["bionote"])
        entry_data.pop("bionote")

    if not any(matches.values()):
        return

    for key in docs.keys():
        if matches[key]:
            keyname = "nlp_results_" + key
            entry_data[keyname] = nlp_result_parser(docs[key], matches[key], structure_type)
            entry_data[keyname]["type"] = key

    print(entry_data)

    return entry_data


def nlp_result_parser(doc, matches, structure_type):
    """
    Analyzes any matches found in a particular doc using a spaCy rule based matcher to determine the term found, its
    context, and which matching rule this term falls in to
    :param doc: spaCy doc object representing particular section which was parsed for matches
    :param matches: list of tuples, each of which contains hashed start and end locations for a match along with the
    hashed match id which can be used to find information such as which rule the matched term fell under
    :return: nlp_results (dictionary of lists): dictionary containing term, context snippets, and rule id's for each
    match found by the spaCy matcher
    """
    terms = []
    context_snippets = []
    rule_ids = []
    for match_id, start, end in matches:
        if structure_type == "EAD":
            context = doc[start - 10:end + 10].text
        else:
            context = doc.text
        terms.append(doc[start:end].text)
        context_snippets.append(context)
        rule_ids.append(nlp.vocab.strings[match_id])
    nlp_results = {"terms": terms, "rule_ids": rule_ids, "context_snippets": context_snippets}
    return nlp_results


def build_csv(output_path, result_struct, file_type, lexicon_test, hatebase_include):
    """
    Creates and writes to CSV using results of NLP matching and data structure of entries.
    :param output_path: (String) file directory path in which created CSV should be stored
    :param result_struct: (list of dicts) data structure containing pertinent information about each entry in archival
    structure and its matches to terms in the lexicon
    :param file_type: (String) type of archival structure, EAD or MARCXML, which was searched and is now being reported
    in CSV format. This determines headings of CSV/keys to access.
    :param lexicon_test: (String) identifies rules being used to detect matches. Used in title of CSV.
    :return: None: this function writes to a CSV file but does not return any data.
    """
    print("CSV writer has been called")
    if file_type == "EAD":
        header = ["eadid", "bibnumber", "collection_title", "match_type", "match_term", "context_snippet", "match_rule"]
    else:
        header = ["oclc_num", "bibnumber", "last_update", "creator", "title", "extent", "match_type", "terms",
                  "context_snippets", "rule_ids"]
    rows = []
    if hatebase_include:
        hatebase = "HB"
    else:
        hatebase = "noHB"
    with open(output_path + "/" + file_type + "_" + lexicon_test + "_" + hatebase + "_nlp_report.csv", 'wt', newline='',
              encoding='utf-8') as csvout:
        for library_item in result_struct:
            if file_type == "EAD":
                repeated_data = [library_item["eadid"],  library_item["bibnumber"],
                                 library_item["collection_title"]]
            if file_type == "MARCXML":
                repeated_data = [library_item["oclc_num"], library_item["bib_num"], library_item["last_update"],
                                 library_item["creator"], library_item["title"], library_item["extent"]]
            if "nlp_results_notes" in library_item.keys():
                [rows.append(list(chain.from_iterable([repeated_data, [library_item["nlp_results_notes"]["type"],
                                                    library_item["nlp_results_notes"]["terms"][count],
                                                    library_item["nlp_results_notes"]["context_snippets"][count],
                                                    library_item["nlp_results_notes"]["rule_ids"][count]]])))
                 for count, value in enumerate(library_item["nlp_results_notes"]["terms"])]
            if "nlp_results_title" in library_item.keys():
                [rows.append(list(chain.from_iterable([repeated_data, [library_item["nlp_results_title"]["type"],
                                                    library_item["nlp_results_title"]["terms"][count],
                                                    library_item["nlp_results_title"]["context_snippets"][count],
                                                    library_item["nlp_results_title"]["rule_ids"][count]]])))
                 for count, value in enumerate(library_item["nlp_results_title"]["terms"])]
            if "nlp_results_summary" in library_item.keys():
                [rows.append(list(chain.from_iterable([repeated_data, [library_item["nlp_results_summary"]["type"],
                                                    library_item["nlp_results_summary"]["terms"][count],
                                                    library_item["nlp_results_summary"]["context_snippets"][count],
                                                    library_item["nlp_results_summary"]["rule_ids"][count]]])))
                 for count, value in enumerate(library_item["nlp_results_summary"]["terms"])]
            if "nlp_results_bionote" in library_item.keys():
                [rows.append(list(chain.from_iterable([repeated_data, [library_item["nlp_results_bionote"]["type"],
                                                    library_item["nlp_results_bionote"]["terms"][count],
                                                    library_item["nlp_results_bionote"]["context_snippets"][count],
                                                    library_item["nlp_results_bionote"]["rule_ids"][count]]])))
                 for count, value in enumerate(library_item["nlp_results_bionote"]["terms"])]
        writer = csv.writer(csvout)
        writer.writerow(header)
        writer.writerows(rows)
        return


def main(lexicon_csv_path, lexicon_test, hatebase_include, output_path, ead_path, marcxml_path):
    """
    Once main arguments have been collected, access raw data, process, and produce outputs that enumerate matches to
    given lexicons
    :param lexicon_csv_path: (String) absolute or relative file path obtained either through GUI or command line
    identifying a CSV file with lists of words in each column that can be used as lists of terms to search through for
    matching terms
    :param lexicon_test: (String) column name(s) to use as lexicons from lexicon CSV. To use multiple columns, separate
    them with a string, or use the string 'ALL' to use all lexicons
    :param hatebase_include: (Bool) True or False value indicating whether to include particularly lengthy or false
    positive-prone lexicons--currently Duke-specific coded, but can be modified in parse_lexicon()
    :param output_path: (String) folder path where
    :param ead_path:
    :param marcxml_path:
    :return: exit status 0 or raise exception
    """
    matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
    phrase_dict = parse_lexicon(lexicon_csv_path, lexicon_test, hatebase_include)
    print(phrase_dict)
    for key in phrase_dict.keys():
        phrase_match = [nlp(term) for term in phrase_dict[key]]
        matcher.add(key, phrase_match)
    if ead_path != 'NONE':
        ead_soup_list = file_soup_maker(ead_path, "EAD")
        searched_ead_structure = structure_builder(ead_soup_list, matcher, "EAD")
        build_csv(output_path, searched_ead_structure, "EAD", lexicon_test, hatebase_include)
    if marcxml_path != "NONE":
        marc_record_list = file_soup_maker(marcxml_path, "MARCXML")
        searched_marc_structure = structure_builder(marc_record_list, matcher, "MARCXML")
        build_csv(output_path, searched_marc_structure, "MARCXML", lexicon_test, hatebase_include)
    return 0
