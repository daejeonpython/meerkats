import math
import pylev
from .en2kr_dict import disease_dict, species_dict

# Use minimum edit distance (Levenshtein distance) to map different strings (e.g., African Swine Fever, africa swine fever, etc.)
# into one predefined term (african swine fever)
def disease_convert(word):
    closest_word = ("", math.inf)
    for key in disease_dict:
        levenshtein_distance = pylev.levenshtein(word, key)
        if levenshtein_distance < closest_word[1]:
            closest_word = (key, levenshtein_distance)

    return disease_dict[closest_word[0]]

def species_convert(word):
    closest_word = ("", math.inf)
    for key in species_dict:
        levenshtein_distance = pylev.levenshtein(word, key)
        if levenshtein_distance < closest_word[1]:
            closest_word = (key, levenshtein_distance)

    return species_dict[closest_word[0]]


if __name__ == "__main__":
    sample = "african swine fever"
    print(disease_convert(sample))

    sample = "wild boar (sus scrofa)"
    print(species_convert(sample))
