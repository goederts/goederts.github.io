import os
import re

def find_files(src):
    files = []
    for file in os.listdir(src):
        if os.path.isdir(file):
            files += [file + f for f in find_files(src + file)]
        else:
            files.append(file)
    return files


def combine(template, file_loc: str, variables):
    f = open('dev/src/' + file_loc)
    file = f.read()
    f.close()

    i = file.index("$ENDHEADER$")
    header = file[:i]
    content = file[i+11:].strip()

    values = {}
    for line in re.findall("%[a-z]+% = .+\n", header):
        values[line[:line.index(' ')]] = line[line.index('=') + 2:-1]

    o = template
    for v in variables:
        if v in values:
            o = re.sub(v, values[v], o)
        else:
            if v != "%content%":
                o = re.sub(v, "", o)


    o = re.sub('%content%', content, o)

    f2 = open(file_loc, 'w')
    f2.write(o)
    f2.close()


def main():
    file = open("dev/template.html", 'r')
    template = file.read()
    file.close()
    variables = re.findall("%[a-z]+%", template)

    files = find_files('dev/src/')
    for file in files:
        combine(template, file, variables)



if __name__ == "__main__":
    main()