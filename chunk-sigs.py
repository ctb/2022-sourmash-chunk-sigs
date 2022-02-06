#! /usr/bin/env python
"""
Break large sketches into many small sketches.
"""
import sys
import argparse

import sourmash
from sourmash import sourmash_args


def chunkify_sketch(ss, chunksize):
    """
    Break signature 'ss' into signatures of size <= chunksize.
    """
    # small? no chunking needed!
    if len(ss.minhash) < chunksize:
        yield ss
        return

    name = ss.name
    filename = ss.filename

    source_mh = ss.minhash
    mh = source_mh.copy_and_clear()
    count = 0
    total = 0

    # iterate through, yielding signatures as we go.
    for hashval in source_mh.hashes:
        mh.add_hash(hashval)
        count += 1
        if count == chunksize:
            total += len(mh)
            yield sourmash.SourmashSignature(mh, name=name,
                                             filename=filename)
            mh = mh.copy_and_clear()

            count = 0

    # leftovers?
    if mh:
        yield sourmash.SourmashSignature(mh, name=name, filename=filename)
        total += len(mh)

    assert total == len(source_mh)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('inp_sigs', nargs='+')
    p.add_argument('-o', '--output', required=True,
                   help="output database location (e.g. .zip)")
    p.add_argument('-m', '--max-hashes-per-sig', default=10000, type=int)
    args = p.parse_args()

    # save to args.output, which should be a zip file or something.
    with sourmash_args.SaveSignaturesToLocation(args.output) as save_sig:

        # for every input file,
        for inp_filename in args.inp_sigs:

            # load as signatures,
            print('loading from', inp_filename)
            db = sourmash.load_file_as_signatures(inp_filename)

            # iterate over,
            for orig_ss in db:
                n_chunks = 0
                total = 0

                # break into chunks.
                for ss in chunkify_sketch(orig_ss, args.max_hashes_per_sig):
                    save_sig.add(ss)
                    total += len(ss.minhash)
                    n_chunks += 1

                assert total == len(orig_ss.minhash)
                print(f'finished sig; {n_chunks} chunks / {total} hashes.')
            


if __name__ == '__main__':
    sys.exit(main())
