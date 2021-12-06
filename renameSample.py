from pathlib import Path
import sys

if __name__ == "__main__":
    pdirs = sys.argv[1]
    ppdirs = sorted(Path(pdirs).glob('*'))
    for e in ppdirs:
        # print(e.name[:7])
        directory = e / "Images"
        startNumber = e.name[:7]
        jpegs = sorted(Path(directory).glob('*.jpg'))
        for jpeg in jpegs:
            jpeg.rename(Path(directory) / f"{startNumber}{jpeg.name}")
        