"""
Submodule for PyHunter integration into Abaddon
Reference: https://github.com/VonStruddle/PyHunter

>>> x = hunter.domain_search('instagram.com')

>>> for i in x['emails']:
...	 print(i['value'])
... 
charliebeeler@instagram.com
shersiewert@instagram.com
kevin@instagram.com
ralph_kristopher@instagram.com
richardcorrell@instagram.com
jimmybarnes@instagram.com
romanelli@instagram.com
deliasolovyev@instagram.com
press@instagram.com
support@instagram.com
"""

from pyhunter import PyHunter
import json

class HunterioManager:

	def __init__(self):
		self.hunter = PyHunter('72ebe102b85923275c17d6b374551edb56dbb898')

	def get_mails(self, domain, company):
		"""
		Wrapper around domain_search
		"""
		results_file = domain + ".txt"
		try:
			if company!="":
				print(company)
				x = self.hunter.domain_search(company=company)
			else:
				print(domain)
				x = self.hunter.domain_search(domain)
			#json.dumps(json_data["data"])

			with open(results_file, 'w') as file:
				#x="{'domain': 'instagram.com', 'disposable': False, 'webmail': False, 'pattern': '{first}{last}', 'organization': 'Instagram', 'emails': [{'value': 'charliebeeler@instagram.com'}]}"
				#file.write(x) ==> not working
				for i in x['emails']:
					print(i['value'])
		except Exception as e:
			raise e
		print("Go to hunter.io/<domain> and explore the results manually")