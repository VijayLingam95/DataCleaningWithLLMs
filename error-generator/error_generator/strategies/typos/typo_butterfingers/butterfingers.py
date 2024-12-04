#clone from git https://github.com/Decagon/butter-fingers.git

from random import randint
import random

def butterfinger(text,prob=0.6,keyboard='querty'):

	keyApprox = {}
	
	if keyboard == "querty":
		keyApprox['q'] = "wasedzx"
		keyApprox['w'] = "qesadrfcx"
		keyApprox['e'] = "wrsfdqazxcvgt"
		keyApprox['r'] = "etdgfwsxcvgt"
		keyApprox['t'] = "ryfhgedcvbnju"
		keyApprox['y'] = "tugjhrfvbnji"
		keyApprox['u'] = "yihkjtgbnmlo"
		keyApprox['i'] = "uojlkyhnmlp"
		keyApprox['o'] = "ipklujm"
		keyApprox['p'] = "lo['ik"

		keyApprox['a'] = "qszwxwdce"
		keyApprox['s'] = "wxadrfv"
		keyApprox['d'] = "ecsfaqgbv"
		keyApprox['f'] = "dgrvwsxyhn"
		keyApprox['g'] = "tbfhedcyjn"
		keyApprox['h'] = "yngjfrvkim"
		keyApprox['j'] = "hknugtblom"
		keyApprox['k'] = "jlinyhn"
		keyApprox['l'] = "okmpujn"

		keyApprox['z'] = "axsvde"
		keyApprox['x'] = "zcsdbvfrewq"
		keyApprox['c'] = "xvdfzswergb"
		keyApprox['v'] = "cfbgxdertyn"
		keyApprox['b'] = "vnghcftyun"
		keyApprox['n'] = "bmhjvgtuik"
		keyApprox['m'] = "nkjloik"
		keyApprox[' '] = "#$%^_-!.,'|/"
		keyApprox[':'] = "/.[]?#@*-"
		keyApprox['-'] = "/.[]?#@*:"
	else:
		print ("Keyboard not supported.")

	probOfTypoArray = []
	probOfTypo = int(prob * 100)
	atleastone = False

	buttertext = ""
	for letter in text:
		lcletter = letter.lower()
		if not lcletter in keyApprox.keys():
			newletter = lcletter
		else:
			if random.choice(range(0, 100)) <= probOfTypo:
				newletter = random.choice(keyApprox[lcletter])
				atleastone = True
			else:
				newletter = lcletter
		# go back to original case
		if not lcletter == letter:
			newletter = newletter.upper()
		buttertext += newletter
	
	if not atleastone:
		valid_indexes = [i for i in range(len(text)) if text[i].lower() in keyApprox.keys()]
		replace_idx = random.choice(valid_indexes)
		new_letter = random.choice(keyApprox[text[replace_idx].lower()])
		buttertext = text[:replace_idx]+new_letter+text[replace_idx+1:]

	return buttertext
