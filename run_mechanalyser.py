"""PyInstaller entry point for the original MechAnalyser package."""
import sys
from mech_analyser.mech_analyser import Application

if __name__ == '__main__':
    if '--self-test' in sys.argv:
        from mech_analyser.experiment.concrete.smoke import run
        sys.exit(run(sys.argv[sys.argv.index('--self-test')+1:]))
    Application()
