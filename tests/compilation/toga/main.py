# /// script
# dependencies = [
#   "toga"
# ]
# ///

import toga
import os


def button_handler(widget):
    print("hello button")


def build(app):
    box = toga.Box()
    button = toga.Button("Hello world", on_press=button_handler)
    button.style.padding = 50
    button.style.flex = 1
    box.add(button)
    return box


def main():
    app = toga.App("First App", "org.nuitka.helloworld", startup=build)

    if os.getenv("NUITKA_TEST_INTERACTIVE") != "0":
        app.main_loop()


if __name__ == "__main__":
    main()
