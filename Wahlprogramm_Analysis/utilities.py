import re
from pathlib import Path
import pdfplumber
from enum import Enum


class Parties(str, Enum):
    AFD = "AfD"
    BSW = "BSW"
    BÜNDNIS_DEUTSCHLAND = "Buendnis-Deutschland"
    UNION = "cdu-csu"
    DIE_GRÜNEN = "Grüne"
    DIE_LINKE = "Linke"
    FAMILIEN_PARTEI = "Familien-Partei"
    FDP = "FDP"
    FREIE_WÄHLER = "Freie-Wähler"
    PARTEI = "Die-Partei"
    PIRATEN = "Die-Piraten"
    SPD = "SPD"
    TIER_SCHUTZ_PARTEI = "Tierschutzpartei"
    VOLT = "Volt"
    ÖDP = "ÖDP"


def normalize_party_name(name):
    # Umlaute manuell ersetzen
    umlaut_replacements = {
        'Ä': 'AE',
        'ä': 'ae',
        'Ö': 'OE',
        'ö': 'oe',
        'Ü': 'UE',
        'ü': 'ue',
        'ß': 'ss'
    }
    for german_char, ascii_replacement in umlaut_replacements.items():
        name = name.replace(german_char, ascii_replacement)

    # Entferne alles außer Buchstaben und Bindestriche und konvertiere in Kleinbuchstaben
    name = re.sub(r'[^a-zA-Z-]+', '', name).lower()
    return name


def replace_linebreaks(content: str):
    # Replace line breaks with spaces
    content = content.replace("-\n", "")
    content = content.replace("- \n", "")
    content = content.replace("\n", " ")
    return content


def remove_disturbances(content: str):
    # Remove groups of non-alphanumeric characters
    content = re.sub(r'\W{3,}', ' ', content)
    return content


def read_election_programs(relative_folder_path: str = "data/election-programs"):
    election_programs = {}
    unmatched_files = []

    print("Lese Parteienprogramme ein...")

    folder_path = Path(__file__).resolve().parent / relative_folder_path

    for pdf_file in folder_path.glob('*.pdf'):
        raw_party_name = pdf_file.stem.split("_")[0]
        party_name = normalize_party_name(raw_party_name)
        matched = False

        print(f"Reading {pdf_file.name}...")

        for party in Parties:
            if party_name == normalize_party_name(party.value):
                with pdfplumber.open(pdf_file) as pdf:
                    content = ''
                    for page in pdf.pages:
                        content += page.extract_text()
                content = replace_linebreaks(content)
                content = remove_disturbances(content)
                election_programs[party.value] = content
                matched = True
                # print green match
                print(f"\033[92mMatched {pdf_file.name} to {party.value}\033[0m")
                break

        if not matched:
            # print red no match
            print(f"\033[91mNo match found for {pdf_file.name}\033[0m")
            unmatched_files.append(pdf_file.name)

    print(f"Unmatched files: {unmatched_files}")

    return election_programs


if __name__ == "__main__":
    programs = read_election_programs()
    print("Gelesene Parteienprogramme:")
    for party_program in programs.keys():
        print(party_program)


def calculate_similarity(sorted_all_words, freq):
    # Calculate the similarity of the two documents
    similarity = 0
    # 100 most common words in election program, extracting just the words
    most_common_words = [word for word, count in freq.most_common(100)]

    for word in sorted_all_words:
        if word in most_common_words:
            similarity += 1

    return similarity
