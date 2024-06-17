import time
import pyautogui
from num2words import num2words

# Fonction pour compter le nombre de caractères sans les espaces et les tirets
def count_letters(word):
    return len(word.replace(" ", "").replace("-", ""))

# Liste pour stocker les résultats
results = []

# Boucle pour vérifier chaque nombre de 0 à 10000
for num in range(4000, 10001):
    # Convertir le nombre en mots en français
    words = num2words(num, lang='fr')
    # Compter les caractères sans espaces ni tirets
    if count_letters(words) == 30:
        results.append((num, words.replace(" ", "").replace("-", "")))

# Fonction pour cliquer avec la souris et saisir un nombre
def click_and_type(number_str):
    # Cliquer à la position actuelle de la souris
    pyautogui.click()
    # Saisir le nombre
    pyautogui.typewrite(number_str)
    # Appuyer sur 'Enter' pour valider la saisie
    pyautogui.press('enter')

# Boucle principale
while results:
    # Prendre le premier élément de la liste
    num, words = results.pop(0)
    # Effectuer le clic et saisir le nombre en toutes lettres
    click_and_type(str(num))
    # Attendre 50 secondes
    time.sleep(2)

print("""Tous les nombres ont ét 3672367636813734374137423745374737483749375637613762376533865
38623867

3861
3856
3849
3848
3847
3845
3842
3841
3834
3780
3769
3768é saisis.""")


767














