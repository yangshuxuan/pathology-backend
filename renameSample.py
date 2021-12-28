from pathlib import Path
import sys

if __name__ == "__main__":
    pdirs = sys.argv[1]
    num = sys.argv[2]

    e = Path(pdirs)
    directory = e / "Images"
    startNumber = e.name[:7]
    jpegs = sorted(Path(directory).glob('*.jpg'))
    for jpeg in jpegs:
        jpeg.rename(Path(directory) / f"{startNumber}({num}){jpeg.name[7:]}")
        