import sys, logging
from mgsquash import MGsquash

logging.basicConfig(level=logging.INFO)
logging.info("Starting MG Squash...")
MGsquash(path=sys.argv[1], silence_len=int(sys.argv[2]), silence_threshold=int(sys.argv[3]))
logging.info("Done!")
