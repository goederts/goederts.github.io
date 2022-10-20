import os
import re
import shutil


def read_all(file_loc):
    """
    Helper function that reads all the content of a text file
    :param file_loc: string of path to file
    :return: string of content of file
    """
    f = open(file_loc, 'r')
    content = f.read()
    f.close()
    return content


def write_all(file_loc, content):
    """
    Writes all content for a file
    :param file_loc: location of the file to write to
    :param content: content tot write to the file
    """
    f = open(file_loc, 'w')
    f.write(content)
    f.close()


def find_files(src):
    """
    Recursively finds the files in the given folder.
    Returns it as a list
    :param src: path to search in
    :return: list of strings of paths, relative to `path`
    """
    files = []
    for file in os.listdir(src):
        if os.path.isdir(src + file):
            files += [file + "/" + f for f in find_files(src + file + "/")]
        elif not file.startswith("_"):  # ignore partial templates since they get processed differently
            files.append(file)
    return files


def get_values(header_content):
    """
    Reads set value from the header of a document
    :param header_content: Header of a document
    :return: dictionary of variable names to set values
    """
    values = {}
    for line in re.findall("%[a-z]+% = .+\n[\r]?", header_content):
        values[line[:line.index(' ')]] = line[line.index('=') + 2:-1]
    return values


def insert_values(body: str, values: dict[str:str]):
    """
    Inserts that values that the variables are to be set to into the correct positions
    :param body: The body of the document to insert the values into
    :param values: Dictionary of variable name to set value
    :return: New document with values inserted
    """
    variables = re.findall("%[a-z]+%", body)
    for v in variables:
        if v in values:
            body = re.sub(v, values[v], body)
        else:  # value not set in file
            if v != "%content%":  # ignore %content% since this is special case
                body = re.sub(v, "", body)
    return body


def find_partial_references(body):
    """
    Find all references in a document to partial templates
    :param body: Document content of file
    :return: list of tuples (name, dictionary of values, tuple of start and stop of reference)
    see `get_values(...)` documentation for more info on the dictionary of values
    """
    results = []
    regex = "(%_[a-z]+_%\n[\r]?(\s+%[a-z]+% = .+\n[\r]?)+\s+%_[a-z]+_%)"
    for find in re.findall(regex, body):
        find = find[0]
        name = find[1:find.index("_%") + 1]
        values = get_values(find)
        location = body.index(find)
        results.append((name, values, (location, location + len(find))))
    return results


def parse_partial(content, rel_loc):
    r = re.search("(%_[a-z]+_%\n[\r]?(\s*%[a-z]+% = .+\n[\r]?)+\s*%_[a-z]+_%)", content)
    while r is not None:  # while there are references, replace them
        ref = r.group()
        name = ref[1:ref.index("_%") + 1]
        values = get_values(ref)

        partial_loc = name + ".html"
        if "/" in rel_loc:
            rel_to_file = rel_loc[:rel_loc.rindex('/') + 1] + partial_loc
        else:
            rel_to_file = partial_loc

        if os.path.exists('dev/src/' + partial_loc):  # test relative to dev/src
            partial_doc = read_all('dev/src/' + partial_loc)
        elif os.path.exists('dev/src/' + rel_to_file):  # test path relative to document
            partial_doc = read_all('dev/src/' + rel_to_file)
        else:
            raise FileNotFoundError(f"Partial template '{partial_loc}' not found")

        partial_doc = insert_values(partial_doc, values)

        content = content[:r.start()] + partial_doc + content[r.end():]

        r = re.search("(%_[a-z]+_%\n[\r]?(\s*%[a-z]+% = .+\n[\r]?)+\s*%_[a-z]+_%)", content)
    return content


def process_file(template, file_loc: str):
    # Create the folder that contains the file if it doesn't exist
    if "/" in file_loc:
        directory = file_loc[:file_loc.rindex("/")]
        if not os.path.exists(directory):
            os.mkdir(directory)

    # Check if it's a html doc, if not just copy the file to the destination
    if file_loc.endswith('.html'):
        # open all target file content
        file = read_all('dev/src/' + file_loc)

        # split target file into info header and html content
        i = file.index("$ENDHEADER$")
        header = file[:i]
        content = file[i + 11:].strip()

        # make lookup that maps variable partial_loc to set value
        values = get_values(header)

        # replace all variables in template with value from target
        new_doc = insert_values(template, values)

        # handle any partial template references
        content = parse_partial(content, file_loc)

        # insert document content into template
        new_doc = re.sub('%content%', content, new_doc)

        write_all(file_loc, new_doc)

    else:
        shutil.copy("dev/src/" + file_loc, file_loc)  # copy non html file


def main():
    # read all content from parent template
    template = read_all('dev/template.html')

    # find all the variables in the parent template

    files = find_files('dev/src/')
    for file_loc in files:
        process_file(template, file_loc)

    # TODO delete production files that are no longer in dev/src/

if __name__ == "__main__":
    main()
