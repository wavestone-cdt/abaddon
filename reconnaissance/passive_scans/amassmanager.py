import subprocess

class AmassManager:

	def get_results(self, domain):
		"""
		Wrapper around docker commands
		docker build -t amass https://github.com/OWASP/Amass.git
		docker run -v OUTPUT_DIR_PATH:/.config/amass/ amass enum -brute -w /wordlists/all.txt -d example.com
		=> replace enum -brute -w /wordlists/all.txt & example.com with arguments to be provided from the GUI
		==> cf https://github.com/OWASP/Amass/blob/master/doc/user_guide.md
		"""
		amass_command = "enum"
		amass_options = "-brute -w /wordlists/all.txt"
		amass_domain = domain
		
		docker_command = "docker run -v amass_results:/.config/amass/ amass " + amass_command + " " + amass_options + " -d " + amass_domain
		print(docker_command)
		try:
			subprocess.call(docker_command, shell=True)
		except Exception as e:
			raise e
		print("Go to the reconnaissance/passive_scans/amass_results directory and explore the results manually")