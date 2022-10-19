import os
import re
import shutil

def find_files(src):
    files = []
    for file in os.listdir(src):
        if os.path.isdir(src + file):
            files += [file + "/" + f for f in find_files(src + file + "/")]
        else:
            files.append(file)
    return files


def combine(template, file_loc: str, variables):

    # Create the folder that contains the file if it doesn't exist
    if "/" in file_loc:
        directory = file_loc[:file_loc.rindex("/")]
        if not os.path.exists(directory):
            os.mkdir(directory)

    # Check if it's a html doc, if not just copy the file to the destination
    if file_loc.endswith('.html'):
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

    else:
        shutil.copy("dev/src/" + file_loc, file_loc)


def main():
    file = open("dev/template.html", 'r')
    template = file.read()
    file.close()
    variables = re.findall("%[a-z]+%", template)

    files = find_files('dev/src/')
    for file_loc in files:
        combine(template, file_loc, variables)



if __name__ == "__main__":
    main()