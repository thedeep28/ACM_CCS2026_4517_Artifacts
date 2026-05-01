import dns.resolver
import dns.rdatatype
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_FILE = "tranco-top1M.txt"
OUTPUT_FILE = "results-top1M-output.jsonl"
RESOLVERS = ["ResolverA, ResolverB, ResolverC, ResolverD"]  # local recursive caching resolvers - hidden for privacy and anonymity
RATE_LIMIT_QPS = 200  # max queries per second
TIMEOUT = 2.0  # seconds
MAX_WORKERS = 200  # match QPS


def query_https(domain, resolver_ip):
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [resolver_ip]
    resolver.timeout = TIMEOUT
    resolver.lifetime = TIMEOUT

    try:
        answer = resolver.resolve(domain, dns.rdatatype.HTTPS, raise_on_no_answer=False)
        raw_answer = [r.to_text() for r in answer] if answer.rrset else []
        return {
            "domain": domain,
            "resolver": resolver_ip,
            "status": "answer" if raw_answer else "no_answer",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "answer_raw": raw_answer
        }
    except Exception as e:
        return {
            "domain": domain,
            "resolver": resolver_ip,
            "status": "error",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "error": str(e),
            "answer_raw": []
        }

def main():
    with open(INPUT_FILE, "r") as f:
        domains = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    total = len(domains)
    print(f"[INFO] Loaded {total} domains.")

    with open(OUTPUT_FILE, "w") as out, ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for i, domain in enumerate(domains):
            resolver_ip = RESOLVERS[i % len(RESOLVERS)]
            futures[executor.submit(query_https, domain, resolver_ip)] = domain

        start = time.time()
        completed = 0

        for future in as_completed(futures):
            result = future.result()
            out.write(json.dumps(result, ensure_ascii=False) + "\n")
            completed += 1

            # crude rate limit logging (not enforcement)
            if completed % 1000 == 0:
                elapsed = time.time() - start
                rate = completed / elapsed
                print(f"[INFO] Processed {completed}/{total} domains — {rate:.1f} QPS")

    print(f"[DONE] All {total} domains processed. Results saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()

