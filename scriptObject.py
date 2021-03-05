filepath = './new_object.txt'
file_object = open('./ayesaac/nlu_prep/entries/objects.txt', 'a')
with open(filepath) as fp:
    line = fp.readline()
    while line:
        line = fp.readline()
        if (line) :
            line = line.split('"')[0]
            line = line.split(',')[1]
        if ':' in line:
            continue
        file_object.write('\n' + line)
file_object.close()
        