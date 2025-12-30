import asyncio
from collections.abc import Iterable
import os
import pathlib
import random

import aiohttp
from rcsbapi.search import AttributeQuery


def download_structures(pdb_ids: Iterable[str],
                        target_fmt: str,
                        save_fmt: str,
                        outfolder: str,
                        base_url: str = f"https://files.rcsb.org/download/"):

    """
    Downloads structures with the given accession IDs from the RSCB Protein Data Bank

    :param pdb_ids: Iterable of four-digit alphanumeric IDs
    :param format_: File format to download, e.g. "pdb"
    :param outfolder: folder to save downloaded structures. Will be created if it doesn't exist
    :param base_url: url to download from
    :return: two lists: successfully downloaded structures IDs, and tuples of (ID, error message)
    """

    outfolder = pathlib.Path(outfolder)
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)

    structures = []
    errors = []

    asyncio.run(get_structures_from_pdb(base_url, pdb_ids, target_fmt, save_fmt, outfolder, structures, errors))

    return structures, errors

async def get_structures_from_pdb(base_url, pdb_ids, target_fmt, save_fmt, outfolder, structures, errors):

    queue = asyncio.Queue()

    async with aiohttp.ClientSession(base_url) as session:
        download_tasks = [asyncio.create_task(get_structure(session, id_, target_fmt, queue)) for id_ in pdb_ids]
        save_task = asyncio.create_task(save_structure(queue, save_fmt, outfolder, structures, errors))

        await asyncio.gather(*download_tasks)
        await queue.put((None,''))

    return structures, errors


async def get_structure(session: aiohttp.ClientSession,
                        id_: str,
                        target_fmt,
                        queue: asyncio.Queue):

    await asyncio.sleep(0.01)

    async with session.get(target_fmt.format(id_)) as response:
        try:
            response.raise_for_status()
            struct = await response.text()
            result = ("Ok", (id_, struct))
        except aiohttp.ClientResponseError as e:
            result = ("Err", (id_, str(e)))

    await queue.put(result)


async def save_structure(queue, save_fmt, outfolder, structures, errors):

    while True:
        res, data = await queue.get()
        if res is None:
            queue.task_done()
            return structures, errors
        elif res == "Err":
            errors.append(data)
        else:
            name, body = data
            with open(outfolder / save_fmt.format(name), "w") as file:
                file.write(body)
            structures.append(name)
        queue.task_done()


def get_all_pdb_ids():

    """Fetches list of all valid accession IDs from the PDB, and saves it to tests/data folder."""

    query = AttributeQuery(
        attribute="rcsb_entry_container_identifiers.entry_id",
        operator="exists",
        value=None
    )

    ids = [_ + "\n" for _ in query()]
    print(len(ids))

    with open("tests/data/pdb_ids.txt", "w") as file:
        file.writelines(ids)


def pdb_atom_sample(pdb_structures_path, outpath="tests/data/pdb_atom_sample.txt"):

    """
    Randomly selects one ATOM or HETATM record from each pdb file in the structure dataset.

    :param pdb_structures_path: path to folder containing structures
    :param outpath: file to save sample to
    :return:
    """

    structures_path = pathlib.Path(pdb_structures_path)
    pdb_names = [f for f in os.listdir(structures_path) if os.path.isfile(structures_path / f)]

    samples = []

    for filename in pdb_names:
        with open(structures_path / filename) as file:
            atom_records = [line.strip("\n") for line in file.readlines()
                            if line.startswith("ATOM") or line.startswith("HETATM")]
            samples.append(random.choice(atom_records) + f"({filename})")

    with open(outpath, "w") as file:
        file.write("\n".join(samples))

if __name__ == '__main__':

    pdb_files = [filename.strip(".pdb") for filename in os.listdir("data/pdb")]
    pdb_files.pop()

    # pdb_files = ["6LFE"]

    base_url = f"https://www.rcsb.org/fasta/entry/"

    structures, errors = download_structures(pdb_files,
                                             target_fmt="{}",
                                             save_fmt="{}.fasta",
                                             outfolder="./data/fasta/",
                                             base_url=base_url)
    print(errors)

