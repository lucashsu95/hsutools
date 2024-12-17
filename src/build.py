import subprocess

# build main
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

command = ['pyinstaller', '-F', '--name=hsu']

for req in requirements:
    command.append('--copy-metadata')
    command.append(req.split("==")[0])

command.append('src/main.py')
print(command)
subprocess.run(command,shell=True)


# build setup
command = ['pyinstaller', '-F', '--name=setup' , 'src/setup.py']
subprocess.run(command,shell=True)
