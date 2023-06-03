import os


def main(supported_types):

    # The number of the lines that are in the whole directory.
    lines_sum = 0

    sum_non_blank = 0

    # All the files in the current directory.
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f != "stats_about_the_project.py" and
                                           f.split(".")[-1] in supported_types and "test" not in f]

    for f in files:

        with open(f, "r") as f1:

            content = f1.readlines()

            lines_sum += len(content)

            content = filter(lambda a: a != "\n", content)

            sum_non_blank += len(content)

    print "Number of lines in project:", lines_sum

    print "Number of lines with content:", sum_non_blank

    print "Percentage of non blank lines:", "{0:.2f}".format((float(sum_non_blank) / lines_sum) * 100), "%"

if __name__ == "__main__":

    main(["py"])