#!/usr/bin/env python3
"""
check_dnssec_ds.py

Usage:
  python3 check_dnssec_ds.py ech_domains.txt --resolvers 1.1.1.1,8.8.8.8,9.9.9.9 --concurrency 50 --rate 200
"""

import argparse
import dns.resolver
import dns.exception
import concurrent.futures
import time
from collections import Counter
from functools import partial

def check_ds(domain, resolver_ip, timeout=3.0):
    """
    Returns: (domain, resolver_ip, status, detail)
    status: 'signed' | 'unsigned' | 'nx' | 'error'
    detail: text message or exception repr
    """
    r = dns.resolver.Resolver(configure=False)
    r.nameservers = [resolver_ip]
    r.timeout = timeout
    r.lifetime = timeout + 1.0
    try:
        # Query DS at the domain (asks the parent for DS)
        # If there is an answer, domain is signed (parent has DS)
        ans = r.resolve(domain, "DS")
        # If we got an answer object with >0 records: signed
        if len(ans) > 0:
            return (domain, resolver_ip, "signed", f"ds_count={len(ans)}")
        else:
            return (domain, resolver_ip, "unsigned", "no DS")
    except dns.resolver.NoAnswer:
        # No DS in parent
        return (domain, resolver_ip, "unsigned", "NoAnswer")
    except dns.resolver.NXDOMAIN:
        return (domain, resolver_ip, "nx", "NXDOMAIN")
    except dns.exception.Timeout:
        return (domain, resolver_ip, "error", "timeout")
    except Exception as e:
        return (domain, resolver_ip, "error", repr(e))


def worker(domain, resolvers, retries=2, backoff=0.2):
    """
    Try each resolver in resolvers in order until we get a non-error result.
    Returns best result tuple as produced by check_ds.
    """
    last_err = None
    for attempt in range(retries):
        for rs in resolvers:
            res = check_ds(domain, rs)
            if res[2] in ("signed", "unsigned", "nx"):
                return res
            last_err = res
        time.sleep(backoff * (attempt + 1))
    # no definitive result
    if last_err:
        domain, resolver_ip, status, detail = last_err
        return (domain, resolver_ip, "error", detail)
    return (domain, resolvers[0], "error", "unknown")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("domains_file", help="one domain per line")
    p.add_argument("--resolvers", default="1.1.1.1,8.8.8.8,9.9.9.9",
                   help="comma-separated resolver IPs to try")
    p.add_argument("--concurrency", type=int, default=100, help="parallel workers")
    p.add_argument("--rate", type=int, default=500, help="max queries per second overall (approx)")
    p.add_argument("--out", default="dnssec_results.csv", help="output CSV")
    args = p.parse_args()

    resolvers = [r.strip() for r in args.resolvers.split(",") if r.strip()]

    with open(args.domains_file) as f:
        domains = [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]

    total = len(domains)
    print(f"Checking {total} domains using resolvers: {resolvers}")

    results = []
    counter = Counter()
    start = time.time()

    # throttle: simplistic global rate control
    sleep_per = max(0.0, 1.0 / float(args.rate))

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as exe:
        futures = {}
        for d in domains:
            futures[exe.submit(worker, d, resolvers)] = d
            time.sleep(sleep_per)
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            # res = (domain, resolver_ip, status, detail)
            results.append(res)
            counter[res[2]] += 1
            if len(results) % 1000 == 0:
                elapsed = time.time() - start
                print(f"{len(results)}/{total} done (elapsed {elapsed:.1f}s). counts: {dict(counter)}")

    elapsed = time.time() - start
    print(f"Done {len(results)} queries in {elapsed:.1f}s")
    print("Summary counts:", dict(counter))

    # write CSV
    import csv
    with open(args.out, "w", newline='') as csvfile:
        w = csv.writer(csvfile)
        w.writerow(["domain", "resolver", "status", "detail"])
        for row in results:
            w.writerow(row)

    signed = counter.get("signed", 0)
    unsigned = counter.get("unsigned", 0)
    nx = counter.get("nx", 0)
    errors = counter.get("error", 0)
    print()
    print(f"signed: {signed} ({signed/total:.3%})")
    print(f"unsigned: {unsigned} ({unsigned/total:.3%})")
    print(f"nx: {nx} ({nx/total:.3%})")
    print(f"errors: {errors} ({errors/total:.3%})")
    print(f"results written to {args.out}")

if __name__ == "__main__":
    main()
