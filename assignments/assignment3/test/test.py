import sys
import subprocess
import filecmp

with open('test-in', 'w') as file:
    file.write("a, 9, 0\n")
    file.write("a, 2, 1\n")
    file.write("a, 17, 2\n")
    file.write("f, 0\n")
    file.write("f, 2\n")
    file.write("f, 1\n")

free_list = "implicit"
fit = "first"
test_in = "~/assignments/assignment3/test/examples/1.in"

subprocess.run(["./A3-ref", "-o", "./teacher-test-out", f"--free-list={free_list}", f"--fit={fit}", f"{test_in}"])

with open("my-test-out", 'r') as outfile:
    subprocess.run(["python3", "../memory-simulator.py", "-v", f"--free-list={free_list}", f"--fit={fit}", f"{test_in}"], stdout=outfile)


print(filecmp.cmp('./teacher-test-out', 'my-test-out'))





