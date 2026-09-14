"""Descobre os sete recursos CSV oficiais; baixa ZIPs e extrai só o CSV.

Execução: python -m src.download_data [--refresh]
O manifesto fixa URLs, IDs, horários, tamanhos e SHA-256 do snapshot.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import re
import shutil
import zipfile
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .common import ROOT, RAW, EVIDENCE, YEARS, PORTAL, setup, sha256, now, write_json

def session():
    s = requests.Session()
    s.headers['User-Agent'] = 'BPS-academic-reproducible-analysis/1.0'
    s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
    return s

def discover():
    response = session().get(PORTAL, timeout=(20, 120))
    response.raise_for_status()
    html = response.content.decode('utf-8')
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not match:
        raise RuntimeError('Metadados do portal mudaram. Rever descoberta; não adivinhar URLs.')
    metadata = json.loads(match.group(1))['props']['pageProps']
    write_json(EVIDENCE / 'portal_metadata.json', metadata)
    resources = {}
    for resource in metadata['resources']:
        year_match = re.search(r'\b(202[0-6])\b', resource.get('name', ''))
        if resource['format'].upper() == 'CSV' and year_match:
            year = int(year_match.group(1))
            if year in resources:
                raise ValueError(f'Mais de um CSV para {year}; requer investigação.')
            resources[year] = resource
    if set(resources) != set(YEARS):
        raise ValueError(f'Anos encontrados: {sorted(resources)}. Exigidos: {YEARS}.')
    return metadata, resources

def download_one(year, resource):
    cache = ROOT / 'data/cache'
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / f'{year}.zip'
    partial = archive.with_suffix('.part')
    with session().get(resource['url'], stream=True, timeout=(20, 180)) as response:
        response.raise_for_status()
        with partial.open('wb') as handle:
            for chunk in response.iter_content(1024 * 1024):
                handle.write(chunk)
        expected = response.headers.get('Content-Length')
        if expected and partial.stat().st_size != int(expected):
            raise ValueError(f'Download incompleto: {year}')
        headers = {k: response.headers.get(k) for k in ('ETag', 'Last-Modified', 'Content-Length', 'Content-Type')}
    partial.replace(archive)
    with zipfile.ZipFile(archive) as zipped:
        candidates = [x for x in zipped.infolist() if x.filename.lower().endswith('.csv') and not x.is_dir()]
        if len(candidates) != 1:
            raise ValueError(f'{year}: esperado exatamente um CSV, encontrados {len(candidates)}')
        member = candidates[0]
        destination = RAW / f'BPS_{year}.csv'
        # Caminho de saída fixo; não usa extractall nem caminhos recebidos no ZIP.
        with zipped.open(member) as source, destination.with_suffix('.part').open('wb') as target:
            shutil.copyfileobj(source, target)
        destination.with_suffix('.part').replace(destination)
    evidence = dict(year=year, resource_id=resource['id'], resource_name=resource['name'],
                    url=resource['url'], resource_page=f"{PORTAL}/resource/{resource['id']}",
                    metadata_modified=resource.get('metadata_modified'), downloaded_at=now(),
                    http_headers=headers, archive_sha256=sha256(archive), archive_bytes=archive.stat().st_size,
                    member_name=member.filename, csv_path=str(destination.relative_to(ROOT)),
                    csv_bytes=destination.stat().st_size, csv_sha256=sha256(destination))
    print(f'{year}: {evidence["csv_bytes"]:,} bytes; SHA-256 {evidence["csv_sha256"]}', flush=True)
    return evidence

def main(refresh=False):
    setup()
    manifest_file = EVIDENCE / 'source_manifest.json'
    if manifest_file.exists() and not refresh:
        saved = json.loads(manifest_file.read_text(encoding='utf-8'))
        if all((ROOT / x['csv_path']).exists() and sha256(ROOT / x['csv_path']) == x['csv_sha256'] for x in saved['files']) and {x['year'] for x in saved['files']} == set(YEARS):
            print('Snapshot local verificado por SHA-256. Use --refresh para nova versão oficial.')
            return
    metadata, resources = discover()
    with ThreadPoolExecutor(max_workers=3) as pool:
        files = list(pool.map(lambda y: download_one(y, resources[y]), YEARS))
    dictionary = next(x for x in metadata['resources'] if x['id'] == '0e76f527-5e7e-417d-9d0b-f46d00afb717')
    response = session().get(dictionary['url'], timeout=(20, 120))
    response.raise_for_status()
    dictionary_path = EVIDENCE / 'official_data_dictionary.pdf'
    dictionary_path.write_bytes(response.content)
    write_json(manifest_file, dict(portal=PORTAL, obtained_at=now(), years=list(YEARS),
               dictionary=dict(url=dictionary['url'], sha256=sha256(dictionary_path)), files=files))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true')
    main(parser.parse_args().refresh)

