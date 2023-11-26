import sys
import subprocess
import filecmp
import os

# with open('test-in', 'w') as file:
#     file.write("a, 9, 0\n")
#     file.write("a, 2, 1\n")
#     file.write("a, 17, 2\n")
#     file.write("f, 0\n")
#     file.write("f, 2\n")
#     file.write("f, 1\n")

# free_list = "implicit"
# fit = "first"
# test_in = "~/assignments/assignment3/test/examples/1.in"





os.chdir("./assignments/assignment3/test")

file_dir = "./examples/"
fileno = 1
input_filepath = file_dir + str(fileno) + ".in"

free_list = "implicit"
fit = "first"

free_lists = ["implicit", "explicit"] 
fits = ["first", "best"]

for fileno in range(1, 13):
    input_filepath = file_dir + str(fileno) + ".in"

    print(f"{'='*20}")
    print(f"Test File: {fileno}")
    print()
    print()

    for free_list in free_lists:
        for fit in fits:
            subprocess.run(["python3", "../memory-simulator.py", f"--free-list={free_list}", f"--fit={fit}", input_filepath])
            orig_out_file = f"./examples/{fileno}.{free_list}.{fit}.out"
            test = filecmp.cmp("./output.txt", orig_out_file)

            print(f"{'-'*80}")
            print(f"{free_list} Free List")
            print(f"{fit} Fit")
            print(f"Test: {test}")
            if not test:
                print(f"{'!'* 100}")
            print(f"{'-'*80}")
            print()
            print()