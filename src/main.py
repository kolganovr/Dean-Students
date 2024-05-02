from ui import UI, PATH_TO_GRAPHS

def main():
    ui = UI()
    ui.run()

    clearTempFiles()

def clearTempFiles():
    import os
    for file in os.listdir(PATH_TO_GRAPHS):
        if file.endswith(".png"):
            os.remove(PATH_TO_GRAPHS + file)

if __name__ == "__main__":
    main()