"""Executa as fases de dados na ordem; interrompe em qualquer falha."""
import argparse
from .download_data import main as download
from .inspect_data import main as inspect
from .consolidate_data import main as consolidate
from .validate_data import main as validate
from .analyze_data import main as analyze
from .export_bi import main as export
from .verify_bi import main as verify_bi

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--refresh',action='store_true',help='Atualizar snapshot oficial; recalcula hashes e resultados.')
    args=parser.parse_args()
    download(refresh=args.refresh)
    inspect()
    consolidate()
    validate()
    analyze()
    export()
    verify_bi()

if __name__=='__main__':
    main()

