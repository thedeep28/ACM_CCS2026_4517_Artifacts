jq -r '                                   
  select(.answer_raw | length > 0) |
  . as $row |
  .answer_raw[] |
  capture("ech=\"(?<ech>[^\"]+)\"")? |
  "\($row.domain) \(.ech)"
' resultsfile

# Ex: resultsfile = 2026-04-28-results-top1M-5X95N.jsonl