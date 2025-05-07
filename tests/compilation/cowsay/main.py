# /// script
# dependencies = [
#   "requests<3",
#   "rich",
#   "cowsay",
# ]
# ///

import cowsay

if __name__ == "__main__":
    print(f"cowsay version: {cowsay.__version__}")
