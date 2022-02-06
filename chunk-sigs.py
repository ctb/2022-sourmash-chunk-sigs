#! /usr/bin/env python
import sys
import argparse

import sourmash
from sourmash import sourmash_args


def main():
    p = argparse.ArgumentParser()
    p.add_argument('inp_sigs', nargs='+')
    p.add_argument('-o', '--output', required=True,
                   help="output database location (e.g. .zip)")
    p.add_argument('-m', '--max-hashes-per-sig', default=10000, type=int)
    args = p.parse_args()

    with sourmash_args.SaveSignaturesToLocation(args.output) as save_sig:
        for inp_filename in args.inp_sigs:
            print('loading from', inp_filename)
            db = sourmash.load_file_as_signatures(inp_filename)
            for ss in db:
                if len(ss.minhash) < args.max_hashes_per_sig:
                    print('finished')
                    save_sig.add(ss)
                else:
                    name = ss.name
                    filename = ss.filename
                    mh_list = []

                    mh = ss.minhash.copy_and_clear()
                    count = 0
                    for hashval in ss.minhash.hashes:
                        count += 1
                        mh.add_hash(hashval)
                        if count == args.max_hashes_per_sig:
                            print('new', count)
                            mh_list.append(mh)
                            mh = mh.copy_and_clear()
                            count = 0

                    if mh:
                        mh_list.append(mh)

                    for mh in mh_list:
                        new_ss = sourmash.SourmashSignature(mh,
                                                            name=name,
                                                            filename=filename)
                        save_sig.add(new_ss)

                    print(f'finished; 1 to {len(mh_list)} chunks.')


if __name__ == '__main__':
    sys.exit(main())
