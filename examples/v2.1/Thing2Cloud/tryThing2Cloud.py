import time
import subprocess

print("To connect to EduBlocks open Your Computers Browser")
print("url: http://thing2cloud.co.uk")
print("select: Raspberry Pi")
print("enter the following IP address in the dialog box")
subprocess.run(["hostname", "-I"]) 

subprocess.run(['edublocks-connect'])


